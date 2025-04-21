"""
Integration tests for Phase 4 features (directions and notations).
"""

import pytest
import tempfile
import os
import xml.etree.ElementTree as ET
from pymusicxml import *
from pymusicxml.importers import import_musicxml
from pymusicxml import Score, Part, Measure, Note
from pymusicxml.spanners import StartBracket, StopBracket

from pymusicxml.importers.musical_elements import MusicalElementsImporter
from pymusicxml.score_components import Note, Notehead
from pymusicxml.directions import Dynamic, MetronomeMark, TextAnnotation, Harmony, Degree


def create_test_musicxml_with_phase4_features():
    """Create a test MusicXML file with Phase 4 features."""
    # Create the root element
    score_partwise = ET.Element("score-partwise", {"version": "3.1"})
    
    # Add part-list
    part_list = ET.SubElement(score_partwise, "part-list")
    score_part = ET.SubElement(part_list, "score-part", {"id": "P1"})
    ET.SubElement(score_part, "part-name").text = "Music"
    
    # Create a part
    part = ET.SubElement(score_partwise, "part", {"id": "P1"})
    
    # Add a measure
    measure = ET.SubElement(part, "measure", {"number": "1"})
    
    # Add attributes
    attributes = ET.SubElement(measure, "attributes")
    ET.SubElement(attributes, "divisions").text = "4"  # 4 divisions per quarter note
    time = ET.SubElement(attributes, "time")
    ET.SubElement(time, "beats").text = "4"
    ET.SubElement(time, "beat-type").text = "4"
    clef = ET.SubElement(attributes, "clef")
    ET.SubElement(clef, "sign").text = "G"
    ET.SubElement(clef, "line").text = "2"
    
    # Add a dynamic marking (f) at the beginning
    direction1 = ET.SubElement(measure, "direction", {"placement": "below"})
    direction_type1 = ET.SubElement(direction1, "direction-type")
    dynamics = ET.SubElement(direction_type1, "dynamics")
    ET.SubElement(dynamics, "f")
    
    # First note (C4 quarter note)
    note1 = ET.SubElement(measure, "note")
    pitch1 = ET.SubElement(note1, "pitch")
    ET.SubElement(pitch1, "step").text = "C"
    ET.SubElement(pitch1, "octave").text = "4"
    ET.SubElement(note1, "duration").text = "4"  # Quarter note (4 divisions)
    ET.SubElement(note1, "type").text = "quarter"
    notehead = ET.SubElement(note1, "notehead", {"filled": "yes"})
    notehead.text = "diamond"
    
    # Add a text annotation (Allegro) at beat 1.5 (offset of 2 divisions)
    direction2 = ET.SubElement(measure, "direction", {"placement": "above"})
    direction_type2 = ET.SubElement(direction2, "direction-type")
    words = ET.SubElement(direction_type2, "words", {"font-style": "italic"})
    words.text = "Allegro"
    # Add offset
    ET.SubElement(direction2, "offset").text = "2"  # 2 divisions = 0.5 quarter notes
    
    # Second note (E4 quarter note)
    note2 = ET.SubElement(measure, "note")
    pitch2 = ET.SubElement(note2, "pitch")
    ET.SubElement(pitch2, "step").text = "E"
    ET.SubElement(pitch2, "octave").text = "4"
    ET.SubElement(note2, "duration").text = "4"  # Quarter note (4 divisions)
    ET.SubElement(note2, "type").text = "quarter"
    
    # Add a metronome mark at beat 2 (right after first quarter note)
    direction3 = ET.SubElement(measure, "direction", {"placement": "above"})
    direction_type3 = ET.SubElement(direction3, "direction-type")
    metronome = ET.SubElement(direction_type3, "metronome")
    ET.SubElement(metronome, "beat-unit").text = "quarter"
    ET.SubElement(metronome, "per-minute").text = "120"
    
    # Add a chord symbol (C major) at beat 3 
    harmony = ET.SubElement(measure, "harmony")
    root = ET.SubElement(harmony, "root")
    ET.SubElement(root, "root-step").text = "C"
    ET.SubElement(root, "root-alter").text = "0"
    ET.SubElement(harmony, "kind").text = "major"
    # Position this after the second note
    ET.SubElement(harmony, "offset").text = "4"  # 4 divisions = 1 quarter note after the second note
    
    # Third note (G4 quarter note)
    note3 = ET.SubElement(measure, "note")
    pitch3 = ET.SubElement(note3, "pitch")
    ET.SubElement(pitch3, "step").text = "G"
    ET.SubElement(pitch3, "octave").text = "4"
    ET.SubElement(note3, "duration").text = "4"  # Quarter note (4 divisions)
    ET.SubElement(note3, "type").text = "quarter"
    
    # Add a chord symbol (F7) at beat 3.5
    harmony2 = ET.SubElement(measure, "harmony")
    root2 = ET.SubElement(harmony2, "root")
    ET.SubElement(root2, "root-step").text = "F"
    ET.SubElement(root2, "root-alter").text = "0"
    ET.SubElement(harmony2, "kind").text = "dominant"
    degree = ET.SubElement(harmony2, "degree")
    ET.SubElement(degree, "degree-value").text = "9"
    ET.SubElement(degree, "degree-alter").text = "1"
    ET.SubElement(degree, "degree-type").text = "add"
    # Position this after beat 3
    ET.SubElement(harmony2, "offset").text = "2"  # 2 divisions = 0.5 quarter notes after 3rd note
    
    # Add a rest on beat 4
    note4 = ET.SubElement(measure, "note")
    ET.SubElement(note4, "rest")
    ET.SubElement(note4, "duration").text = "4"  # Quarter note rest (4 divisions)
    ET.SubElement(note4, "type").text = "quarter"
    
    # Save to a temporary file
    tree = ET.ElementTree(score_partwise)
    fd, path = tempfile.mkstemp(suffix='.xml')
    os.close(fd)
    tree.write(path, encoding='utf-8', xml_declaration=True)
    return path


