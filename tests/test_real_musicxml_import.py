"""
Tests for importing real MusicXML files.
"""

import os
import pytest
from pathlib import Path

from pymusicxml import import_musicxml, TraditionalKeySignature


def test_import_main_musicxml():
    """Test importing the main.musicxml file from the project."""
    # Path to the main.musicxml file
    file_path = Path("main.musicxml")
    
    # Make sure the file exists
    assert file_path.exists(), f"Test file {file_path} does not exist"
    
    # Import the score
    score = import_musicxml(file_path)
    
    # Check basic structure
    assert score.title == "Directly Created MusicXML"
    assert score.composer == "HTMLvis"
    
    # Check parts structure
    assert len(score.parts) == 3
    assert score.parts[0].part_name == "Oboe"
    assert score.parts[1].part_name == "Bb Clarinet"
    assert score.parts[2].part_name == "Bassoon"
    
    # Check part grouping
    assert len(score.contents) == 2  # One PartGroup and one Part
    assert score.contents[1].part_name == "Bassoon"  # The standalone part
    
    # Check measures
    for part in score.parts:
        assert len(part.measures) > 0


def test_import_simple_musicxml():
    """
    Test importing a simple static MusicXML string.
    """
    import tempfile
    
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
        imported_score = import_musicxml(temp_file)
        
        # Test score metadata
        assert imported_score.title == "Test Score"
        assert imported_score.composer == "Test Composer"
        
        # Test score structure
        assert len(imported_score.parts) == 1
        assert imported_score.parts[0].part_name == "Test Part"
        
        # Test measures
        assert len(imported_score.parts[0].measures) == 1
        
        # Test first part details
        measure = imported_score.parts[0].measures[0]
        assert measure.time_signature == (4, 4)
        assert measure.clef.sign == "G"
        assert measure.clef.line == "2"
        
        # Test key signatures
        assert isinstance(measure.key, TraditionalKeySignature)
        assert measure.key.fifths == 0
        
    finally:
        # Clean up
        os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 