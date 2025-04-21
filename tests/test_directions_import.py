"""
Tests for importing direction elements from MusicXML files.
"""

import pytest
import xml.etree.ElementTree as ET

from pymusicxml.importers.directions_notations import DirectionsImporter
from pymusicxml.directions import Dynamic, MetronomeMark, TextAnnotation, Harmony, Degree
from pymusicxml.spanners import StartBracket, StopBracket


def create_test_dynamic_element(dynamic_type="f", placement="below"):
    """Helper function to create a test dynamic element."""
    direction_elem = ET.Element("direction", {"placement": placement})
    direction_type = ET.SubElement(direction_elem, "direction-type")
    dynamics_elem = ET.SubElement(direction_type, "dynamics")
    
    if dynamic_type in Dynamic.STANDARD_TYPES:
        ET.SubElement(dynamics_elem, dynamic_type)
    else:
        other_dynamics = ET.SubElement(dynamics_elem, "other-dynamics")
        other_dynamics.text = dynamic_type
    
    return direction_elem


def create_test_metronome_element(beat_unit="quarter", per_minute=120, dots=0, placement="above", parentheses=False):
    """Helper function to create a test metronome element."""
    direction_elem = ET.Element("direction", {"placement": placement})
    direction_type = ET.SubElement(direction_elem, "direction-type")
    
    metronome_attrs = {}
    if parentheses:
        metronome_attrs["parentheses"] = "yes"
        
    metronome_elem = ET.SubElement(direction_type, "metronome", metronome_attrs)
    ET.SubElement(metronome_elem, "beat-unit").text = beat_unit
    
    for _ in range(dots):
        ET.SubElement(metronome_elem, "beat-unit-dot")
        
    ET.SubElement(metronome_elem, "per-minute").text = str(per_minute)
    
    return direction_elem


def create_test_text_annotation_element(text="Andante", font_size=12, italic=False, bold=False, placement="above"):
    """Helper function to create a test text annotation element."""
    direction_elem = ET.Element("direction", {"placement": placement})
    direction_type = ET.SubElement(direction_elem, "direction-type")
    
    words_attrs = {"font-size": str(font_size)}
    if italic:
        words_attrs["font-style"] = "italic"
    if bold:
        words_attrs["font-weight"] = "bold"
        
    words_elem = ET.SubElement(direction_type, "words", words_attrs)
    words_elem.text = text
    
    return direction_elem


def create_test_harmony_element(root_step="C", root_alter=0, kind="major", placement="above", degrees=None):
    """Helper function to create a test harmony element."""
    direction_elem = ET.Element("direction", {"placement": placement})
    
    harmony_elem = ET.SubElement(direction_elem, "harmony")
    root_elem = ET.SubElement(harmony_elem, "root")
    ET.SubElement(root_elem, "root-step").text = root_step
    ET.SubElement(root_elem, "root-alter").text = str(root_alter)
    
    kind_elem = ET.SubElement(harmony_elem, "kind")
    kind_elem.text = kind
    
    if degrees:
        for degree_info in degrees:
            degree_elem = ET.SubElement(harmony_elem, "degree")
            ET.SubElement(degree_elem, "degree-value").text = str(degree_info["value"])
            ET.SubElement(degree_elem, "degree-alter").text = str(degree_info["alter"])
            ET.SubElement(degree_elem, "degree-type").text = degree_info.get("type", "alter")
    
    return direction_elem


def test_import_dynamic():
    """Test importing a dynamic from MusicXML."""
    # Test a standard dynamic
    direction_elem = create_test_dynamic_element(dynamic_type="f", placement="below")
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
        
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    dynamic = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert dynamic is not None
    assert isinstance(dynamic, Dynamic)
    assert dynamic.dynamic_text == "f"
    assert dynamic.placement.value == "below"
    
    # Test a custom dynamic
    direction_elem = create_test_dynamic_element(dynamic_type="sfzp", placement="below")
    dynamic = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert dynamic is not None
    assert isinstance(dynamic, Dynamic)
    assert dynamic.dynamic_text == "sfzp"


def test_import_metronome_mark():
    """Test importing a metronome mark from MusicXML."""
    # Test a simple quarter = 120
    direction_elem = create_test_metronome_element(beat_unit="quarter", per_minute=120)
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
        
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    metronome = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert metronome is not None
    assert isinstance(metronome, MetronomeMark)
    assert metronome.beat_unit.note_type == "quarter"
    assert metronome.bpm == 120
    
    # Test a dotted eighth = 60
    direction_elem = create_test_metronome_element(beat_unit="eighth", per_minute=60, dots=1)
    metronome = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert metronome is not None
    assert isinstance(metronome, MetronomeMark)
    # The beat_unit should be dotted eighth equivalent
    assert metronome.beat_unit.note_type == "eighth"
    assert metronome.beat_unit.num_dots == 1
    assert metronome.bpm == 60
    
    # Test with parentheses
    direction_elem = create_test_metronome_element(beat_unit="quarter", per_minute=80, parentheses=True)
    metronome = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert metronome is not None
    assert isinstance(metronome, MetronomeMark)
    assert metronome.beat_unit.note_type == "quarter"
    assert metronome.bpm == 80
    assert "parentheses" in metronome.other_attributes
    assert metronome.other_attributes["parentheses"] == "yes"


