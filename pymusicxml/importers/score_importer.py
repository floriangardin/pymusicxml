"""
Score importer module for importing score-level MusicXML elements.

This module provides functionality for importing score, part, and measure elements
from MusicXML files.
"""

import logging
from typing import Dict, Optional, Sequence, Union
from pathlib import Path

from pymusicxml.importers.base_importer import MusicXMLImporter
from pymusicxml.importers.musical_elements import MusicalElementsImporter
from pymusicxml.score_components import (
    Score, Part, PartGroup, Measure, Clef, KeySignature,
    TraditionalKeySignature, NonTraditionalKeySignature, Transpose,
    Note, Rest, BarRest, Chord, BeamedGroup
)

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
        
        Returns:
            A Score object representing the imported MusicXML file
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
        
        Returns:
            A Score object representing the imported MusicXML file
        """
        # Extract metadata
        work = self._find_element(self.root, "work")
        title = self._get_text(work, "work-title") if work is not None else None
        
        identification = self._find_element(self.root, "identification")
        composer = None
        if identification is not None:
            creator_elements = self._find_elements(identification, "creator")
            for creator in creator_elements:
                if creator.get("type") == "composer":
                    composer = creator.text
                    break
        
        # Import parts and part groups
        part_list_elem = self._find_element(self.root, "part-list", required=True)
        parts_and_groups = self._import_part_list(part_list_elem)
        
        # Create score
        score = Score(contents=parts_and_groups, title=title, composer=composer)
        logger.info(f"Successfully imported score: {title}")
        return score
    
    def _import_part_list(self, part_list_elem) -> Sequence[Union[Part, PartGroup]]:
        """
        Import the part-list element.
        
        Args:
            part_list_elem: The part-list element
            
        Returns:
            A list of Part and PartGroup objects
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
        
        Args:
            part_elem: The part element
            part_name: The name of the part
            part_id: The ID of the part
            
        Returns:
            A Part object
        """
        measures = []
        
        # Extract measures
        for measure_elem in self._find_elements(part_elem, "measure"):
            measure = self._import_measure(measure_elem)
            measures.append(measure)
            
        # Create part
        part = Part(part_name=part_name, measures=measures, part_id=int(part_id[1:]) if part_id[0] == 'P' else part_id)
        logger.info(f"Imported part: {part_name}")
        return part
    
    def _import_measure(self, measure_elem) -> Measure:
        """
        Import a measure element.
        
        Args:
            measure_elem: The measure element
            
        Returns:
            A Measure object
        """
        measure_number = int(measure_elem.get("number", "1"))
        
        # Default values
        time_signature = None
        key = None
        clef = None
        transpose = None
        barline = None
        
        # Extract attributes
        attributes_elem = self._find_element(measure_elem, "attributes")
        if attributes_elem is not None:
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
                key_step = self._get_text(key_elem, "key-step")
                key_alter = self._get_text(key_elem, "key-alter")
                key_octave = self._get_text(key_elem, "key-octave")
                
                if key_step and key_octave:
                    # Non-traditional key signature
                    key_alter_value = float(key_alter) if key_alter else 0
                    key = NonTraditionalKeySignature(
                        tonic_step=key_step,
                        tonic_alter=key_alter_value,
                        tonic_octave=int(key_octave),
                        mode=mode
                    )
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
        
        # Create measure
        measure = Measure(
            contents=contents,
            time_signature=time_signature,
            key=key,
            clef=clef,
            transpose=transpose,
            barline=barline
        )
        
        return measure
    
    def _import_measure_contents(self, measure_elem) -> list:
        """
        Import the contents of a measure (notes, rests, chords, etc.).
        
        Args:
            measure_elem: The measure element
            
        Returns:
            A list of musical elements organized by voice
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
    
    Args:
        file_path: Path to the MusicXML file to import
        
    Returns:
        A Score object representing the imported MusicXML file
    """
    importer = ScoreImporter(file_path)
    return importer.import_score() 