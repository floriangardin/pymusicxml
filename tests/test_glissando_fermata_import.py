"""
Test module for importing glissando, fermata, and other missing notations from MusicXML files.

This module provides test cases for the import of glissando notations (StartGliss, StopGliss),
Fermata, SnapPizzicato, and Stopped technical notations.
"""

import io
import tempfile
import pytest
from xml.etree import ElementTree as ET

from pymusicxml import Score, Part, Measure, Note, Chord
from pymusicxml.importer import import_musicxml
from pymusicxml.notations import (
    StartGliss, StopGliss, StartMultiGliss, StopMultiGliss, Fermata,
    SnapPizzicato, Stopped
)


def get_musicxml_with_notations():
    """Create a simple MusicXML string with various notations for testing."""
    root = ET.Element("score-partwise", {"version": "3.1"})
    
    # Add part-list with one part
    part_list = ET.SubElement(root, "part-list")
    score_part = ET.SubElement(part_list, "score-part", {"id": "P1"})
    ET.SubElement(score_part, "part-name").text = "Test Notations"
    
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
    
    # Note with fermata
    note1 = ET.SubElement(measure, "note")
    pitch1 = ET.SubElement(note1, "pitch")
    ET.SubElement(pitch1, "step").text = "C"
    ET.SubElement(pitch1, "octave").text = "5"
    ET.SubElement(note1, "duration").text = "4"
    ET.SubElement(note1, "voice").text = "1"
    ET.SubElement(note1, "type").text = "quarter"
    notations1 = ET.SubElement(note1, "notations")
    ET.SubElement(notations1, "fermata")
    
    # Note with inverted fermata
    note2 = ET.SubElement(measure, "note")
    pitch2 = ET.SubElement(note2, "pitch")
    ET.SubElement(pitch2, "step").text = "D"
    ET.SubElement(pitch2, "octave").text = "5"
    ET.SubElement(note2, "duration").text = "4"
    ET.SubElement(note2, "voice").text = "1"
    ET.SubElement(note2, "type").text = "quarter"
    notations2 = ET.SubElement(note2, "notations")
    ET.SubElement(notations2, "fermata", {"type": "inverted"})
    
    # Note with glissando start
    note3 = ET.SubElement(measure, "note")
    pitch3 = ET.SubElement(note3, "pitch")
    ET.SubElement(pitch3, "step").text = "E"
    ET.SubElement(pitch3, "octave").text = "5"
    ET.SubElement(note3, "duration").text = "4"
    ET.SubElement(note3, "voice").text = "1"
    ET.SubElement(note3, "type").text = "quarter"
    notations3 = ET.SubElement(note3, "notations")
    ET.SubElement(notations3, "slide", {"type": "start", "number": "1"})
    
    # Note with glissando stop
    note4 = ET.SubElement(measure, "note")
    pitch4 = ET.SubElement(note4, "pitch")
    ET.SubElement(pitch4, "step").text = "F"
    ET.SubElement(pitch4, "octave").text = "5"
    ET.SubElement(note4, "duration").text = "4"
    ET.SubElement(note4, "voice").text = "1"
    ET.SubElement(note4, "type").text = "quarter"
    notations4 = ET.SubElement(note4, "notations")
    ET.SubElement(notations4, "slide", {"type": "stop", "number": "1"})
    
    # Create a second measure
    measure2 = ET.SubElement(part, "measure", {"number": "2"})
    
    # Note with technical notations (stopped)
    note5 = ET.SubElement(measure2, "note")
    pitch5 = ET.SubElement(note5, "pitch")
    ET.SubElement(pitch5, "step").text = "G"
    ET.SubElement(pitch5, "octave").text = "5"
    ET.SubElement(note5, "duration").text = "4"
    ET.SubElement(note5, "voice").text = "1"
    ET.SubElement(note5, "type").text = "quarter"
    notations5 = ET.SubElement(note5, "notations")
    technical5 = ET.SubElement(notations5, "technical")
    ET.SubElement(technical5, "stopped")
    
    # Note with technical notations (snap-pizzicato)
    note6 = ET.SubElement(measure2, "note")
    pitch6 = ET.SubElement(note6, "pitch")
    ET.SubElement(pitch6, "step").text = "A"
    ET.SubElement(pitch6, "octave").text = "5"
    ET.SubElement(note6, "duration").text = "4"
    ET.SubElement(note6, "voice").text = "1"
    ET.SubElement(note6, "type").text = "quarter"
    notations6 = ET.SubElement(note6, "notations")
    technical6 = ET.SubElement(notations6, "technical")
    ET.SubElement(technical6, "snap-pizzicato")
    
    # Chord with multiple glisses start
    # First note of chord
    chord1 = ET.SubElement(measure2, "note")
    pitch_c1 = ET.SubElement(chord1, "pitch")
    ET.SubElement(pitch_c1, "step").text = "C"
    ET.SubElement(pitch_c1, "octave").text = "5"
    ET.SubElement(chord1, "duration").text = "4"
    ET.SubElement(chord1, "voice").text = "1"
    ET.SubElement(chord1, "type").text = "quarter"
    notations_c1 = ET.SubElement(chord1, "notations")
    ET.SubElement(notations_c1, "slide", {"type": "start", "number": "1"})
    
    # Second note of chord
    chord2 = ET.SubElement(measure2, "note")
    chord_tag = ET.SubElement(chord2, "chord")
    pitch_c2 = ET.SubElement(chord2, "pitch")
    ET.SubElement(pitch_c2, "step").text = "E"
    ET.SubElement(pitch_c2, "octave").text = "5"
    ET.SubElement(chord2, "duration").text = "4"
    ET.SubElement(chord2, "voice").text = "1"
    ET.SubElement(chord2, "type").text = "quarter"
    notations_c2 = ET.SubElement(chord2, "notations")
    ET.SubElement(notations_c2, "slide", {"type": "start", "number": "2"})
    
    # Third note of chord
    chord3 = ET.SubElement(measure2, "note")
    chord_tag2 = ET.SubElement(chord3, "chord")
    pitch_c3 = ET.SubElement(chord3, "pitch")
    ET.SubElement(pitch_c3, "step").text = "G"
    ET.SubElement(pitch_c3, "octave").text = "5"
    ET.SubElement(chord3, "duration").text = "4"
    ET.SubElement(chord3, "voice").text = "1"
    ET.SubElement(chord3, "type").text = "quarter"
    notations_c3 = ET.SubElement(chord3, "notations")
    ET.SubElement(notations_c3, "slide", {"type": "start", "number": "3"})
    
    # Chord with multiple glisses stop
    # First note of chord
    chord4 = ET.SubElement(measure2, "note")
    pitch_c4 = ET.SubElement(chord4, "pitch")
    ET.SubElement(pitch_c4, "step").text = "D"
    ET.SubElement(pitch_c4, "octave").text = "5"
    ET.SubElement(chord4, "duration").text = "4"
    ET.SubElement(chord4, "voice").text = "1"
    ET.SubElement(chord4, "type").text = "quarter"
    notations_c4 = ET.SubElement(chord4, "notations")
    ET.SubElement(notations_c4, "slide", {"type": "stop", "number": "1"})
    
    # Second note of chord
    chord5 = ET.SubElement(measure2, "note")
    chord_tag3 = ET.SubElement(chord5, "chord")
    pitch_c5 = ET.SubElement(chord5, "pitch")
    ET.SubElement(pitch_c5, "step").text = "F"
    ET.SubElement(pitch_c5, "octave").text = "5"
    ET.SubElement(chord5, "duration").text = "4"
    ET.SubElement(chord5, "voice").text = "1"
    ET.SubElement(chord5, "type").text = "quarter"
    notations_c5 = ET.SubElement(chord5, "notations")
    ET.SubElement(notations_c5, "slide", {"type": "stop", "number": "2"})
    
    # Third note of chord
    chord6 = ET.SubElement(measure2, "note")
    chord_tag4 = ET.SubElement(chord6, "chord")
    pitch_c6 = ET.SubElement(chord6, "pitch")
    ET.SubElement(pitch_c6, "step").text = "A"
    ET.SubElement(pitch_c6, "octave").text = "5"
    ET.SubElement(chord6, "duration").text = "4"
    ET.SubElement(chord6, "voice").text = "1"
    ET.SubElement(chord6, "type").text = "quarter"
    notations_c6 = ET.SubElement(chord6, "notations")
    ET.SubElement(notations_c6, "slide", {"type": "stop", "number": "3"})
    
    xml_string = ET.tostring(root, encoding="unicode")
    return xml_string


