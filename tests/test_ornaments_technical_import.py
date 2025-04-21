"""
Test module for importing ornaments and technical notations from MusicXML files.

This module provides test cases for the import of ornaments, technical notations,
and other Phase 6 features.
"""

import io
import tempfile
import pytest
from xml.etree import ElementTree as ET

from pymusicxml import Score, Part, Measure, Note, Chord
from pymusicxml.importer import import_musicxml
from pymusicxml.notations import (
    Mordent, Turn, Schleifer, Tremolo, UpBow, DownBow, OpenString, Harmonic,
    Arpeggiate, NonArpeggiate
)


def get_musicxml_with_ornaments():
    """Create a simple MusicXML string with various ornaments for testing."""
    root = ET.Element("score-partwise", {"version": "3.1"})
    
    # Add part-list with one part
    part_list = ET.SubElement(root, "part-list")
    score_part = ET.SubElement(part_list, "score-part", {"id": "P1"})
    ET.SubElement(score_part, "part-name").text = "Test Ornaments"
    
    # Create the part
    part = ET.SubElement(root, "part", {"id": "P1"})
    
    # Create a measure
    measure = ET.SubElement(part, "measure", {"number": "1"})
    
    # Add attributes
    attributes = ET.SubElement(measure, "attributes")
    ET.SubElement(attributes, "divisions").text = "4"
    time = ET.SubElement(attributes, "time")
    ET.SubElement(time, "beats").text = "4"
    ET.SubElement(time, "beat-type").text = "4"
    
    # Note with mordent
    note1 = ET.SubElement(measure, "note")
    pitch1 = ET.SubElement(note1, "pitch")
    ET.SubElement(pitch1, "step").text = "C"
    ET.SubElement(pitch1, "octave").text = "5"
    ET.SubElement(note1, "duration").text = "4"
    ET.SubElement(note1, "voice").text = "1"
    ET.SubElement(note1, "type").text = "quarter"
    notations1 = ET.SubElement(note1, "notations")
    ornaments1 = ET.SubElement(notations1, "ornaments")
    ET.SubElement(ornaments1, "mordent")
    
    # Note with inverted mordent
    note2 = ET.SubElement(measure, "note")
    pitch2 = ET.SubElement(note2, "pitch")
    ET.SubElement(pitch2, "step").text = "D"
    ET.SubElement(pitch2, "octave").text = "5"
    ET.SubElement(note2, "duration").text = "4"
    ET.SubElement(note2, "voice").text = "1"
    ET.SubElement(note2, "type").text = "quarter"
    notations2 = ET.SubElement(note2, "notations")
    ornaments2 = ET.SubElement(notations2, "ornaments")
    ET.SubElement(ornaments2, "inverted-mordent")
    
    # Note with turn
    note3 = ET.SubElement(measure, "note")
    pitch3 = ET.SubElement(note3, "pitch")
    ET.SubElement(pitch3, "step").text = "E"
    ET.SubElement(pitch3, "octave").text = "5"
    ET.SubElement(note3, "duration").text = "4"
    ET.SubElement(note3, "voice").text = "1"
    ET.SubElement(note3, "type").text = "quarter"
    notations3 = ET.SubElement(note3, "notations")
    ornaments3 = ET.SubElement(notations3, "ornaments")
    ET.SubElement(ornaments3, "turn")
    
    # Note with schleifer
    note4 = ET.SubElement(measure, "note")
    pitch4 = ET.SubElement(note4, "pitch")
    ET.SubElement(pitch4, "step").text = "F"
    ET.SubElement(pitch4, "octave").text = "5"
    ET.SubElement(note4, "duration").text = "4"
    ET.SubElement(note4, "voice").text = "1"
    ET.SubElement(note4, "type").text = "quarter"
    notations4 = ET.SubElement(note4, "notations")
    ornaments4 = ET.SubElement(notations4, "ornaments")
    ET.SubElement(ornaments4, "schleifer")
    
    # Create a second measure
    measure2 = ET.SubElement(part, "measure", {"number": "2"})
    
    # Note with tremolo
    note5 = ET.SubElement(measure2, "note")
    pitch5 = ET.SubElement(note5, "pitch")
    ET.SubElement(pitch5, "step").text = "G"
    ET.SubElement(pitch5, "octave").text = "5"
    ET.SubElement(note5, "duration").text = "4"
    ET.SubElement(note5, "voice").text = "1"
    ET.SubElement(note5, "type").text = "quarter"
    notations5 = ET.SubElement(note5, "notations")
    ornaments5 = ET.SubElement(notations5, "ornaments")
    tremolo = ET.SubElement(ornaments5, "tremolo", {"type": "single"})
    tremolo.text = "3"
    
    # Note with up bow
    note6 = ET.SubElement(measure2, "note")
    pitch6 = ET.SubElement(note6, "pitch")
    ET.SubElement(pitch6, "step").text = "A"
    ET.SubElement(pitch6, "octave").text = "5"
    ET.SubElement(note6, "duration").text = "4"
    ET.SubElement(note6, "voice").text = "1"
    ET.SubElement(note6, "type").text = "quarter"
    notations6 = ET.SubElement(note6, "notations")
    technical6 = ET.SubElement(notations6, "technical")
    ET.SubElement(technical6, "up-bow")
    
    # Note with down bow
    note7 = ET.SubElement(measure2, "note")
    pitch7 = ET.SubElement(note7, "pitch")
    ET.SubElement(pitch7, "step").text = "B"
    ET.SubElement(pitch7, "octave").text = "5"
    ET.SubElement(note7, "duration").text = "4"
    ET.SubElement(note7, "voice").text = "1"
    ET.SubElement(note7, "type").text = "quarter"
    notations7 = ET.SubElement(note7, "notations")
    technical7 = ET.SubElement(notations7, "technical")
    ET.SubElement(technical7, "down-bow")
    
    # Note with harmonic
    note8 = ET.SubElement(measure2, "note")
    pitch8 = ET.SubElement(note8, "pitch")
    ET.SubElement(pitch8, "step").text = "C"
    ET.SubElement(pitch8, "octave").text = "6"
    ET.SubElement(note8, "duration").text = "4"
    ET.SubElement(note8, "voice").text = "1"
    ET.SubElement(note8, "type").text = "quarter"
    notations8 = ET.SubElement(note8, "notations")
    technical8 = ET.SubElement(notations8, "technical")
    ET.SubElement(technical8, "harmonic")
    
    # Create a third measure
    measure3 = ET.SubElement(part, "measure", {"number": "3"})
    
    # Note with open string
    note9 = ET.SubElement(measure3, "note")
    pitch9 = ET.SubElement(note9, "pitch")
    ET.SubElement(pitch9, "step").text = "D"
    ET.SubElement(pitch9, "octave").text = "5"
    ET.SubElement(note9, "duration").text = "4"
    ET.SubElement(note9, "voice").text = "1"
    ET.SubElement(note9, "type").text = "quarter"
    notations9 = ET.SubElement(note9, "notations")
    technical9 = ET.SubElement(notations9, "technical")
    ET.SubElement(technical9, "open-string")
    
    # Chord with arpeggiate
    # First note of chord
    chord1 = ET.SubElement(measure3, "note")
    pitch_c1 = ET.SubElement(chord1, "pitch")
    ET.SubElement(pitch_c1, "step").text = "C"
    ET.SubElement(pitch_c1, "octave").text = "5"
    ET.SubElement(chord1, "duration").text = "4"
    ET.SubElement(chord1, "voice").text = "1"
    ET.SubElement(chord1, "type").text = "quarter"
    
    # Second note of chord
    chord2 = ET.SubElement(measure3, "note")
    chord_tag = ET.SubElement(chord2, "chord")
    pitch_c2 = ET.SubElement(chord2, "pitch")
    ET.SubElement(pitch_c2, "step").text = "E"
    ET.SubElement(pitch_c2, "octave").text = "5"
    ET.SubElement(chord2, "duration").text = "4"
    ET.SubElement(chord2, "voice").text = "1"
    ET.SubElement(chord2, "type").text = "quarter"
    notations_chord = ET.SubElement(chord2, "notations")
    ET.SubElement(notations_chord, "arpeggiate")
    
    # Chord with non-arpeggiate
    # First note of chord
    chord3 = ET.SubElement(measure3, "note")
    pitch_c3 = ET.SubElement(chord3, "pitch")
    ET.SubElement(pitch_c3, "step").text = "D"
    ET.SubElement(pitch_c3, "octave").text = "5"
    ET.SubElement(chord3, "duration").text = "4"
    ET.SubElement(chord3, "voice").text = "1"
    ET.SubElement(chord3, "type").text = "quarter"
    
    # Second note of chord
    chord4 = ET.SubElement(measure3, "note")
    chord_tag2 = ET.SubElement(chord4, "chord")
    pitch_c4 = ET.SubElement(chord4, "pitch")
    ET.SubElement(pitch_c4, "step").text = "F"
    ET.SubElement(pitch_c4, "octave").text = "5"
    ET.SubElement(chord4, "duration").text = "4"
    ET.SubElement(chord4, "voice").text = "1"
    ET.SubElement(chord4, "type").text = "quarter"
    notations_chord2 = ET.SubElement(chord4, "notations")
    ET.SubElement(notations_chord2, "non-arpeggiate")
    
    # Note with multiple notations
    note10 = ET.SubElement(measure3, "note")
    pitch10 = ET.SubElement(note10, "pitch")
    ET.SubElement(pitch10, "step").text = "G"
    ET.SubElement(pitch10, "octave").text = "5"
    ET.SubElement(note10, "duration").text = "4"
    ET.SubElement(note10, "voice").text = "1"
    ET.SubElement(note10, "type").text = "quarter"
    notations10 = ET.SubElement(note10, "notations")
    technical10 = ET.SubElement(notations10, "technical")
    ET.SubElement(technical10, "harmonic")
    ET.SubElement(technical10, "open-string")
    
    xml_string = ET.tostring(root, encoding="unicode")
    return xml_string


