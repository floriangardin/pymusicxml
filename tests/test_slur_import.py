"""
Tests for importing slurs from MusicXML files.
"""

import pytest
import xml.etree.ElementTree as ET

from pymusicxml.importers.musical_elements import MusicalElementsImporter
from pymusicxml.spanners import StartSlur, StopSlur


def create_test_note_with_slur(step="C", octave=4, slur_type=None, slur_number="1"):
    """Helper function to create a test note element with a slur."""
    note_elem = ET.Element("note")
    
    # Create pitch element
    pitch_elem = ET.SubElement(note_elem, "pitch")
    ET.SubElement(pitch_elem, "step").text = step
    ET.SubElement(pitch_elem, "octave").text = str(octave)
    
    # Add duration and type
    ET.SubElement(note_elem, "duration").text = "4"
    ET.SubElement(note_elem, "type").text = "quarter"
    
    # Add notations with slur if specified
    if slur_type:
        notations_elem = ET.SubElement(note_elem, "notations")
        slur_elem = ET.SubElement(notations_elem, "slur")
        slur_elem.set("type", slur_type)
        slur_elem.set("number", slur_number)
    
    return note_elem


def test_import_start_slur():
    """Test importing a note with a start slur notation."""
    note_elem = create_test_note_with_slur(slur_type="start", slur_number="1")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
    
    assert len(notations) == 1
    assert isinstance(notations[0], StartSlur)
    assert notations[0].label == "1"


def test_import_stop_slur():
    """Test importing a note with a stop slur notation."""
    note_elem = create_test_note_with_slur(slur_type="stop", slur_number="1")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
    
    assert len(notations) == 1
    assert isinstance(notations[0], StopSlur)
    assert notations[0].label == "1"


def test_import_multiple_slurs():
    """Test importing a note with multiple slurs."""
    # Create a note with two slurs (one start, one stop)
    note_elem = ET.Element("note")
    
    # Create pitch element
    pitch_elem = ET.SubElement(note_elem, "pitch")
    ET.SubElement(pitch_elem, "step").text = "C"
    ET.SubElement(pitch_elem, "octave").text = "4"
    
    # Add duration and type
    ET.SubElement(note_elem, "duration").text = "4"
    ET.SubElement(note_elem, "type").text = "quarter"
    
    # Add notations with multiple slurs
    notations_elem = ET.SubElement(note_elem, "notations")
    
    slur1_elem = ET.SubElement(notations_elem, "slur")
    slur1_elem.set("type", "start")
    slur1_elem.set("number", "1")
    
    slur2_elem = ET.SubElement(notations_elem, "slur")
    slur2_elem.set("type", "stop")
    slur2_elem.set("number", "2")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
    
    assert len(notations) == 2
    
    # Check that we have both a StartSlur and a StopSlur
    start_slurs = [n for n in notations if isinstance(n, StartSlur)]
    stop_slurs = [n for n in notations if isinstance(n, StopSlur)]
    
    assert len(start_slurs) == 1
    assert len(stop_slurs) == 1
    
    assert start_slurs[0].label == "1"
    assert stop_slurs[0].label == "2"


def test_import_note_with_slur():
    """Test importing a complete note with a slur notation."""
    note_elem = create_test_note_with_slur(slur_type="start", slur_number="1")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    note = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
    
    assert note is not None
    assert len(note.notations) == 1
    assert isinstance(note.notations[0], StartSlur)
    assert note.notations[0].label == "1"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 