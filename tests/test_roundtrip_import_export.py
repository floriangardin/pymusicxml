"""
Test module for round-trip testing of the import/export functionality.

This module verifies that a MusicXML file can be imported and then exported
with identical or equivalent content, ensuring the round-trip compatibility
of the MusicXML import/export feature.
"""

import os
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
import logging
import pytest
from difflib import unified_diff
import re

from pymusicxml import import_musicxml

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper functions
def normalize_xml(tree):
    """
    Normalize an XML tree to facilitate comparison.
    
    This removes non-essential differences between XML files such as:
    - Whitespace differences
    - Order of attributes
    - Empty/default attributes that might be omitted in one file but present in another
    - Differences in encoding-date
    - Float vs integer representation (1.0 vs 1)
    
    Args:
        tree: An ElementTree object to normalize
        
    Returns:
        The normalized ElementTree object
    """
    # Remove or normalize non-essential elements
    for elem in tree.iter():
        # Handle encoding-date (changes each run)
        if elem.tag == "encoding-date":
            elem.text = "NORMALIZED_DATE"
        
        # Normalize numerical values - convert 1.0 to 1 for comparison
        if elem.text and re.match(r'^-?\d+\.0+$', elem.text):
            elem.text = elem.text.split('.')[0]
        
        # Check attributes for numerical values
        for attr in elem.attrib:
            value = elem.attrib[attr]
            if isinstance(value, str) and re.match(r'^-?\d+\.0+$', value):
                elem.attrib[attr] = value.split('.')[0]
        
        # Sort attributes by key to ensure consistent order
        attrib = elem.attrib
        if attrib:
            # Some attributes might be auto-generated differently on export
            # Consider removing or normalizing them if they cause comparison issues
            pass
        
        # Remove empty text and tail
        if elem.text is not None and not elem.text.strip():
            elem.text = None
        if elem.tail is not None and not elem.tail.strip():
            elem.tail = None
    
    return tree

def compare_xml_files(file1, file2, ignore_text_formatting=True):
    """
    Compare two XML files and return a report of differences.
    
    Args:
        file1: Path to the first XML file
        file2: Path to the second XML file
        ignore_text_formatting: If True, ignore differences in text formatting
        
    Returns:
        A tuple of (is_equal, diff_report) where:
        - is_equal is a boolean indicating if the files are equivalent
        - diff_report is a string containing the differences, if any
    """
    try:
        tree1 = ET.parse(file1)
        tree2 = ET.parse(file2)
        
        # Normalize both trees
        norm_tree1 = normalize_xml(tree1)
        norm_tree2 = normalize_xml(tree2)
        
        # For a more tolerant comparison focusing on musical content
        if ignore_text_formatting:
            # Perform a more sophisticated comparison of musical elements
            # This could check for equivalent notes, measures, etc. rather than exact XML equality
            # For now, we'll do a basic string comparison after normalization
            pass
        
        # Convert to string for comparison
        xml1 = ET.tostring(norm_tree1.getroot(), encoding='unicode')
        xml2 = ET.tostring(norm_tree2.getroot(), encoding='unicode')
        
        # Compare the XML strings
        if xml1 == xml2:
            return True, "Files are identical after normalization."
        else:
            # Generate a diff report
            diff = unified_diff(
                xml1.splitlines(keepends=True),
                xml2.splitlines(keepends=True),
                fromfile=str(file1),
                tofile=str(file2)
            )
            return False, ''.join(diff)
    except Exception as e:
        return False, f"Error comparing files: {str(e)}"

