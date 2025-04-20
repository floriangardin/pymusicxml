"""
Tests for importing musical elements from MusicXML files.

This module tests the import functionality for musical elements like
notes, chords, beamed groups, and tuplets.
"""

import os
import tempfile
import xml.etree.ElementTree as ET
import pytest

from pymusicxml.importers.musical_elements import MusicalElementsImporter
from pymusicxml import (
    Score, Part, Measure, Note, Rest, Chord, GraceNote, GraceChord,
    Pitch, Duration, BeamedGroup, Tuplet
)
from pymusicxml.importer import import_musicxml


def test_import_chord():
    """Test importing a chord element."""
    # Create a simple MusicXML file with a chord
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise version="3.1">
      <part-list>
        <score-part id="P1">
          <part-name>Music</part-name>
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
            <pitch>
              <step>C</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>E</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
            <voice>1</voice>
            <chord/>
          </note>
          <note>
            <pitch>
              <step>G</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
            <voice>1</voice>
            <chord/>
          </note>
        </measure>
      </part>
    </score-partwise>
    """
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".musicxml")
    with os.fdopen(temp_fd, 'w') as f:
        f.write(xml_content)
    
    try:
        # Import the score
        score = import_musicxml(temp_path)
        
        # Check that we got a chord
        assert len(score.parts) == 1
        assert len(score.parts[0].measures) == 1
        assert len(score.parts[0].measures[0].contents) == 1
        
        chord = score.parts[0].measures[0].contents[0]
        assert isinstance(chord, Chord)
        assert len(chord.notes) == 3
        
        # Check the pitches
        assert chord.notes[0].pitch.step == "C"
        assert chord.notes[0].pitch.octave == 4
        assert chord.notes[1].pitch.step == "E" 
        assert chord.notes[1].pitch.octave == 4
        assert chord.notes[2].pitch.step == "G"
        assert chord.notes[2].pitch.octave == 4
        
        # Check that chord members are correctly marked
        assert not chord.notes[0].is_chord_member
        assert chord.notes[1].is_chord_member
        assert chord.notes[2].is_chord_member
        
    finally:
        os.unlink(temp_path)


def test_import_grace_chord():
    """Test importing a grace chord element."""
    # Create a simple MusicXML file with a grace chord
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise version="3.1">
      <part-list>
        <score-part id="P1">
          <part-name>Music</part-name>
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
            <grace slash="yes"/>
            <pitch>
              <step>D</step>
              <octave>4</octave>
            </pitch>
            <type>eighth</type>
            <voice>1</voice>
          </note>
          <note>
            <grace slash="yes"/>
            <pitch>
              <step>F</step>
              <octave>4</octave>
            </pitch>
            <type>eighth</type>
            <voice>1</voice>
            <chord/>
          </note>
          <note>
            <pitch>
              <step>E</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>quarter</type>
            <voice>1</voice>
          </note>
        </measure>
      </part>
    </score-partwise>
    """
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".musicxml")
    with os.fdopen(temp_fd, 'w') as f:
        f.write(xml_content)
    
    try:
        # Import the score
        score = import_musicxml(temp_path)
        
        # Check that we got a grace chord followed by a normal note
        assert len(score.parts) == 1
        assert len(score.parts[0].measures) == 1
        assert len(score.parts[0].measures[0].contents) == 2
        
        grace_chord = score.parts[0].measures[0].contents[0]
        assert isinstance(grace_chord, GraceChord)
        assert len(grace_chord.notes) == 2
        
        # Check the pitches
        assert grace_chord.notes[0].pitch.step == "D"
        assert grace_chord.notes[0].pitch.octave == 4
        assert grace_chord.notes[1].pitch.step == "F"
        assert grace_chord.notes[1].pitch.octave == 4
        
        # Check that it's a slashed grace chord
        assert grace_chord.notes[0].slashed
        assert grace_chord.notes[1].slashed
        
        # Check that the next note is a regular note
        note = score.parts[0].measures[0].contents[1]
        assert isinstance(note, Note)
        assert note.pitch.step == "E"
        assert note.pitch.octave == 4
        
    finally:
        os.unlink(temp_path)


