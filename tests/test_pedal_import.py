"""
Tests for importing pedal directions from MusicXML files.
"""

import pytest
import xml.etree.ElementTree as ET

from pymusicxml.importers.directions_notations import DirectionsImporter
from pymusicxml.spanners import StartPedal, StopPedal, ChangePedal


def create_test_pedal_direction(pedal_type="start", number="1", sign="yes", line="yes", placement="below"):
    """Helper function to create a test direction element with a pedal marking."""
    direction_elem = ET.Element("direction")
    
    if placement:
        direction_elem.set("placement", placement)
    
    direction_type_elem = ET.SubElement(direction_elem, "direction-type")
    pedal_elem = ET.SubElement(direction_type_elem, "pedal")
    
    pedal_elem.set("type", pedal_type)
    pedal_elem.set("number", number)
    
    if sign:
        pedal_elem.set("sign", sign)
    if line:
        pedal_elem.set("line", line)
    
    return direction_elem


def test_import_start_pedal():
    """Test importing a start pedal direction."""
    direction_elem = create_test_pedal_direction(pedal_type="start", number="1", sign="yes", line="yes")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    pedal = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert pedal is not None
    assert isinstance(pedal, StartPedal)
    assert pedal.label == "1"
    assert pedal.sign is True
    assert pedal.line is True
    assert pedal.placement.value == "below"


def test_import_stop_pedal():
    """Test importing a stop pedal direction."""
    direction_elem = create_test_pedal_direction(pedal_type="stop", number="1", sign="no", line="yes")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    pedal = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert pedal is not None
    assert isinstance(pedal, StopPedal)
    assert pedal.label == "1"
    assert pedal.sign is False  # "no" sign
    assert pedal.line is True
    assert pedal.placement.value == "below"


def test_import_change_pedal():
    """Test importing a change pedal direction."""
    direction_elem = create_test_pedal_direction(pedal_type="change", number="1", sign="yes", line="yes")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    pedal = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert pedal is not None
    assert isinstance(pedal, ChangePedal)
    assert pedal.label == "1"
    assert pedal.sign is True
    assert pedal.line is True
    assert pedal.placement.value == "below"


def test_import_pedal_with_custom_placement():
    """Test importing a pedal direction with custom placement."""
    direction_elem = create_test_pedal_direction(pedal_type="start", number="1", sign="yes", line="yes", placement="above")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    pedal = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert pedal is not None
    assert isinstance(pedal, StartPedal)
    assert pedal.placement.value == "above"


def test_import_pedal_with_staff_voice():
    """Test importing a pedal direction with staff and voice attributes."""
    direction_elem = create_test_pedal_direction(pedal_type="start", number="1")
    
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
    
    pedal = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert pedal is not None
    assert isinstance(pedal, StartPedal)
    assert pedal.staff == 2
    assert pedal.voice == 3


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 