def test_phase4_integration():
    """Test importing a MusicXML file with all Phase 4 features."""
    # Create test file
    xml_path = create_test_musicxml_with_phase4_features()
    
    try:
        # Import the MusicXML file
        score = import_musicxml(xml_path)
        
        # Verify the score was imported
        assert score is not None
        
        # Check for directions
        directions_with_positions = []
        for part in score.parts:
            for measure in part.measures:
                for direction, offset in measure.iter_directions():
                    directions_with_positions.append((direction, offset))
        
        # Verify all direction types are present with correct positions
        dynamic_found = False
        text_found = False
        metronome_found = False
        harmony_c_found = False
        harmony_f_found = False
        notehead_found = False
        
        for direction, offset in directions_with_positions:
            print(f"Found direction: {type(direction).__name__} at position {offset}")
            
            if isinstance(direction, Dynamic):
                dynamic_found = True
                assert direction.dynamic_text == "f"
                assert abs(offset - 0.0) < 0.01, f"Dynamic should be at beat 1, got {offset}"
                
            elif isinstance(direction, TextAnnotation):
                text_found = True
                assert direction.text == "Allegro"
                assert abs(offset - 1.5) < 0.01, f"Text should be at beat 1.5, got {offset}"
                
            elif isinstance(direction, MetronomeMark):
                metronome_found = True
                assert direction.bpm == 120
                assert abs(offset - 2.0) < 0.01, f"Metronome mark should be at beat 2, got {offset}"
                
            elif isinstance(direction, Harmony):
                if direction.root_letter == "C":
                    harmony_c_found = True
                    assert abs(offset - 3.0) < 0.01, f"C harmony should be at beat 3, got {offset}"
                elif direction.root_letter == "F":
                    harmony_f_found = True 
                    assert abs(offset - 3.5) < 0.01, f"F harmony should be at beat 3.5, got {offset}"
        
        # Check for notehead
        for part in score.parts:
            for measure in part.measures:
                for voice in measure.voices:
                    for element in voice:
                        if isinstance(element, Note) and element.notehead is not None:
                            notehead_found = True
                            assert element.notehead.notehead_name == "diamond"
                            assert element.notehead.filled == "yes"
        
        # Assert all features were found
        assert dynamic_found, "Dynamic was not found in the imported score"
        assert text_found, "Text annotation was not found in the imported score"
        assert metronome_found, "Metronome mark was not found in the imported score"
        assert harmony_c_found, "C harmony was not found in the imported score"
        assert harmony_f_found, "F harmony was not found in the imported score"
        assert notehead_found, "Notehead was not found in the imported score"
        
    finally:
        # Clean up
        if os.path.exists(xml_path):
            os.remove(xml_path)


def test_import_export_with_brackets():
    """Test that brackets with text are correctly imported and exported."""
    # Create a score with brackets
    score = Score([
        Part("Test Part", [
            Measure([
                Note("C4", 1.0, directions=StartBracket(text="roguishly", line_type="dashed", line_end="none")),
                Note("D4", 1.0),
                Note("E4", 1.0, directions=StopBracket(line_end="down")),
                Note("F4", 1.0)
            ])
        ])
    ])
    
    # Create a temporary file
    temp_file = tempfile.mktemp(suffix=".musicxml")
    
    try:
        # Export the score
        score.export_to_file(temp_file)
        
        # Import the score
        imported_score = import_musicxml(temp_file)
        
        # Export the imported score
        temp_file2 = tempfile.mktemp(suffix=".musicxml")
        imported_score.export_to_file(temp_file2)
        
        # Parse both files
        tree1 = ET.parse(temp_file)
        tree2 = ET.parse(temp_file2)
        
        # Check that both files have the same bracket elements
        # Find bracket in first file
        bracket_start1 = tree1.find(".//bracket[@type='start']")
        bracket_stop1 = tree1.find(".//bracket[@type='stop']")
        
        # Find bracket in second file
        bracket_start2 = tree2.find(".//bracket[@type='start']")
        bracket_stop2 = tree2.find(".//bracket[@type='stop']")
        
        # Check start bracket attributes
        assert bracket_start1 is not None
        assert bracket_start2 is not None
        assert bracket_start1.get("type") == bracket_start2.get("type") == "start"
        assert bracket_start1.get("line-type") == bracket_start2.get("line-type") == "dashed"
        assert bracket_start1.get("line-end") == bracket_start2.get("line-end") == "none"
        
        # Check stop bracket attributes
        assert bracket_stop1 is not None
        assert bracket_stop2 is not None
        assert bracket_stop1.get("type") == bracket_stop2.get("type") == "stop"
        assert bracket_stop1.get("line-end") == bracket_stop2.get("line-end") == "down"
        
        # Check text annotation
        text1 = tree1.find(".//words")
        text2 = tree2.find(".//words")
        assert text1 is not None
        assert text2 is not None
        assert text1.text == text2.text == "roguishly"
        
    finally:
        # Clean up
        for f in [temp_file, temp_file2]:
            if os.path.exists(f):
                os.unlink(f)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 