def test_import_beamed_group():
    """Test importing a beamed group."""
    # Create a simple MusicXML file with a beamed group
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise version="3.1">
      <part-list>
        <score-part id="P1">
          <part-name>Music</part-name>
        </score-part>
      </part-list>
      <part id="P1">
        <measure number="1">
          <attributes>
            <divisions>2</divisions>
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
            <pitch>
              <step>C</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>eighth</type>
            <beam number="1">begin</beam>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>D</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>eighth</type>
            <beam number="1">continue</beam>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>E</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>eighth</type>
            <beam number="1">continue</beam>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>F</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>eighth</type>
            <beam number="1">end</beam>
            <voice>1</voice>
          </note>
        </measure>
      </part>
    </score-partwise>
    """
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".musicxml")
    with os.fdopen(temp_fd, 'w') as f:
        f.write(xml_content)
    
    try:
        # Import the score
        score = import_musicxml(temp_path)
        
        # Check that we got a beamed group
        assert len(score.parts) == 1
        assert len(score.parts[0].measures) == 1
        assert len(score.parts[0].measures[0].contents) == 1
        
        beamed_group = score.parts[0].measures[0].contents[0]
        assert isinstance(beamed_group, BeamedGroup)
        assert len(beamed_group.contents) == 4
        
        # Check the pitches in the group
        assert beamed_group.contents[0].pitch.step == "C"
        assert beamed_group.contents[1].pitch.step == "D"
        assert beamed_group.contents[2].pitch.step == "E"
        assert beamed_group.contents[3].pitch.step == "F"
        
    finally:
        os.unlink(temp_path)


def test_import_tuplet():
    """Test importing a tuplet."""
    # Create a simple MusicXML file with a tuplet
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise version="3.1">
      <part-list>
        <score-part id="P1">
          <part-name>Music</part-name>
        </score-part>
      </part-list>
      <part id="P1">
        <measure number="1">
          <attributes>
            <divisions>3</divisions>
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
            <pitch>
              <step>C</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <time-modification>
              <actual-notes>3</actual-notes>
              <normal-notes>2</normal-notes>
            </time-modification>
            <type>eighth</type>
            <notations>
              <tuplet type="start" number="1" bracket="yes"/>
            </notations>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>D</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <time-modification>
              <actual-notes>3</actual-notes>
              <normal-notes>2</normal-notes>
            </time-modification>
            <type>eighth</type>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>E</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <time-modification>
              <actual-notes>3</actual-notes>
              <normal-notes>2</normal-notes>
            </time-modification>
            <type>eighth</type>
            <notations>
              <tuplet type="stop" number="1"/>
            </notations>
            <voice>1</voice>
          </note>
        </measure>
      </part>
    </score-partwise>
    """
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".musicxml")
    with os.fdopen(temp_fd, 'w') as f:
        f.write(xml_content)
    
    try:
        # Import the score
        score = import_musicxml(temp_path)
        
        # Check that we got a tuplet
        assert len(score.parts) == 1
        assert len(score.parts[0].measures) == 1
        assert len(score.parts[0].measures[0].contents) == 1
        
        tuplet = score.parts[0].measures[0].contents[0]
        assert isinstance(tuplet, Tuplet)
        assert len(tuplet.contents) == 3
        
        # Check the pitches in the tuplet
        assert tuplet.contents[0].pitch.step == "C"
        assert tuplet.contents[1].pitch.step == "D"
        assert tuplet.contents[2].pitch.step == "E"
        
        # Check the tuplet ratio
        assert tuplet.ratio == (3, 2)
        
        # Check that all notes have the correct tuplet ratio
        for note in tuplet.contents:
            assert note.duration.tuplet_ratio == (3, 2)
        
    finally:
        os.unlink(temp_path)