def test_import_notations():
    """Test importing fermata, glissando, and technical notations from a MusicXML file."""
    # Create a temporary MusicXML file with notations
    xml_string = get_musicxml_with_notations()
    
    # Import the MusicXML string
    with tempfile.NamedTemporaryFile(suffix=".musicxml", mode="w") as tmp:
        tmp.write(xml_string)
        tmp.flush()
        score = import_musicxml(tmp.name)
    
    # Check the imported score
    assert len(score.parts) == 1
    part = score.parts[0]
    assert len(part.measures) == 2
    
    # Check measure 1 with fermata, inverted fermata, glissando start and stop
    measure1 = part.measures[0]
    assert len(measure1.contents) == 4
    
    # Check note with fermata
    note1 = measure1.contents[0]
    assert isinstance(note1, Note)
    assert len(note1.notations) == 1
    assert isinstance(note1.notations[0], Fermata)
    assert not note1.notations[0].inverted
    
    # Check note with inverted fermata
    note2 = measure1.contents[1]
    assert isinstance(note2, Note)
    assert len(note2.notations) == 1
    assert isinstance(note2.notations[0], Fermata)
    assert note2.notations[0].inverted
    
    # Check note with glissando start
    note3 = measure1.contents[2]
    assert isinstance(note3, Note)
    assert len(note3.notations) == 1
    assert isinstance(note3.notations[0], StartGliss)
    assert note3.notations[0].number == '1'
    
    # Check note with glissando stop
    note4 = measure1.contents[3]
    assert isinstance(note4, Note)
    assert len(note4.notations) == 1
    assert isinstance(note4.notations[0], StopGliss)
    assert note4.notations[0].number == '1'
    
    # Check measure 2 with stopped, snap-pizzicato, and multi-gliss
    measure2 = part.measures[1]
    assert len(measure2.contents) == 4
    
    # Check note with stopped
    note5 = measure2.contents[0]
    assert isinstance(note5, Note)
    assert len(note5.notations) == 1
    assert isinstance(note5.notations[0], Stopped)
    
    # Check note with snap-pizzicato
    note6 = measure2.contents[1]
    assert isinstance(note6, Note)
    assert len(note6.notations) == 1
    assert isinstance(note6.notations[0], SnapPizzicato)
    
    # Check chord with multiple glisses start
    chord1 = measure2.contents[2]
    assert isinstance(chord1, Chord)
    # Depending on the implementation, we expect either:
    # 1. Multiple StartGliss objects (one per note)
    # 2. Or a single StartMultiGliss object
    gliss_count = 0
    multi_gliss = None
    for notation in chord1.notations:
        if isinstance(notation, StartGliss):
            gliss_count += 1
        elif isinstance(notation, StartMultiGliss):
            multi_gliss = notation
    
    # Assert either we have multiple StartGliss notations or a single StartMultiGliss
    assert (gliss_count > 0) or (multi_gliss is not None), "No glissando notations found on chord"
    if multi_gliss is not None:
        assert len(multi_gliss.numbers) == 3
    
    # Check chord with multiple glisses stop
    chord2 = measure2.contents[3]
    assert isinstance(chord2, Chord)
    # Depending on the implementation, we expect either:
    # 1. Multiple StopGliss objects (one per note)
    # 2. Or a single StopMultiGliss object
    gliss_count = 0
    multi_gliss = None
    for notation in chord2.notations:
        if isinstance(notation, StopGliss):
            gliss_count += 1
        elif isinstance(notation, StopMultiGliss):
            multi_gliss = notation
    
    # Assert either we have multiple StopGliss notations or a single StopMultiGliss
    assert (gliss_count > 0) or (multi_gliss is not None), "No glissando notations found on chord"
    if multi_gliss is not None:
        assert len(multi_gliss.numbers) == 3