def test_import_ornaments():
    """Test importing ornaments from a MusicXML file."""
    # Create a temporary MusicXML file with ornaments
    xml_string = get_musicxml_with_ornaments()
    
    # Import the MusicXML string
    with tempfile.NamedTemporaryFile(suffix=".musicxml", mode="w") as tmp:
        tmp.write(xml_string)
        tmp.flush()
        score = import_musicxml(tmp.name)
    
    # Check the imported score
    assert len(score.parts) == 1
    part = score.parts[0]
    assert len(part.measures) == 3
    
    # Check measure 1 with mordent, inverted mordent, turn, and schleifer
    measure1 = part.measures[0]
    assert len(measure1.contents) == 4
    
    # Check note with mordent
    note1 = measure1.contents[0]
    assert isinstance(note1, Note)
    assert len(note1.notations) == 1
    assert isinstance(note1.notations[0], Mordent)
    assert not note1.notations[0].inverted
    
    # Check note with inverted mordent
    note2 = measure1.contents[1]
    assert isinstance(note2, Note)
    assert len(note2.notations) == 1
    assert isinstance(note2.notations[0], Mordent)
    assert note2.notations[0].inverted
    
    # Check note with turn
    note3 = measure1.contents[2]
    assert isinstance(note3, Note)
    assert len(note3.notations) == 1
    assert isinstance(note3.notations[0], Turn)
    assert not note3.notations[0].inverted
    assert not note3.notations[0].delayed
    
    # Check note with schleifer
    note4 = measure1.contents[3]
    assert isinstance(note4, Note)
    assert len(note4.notations) == 1
    assert isinstance(note4.notations[0], Schleifer)
    
    # Check measure 2 with tremolo, up-bow, down-bow, and harmonic
    measure2 = part.measures[1]
    assert len(measure2.contents) == 4
    
    # Check note with tremolo
    note5 = measure2.contents[0]
    assert isinstance(note5, Note)
    assert len(note5.notations) == 1
    assert isinstance(note5.notations[0], Tremolo)
    assert note5.notations[0].num_lines == 3
    
    # Check note with up-bow
    note6 = measure2.contents[1]
    assert isinstance(note6, Note)
    assert len(note6.notations) == 1
    assert isinstance(note6.notations[0], UpBow)
    
    # Check note with down-bow
    note7 = measure2.contents[2]
    assert isinstance(note7, Note)
    assert len(note7.notations) == 1
    assert isinstance(note7.notations[0], DownBow)
    
    # Check note with harmonic
    note8 = measure2.contents[3]
    assert isinstance(note8, Note)
    assert len(note8.notations) == 1
    assert isinstance(note8.notations[0], Harmonic)
    
    # Check measure 3 with open-string, arpeggiate, non-arpeggiate, and multiple notations
    measure3 = part.measures[2]
    assert len(measure3.contents) == 4
    
    # Check note with open-string
    note9 = measure3.contents[0]
    assert isinstance(note9, Note)
    assert len(note9.notations) == 1
    assert isinstance(note9.notations[0], OpenString)
    
    # Check chord with arpeggiate
    chord1 = measure3.contents[1]
    assert isinstance(chord1, Chord)
    assert len(chord1.notations) == 1
    assert isinstance(chord1.notations[0], Arpeggiate)
    
    # Check chord with non-arpeggiate
    chord2 = measure3.contents[2]
    assert isinstance(chord2, Chord)
    assert len(chord2.notations) == 1
    assert isinstance(chord2.notations[0], NonArpeggiate)
    
    # Check note with multiple notations (harmonic and open-string)
    note10 = measure3.contents[3]
    assert isinstance(note10, Note)
    assert len(note10.notations) == 2
    assert any(isinstance(notation, Harmonic) for notation in note10.notations)
    assert any(isinstance(notation, OpenString) for notation in note10.notations)


