"""
Score importer module for importing score-level MusicXML elements.

This module provides functionality for importing score, part, and measure elements
from MusicXML files.
"""

#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  #
#  Copyright © 2025 Florian GARDIN <fgardin.pro@gmail.com>.                                      #
#                                                                                                #
#  This program is free software: you can redistribute it and/or modify it under the terms of    #
#  the GNU General Public License as published by the Free Software Foundation, either version   #
#  3 of the License, or (at your option) any later version.                                      #
#                                                                                                #
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;     #
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.     #
#  See the GNU General Public License for more details.                                          #
#                                                                                                #
#  You should have received a copy of the GNU General Public License along with this program.    #
#  If not, see <http://www.gnu.org/licenses/>.                                                   #
#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  #

import logging
from typing import Dict, Optional, Sequence, Union
from pathlib import Path
import xml.etree.ElementTree as ET

from pymusicxml.importers.base_importer import MusicXMLImporter
from pymusicxml.importers.musical_elements import MusicalElementsImporter
from pymusicxml.score_components import (
    Score, Part, PartGroup, Measure, Clef, KeySignature,
    TraditionalKeySignature, NonTraditionalKeySignature, Transpose,
    Note, Rest, BarRest, Chord, BeamedGroup
)
from pymusicxml.importers.directions_notations import DirectionsImporter

# Set up logging
logger = logging.getLogger(__name__)


