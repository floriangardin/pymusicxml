"""
Tests for importing notehead elements from MusicXML files.
"""

import pytest
import xml.etree.ElementTree as ET

from pymusicxml.importers.musical_elements import MusicalElementsImporter
from pymusicxml.score_components import Notehead


def create_test_note_with_notehead(notehead_type="normal", filled=None, step="C", octave=4):
    """Helper function to create a test note element with a notehead."""
    note_elem = ET.Element("note")
    
    # Add pitch
    pitch_elem = ET.SubElement(note_elem, "pitch")
    ET.SubElement(pitch_elem, "step").text = step
    ET.SubElement(pitch_elem, "octave").text = str(octave)
    
    # Add duration and type
    ET.SubElement(note_elem, "duration").text = "4"
    ET.SubElement(note_elem, "type").text = "quarter"
    
    # Add notehead
    notehead_attrs = {}
    if filled is not None:
        notehead_attrs["filled"] = "yes" if filled else "no"
        
    notehead_elem = ET.SubElement(note_elem, "notehead", notehead_attrs)
    notehead_elem.text = notehead_type
    
    return note_elem


def test_import_normal_notehead():
    """Test importing a normal notehead from MusicXML."""
    note_elem = create_test_note_with_notehead(notehead_type="normal", filled=None)
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
    
    notehead = MusicalElementsImporter.import_notehead(note_elem, find_element, get_text)
    
    assert notehead is not None
    assert isinstance(notehead, Notehead)
    assert notehead.notehead_name == "normal"
    assert notehead.filled is None


def test_import_filled_notehead():
    """Test importing a filled notehead from MusicXML."""
    note_elem = create_test_note_with_notehead(notehead_type="diamond", filled=True)
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
    
    notehead = MusicalElementsImporter.import_notehead(note_elem, find_element, get_text)
    
    assert notehead is not None
    assert isinstance(notehead, Notehead)
    assert notehead.notehead_name == "diamond"
    assert notehead.filled == "yes"
    
    # Test explicitly not filled
    note_elem = create_test_note_with_notehead(notehead_type="diamond", filled=False)
    notehead = MusicalElementsImporter.import_notehead(note_elem, find_element, get_text)
    
    assert notehead is not None
    assert isinstance(notehead, Notehead)
    assert notehead.notehead_name == "diamond"
    assert notehead.filled == "no"


def test_import_various_notehead_types():
    """Test importing various notehead types from MusicXML."""
    # Test various valid notehead types
    valid_types = ["normal", "diamond", "triangle", "slash", "cross", "x", "circle-x", 
                   "square", "none"]
                   
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
    
    for notehead_type in valid_types:
        note_elem = create_test_note_with_notehead(notehead_type=notehead_type)
        notehead = MusicalElementsImporter.import_notehead(note_elem, find_element, get_text)
        
        assert notehead is not None
        assert isinstance(notehead, Notehead)
        assert notehead.notehead_name == notehead_type


def test_import_invalid_notehead_type():
    """Test importing an invalid notehead type from MusicXML."""
    note_elem = create_test_note_with_notehead(notehead_type="invalid_type")
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
    
    notehead = MusicalElementsImporter.import_notehead(note_elem, find_element, get_text)
    
    # Should default to normal when invalid
    assert notehead is not None
    assert isinstance(notehead, Notehead)
    assert notehead.notehead_name == "normal"


def test_extra_whitespace_handling():
    """Test handling of extra whitespace in notehead types."""
    note_elem = create_test_note_with_notehead(notehead_type="  diamond  ")
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
    
    notehead = MusicalElementsImporter.import_notehead(note_elem, find_element, get_text)
    
    assert notehead is not None
    assert isinstance(notehead, Notehead)
    assert notehead.notehead_name == "diamond"


def test_case_insensitivity():
    """Test case insensitivity of notehead types."""
    note_elem = create_test_note_with_notehead(notehead_type="DiAmOnD")
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
    
    notehead = MusicalElementsImporter.import_notehead(note_elem, find_element, get_text)
    
    assert notehead is not None
    assert isinstance(notehead, Notehead)
    assert notehead.notehead_name == "diamond"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 