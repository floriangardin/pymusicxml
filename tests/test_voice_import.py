"""
Tests for importing voices from MusicXML files.
"""

import pytest
import tempfile
import os
import xml.etree.ElementTree as ET

from pymusicxml import import_musicxml
from pymusicxml.score_components import Note, Rest, Chord, Measure


def create_test_musicxml_with_voices():
    """Create a simple MusicXML file with multiple voices."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise>
        <work>
            <work-title>Voice Test Score</work-title>
        </work>
        <identification>
            <creator type="composer">Test Composer</creator>
        </identification>
        <part-list>
            <score-part id="P1">
                <part-name>Test Part</part-name>
            </score-part>
        </part-list>
        <part id="P1">
            <measure number="1">
                <attributes>
                    <divisions>4</divisions>
                    <time>
                        <beats>4</beats>
                        <beat-type>4</beat-type>
                    </time>
                    <key>
                        <fifths>0</fifths>
                        <mode>major</mode>
                    </key>
                    <clef>
                        <sign>G</sign>
                        <line>2</line>
                    </clef>
                </attributes>
                <!-- Voice 1 -->
                <note>
                    <pitch>
                        <step>C</step>
                        <octave>5</octave>
                    </pitch>
                    <duration>4</duration>
                    <voice>1</voice>
                    <type>quarter</type>
                </note>
                <note>
                    <pitch>
                        <step>D</step>
                        <octave>5</octave>
                    </pitch>
                    <duration>4</duration>
                    <voice>1</voice>
                    <type>quarter</type>
                </note>
                <!-- Voice 2 (parallel to voice 1) -->
                <backup>
                    <duration>8</duration>
                </backup>
                <note>
                    <pitch>
                        <step>E</step>
                        <octave>4</octave>
                    </pitch>
                    <duration>2</duration>
                    <voice>2</voice>
                    <type>eighth</type>
                </note>
                <note>
                    <pitch>
                        <step>F</step>
                        <octave>4</octave>
                    </pitch>
                    <duration>2</duration>
                    <voice>2</voice>
                    <type>eighth</type>
                </note>
                <note>
                    <pitch>
                        <step>G</step>
                        <octave>4</octave>
                    </pitch>
                    <duration>4</duration>
                    <voice>2</voice>
                    <type>quarter</type>
                </note>
                <!-- Continue voice 1 -->
                <backup>
                    <duration>0</duration>
                </backup>
                <note>
                    <pitch>
                        <step>E</step>
                        <octave>5</octave>
                    </pitch>
                    <duration>4</duration>
                    <voice>1</voice>
                    <type>quarter</type>
                </note>
                <note>
                    <pitch>
                        <step>F</step>
                        <octave>5</octave>
                    </pitch>
                    <duration>4</duration>
                    <voice>1</voice>
                    <type>quarter</type>
                </note>
                <!-- Continue voice 2 -->
                <backup>
                    <duration>8</duration>
                </backup>
                <note>
                    <pitch>
                        <step>A</step>
                        <octave>4</octave>
                    </pitch>
                    <duration>8</duration>
                    <voice>2</voice>
                    <type>half</type>
                </note>
            </measure>
        </part>
    </score-partwise>
    """
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as f:
        f.write(xml_content.encode('utf-8'))
        return f.name


def test_voice_import():
    """Test importing voices from MusicXML."""
    # Create test file
    temp_file = create_test_musicxml_with_voices()
    
    try:
        # Import score
        score = import_musicxml(temp_file)
        
        # Check score structure
        assert len(score.parts) == 1
        part = score.parts[0]
        assert len(part.measures) == 1
        measure = part.measures[0]
        
        # Check if voices are correctly separated
        voices = measure.voices
        assert len(voices) == 2, f"Expected 2 voices, got {len(voices)}"
        
        # Check voice 1 (index 0)
        voice1 = voices[0]
        assert len(voice1) == 4, f"Expected 4 notes in voice 1, got {len(voice1)}"
        assert all(isinstance(note, Note) for note in voice1)
        assert all(note.voice == 1 for note in voice1)
        assert [note.pitch.step for note in voice1] == ["C", "D", "E", "F"]
        
        # Check voice 2 (index 1)
        voice2 = voices[1]
        assert len(voice2) == 4, f"Expected 4 notes in voice 2, got {len(voice2)}"
        assert all(isinstance(note, Note) for note in voice2)
        assert all(note.voice == 2 for note in voice2)
        assert [note.pitch.step for note in voice2] == ["E", "F", "G", "A"]
        
        # Test leaf iteration
        leaves = list(measure.iter_leaves())
        # We expect the notes to be ordered by beat within measure
        assert len(leaves) == 8
        
        # Test filtering by voice
        voice1_leaves = list(measure.iter_leaves([0]))
        assert len(voice1_leaves) == 4
        assert all(leaf[0].voice == 1 for leaf in voice1_leaves)
        
        voice2_leaves = list(measure.iter_leaves([1]))
        assert len(voice2_leaves) == 4
        assert all(leaf[0].voice == 2 for leaf in voice2_leaves)
        
    finally:
        # Clean up
        os.unlink(temp_file)


def test_single_voice_import():
    """Test that a measure with a single voice still works correctly."""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise>
        <part-list>
            <score-part id="P1">
                <part-name>Test Part</part-name>
            </score-part>
        </part-list>
        <part id="P1">
            <measure number="1">
                <attributes>
                    <divisions>4</divisions>
                    <time><beats>4</beats><beat-type>4</beat-type></time>
                </attributes>
                <note>
                    <pitch><step>C</step><octave>4</octave></pitch>
                    <duration>4</duration>
                    <voice>1</voice>
                    <type>quarter</type>
                </note>
                <note>
                    <pitch><step>D</step><octave>4</octave></pitch>
                    <duration>4</duration>
                    <voice>1</voice>
                    <type>quarter</type>
                </note>
                <note>
                    <pitch><step>E</step><octave>4</octave></pitch>
                    <duration>4</duration>
                    <voice>1</voice>
                    <type>quarter</type>
                </note>
                <note>
                    <pitch><step>F</step><octave>4</octave></pitch>
                    <duration>4</duration>
                    <voice>1</voice>
                    <type>quarter</type>
                </note>
            </measure>
        </part>
    </score-partwise>
    """
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as f:
        f.write(xml_content.encode('utf-8'))
        temp_file = f.name
    
    try:
        # Import score
        score = import_musicxml(temp_file)
        
        # Check measure contents
        measure = score.parts[0].measures[0]
        
        # Check if contents is a flat list, not a list of voices
        assert len(measure.voices) == 1, "Expected 1 voice"
        assert len(measure.voices[0]) == 4, "Expected 4 notes"
        
        # Check notes
        notes = measure.voices[0]
        assert all(isinstance(note, Note) for note in notes)
        assert all(note.voice == 1 for note in notes)
        assert [note.pitch.step for note in notes] == ["C", "D", "E", "F"]
        
    finally:
        # Clean up
        os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 