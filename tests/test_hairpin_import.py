"""
Tests for importing hairpin (wedge) directions from MusicXML files.
"""

import pytest
import xml.etree.ElementTree as ET

from pymusicxml.importers.directions_notations import DirectionsImporter
from pymusicxml.spanners import StartHairpin, StopHairpin
from pymusicxml.enums import HairpinType


def create_test_hairpin_direction(wedge_type="crescendo", number="1", spread=None, niente=None, placement="below"):
    """Helper function to create a test direction element with a hairpin marking."""
    direction_elem = ET.Element("direction")
    
    if placement:
        direction_elem.set("placement", placement)
    
    direction_type_elem = ET.SubElement(direction_elem, "direction-type")
    wedge_elem = ET.SubElement(direction_type_elem, "wedge")
    
    wedge_elem.set("type", wedge_type)
    wedge_elem.set("number", number)
    
    if spread is not None:
        wedge_elem.set("spread", str(spread))
    if niente is not None and niente:
        wedge_elem.set("niente", "yes")
    
    return direction_elem


def test_import_crescendo_hairpin():
    """Test importing a crescendo hairpin direction."""
    direction_elem = create_test_hairpin_direction(wedge_type="crescendo", number="1")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    hairpin = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert hairpin is not None
    assert isinstance(hairpin, StartHairpin)
    assert hairpin.label == "1"
    assert hairpin.hairpin_type == HairpinType.crescendo
    assert hairpin.placement.value == "below"
    assert hairpin.niente is False


def test_import_diminuendo_hairpin():
    """Test importing a diminuendo hairpin direction."""
    direction_elem = create_test_hairpin_direction(wedge_type="diminuendo", number="1")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    hairpin = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert hairpin is not None
    assert isinstance(hairpin, StartHairpin)
    assert hairpin.label == "1"
    assert hairpin.hairpin_type == HairpinType.diminuendo
    assert hairpin.placement.value == "below"
    assert hairpin.niente is False


def test_import_stop_hairpin():
    """Test importing a stop hairpin direction."""
    direction_elem = create_test_hairpin_direction(wedge_type="stop", number="1")
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    hairpin = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert hairpin is not None
    assert isinstance(hairpin, StopHairpin)
    assert hairpin.label == "1"
    assert hairpin.placement.value == "below"


def test_import_hairpin_with_attributes():
    """Test importing a hairpin with additional attributes."""
    direction_elem = create_test_hairpin_direction(
        wedge_type="crescendo", 
        number="2", 
        spread=8.5, 
        niente=True, 
        placement="above"
    )
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    hairpin = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert hairpin is not None
    assert isinstance(hairpin, StartHairpin)
    assert hairpin.label == "2"
    assert hairpin.spread == 8.5
    assert hairpin.niente is True
    assert hairpin.placement.value == "above"


def test_import_stop_hairpin_with_spread():
    """Test importing a stop hairpin with spread attribute."""
    direction_elem = create_test_hairpin_direction(wedge_type="stop", number="1", spread=15)
    
    def find_element(parent, tag):
        return parent.find(f".//{tag}")
    
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    def get_text(parent, tag, default=None):
        elem = find_element(parent, tag)
        return elem.text if elem is not None else default
    
    hairpin = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert hairpin is not None
    assert isinstance(hairpin, StopHairpin)
    assert hairpin.label == "1"
    assert hairpin.spread == 15.0


def test_import_hairpin_with_staff_voice():
    """Test importing a hairpin direction with staff and voice attributes."""
    direction_elem = create_test_hairpin_direction(wedge_type="crescendo", number="1")
    
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
    
    hairpin = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert hairpin is not None
    assert isinstance(hairpin, StartHairpin)
    assert hairpin.staff == 2
    assert hairpin.voice == 3


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 