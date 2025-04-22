"""
Tests for pickup measures in import/export.
"""
import os
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from pymusicxml import import_musicxml


class TestPickupMeasures(unittest.TestCase):
    """Tests for pickup/anacrusis measures in import/export operations."""
    
    def test_pickup_measure_number_preserved(self):
        """Test that pickup measure number is preserved during import/export."""
        # Path to the test file
        test_file_path = Path(__file__).parent / "../examples/import/MozartTrio.musicxml"
        
        # Import the MusicXML file
        score = import_musicxml(test_file_path)
        
        # Create a temporary file for the exported score
        temp_export_path = Path(__file__).parent / "temp_pickup_test.musicxml"
        
        try:
            # Export the score
            score.export_to_file(temp_export_path)
            
            # Parse the original and exported files
            original_tree = ET.parse(test_file_path)
            exported_tree = ET.parse(temp_export_path)
            
            # Get all measure elements from the first part in each file
            original_measures = original_tree.findall(".//part[@id='P1']/measure")
            exported_measures = exported_tree.findall(".//part[@id='P1']/measure")
            
            # Check that the number of measures is the same
            self.assertEqual(len(original_measures), len(exported_measures))
            
            # Check that the first measure has number="0" in both files
            self.assertEqual(original_measures[0].get("number"), "0")
            self.assertEqual(exported_measures[0].get("number"), "0")
            
            # Check that the second measure has number="1" in both files
            self.assertEqual(original_measures[1].get("number"), "1")
            self.assertEqual(exported_measures[1].get("number"), "1")
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_export_path):
                os.remove(temp_export_path)


if __name__ == "__main__":
    unittest.main() 