def test_import_text_annotation():
    """Test importing a text annotation from MusicXML."""
    # Test a simple text
    direction_elem = create_test_text_annotation_element(text="Andante", font_size=12)
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
        
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    text_annotation = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert text_annotation is not None
    assert isinstance(text_annotation, TextAnnotation)
    assert text_annotation.text == "Andante"
    assert "font-size" in text_annotation.text_properties
    assert text_annotation.text_properties["font-size"] == 12
    
    # Test with formatting
    direction_elem = create_test_text_annotation_element(text="espressivo", italic=True, bold=True)
    text_annotation = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert text_annotation is not None
    assert isinstance(text_annotation, TextAnnotation)
    assert text_annotation.text == "espressivo"
    assert "font-style" in text_annotation.text_properties
    assert text_annotation.text_properties["font-style"] == "italic"
    assert "font-weight" in text_annotation.text_properties
    assert text_annotation.text_properties["font-weight"] == "bold"


def test_import_harmony():
    """Test importing a harmony from MusicXML."""
    # Test a simple C major chord
    direction_elem = create_test_harmony_element(root_step="C", root_alter=0, kind="major")
    
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
        
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    harmony = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert harmony is not None
    assert isinstance(harmony, Harmony)
    assert harmony.root_letter == "C"
    assert harmony.root_alter == 0
    assert harmony.kind == "major"
    assert len(harmony.degrees) == 0
    
    # Print all valid harmony kinds for debugging
    print("Valid Harmony.KINDS:", Harmony.KINDS)
    
    # Test a dominant seventh chord
    direction_elem = create_test_harmony_element(
        root_step="F",
        root_alter=1,
        kind="dominant",  # Use "dominant" instead of "dominant-seventh"
        degrees=[]
    )
    
    harmony = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert harmony is not None
    assert isinstance(harmony, Harmony)
    assert harmony.root_letter == "F"
    assert harmony.root_alter == 1
    assert harmony.kind == "dominant"


def create_test_bracket_element(bracket_type="start", number="1", line_type="dashed", 
                              line_end=None, end_length=None, placement="above", 
                              with_text=False, text="roguishly"):
    """Helper function to create a test bracket element.
    
    Args:
        bracket_type: The type of bracket ("start" or "stop")
        number: The bracket number attribute
        line_type: The line type attribute for start brackets
        line_end: The line end attribute
        end_length: The end length attribute
        placement: The placement attribute
        with_text: Whether to include a text annotation
        text: The text content if with_text is True
        
    Returns:
        A direction element with the specified bracket attributes
    """
    direction_elem = ET.Element("direction", {"placement": placement})
    
    # Add text annotation if requested
    if with_text:
        direction_type_text = ET.SubElement(direction_elem, "direction-type")
        words_elem = ET.SubElement(direction_type_text, "words")
        words_elem.text = text
    
    # Add bracket
    direction_type = ET.SubElement(direction_elem, "direction-type")
    
    bracket_attrs = {"type": bracket_type, "number": number}
    if bracket_type == "start" and line_type:
        bracket_attrs["line-type"] = line_type
    if line_end:
        bracket_attrs["line-end"] = line_end
    if end_length:
        bracket_attrs["end-length"] = str(end_length)
        
    ET.SubElement(direction_type, "bracket", bracket_attrs)
    
    # Add voice
    voice_elem = ET.SubElement(direction_elem, "voice")
    voice_elem.text = "1"
    
    return direction_elem


def test_import_bracket():
    """Test importing brackets from MusicXML."""
    # Setup helper functions
    def find_element(parent, tag):
        elements = parent.findall(f".//{tag}")
        return elements[0] if elements else None
    
    def get_text(parent, tag, default=None):
        elem = parent.find(f".//{tag}")
        return elem.text if elem is not None and elem.text else default
        
    def find_elements(parent, tag):
        return parent.findall(f".//{tag}")
    
    # Test Start Bracket without text
    direction_elem = create_test_bracket_element(
        bracket_type="start", 
        number="1", 
        line_type="dashed", 
        line_end="none"
    )
    
    bracket = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert bracket is not None
    assert isinstance(bracket, StartBracket)
    assert bracket.label == "1"
    assert bracket.line_type.value == "dashed"
    assert bracket.line_end.value == "none"
    assert bracket.text is None
    
    # Test Start Bracket with text
    direction_elem = create_test_bracket_element(
        bracket_type="start", 
        number="2", 
        line_type="solid", 
        line_end="none",
        with_text=True,
        text="expressively"
    )
    
    bracket = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert bracket is not None
    assert isinstance(bracket, StartBracket)
    assert bracket.label == "2"
    assert bracket.line_type.value == "solid"
    assert bracket.line_end.value == "none"
    assert bracket.text is not None
    assert bracket.text.text == "expressively"
    
    # Test Stop Bracket
    direction_elem = create_test_bracket_element(
        bracket_type="stop", 
        number="1", 
        line_end="down"
    )
    
    bracket = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert bracket is not None
    assert isinstance(bracket, StopBracket)
    assert bracket.label == "1"
    assert bracket.line_end.value == "down"
    
    # Test end_length attribute
    direction_elem = create_test_bracket_element(
        bracket_type="stop", 
        number="3", 
        line_end="arrow",
        end_length="5.5"
    )
    
    bracket = DirectionsImporter.import_direction(direction_elem, find_element, get_text, find_elements)
    
    assert bracket is not None
    assert isinstance(bracket, StopBracket)
    assert bracket.label == "3"
    assert bracket.line_end.value == "arrow"
    assert bracket.end_length == 5.5


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 