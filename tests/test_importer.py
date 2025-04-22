"""
Tests for the MusicXML importer functionality.
"""

import os
import pytest
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import zipfile
import shutil

from pymusicxml import (
    Score, Part, PartGroup, Measure, Clef,
    Pitch, Duration, Note, Chord, Rest, import_musicxml
)
from pymusicxml.importers.base_importer import MusicXMLImporter


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


def test_import_mxl_file():
    """Test importing a compressed MusicXML (.mxl) file."""
    # Create a temporary directory for our test
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a simple MusicXML file
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
        <score-partwise>
            <work>
                <work-title>Test MXL Score</work-title>
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
                    </attributes>
                </measure>
            </part>
        </score-partwise>
        """
        
        # Create paths for our files
        xml_path = os.path.join(temp_dir, "score.xml")
        mxl_path = os.path.join(temp_dir, "score.mxl")
        
        # Write the XML content to a file
        with open(xml_path, 'w') as f:
            f.write(xml_content)
        
        # Create META-INF directory and container.xml file
        meta_inf_dir = os.path.join(temp_dir, "META-INF")
        os.makedirs(meta_inf_dir, exist_ok=True)
        
        container_content = """<?xml version="1.0" encoding="UTF-8"?>
        <container>
            <rootfiles>
                <rootfile full-path="score.xml" media-type="application/vnd.recordare.musicxml+xml"/>
            </rootfiles>
        </container>
        """
        
        with open(os.path.join(meta_inf_dir, "container.xml"), 'w') as f:
            f.write(container_content)
        
        # Create the MXL file (ZIP archive)
        with zipfile.ZipFile(mxl_path, 'w') as zipf:
            # Add the score.xml file
            zipf.write(xml_path, arcname="score.xml")
            # Add the META-INF/container.xml file
            zipf.write(os.path.join(meta_inf_dir, "container.xml"), 
                      arcname="META-INF/container.xml")
        
        # Now test our MXL importer
        importer = MusicXMLImporter(mxl_path)
        
        # Check that the root element was extracted correctly
        assert importer.root is not None
        assert importer.root.tag == "score-partwise"
        
        # Test importing the score using the import_musicxml function
        score = import_musicxml(mxl_path)
        
        # Verify score details
        assert score.title == "Test MXL Score"
        assert score.composer == "Test Composer"
        assert len(score.parts) == 1
        assert score.parts[0].part_name == "Test Part"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 