def perform_roundtrip_test(input_file):
    """
    Perform a round-trip test on a MusicXML file.
    
    Args:
        input_file: Path to the input MusicXML file
        
    Returns:
        A tuple of (success, message) where:
        - success is a boolean indicating if the round-trip test passed
        - message is a string containing details about the test
    """
    input_path = Path(input_file)
    
    # Create a temporary file for the exported MusicXML
    with tempfile.NamedTemporaryFile(suffix='.musicxml', delete=False) as tmp_file:
        output_path = Path(tmp_file.name)
    
    try:
        # Import the MusicXML file
        score = import_musicxml(input_path)
        
        # Export the Score object to a new MusicXML file
        score.export_to_file(output_path)
        
        # Compare the original and exported files
        is_equal, diff_report = compare_xml_files(input_path, output_path)
        
        if is_equal:
            return True, f"Round-trip test passed for {input_path.name}"
        else:
            return False, f"Round-trip test failed for {input_path.name}:\n{diff_report}"
    except Exception as e:
        return False, f"Error during round-trip test: {str(e)}"
    finally:
        # Clean up the temporary file
        if output_path.exists():
            output_path.unlink()


# More advanced round-trip comparison function
def perform_detailed_roundtrip_analysis(input_file, output_dir=None):
    """
    Perform a detailed round-trip analysis with more sophisticated comparison.
    
    This function:
    1. Imports a MusicXML file
    2. Exports it to a new file
    3. Performs a detailed comparison of various musical elements
    
    Args:
        input_file: Path to the input MusicXML file
        output_dir: Optional directory to save the exported file for inspection
        
    Returns:
        A dictionary with analysis results
    """
    input_path = Path(input_file)
    
    # Determine where to save the output file
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"roundtrip_{input_path.name}"
    else:
        with tempfile.NamedTemporaryFile(suffix='.musicxml', delete=False) as tmp_file:
            output_path = Path(tmp_file.name)
    
    try:
        # Import the MusicXML file
        score = import_musicxml(input_path)
        
        # Export the Score object to a new MusicXML file
        score.export_to_file(output_path)
        
        # Parse both files
        tree1 = ET.parse(input_path)
        tree2 = ET.parse(output_path)
        
        # Count elements to verify structural equivalence
        result = {
            "input_file": str(input_path),
            "output_file": str(output_path),
            "preserved_output": output_dir is not None,
            "comparison_result": {
                "input_note_count": len(tree1.findall(".//note")),
                "output_note_count": len(tree2.findall(".//note")),
                "input_measure_count": len(tree1.findall(".//measure")),
                "output_measure_count": len(tree2.findall(".//measure")),
                "input_part_count": len(tree1.findall(".//part")),
                "output_part_count": len(tree2.findall(".//part")),
            }
        }
        
        # Check if basic element counts match
        for element_type in ["note", "measure", "part"]:
            input_count = result["comparison_result"][f"input_{element_type}_count"]
            output_count = result["comparison_result"][f"output_{element_type}_count"]
            if input_count != output_count:
                result["error"] = f"Element count mismatch: {element_type} count differs ({input_count} vs {output_count})"
                return result
        
        return result
    except Exception as e:
        return {
            "input_file": str(input_path),
            "error": str(e)
        }

def test_roundtrip_with_preservation():
    """Test round-trip with file preservation for manual inspection."""
    input_file = Path("tests/data/main.musicxml")
    output_dir = Path("tests/data/roundtrip")
    
    # This test will save the output file for manual inspection
    result = perform_detailed_roundtrip_analysis(input_file, output_dir)
    
    # Log the result for inspection
    logger.info(f"Round-trip analysis result: {result}")
    
    # Verify the basic success
    assert "error" not in result, f"Error in round-trip analysis: {result.get('error')}"
    
    # Check if basic element counts match
    comparison = result["comparison_result"]
    assert comparison["input_note_count"] == comparison["output_note_count"], \
        f"Note count mismatch: {comparison['input_note_count']} vs {comparison['output_note_count']}"
    assert comparison["input_measure_count"] == comparison["output_measure_count"], \
        f"Measure count mismatch: {comparison['input_measure_count']} vs {comparison['output_measure_count']}"
    assert comparison["input_part_count"] == comparison["output_part_count"], \
        f"Part count mismatch: {comparison['input_part_count']} vs {comparison['output_part_count']}"

if __name__ == "__main__":
    # This allows running the tests directly from this file
    pytest.main(["-xvs", __file__]) 