"""
Tests for importing dashes directions from MusicXML files.
"""

import pytest
import xml.etree.ElementTree as ET

from pymusicxml.importers.directions_notations import DirectionsImporter
from pymusicxml.spanners import StartDashes, StopDashes
from pymusicxml.directions import TextAnnotation


def create_test_dashes_direction(
    dashes_type="start", 
    number="1", 
    dash_length=None, 
    space_length=None, 
    text=None, 
    placement="above"
):
    """Helper function to create a test direction element with dashes."""
    direction_elem = ET.Element("direction")
    
    if placement:
        direction_elem.set("placement", placement)
    
    direction_type_elem = ET.SubElement(direction_elem, "direction-type")
    
    # Add text if provided
    if text is not None:
        words_elem = ET.SubElement(direction_type_elem, "words")
        words_elem.text = text
    
    # Add dashes element
    dashes_elem = ET.SubElement(direction_type_elem, "dashes")
    dashes_elem.set("type", dashes_type)
    dashes_elem.set("number", number)
    
    if dash_length is not None:
        dashes_elem.set("dash-length", str(dash_length))
    if space_length is not None:
        dashes_elem.set("space-length", str(space_length))
    
    return direction_elem


def test_import_start_dashes():
    """Test importing a start dashes direction."""
    direction_elem = create_test_dashes_direction(dashes_type="start", number="1")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    dashes = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert dashes is not None
    assert isinstance(dashes, StartDashes)
    assert dashes.label == "1"
    assert dashes.placement.value == "above"
    assert dashes.text is None
    assert dashes.dash_length is None
    assert dashes.space_length is None


def test_import_stop_dashes():
    """Test importing a stop dashes direction."""
    direction_elem = create_test_dashes_direction(dashes_type="stop", number="1")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    dashes = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert dashes is not None
    assert isinstance(dashes, StopDashes)
    assert dashes.label == "1"
    assert dashes.placement.value == "above"
    assert dashes.text is None


def test_import_dashes_with_attributes():
    """Test importing dashes with additional attributes."""
    direction_elem = create_test_dashes_direction(
        dashes_type="start",
        number="2",
        dash_length=2.0,
        space_length=1.5,
        placement="below"
    )
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    dashes = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert dashes is not None
    assert isinstance(dashes, StartDashes)
    assert dashes.label == "2"
    assert dashes.placement.value == "below"
    assert dashes.dash_length == 2.0
    assert dashes.space_length == 1.5


def test_import_dashes_with_text():
    """Test importing dashes with text."""
    direction_elem = create_test_dashes_direction(
        dashes_type="start",
        text="cresc.",
        placement="above"
    )
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    dashes = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert dashes is not None
    assert isinstance(dashes, StartDashes)
    assert dashes.text is not None
    assert isinstance(dashes.text, TextAnnotation)
    assert dashes.text.text == "cresc."


def test_import_dashes_with_staff_voice():
    """Test importing a dashes direction with staff and voice attributes."""
    direction_elem = create_test_dashes_direction(dashes_type="start", number="1")
    
    # Add staff and voice elements
    ET.SubElement(direction_elem, "staff").text = "2"
    ET.SubElement(direction_elem, "voice").text = "3"
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    dashes = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert dashes is not None
    assert isinstance(dashes, StartDashes)
    assert dashes.staff == 2
    assert dashes.voice == 3


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 