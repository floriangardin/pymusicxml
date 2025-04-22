"""
Test the import of articulations from MusicXML files.
"""

import unittest
import xml.etree.ElementTree as ET
from pymusicxml.importers.musical_elements import MusicalElementsImporter
from pymusicxml.score_components import Note, Chord


class TestArticulationImport(unittest.TestCase):
    """Test the import of articulations from MusicXML files."""

    def test_import_single_articulation(self):
        """Test importing a single articulation."""
        # Create a simple note with staccato
        xml_str = """
        <note>
            <pitch>
                <step>C</step>
                <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
            <notations>
                <articulations>
                    <staccato/>
                </articulations>
            </notations>
        </note>
        """
        note_elem = ET.fromstring(xml_str)
        
        # Create helper functions for element access
        find_element = lambda elem, tag: elem.find(tag)
        get_text = lambda elem, tag, default=None: elem.findtext(tag) if elem.findtext(tag) is not None else default
        find_elements = lambda elem, tag: elem.findall(tag)
        
        # Import the note
        note = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
        
        # Check that we got a note with the correct articulation
        self.assertIsInstance(note, Note)
        self.assertEqual(len(note.articulations), 1)
        self.assertEqual(note.articulations[0], "staccato")

    def test_import_multiple_articulations(self):
        """Test importing multiple articulations on a single note."""
        # Create a note with multiple articulations
        xml_str = """
        <note>
            <pitch>
                <step>C</step>
                <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
            <notations>
                <articulations>
                    <staccato/>
                    <accent/>
                    <tenuto/>
                </articulations>
            </notations>
        </note>
        """
        note_elem = ET.fromstring(xml_str)
        
        # Create helper functions for element access
        find_element = lambda elem, tag: elem.find(tag)
        get_text = lambda elem, tag, default=None: elem.findtext(tag) if elem.findtext(tag) is not None else default
        find_elements = lambda elem, tag: elem.findall(tag)
        
        # Import the note
        note = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
        
        # Check that we got a note with the correct articulations
        self.assertIsInstance(note, Note)
        self.assertEqual(len(note.articulations), 3)
        self.assertIn("staccato", note.articulations)
        self.assertIn("accent", note.articulations)
        self.assertIn("tenuto", note.articulations)

    def test_import_chord_with_articulations(self):
        """Test importing articulations on a chord."""
        # Create a first note of a chord with articulations
        first_note_xml = """
        <note>
            <pitch>
                <step>C</step>
                <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
            <notations>
                <articulations>
                    <staccato/>
                    <accent/>
                </articulations>
            </notations>
        </note>
        """
        first_note_elem = ET.fromstring(first_note_xml)
        
        # Create a second note of the chord
        second_note_xml = """
        <note>
            <chord/>
            <pitch>
                <step>E</step>
                <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
        </note>
        """
        second_note_elem = ET.fromstring(second_note_xml)
        
        # Create helper functions for element access
        find_element = lambda elem, tag: elem.find(tag)
        get_text = lambda elem, tag, default=None: elem.findtext(tag) if elem.findtext(tag) is not None else default
        find_elements = lambda elem, tag: elem.findall(tag)
        
        # Import the chord
        chord = MusicalElementsImporter.import_chord(
            first_note_elem, [first_note_elem, second_note_elem], 
            find_element, get_text, find_elements
        )
        
        # Check that we got a chord with the correct articulations
        self.assertIsInstance(chord, Chord)
        self.assertEqual(len(chord.articulations), 2)
        self.assertIn("staccato", chord.articulations)
        self.assertIn("accent", chord.articulations)

    def test_all_possible_articulations(self):
        """Test importing all possible articulations."""
        # Create a note with all articulation types
        xml_str = """
        <note>
            <pitch>
                <step>C</step>
                <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
            <notations>
                <articulations>
                    <accent/>
                    <strong-accent/>
                    <staccato/>
                    <tenuto/>
                    <detached-legato/>
                    <staccatissimo/>
                    <spiccato/>
                    <scoop/>
                    <plop/>
                    <doit/>
                    <falloff/>
                    <breath-mark/>
                    <caesura/>
                    <stress/>
                    <unstress/>
                </articulations>
            </notations>
        </note>
        """
        note_elem = ET.fromstring(xml_str)
        
        # Create helper functions for element access
        find_element = lambda elem, tag: elem.find(tag)
        get_text = lambda elem, tag, default=None: elem.findtext(tag) if elem.findtext(tag) is not None else default
        find_elements = lambda elem, tag: elem.findall(tag)
        
        # Import the note
        note = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
        
        # Check that we got a note with all articulations
        self.assertIsInstance(note, Note)
        self.assertEqual(len(note.articulations), 15)
        
        # Expected articulation types
        expected_articulations = [
            "accent", "strong-accent", "staccato", "tenuto", "detached-legato", 
            "staccatissimo", "spiccato", "scoop", "plop", "doit", "falloff", 
            "breath-mark", "caesura", "stress", "unstress"
        ]
        
        # Check that all expected articulations are present
        for art in expected_articulations:
            self.assertIn(art, note.articulations)

    def test_no_articulations(self):
        """Test importing a note with no articulations."""
        # Create a simple note with no articulations
        xml_str = """
        <note>
            <pitch>
                <step>C</step>
                <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
        </note>
        """
        note_elem = ET.fromstring(xml_str)
        
        # Create helper functions for element access
        find_element = lambda elem, tag: elem.find(tag)
        get_text = lambda elem, tag, default=None: elem.findtext(tag) if elem.findtext(tag) is not None else default
        find_elements = lambda elem, tag: elem.findall(tag)
        
        # Import the note
        note = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
        
        # Check that we got a note with no articulations
        self.assertIsInstance(note, Note)
        self.assertEqual(len(note.articulations), 0)


if __name__ == '__main__':
    unittest.main() 