def test_round_trip():
    """Test round-trip import/export of a score with fermata, glissando, and technical notations."""
    # Create a score with fermata, glissando, and technical notations
    score = Score([
        Part("Notations Test", [
            Measure([
                Note("c5", 1, notations=[Fermata()]),
                Note("d5", 1, notations=[Fermata(inverted=True)]),
                Note("e5", 1, notations=[StartGliss(1)]),
                Note("f5", 1, notations=[StopGliss(1)])
            ], time_signature=(4, 4)),
            Measure([
                Note("g5", 1, notations=[Stopped()]),
                Note("a5", 1, notations=[SnapPizzicato()]),
                Chord(["c5", "e5", "g5"], 1, notations=[StartMultiGliss((1, 2, 3))]),
                Chord(["d5", "f5", "a5"], 1, notations=[StopMultiGliss((1, 2, 3))])
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
    assert len(part.measures) == 2
    
    # Verify measure 1
    measure1 = part.measures[0]
    assert len(measure1.contents) == 4
    assert isinstance(measure1.contents[0].notations[0], Fermata)
    assert not measure1.contents[0].notations[0].inverted
    assert isinstance(measure1.contents[1].notations[0], Fermata)
    assert measure1.contents[1].notations[0].inverted
    assert isinstance(measure1.contents[2].notations[0], StartGliss)
    assert measure1.contents[2].notations[0].number == '1'
    assert isinstance(measure1.contents[3].notations[0], StopGliss)
    assert measure1.contents[3].notations[0].number == '1'
    
    # Verify measure 2
    measure2 = part.measures[1]
    assert len(measure2.contents) == 4
    assert isinstance(measure2.contents[0].notations[0], Stopped)
    assert isinstance(measure2.contents[1].notations[0], SnapPizzicato)
    
    # Check chord with multiple glisses start
    chord1 = measure2.contents[2]
    assert isinstance(chord1, Chord)
    # Count the number of StartGliss notations or verify StartMultiGliss
    gliss_count = 0
    multi_gliss = None
    for notation in chord1.notations:
        if isinstance(notation, StartGliss):
            gliss_count += 1
        elif isinstance(notation, StartMultiGliss):
            multi_gliss = notation
    
    # Assert either we have multiple StartGliss notations or a single StartMultiGliss
    assert (gliss_count > 0) or (multi_gliss is not None), "No glissando notations found on chord"
    
    # Check chord with multiple glisses stop
    chord2 = measure2.contents[3]
    assert isinstance(chord2, Chord)
    # Count the number of StopGliss notations or verify StopMultiGliss
    gliss_count = 0
    multi_gliss = None
    for notation in chord2.notations:
        if isinstance(notation, StopGliss):
            gliss_count += 1
        elif isinstance(notation, StopMultiGliss):
            multi_gliss = notation
    
    # Assert either we have multiple StopGliss notations or a single StopMultiGliss
    assert (gliss_count > 0) or (multi_gliss is not None), "No glissando notations found on chord"


def test_import_from_real_file():
    """Test importing notations from the main_test.musicxml file."""
    try:
        score = import_musicxml("main_test.musicxml")
        
        # Look for fermatas, glisses, and technical notations in the score
        found_fermata = False
        found_gliss_start = False
        found_gliss_stop = False
        
        for part in score.parts:
            for measure in part.measures:
                for item in measure.contents:
                    if hasattr(item, 'notations') and item.notations:
                        for notation in item.notations:
                            if isinstance(notation, Fermata):
                                found_fermata = True
                            elif isinstance(notation, StartGliss):
                                found_gliss_start = True
                            elif isinstance(notation, StopGliss):
                                found_gliss_stop = True
        
        # The main_test file should contain gliss notations
        assert found_gliss_start, "StartGliss notation not found in main_test.musicxml"
        assert found_gliss_stop, "StopGliss notation not found in main_test.musicxml"
        
        # Note: Fermata might not be in the main_test, so we don't assert it
        
    except FileNotFoundError:
        pytest.skip("main_test.musicxml file not found, skipping test") 