class ScoreImporter(MusicXMLImporter):
    """
    Class for importing score-level elements from MusicXML files.
    
    This class extends the base importer to provide functionality specific to
    importing scores, parts, and measures.
    """
    
    def import_score(self) -> Score:
        """
        Import the MusicXML file as a Score object.
        
        :returns: A Score object representing the imported MusicXML file
        """
        if self.root.tag.endswith('score-partwise'):
            return self._import_partwise_score()
        elif self.root.tag.endswith('score-timewise'):
            logger.error("Timewise scores are not supported yet")
            raise NotImplementedError("Timewise scores are not supported yet")
        else:
            logger.error(f"Unknown score type: {self.root.tag}")
            raise ValueError(f"Unknown score type: {self.root.tag}")
    
    def _import_partwise_score(self) -> Score:
        """
        Import a partwise MusicXML score.
        
        :returns: A Score object representing the imported MusicXML file
        """
        # Extract metadata
        work = self._find_element(self.root, "work")
        title = self._get_text(work, "work-title") if work is not None else None
        
        # Check for movement-title if work-title is not found
        if title is None:
            movement_title = self._find_element(self.root, "movement-title")
            if movement_title is not None and movement_title.text:
                title = movement_title.text
        
        identification = self._find_element(self.root, "identification")
        composer = None
        copyright = None
        if identification is not None:
            creator_elements = self._find_elements(identification, "creator")
            for creator in creator_elements:
                if creator.get("type") == "composer":
                    composer = creator.text
                    break
            
            # Get copyright information from identification/rights
            rights_element = self._find_element(identification, "rights")
            if rights_element is not None and rights_element.text:
                copyright = rights_element.text
        
        # Look for credit elements that might contain title, composer or copyright info
        credit_elements = self._find_elements(self.root, "credit")
        for credit in credit_elements:
            credit_type_elem = self._find_element(credit, "credit-type")
            credit_words_elem = self._find_element(credit, "credit-words")
            
            if credit_type_elem is not None and credit_words_elem is not None and credit_words_elem.text:
                # If we find a rights credit, use it for copyright info
                if credit_type_elem.text == "rights" and copyright is None:
                    copyright = credit_words_elem.text
                # If we find a title credit and title is still not set, use it
                elif credit_type_elem.text == "title" and title is None:
                    title = credit_words_elem.text
                # If we find a composer credit and composer is still not set, use it
                elif credit_type_elem.text == "composer" and composer is None:
                    composer = credit_words_elem.text
        
        # Import parts and part groups
        part_list_elem = self._find_element(self.root, "part-list", required=True)
        parts_and_groups = self._import_part_list(part_list_elem)
        
        # Create score
        score = Score(contents=parts_and_groups, title=title, composer=composer, copyright=copyright)
        logger.info(f"Successfully imported score: {title}")
        return score
    
    def _import_part_list(self, part_list_elem) -> Sequence[Union[Part, PartGroup]]:
        """
        Import the part-list element.
        
        :param part_list_elem: The part-list element
        :returns: A list of Part and PartGroup objects
        """
        parts_and_groups = []
        part_elems = {}  # Map part IDs to their elements
        
        # Get all part elements in the score
        for part_elem in self._find_elements(self.root, "part"):
            part_id = part_elem.get("id")
            if part_id:
                part_elems[part_id] = part_elem
                
        # Process the part-list to create parts and groups
        current_group = None
        group_parts = []
        
        for child in part_list_elem:
            if child.tag.endswith("part-group"):
                group_type = child.get("type")
                if group_type == "start":
                    # Start a new part group
                    has_bracket = True
                    has_group_bar_line = True
                    
                    group_symbol_elem = self._find_element(child, "group-symbol")
                    if group_symbol_elem is not None and group_symbol_elem.text == "none":
                        has_bracket = False
                        
                    group_barline_elem = self._find_element(child, "group-barline")
                    if group_barline_elem is not None and group_barline_elem.text == "no":
                        has_group_bar_line = False
                        
                    current_group = {
                        "has_bracket": has_bracket,
                        "has_group_bar_line": has_group_bar_line
                    }
                    group_parts = []
                elif group_type == "stop" and current_group:
                    # End the current part group
                    if group_parts:
                        parts_and_groups.append(
                            PartGroup(
                                parts=group_parts,
                                has_bracket=current_group["has_bracket"],
                                has_group_bar_line=current_group["has_group_bar_line"]
                            )
                        )
                    current_group = None
                    group_parts = []
            
            elif child.tag.endswith("score-part"):
                part_id = child.get("id")
                if part_id in part_elems:
                    part_name = self._get_text(child, "part-name")
                    part = self._import_part(part_elems[part_id], part_name, part_id)
                    
                    if current_group:
                        group_parts.append(part)
                    else:
                        parts_and_groups.append(part)
        
        # Handle any unclosed groups
        if current_group and group_parts:
            parts_and_groups.append(
                PartGroup(
                    parts=group_parts,
                    has_bracket=current_group["has_bracket"],
                    has_group_bar_line=current_group["has_group_bar_line"]
                )
            )
            
        return parts_and_groups
    
    def _import_part(self, part_elem, part_name, part_id) -> Part:
        """
        Import a part element.
        
        :param part_elem: The part element
        :param part_name: The name of the part
        :param part_id: The ID of the part
        :returns: A Part object
        """
        measures = []
        current_divisions = None
        
        # Extract measures
        for measure_elem in self._find_elements(part_elem, "measure"):
            # Check if this measure has its own divisions setting
            attributes_elem = self._find_element(measure_elem, "attributes")
            if attributes_elem is not None:
                divisions_text = self._get_text(attributes_elem, "divisions")
                if divisions_text:
                    try:
                        current_divisions = float(divisions_text)
                    except ValueError:
                        logger.warning(f"Invalid divisions value: {divisions_text}")
            
            # Import the measure
            measure = self._import_measure(measure_elem, current_divisions)
            measures.append(measure)
            
        # Create part
        part = Part(part_name=part_name, measures=measures, part_id=int(part_id[1:]) if part_id[0] == 'P' else part_id)
        logger.info(f"Imported part: {part_name}")
        return part
    
    def _import_measure(self, measure_elem, inherited_divisions=None) -> Measure:
        """
        Import a measure element.
        
        :param measure_elem: The measure element
        :param inherited_divisions: The divisions value inherited from previous measures
        :returns: A Measure object
        """
        
        # Default values
        time_signature = None
        key = None
        clef = None
        transpose = None
        barline = None
        divisions = inherited_divisions or 1  # Use inherited value or default to 1
        
        # Get measure number
        measure_number = measure_elem.get("number")
        is_pickup = measure_number == "0" and measure_elem.get("implicit") == "yes"
        
        # Extract attributes
        attributes_elem = self._find_element(measure_elem, "attributes")
        if attributes_elem is not None:
            # Get divisions value for timing calculations
            divisions_text = self._get_text(attributes_elem, "divisions")
            if divisions_text:
                try:
                    divisions = float(divisions_text)
                except ValueError:
                    logger.warning(f"Invalid divisions value: {divisions_text}")
            
            # Import time signature
            time_elem = self._find_element(attributes_elem, "time")
            if time_elem is not None:
                beats = self._get_text(time_elem, "beats")
                beat_type = self._get_text(time_elem, "beat-type")
                if beats and beat_type:
                    time_signature = (int(beats), int(beat_type))
            
            # Import key signature
            key_elem = self._find_element(attributes_elem, "key")
            if key_elem is not None:
                fifths = self._get_text(key_elem, "fifths")
                mode = self._get_text(key_elem, "mode", "major")
                
                # Check for non-traditional key
                key_steps = self._find_elements(key_elem, "key-step")
                
                if key_steps:
                    # Non-traditional key signature with multiple alterations
                    key = NonTraditionalKeySignature()
                    step_elements = [(
                        self._get_text(key_elem, f"key-step", None, i),
                        self._get_text(key_elem, f"key-alter", "0", i),
                        self._get_text(key_elem, f"key-accidental", None, i)
                    ) for i in range(len(key_steps))]
                    
                    for step, alter, accidental in step_elements:
                        if step:
                            try:
                                alter_value = float(alter) if alter else 0
                                key.add_alteration(step, alter_value, accidental)
                            except ValueError:
                                logger.warning(f"Invalid key alteration value: {alter}")
                elif fifths:
                    # Traditional key signature
                    key = TraditionalKeySignature(fifths=int(fifths), mode=mode)
                
            # Import clef
            clef_elem = self._find_element(attributes_elem, "clef")
            if clef_elem is not None:
                sign = self._get_text(clef_elem, "sign", "G")
                line = self._get_text(clef_elem, "line", "2")
                octave_change = self._get_text(clef_elem, "clef-octave-change")
                octaves_transposition = int(octave_change) if octave_change else 0
                
                clef = Clef(sign=sign, line=line, octaves_transposition=octaves_transposition)
                
            # Import transpose
            transpose_elem = self._find_element(attributes_elem, "transpose")
            if transpose_elem is not None:
                chromatic = int(self._get_text(transpose_elem, "chromatic", "0"))
                diatonic = self._get_text(transpose_elem, "diatonic")
                diatonic = int(diatonic) if diatonic else None
                octave_change = self._get_text(transpose_elem, "octave-change")
                octave_change = int(octave_change) if octave_change else None
                
                transpose = Transpose(
                    chromatic=chromatic,
                    diatonic=diatonic,
                    octave=octave_change
                )
        
        # Import notes, rests, and other musical elements
        contents = self._import_measure_contents(measure_elem)
        
        # Process all elements chronologically to build a position map
        element_positions = {}  # Maps elements to their positions in the measure
        current_position = 0.0  # Position in quarter notes
        
        # First pass: Process all child elements in order and track positions
        for child in measure_elem:
            if child.tag.endswith("note"):
                is_grace = self._find_element(child, "grace") is not None
                is_chord = self._find_element(child, "chord") is not None
                
                # Skip chord members (handled with main chord note)
                if is_chord:
                    continue
                    
                # Grace notes don't advance position
                if is_grace:
                    element_positions[child] = current_position
                    continue
                
                # Regular notes/rests advance position based on duration
                duration_text = self._get_text(child, "duration")
                if duration_text:
                    try:
                        duration_divisions = float(duration_text)
                        duration_quarters = duration_divisions / divisions
                        
                        # Store position and advance
                        element_positions[child] = current_position
                        current_position += duration_quarters
                    except ValueError:
                        logger.warning(f"Invalid duration value: {duration_text}")
            
            # Handle forward elements (advance position without creating an element)
            elif child.tag.endswith("forward"):
                duration_text = self._get_text(child, "duration")
                if duration_text:
                    try:
                        duration_divisions = float(duration_text)
                        duration_quarters = duration_divisions / divisions
                        
                        # Advance position
                        current_position += duration_quarters
                    except ValueError:
                        logger.warning(f"Invalid duration value in forward: {duration_text}")
            
            # Handle backup elements (move position backwards)
            elif child.tag.endswith("backup"):
                duration_text = self._get_text(child, "duration")
                if duration_text:
                    try:
                        duration_divisions = float(duration_text)
                        duration_quarters = duration_divisions / divisions
                        
                        # Move position backwards
                        current_position -= duration_quarters
                        # Prevent negative position
                        current_position = max(0.0, current_position)
                    except ValueError:
                        logger.warning(f"Invalid duration value in backup: {duration_text}")
            
            # Store position for non-note elements (e.g., directions, harmonies)
            elif child.tag.endswith("direction") or child.tag.endswith("harmony"):
                element_positions[child] = current_position
                
                # Check for offset
                offset_elem = self._find_element(child, "offset")
                if offset_elem is not None and offset_elem.text:
                    try:
                        offset_divisions = float(offset_elem.text)
                        offset_quarters = offset_divisions / divisions
                        
                        # Update position with offset
                        element_positions[child] += offset_quarters
                    except ValueError:
                        logger.warning(f"Invalid offset value: {offset_elem.text}")
        
        # Process directions and harmonies with correct positions
        directions_with_displacements = []
        
        # Process direction elements
        for direction_elem in self._find_elements(measure_elem, "direction"):
            direction = DirectionsImporter.import_direction(
                direction_elem, self._find_element, self._get_text, self._find_elements
            )
            
            if direction:
                # Use position from the map
                position = element_positions.get(direction_elem, 0.0)
                directions_with_displacements.append((direction, position))
        
        # Process harmony elements
        for harmony_elem in self._find_elements(measure_elem, "harmony"):
            # Create a temporary direction element to wrap the harmony
            temp_direction = ET.Element("direction")
            temp_direction.append(harmony_elem)
            
            harmony = DirectionsImporter.import_direction(
                temp_direction, self._find_element, self._get_text, self._find_elements
            )
            
            if harmony:
                # Use position from the map
                position = element_positions.get(harmony_elem, 0.0)
                directions_with_displacements.append((harmony, position))
        
        # Create measure
        measure = Measure(
            contents=contents,
            time_signature=time_signature,
            key=key,
            clef=clef,
            transpose=transpose,
            barline=barline,
            directions_with_displacements=directions_with_displacements,
            number=int(measure_number) if measure_number.isdigit() else measure_number,
            original_divisions=int(divisions) if divisions == int(divisions) else divisions
        )
        
        return measure
    
    def _import_measure_contents(self, measure_elem) -> list:
        """
        Import the contents of a measure (notes, rests, chords, etc.).
        
        :param measure_elem: The measure element
        :returns: A list of musical elements organized by voice
        """
        # Use the new method to identify and process groups
        all_elements = MusicalElementsImporter.identify_groups_in_measure(
            measure_elem, self._find_element, self._find_elements, self._get_text
        )
        
        # Dictionary to organize elements by voice
        voice_elements = {}
        
        # Process all elements and organize by voice
        for element in all_elements:
            # Get the voice number (default to 1 if not specified)
            voice = getattr(element, 'voice', 1) or 1
            
            # Add to the corresponding voice
            if voice not in voice_elements:
                voice_elements[voice] = []
            voice_elements[voice].append(element)
        
        # Check if we have only one voice
        if len(voice_elements) == 1:
            # Return a flat list of elements
            return list(voice_elements.values())[0]
        else:
            # Return a list of voice lists
            # Sort by voice number and create a list of lists
            contents = []
            for voice_num in sorted(voice_elements.keys()):
                contents.append(voice_elements[voice_num])
            return contents


def import_musicxml(file_path: Union[str, Path]) -> Score:
    """
    Import a MusicXML file and return a Score object.
    
    :param file_path: Path to the MusicXML file to import
    :returns: A Score object representing the imported MusicXML file
    """
    importer = ScoreImporter(file_path)
    return importer.import_score() 