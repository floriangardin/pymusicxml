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


def test_import_score_with_credits():
    """Test importing a score with title, composer, and copyright information."""
    
    # Create a temporary MusicXML file with title, composer, and copyright
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
  <movement-title>Test Score Title</movement-title>
  <identification>
    <creator type="composer">Test Composer Name</creator>
    <rights>Copyright © 2025 Test Copyright</rights>
    <encoding>
      <software>TestSoftware</software>
      <encoding-date>2025-01-01</encoding-date>
    </encoding>
  </identification>
  <credit page="1">
    <credit-type>title</credit-type>
    <credit-words default-x="850" default-y="2106" justify="center" valign="top" font-size="22">Test Score Title</credit-words>
  </credit>
  <credit page="1">
    <credit-type>composer</credit-type>
    <credit-words default-x="1645" default-y="1968" justify="right" valign="bottom" font-size="10">Test Composer Name</credit-words>
  </credit>
  <credit page="1">
    <credit-type>rights</credit-type>
    <credit-words default-x="850" default-y="94" justify="center" valign="bottom">Copyright © 2025 Test Copyright</credit-words>
  </credit>
  <part-list>
    <score-part id="P1">
      <part-name>Test Part</part-name>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <key>
          <fifths>0</fifths>
        </key>
        <time>
          <beats>4</beats>
          <beat-type>4</beat-type>
        </time>
        <clef>
          <sign>G</sign>
          <line>2</line>
        </clef>
      </attributes>
      <note>
        <rest/>
        <duration>4</duration>
        <voice>1</voice>
        <type>whole</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""
    
    # Create temp file
    temp_file = os.path.join(tempfile.gettempdir(), "test_credits.musicxml")
    with open(temp_file, 'w') as f:
        f.write(xml_content)
    
    try:
        # Import the score
        score = import_musicxml(temp_file)
        
        # Test score metadata
        assert score.title == "Test Score Title"
        assert score.composer == "Test Composer Name"
        assert score.copyright == "Copyright © 2025 Test Copyright"
        
        # Export to a new file
        export_file = os.path.join(tempfile.gettempdir(), "test_credits_exported.musicxml")
        score.export_to_file(export_file)
        
        # Re-import the exported file to verify credits were preserved
        exported_score = import_musicxml(export_file)
        
        # Verify metadata in re-imported score
        assert exported_score.title == "Test Score Title"
        assert exported_score.composer == "Test Composer Name"
        assert exported_score.copyright == "Copyright © 2025 Test Copyright"
        
        # Verify credit elements in the XML
        tree = ET.parse(export_file)
        root = tree.getroot()
        
        # Check for identification/rights
        rights_elem = root.find(".//identification/rights")
        assert rights_elem is not None
        assert rights_elem.text == "Copyright © 2025 Test Copyright"
        
        # Check for credit elements
        credit_elements = root.findall(".//credit")
        assert len(credit_elements) >= 3
        
        # Check for rights credit
        found_rights_credit = False
        for credit in credit_elements:
            credit_type = credit.find("credit-type")
            if credit_type is not None and credit_type.text == "rights":
                credit_words = credit.find("credit-words")
                assert credit_words is not None
                assert credit_words.text == "Copyright © 2025 Test Copyright"
                found_rights_credit = True
        
        assert found_rights_credit, "Copyright credit element not found in exported XML"
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        if os.path.exists(export_file):
            os.unlink(export_file)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 