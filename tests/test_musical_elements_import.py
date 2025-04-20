"""
Tests for importing musical elements from MusicXML files.
"""

import pytest
import tempfile
import os
import xml.etree.ElementTree as ET

from pymusicxml.importers.musical_elements import MusicalElementsImporter
from pymusicxml.score_components import Note, Rest, BarRest, Chord, Pitch, Duration, Notehead


def create_test_note_element(step="C", alter=0, octave=4, duration=4, note_type="quarter", 
                             dots=0, grace=False, chord=False, rest=False, measure_rest=False):
    """Helper function to create a test note element."""
    note_elem = ET.Element("note")
    
    if chord:
        ET.SubElement(note_elem, "chord")
    
    if grace:
        ET.SubElement(note_elem, "grace")
    
    if rest:
        rest_elem = ET.SubElement(note_elem, "rest")
        if measure_rest:
            rest_elem.set("measure", "yes")
    else:
        pitch_elem = ET.SubElement(note_elem, "pitch")
        ET.SubElement(pitch_elem, "step").text = step
        if alter != 0:
            ET.SubElement(pitch_elem, "alter").text = str(alter)
        ET.SubElement(pitch_elem, "octave").text = str(octave)
    
    if not grace:
        ET.SubElement(note_elem, "duration").text = str(duration)
    
    ET.SubElement(note_elem, "type").text = note_type
    
    for _ in range(dots):
        ET.SubElement(note_elem, "dot")
    
    return note_elem


def test_import_pitch():
    """Test importing a pitch from MusicXML."""
    note_elem = create_test_note_element(step="D", alter=1, octave=5)
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    pitch = MusicalElementsImporter.import_pitch(note_elem, find_element, get_text)
    
    assert pitch is not None
    assert pitch.step == "D"
    assert pitch.alteration == 1.0
    assert pitch.octave == 5


def test_import_duration():
    """Test importing a duration from MusicXML."""
    # Test regular quarter note
    note_elem = create_test_note_element(note_type="quarter", dots=0)
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements if len(elements) > 1 else (elements[0] if elements else None)
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None else default
    
    duration = MusicalElementsImporter.import_duration(note_elem, find_element, get_text)
    
    assert duration is not None
    assert duration.note_type == "quarter"
    assert duration.num_dots == 0
    assert duration.tuplet_ratio is None
    
    # Test dotted half note
    note_elem = create_test_note_element(note_type="half", dots=1)
    duration = MusicalElementsImporter.import_duration(note_elem, find_element, get_text)
    
    assert duration is not None
    assert duration.note_type == "half"
    assert duration.num_dots == 1
    assert duration.tuplet_ratio is None


def test_import_regular_note():
    """Test importing a regular note from MusicXML."""
    note_elem = create_test_note_element(step="E", alter=-1, octave=4, note_type="eighth")
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements if len(elements) > 1 else (elements[0] if elements else None)
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None else default
        
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    note = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
    
    assert note is not None
    assert isinstance(note, Note)
    assert note.pitch.step == "E"
    assert note.pitch.alteration == -1.0
    assert note.pitch.octave == 4
    assert note.duration.note_type == "eighth"


def test_import_rest():
    """Test importing a rest from MusicXML."""
    note_elem = create_test_note_element(rest=True, note_type="quarter")
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements if len(elements) > 1 else (elements[0] if elements else None)
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None else default
        
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    rest = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
    
    assert rest is not None
    assert isinstance(rest, Rest)
    assert rest.duration.note_type == "quarter"


def test_import_bar_rest():
    """Test importing a measure rest from MusicXML."""
    note_elem = create_test_note_element(rest=True, measure_rest=True, note_type="whole")
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements if len(elements) > 1 else (elements[0] if elements else None)
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None else default
        
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    bar_rest = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
    
    assert bar_rest is not None
    assert isinstance(bar_rest, BarRest)
    assert bar_rest.true_length > 0  # BarRest uses true_length, not bar_length


def test_import_chord():
    """Test importing a chord from MusicXML."""
    # Create a chord with two notes
    note1 = create_test_note_element(step="C", octave=4, note_type="quarter")
    note2 = create_test_note_element(step="E", octave=4, note_type="quarter", chord=True)
    note3 = create_test_note_element(step="G", octave=4, note_type="quarter", chord=True)
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements if len(elements) > 1 else (elements[0] if elements else None)
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None else default
        
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    chord = MusicalElementsImporter.import_chord(note1, [note1, note2, note3], find_element, get_text, find_elements)
    
    assert chord is not None
    assert isinstance(chord, Chord)
    assert len(chord.pitches) == 3
    assert chord.pitches[0].step == "C"
    assert chord.pitches[1].step == "E"
    assert chord.pitches[2].step == "G"
    assert chord.duration.note_type == "quarter"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 