def test_complex_measure_with_tuplet_and_chord():
    """Test importing a complex measure with tuplet and chord."""
    # Create a MusicXML file with a measure containing a tuplet with a chord
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise version="3.1">
      <part-list>
        <score-part id="P1">
          <part-name>Music</part-name>
        </score-part>
      </part-list>
      <part id="P1">
        <measure number="1">
          <attributes>
            <divisions>6</divisions>
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
            <pitch>
              <step>C</step>
              <octave>4</octave>
            </pitch>
            <duration>2</duration>
            <time-modification>
              <actual-notes>3</actual-notes>
              <normal-notes>2</normal-notes>
            </time-modification>
            <type>eighth</type>
            <notations>
              <tuplet type="start" number="1"/>
            </notations>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>E</step>
              <octave>4</octave>
            </pitch>
            <duration>2</duration>
            <time-modification>
              <actual-notes>3</actual-notes>
              <normal-notes>2</normal-notes>
            </time-modification>
            <type>eighth</type>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>G</step>
              <octave>4</octave>
            </pitch>
            <duration>2</duration>
            <time-modification>
              <actual-notes>3</actual-notes>
              <normal-notes>2</normal-notes>
            </time-modification>
            <type>eighth</type>
            <voice>1</voice>
            <chord/>
          </note>
          <note>
            <pitch>
              <step>F</step>
              <octave>4</octave>
            </pitch>
            <duration>2</duration>
            <time-modification>
              <actual-notes>3</actual-notes>
              <normal-notes>2</normal-notes>
            </time-modification>
            <type>eighth</type>
            <notations>
              <tuplet type="stop" number="1"/>
            </notations>
            <voice>1</voice>
          </note>
        </measure>
      </part>
    </score-partwise>
    """
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".musicxml")
    with os.fdopen(temp_fd, 'w') as f:
        f.write(xml_content)
    
    try:
        # Import the score
        score = import_musicxml(temp_path)
        
        # Check that we got a tuplet
        assert len(score.parts) == 1
        assert len(score.parts[0].measures) == 1
        assert len(score.parts[0].measures[0].contents) == 1
        
        tuplet = score.parts[0].measures[0].contents[0]
        assert isinstance(tuplet, Tuplet)
        
        # A tuplet with 3 contents: two notes and a chord
        assert len(tuplet.contents) == 3
        
        # Check the first note
        assert isinstance(tuplet.contents[0], Note)
        assert tuplet.contents[0].pitch.step == "C"
        
        # Check the second element is a chord
        assert isinstance(tuplet.contents[1], Chord)
        assert len(tuplet.contents[1].notes) == 2
        assert tuplet.contents[1].notes[0].pitch.step == "E"
        assert tuplet.contents[1].notes[1].pitch.step == "G"
        
        # Check the third note
        assert isinstance(tuplet.contents[2], Note)
        assert tuplet.contents[2].pitch.step == "F"
        
        # Check the tuplet ratio
        assert tuplet.ratio == (3, 2)
        
    finally:
        os.unlink(temp_path)


def test_element_order_preservation():
    """Test that elements are preserved in the correct order when imported."""
    # Create a MusicXML file with specific ordering of elements
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
    <score-partwise version="3.1">
      <part-list>
        <score-part id="P1">
          <part-name>Music</part-name>
        </score-part>
      </part-list>
      <part id="P1">
        <measure number="1">
          <attributes>
            <divisions>4</divisions>
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
          <!-- First element: a quarter note -->
          <note>
            <pitch>
              <step>D</step>
              <octave>4</octave>
            </pitch>
            <duration>4</duration>
            <type>quarter</type>
            <voice>1</voice>
          </note>
          
          <!-- Second element: a beamed group of sixteenth notes -->
          <note>
            <pitch>
              <step>F</step>
              <alter>1</alter>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>16th</type>
            <beam number="1">begin</beam>
            <beam number="2">begin</beam>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>A</step>
              <alter>1</alter>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>16th</type>
            <beam number="1">continue</beam>
            <beam number="2">continue</beam>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>G</step>
              <alter>1</alter>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>16th</type>
            <beam number="1">continue</beam>
            <beam number="2">continue</beam>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>B</step>
              <octave>4</octave>
            </pitch>
            <duration>1</duration>
            <type>16th</type>
            <beam number="1">end</beam>
            <beam number="2">end</beam>
            <voice>1</voice>
          </note>
          
          <!-- Third element: a chord -->
          <note>
            <pitch>
              <step>C</step>
              <octave>5</octave>
            </pitch>
            <duration>4</duration>
            <type>quarter</type>
            <voice>1</voice>
          </note>
          <note>
            <pitch>
              <step>E</step>
              <alter>-1</alter>
              <octave>5</octave>
            </pitch>
            <duration>4</duration>
            <type>quarter</type>
            <voice>1</voice>
            <chord/>
          </note>
          <note>
            <pitch>
              <step>G</step>
              <octave>5</octave>
            </pitch>
            <duration>4</duration>
            <type>quarter</type>
            <voice>1</voice>
            <chord/>
          </note>
        </measure>
      </part>
    </score-partwise>
    """
    
    # Create temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=".musicxml")
    with os.fdopen(temp_fd, 'w') as f:
        f.write(xml_content)
    
    try:
        # Import the score
        score = import_musicxml(temp_path)
        
        # Check measure structure
        assert len(score.parts) == 1
        assert len(score.parts[0].measures) == 1
        
        # There should be 3 elements in the order specified:
        # 1. A quarter note
        # 2. A beamed group of 4 sixteenth notes
        # 3. A chord with 3 notes
        measure_contents = score.parts[0].measures[0].contents
        assert len(measure_contents) == 3
        
        # Check first element is a D quarter note
        assert isinstance(measure_contents[0], Note)
        assert measure_contents[0].pitch.step == "D"
        assert measure_contents[0].duration.note_type == "quarter"
        
        # Check second element is a beamed group
        assert isinstance(measure_contents[1], BeamedGroup)
        assert len(measure_contents[1].contents) == 4
        
        # Check the beamed group notes
        assert measure_contents[1].contents[0].pitch.step == "F"
        assert measure_contents[1].contents[0].pitch.alteration == 1  # F#
        assert measure_contents[1].contents[1].pitch.step == "A"
        assert measure_contents[1].contents[1].pitch.alteration == 1  # A#
        assert measure_contents[1].contents[2].pitch.step == "G"
        assert measure_contents[1].contents[2].pitch.alteration == 1  # G#
        assert measure_contents[1].contents[3].pitch.step == "B"
        
        # Check third element is a C-Eb-G chord
        assert isinstance(measure_contents[2], Chord)
        assert len(measure_contents[2].notes) == 3
        assert measure_contents[2].notes[0].pitch.step == "C"
        assert measure_contents[2].notes[1].pitch.step == "E"
        assert measure_contents[2].notes[1].pitch.alteration == -1  # Eb
        assert measure_contents[2].notes[2].pitch.step == "G"
        
    finally:
        os.unlink(temp_path) 