def test_round_trip():
    """Test round-trip import/export of a score with ornaments and technical notations."""
    # Create a score with ornaments and technical notations
    score = Score([
        Part("Ornaments Test", [
            Measure([
                Note("c5", 1, notations=[Mordent()]),
                Note("d5", 1, notations=[Mordent(inverted=True)]),
                Note("e5", 1, notations=[Turn()]),
                Note("f5", 1, notations=[Schleifer()])
            ], time_signature=(4, 4)),
            Measure([
                Note("g5", 1, notations=[Tremolo(3)]),
                Note("a5", 1, notations=[UpBow()]),
                Note("b5", 1, notations=[DownBow()]),
                Note("c6", 1, notations=[Harmonic()])
            ]),
            Measure([
                Note("d5", 1, notations=[OpenString()]),
                Chord(["c5", "e5"], 1, notations=[Arpeggiate()]),
                Chord(["d5", "f5"], 1, notations=[NonArpeggiate()]),
                Note("g5", 1, notations=[Harmonic(), OpenString()])
            ])
        ])
    ])
    
    # Export to MusicXML and import back
    with tempfile.NamedTemporaryFile(suffix=".musicxml") as tmp:
        score.export_to_file(tmp.name)
        reimported_score = import_musicxml(tmp.name)
    
    # Check the reimported score matches the original
    assert len(reimported_score.parts) == 1
    part = reimported_score.parts[0]
    assert len(part.measures) == 3
    
    # Verify measure 1
    measure1 = part.measures[0]
    assert len(measure1.contents) == 4
    assert isinstance(measure1.contents[0].notations[0], Mordent)
    assert not measure1.contents[0].notations[0].inverted
    assert isinstance(measure1.contents[1].notations[0], Mordent)
    assert measure1.contents[1].notations[0].inverted
    assert isinstance(measure1.contents[2].notations[0], Turn)
    assert isinstance(measure1.contents[3].notations[0], Schleifer)
    
    # Verify measure 2
    measure2 = part.measures[1]
    assert len(measure2.contents) == 4
    assert isinstance(measure2.contents[0].notations[0], Tremolo)
    assert measure2.contents[0].notations[0].num_lines == 3
    assert isinstance(measure2.contents[1].notations[0], UpBow)
    assert isinstance(measure2.contents[2].notations[0], DownBow)
    assert isinstance(measure2.contents[3].notations[0], Harmonic)
    
    # Verify measure 3
    measure3 = part.measures[2]
    assert len(measure3.contents) == 4
    assert isinstance(measure3.contents[0].notations[0], OpenString)
    assert isinstance(measure3.contents[1], Chord)
    assert isinstance(measure3.contents[1].notations[0], Arpeggiate)
    assert isinstance(measure3.contents[2], Chord)
    assert isinstance(measure3.contents[2].notations[0], NonArpeggiate)
    
    # Check note with multiple notations
    note10 = measure3.contents[3]
    assert len(note10.notations) == 2
    assert any(isinstance(notation, Harmonic) for notation in note10.notations)
    assert any(isinstance(notation, OpenString) for notation in note10.notations)


