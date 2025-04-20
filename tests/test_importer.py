"""
Tests for the MusicXML importer functionality.
"""

import os
import pytest
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET

from pymusicxml import (
    Score, Part, PartGroup, Measure, Clef,
    Pitch, Duration, Note, Chord, Rest, import_musicxml
)


def test_import_empty_score():
    """Test importing an empty score with just metadata."""
    # Create a simple MusicXML file
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise>
        <work>
            <work-title>Test Score</work-title>
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
            </measure>
        </part>
    </score-partwise>
    """
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as f:
        f.write(xml_content.encode('utf-8'))
        temp_file = f.name
    
    try:
        # Import the score
        score = import_musicxml(temp_file)
        
        # Test score metadata
        assert score.title == "Test Score"
        assert score.composer == "Test Composer"
        
        # Test score structure
        assert len(score.parts) == 1
        assert score.parts[0].part_name == "Test Part"
        assert score.parts[0].part_id == 1
        
        # Test measure attributes
        assert len(score.parts[0].measures) == 1
        measure = score.parts[0].measures[0]
        assert measure.time_signature == (4, 4)
        assert measure.clef.sign == "G"
        assert measure.clef.line == "2"  # Line is stored as a string in the Clef class
        
    finally:
        # Clean up
        os.unlink(temp_file)


def test_import_part_group():
    """Test importing a score with a part group."""
    # Create a MusicXML file with a part group
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise>
        <part-list>
            <part-group type="start">
                <group-symbol>bracket</group-symbol>
                <group-barline>yes</group-barline>
            </part-group>
            <score-part id="P1">
                <part-name>Oboe</part-name>
            </score-part>
            <score-part id="P2">
                <part-name>Clarinet</part-name>
            </score-part>
            <part-group type="stop"/>
            <score-part id="P3">
                <part-name>Bassoon</part-name>
            </score-part>
        </part-list>
        <part id="P1">
            <measure number="1"/>
        </part>
        <part id="P2">
            <measure number="1"/>
        </part>
        <part id="P3">
            <measure number="1"/>
        </part>
    </score-partwise>
    """
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as f:
        f.write(xml_content.encode('utf-8'))
        temp_file = f.name
    
    try:
        # Import the score
        score = import_musicxml(temp_file)
        
        # Check the top-level structure
        assert len(score.contents) == 2  # One PartGroup and one Part
        assert isinstance(score.contents[0], PartGroup)
        assert isinstance(score.contents[1], Part)
        
        # Check the part group
        part_group = score.contents[0]
        assert len(part_group.parts) == 2
        assert part_group.parts[0].part_name == "Oboe"
        assert part_group.parts[1].part_name == "Clarinet"
        assert part_group.has_bracket is True
        assert part_group.has_group_bar_line is True
        
        # Check the standalone part
        assert score.contents[1].part_name == "Bassoon"
        
    finally:
        # Clean up
        os.unlink(temp_file)


def test_import_transpose():
    """Test importing a score with transposition."""
    # Create a MusicXML file with transposition
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise>
        <part-list>
            <score-part id="P1">
                <part-name>Clarinet in Bb</part-name>
            </score-part>
        </part-list>
        <part id="P1">
            <measure number="1">
                <attributes>
                    <divisions>4</divisions>
                    <transpose>
                        <diatonic>-1</diatonic>
                        <chromatic>-2</chromatic>
                        <octave-change>0</octave-change>
                    </transpose>
                </attributes>
            </measure>
        </part>
    </score-partwise>
    """
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as f:
        f.write(xml_content.encode('utf-8'))
        temp_file = f.name
    
    try:
        # Import the score
        score = import_musicxml(temp_file)
        
        # Check the transpose element
        measure = score.parts[0].measures[0]
        assert measure.transpose is not None
        assert measure.transpose.chromatic == -2
        assert measure.transpose.diatonic == -1
        assert measure.transpose.octave == 0
        
    finally:
        # Clean up
        os.unlink(temp_file)


def test_basic_import_export():
    """Test a basic import/export scenario without a complete round trip."""
    # Create a minimal score with just one empty measure
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise>
        <work>
            <work-title>Basic Test Score</work-title>
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
                        <beats>3</beats>
                        <beat-type>4</beat-type>
                    </time>
                    <key>
                        <fifths>0</fifths>
                        <mode>major</mode>
                    </key>
                </attributes>
            </measure>
        </part>
    </score-partwise>
    """
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(suffix=".musicxml", delete=False) as f:
        f.write(xml_content.encode('utf-8'))
        temp_file = f.name
    
    try:
        # Import the score
        imported_score = import_musicxml(temp_file)
        
        # Test score metadata
        assert imported_score.title == "Basic Test Score"
        assert imported_score.composer == "Test Composer"
        
        # Test score structure
        assert len(imported_score.parts) == 1
        assert imported_score.parts[0].part_name == "Test Part"
        
        # Test measure attributes
        measure = imported_score.parts[0].measures[0]
        assert measure.time_signature == (3, 4)
        
    finally:
        # Clean up
        os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 