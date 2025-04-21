"""
Tests for importing trill notations from MusicXML files.
"""

import pytest
import xml.etree.ElementTree as ET

from pymusicxml.importers.musical_elements import MusicalElementsImporter
from pymusicxml.spanners import StartTrill, StopTrill, StartSlur
from pymusicxml.notations import TrillMark
from pymusicxml.enums import AccidentalType


def create_test_note_with_trill(step="C", octave=4, trill_type=None, accidental=None, placement="above", number="1"):
    """Helper function to create a test note element with trill notations."""
    note_elem = ET.Element("note")
    
    # Create pitch element
    pitch_elem = ET.SubElement(note_elem, "pitch")
    ET.SubElement(pitch_elem, "step").text = step
    ET.SubElement(pitch_elem, "octave").text = str(octave)
    
    # Add duration and type
    ET.SubElement(note_elem, "duration").text = "4"
    ET.SubElement(note_elem, "type").text = "quarter"
    
    # Add notations with ornaments if specified
    if trill_type is not None:
        notations_elem = ET.SubElement(note_elem, "notations")
        ornaments_elem = ET.SubElement(notations_elem, "ornaments")
        
        if trill_type == "trill-mark":
            ET.SubElement(ornaments_elem, "trill-mark")
        elif trill_type in ["start", "stop"]:
            wavy_line = ET.SubElement(ornaments_elem, "wavy-line")
            wavy_line.set("type", trill_type)
            wavy_line.set("number", number)
            if placement is not None:
                wavy_line.set("placement", placement)
            
            # Add accidental if provided
            if accidental is not None and trill_type == "start":
                accidental_mark = ET.SubElement(ornaments_elem, "accidental-mark")
                accidental_mark.text = accidental
    
    return note_elem


def test_import_trill_mark():
    """Test importing a note with a trill mark."""
    note_elem = create_test_note_with_trill(trill_type="trill-mark")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
    
    assert len(notations) == 1
    assert isinstance(notations[0], TrillMark)


def test_import_start_trill():
    """Test importing a note with a start trill notation."""
    note_elem = create_test_note_with_trill(trill_type="start", number="2", placement="above")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
    
    assert len(notations) == 1
    assert isinstance(notations[0], StartTrill)
    assert notations[0].label == "2"
    assert notations[0].placement.value == "above"
    assert notations[0].accidental is None


def test_import_stop_trill():
    """Test importing a note with a stop trill notation."""
    note_elem = create_test_note_with_trill(trill_type="stop", number="2", placement="below")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
    
    assert len(notations) == 1
    assert isinstance(notations[0], StopTrill)
    assert notations[0].label == "2"
    assert notations[0].placement.value == "below"


def test_import_trill_with_accidental():
    """Test importing a trill with an accidental."""
    note_elem = create_test_note_with_trill(trill_type="start", accidental="sharp", placement="above")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
    
    assert len(notations) == 1
    assert isinstance(notations[0], StartTrill)
    assert notations[0].accidental == AccidentalType.sharp


def test_import_trill_combined_with_other_notations():
    """Test importing a note with both a trill mark and other notations."""
    note_elem = ET.Element("note")
    
    # Create pitch element
    pitch_elem = ET.SubElement(note_elem, "pitch")
    ET.SubElement(pitch_elem, "step").text = "C"
    ET.SubElement(pitch_elem, "octave").text = "4"
    
    # Add duration and type
    ET.SubElement(note_elem, "duration").text = "4"
    ET.SubElement(note_elem, "type").text = "quarter"
    
    # Add notations with ornaments and slur
    notations_elem = ET.SubElement(note_elem, "notations")
    
    # Add trill
    ornaments_elem = ET.SubElement(notations_elem, "ornaments")
    ET.SubElement(ornaments_elem, "trill-mark")
    
    # Add slur
    slur_elem = ET.SubElement(notations_elem, "slur")
    slur_elem.set("type", "start")
    slur_elem.set("number", "1")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
    
    assert len(notations) == 2
    
    # Check that we have both a TrillMark and a StartSlur
    trill_marks = [n for n in notations if isinstance(n, TrillMark)]
    start_slurs = [n for n in notations if isinstance(n, StartSlur)]
    
    assert len(trill_marks) == 1
    assert len(start_slurs) == 1
    assert start_slurs[0].label == "1"


def test_import_note_with_trill():
    """Test importing a complete note with a trill notation."""
    note_elem = create_test_note_with_trill(trill_type="start", accidental="flat")
    
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
    assert isinstance(note.notations[0], StartTrill)
    assert note.notations[0].accidental == AccidentalType.flat


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 