def test_import_from_main_test():
    """Test importing ornaments and technical notations from the main_test.musicxml file."""
    # Try to import the main_test.musicxml file (which should already exist)
    try:
        score = import_musicxml("main_test.musicxml")
        
        # Check the violin part has the Phase 6 features
        violin_part = None
        for part in score.parts:
            if "Violin" in part.part_name:
                violin_part = part
                break
        
        assert violin_part is not None
        
        # Check the violin part measures
        assert len(violin_part.measures) >= 4
        
        # Measure 1 should have Mordent, Turn, Schleifer, and Tremolo
        measure1 = violin_part.measures[0]
        assert any(isinstance(note.notations[0], Mordent) for note in measure1.contents if hasattr(note, 'notations') and note.notations)
        assert any(isinstance(note.notations[0], Turn) for note in measure1.contents if hasattr(note, 'notations') and note.notations)
        assert any(isinstance(note.notations[0], Schleifer) for note in measure1.contents if hasattr(note, 'notations') and note.notations)
        assert any(isinstance(note.notations[0], Tremolo) for note in measure1.contents if hasattr(note, 'notations') and note.notations)
        
        # Measure 2 should have UpBow, DownBow, Harmonic, and OpenString
        measure2 = violin_part.measures[1]
        
        # Get all leaves from the measure (individual notes, including those in beamed groups)
        all_leaves = list(measure2.iter_leaves())
        
        # Check for technical notations in the leaves
        assert any(isinstance(notation, UpBow) 
                  for leaf, _ in all_leaves if hasattr(leaf, 'notations') 
                  for notation in leaf.notations), "UpBow notation not found in measure 2"
        assert any(isinstance(notation, DownBow) 
                  for leaf, _ in all_leaves if hasattr(leaf, 'notations') 
                  for notation in leaf.notations), "DownBow notation not found in measure 2"
        assert any(isinstance(notation, Harmonic) 
                  for leaf, _ in all_leaves if hasattr(leaf, 'notations') 
                  for notation in leaf.notations), "Harmonic notation not found in measure 2"
        assert any(isinstance(notation, OpenString) 
                  for leaf, _ in all_leaves if hasattr(leaf, 'notations') 
                  for notation in leaf.notations), "OpenString notation not found in measure 2"
        
        # Measure 3 should have Arpeggiate and NonArpeggiate
        measure3 = violin_part.measures[2]
        assert any(isinstance(notation, Arpeggiate) for element in measure3.contents 
                  if hasattr(element, 'notations') for notation in element.notations)
        assert any(isinstance(notation, NonArpeggiate) for element in measure3.contents 
                  if hasattr(element, 'notations') for notation in element.notations)
                  
    except FileNotFoundError:
        pytest.skip("main_test.musicxml file not found, skipping test") 