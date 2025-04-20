"""
Module for importing MusicXML files into pymusicxml object hierarchy.

This module provides functions and classes for parsing MusicXML files and
creating the corresponding pymusicxml objects.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Sequence, Tuple, Union, Any
from pathlib import Path
import re

from pymusicxml.score_components import (
    Score, Part, PartGroup, Measure, Clef, KeySignature,
    TraditionalKeySignature, NonTraditionalKeySignature,
    Note, Rest, BarRest, Chord, Pitch, Duration, Transpose
)
from pymusicxml.directions import Direction
from pymusicxml.notations import Notation
from pymusicxml.enums import StaffPlacement

# Set up logging
logger = logging.getLogger(__name__)


class MusicXMLImporter:
    """
    Class for importing MusicXML files and converting them to pymusicxml objects.
    
    This class handles the parsing of MusicXML files and the creation of the
    corresponding pymusicxml objects.
    """
    
    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize the importer with a file path.
        
        Args:
            file_path: Path to the MusicXML file to import
        """
        self.file_path = Path(file_path)
        self.root = None
        self.ns = {}  # Namespace dictionary
        self._parse_file()
        
    def _parse_file(self):
        """Parse the MusicXML file and extract the root element."""
        try:
            tree = ET.parse(self.file_path)
            self.root = tree.getroot()
            # Extract namespaces if present
            self._extract_namespaces()
            logger.info(f"Successfully parsed MusicXML file: {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to parse MusicXML file: {self.file_path}")
            logger.error(f"Error: {str(e)}")
            raise
            
    def _extract_namespaces(self):
        """Extract any namespaces from the MusicXML file."""
        # Extract namespaces from the root tag
        match = re.match(r'{(.*)}.*', self.root.tag)
        if match:
            namespace = match.group(1)
            self.ns = {'ns': namespace}
            logger.debug(f"Found namespace: {namespace}")
            
    def _find_element(self, parent, tag, required=False) -> Optional[ET.Element]:
        """
        Find an element within the parent, handling namespaces.
        
        Args:
            parent: Parent element to search in
            tag: Tag name to search for
            required: Whether the element is required (raises error if not found)
            
        Returns:
            The found element or None if not found and not required
        """
        if self.ns:
            element = parent.find(f"./ns:{tag}", self.ns)
        else:
            element = parent.find(f".//{tag}")
            
        if required and element is None:
            logger.error(f"Required element {tag} not found in {parent.tag}")
            raise ValueError(f"Required element {tag} not found")
            
        return element
        
    def _find_elements(self, parent, tag) -> Sequence[ET.Element]:
        """
        Find all elements matching the tag within the parent, handling namespaces.
        
        Args:
            parent: Parent element to search in
            tag: Tag name to search for
            
        Returns:
            List of found elements
        """
        if self.ns:
            elements = parent.findall(f".//ns:{tag}", self.ns)
        else:
            elements = parent.findall(f".//{tag}")
            
        return elements
    
    def _get_text(self, parent, tag, default=None) -> str:
        """
        Get the text content of an element within the parent.
        
        Args:
            parent: Parent element to search in
            tag: Tag name to search for
            default: Default value to return if element not found
            
        Returns:
            Text content of the element or default if not found
        """
        element = self._find_element(parent, tag)
        return element.text if element is not None else default
    
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
            # Time signature
            time_elem = self._find_element(attributes_elem, "time")
            if time_elem is not None:
                beats = int(self._get_text(time_elem, "beats", "4"))
                beat_type = int(self._get_text(time_elem, "beat-type", "4"))
                time_signature = (beats, beat_type)
                
            # Key signature
            key_elem = self._find_element(attributes_elem, "key")
            if key_elem is not None:
                fifths = int(self._get_text(key_elem, "fifths", "0"))
                mode = self._get_text(key_elem, "mode", "major")
                key = TraditionalKeySignature(fifths=fifths, mode=mode)
                
            # Clef
            clef_elem = self._find_element(attributes_elem, "clef")
            if clef_elem is not None:
                sign = self._get_text(clef_elem, "sign", "G")
                line_str = self._get_text(clef_elem, "line", "2")
                line = int(line_str)  # Convert to integer
                clef = Clef(sign=sign, line=line)
                
            # Transpose
            transpose_elem = self._find_element(attributes_elem, "transpose")
            if transpose_elem is not None:
                chromatic = int(self._get_text(transpose_elem, "chromatic", "0"))
                diatonic_text = self._get_text(transpose_elem, "diatonic")
                diatonic = int(diatonic_text) if diatonic_text else None
                octave_text = self._get_text(transpose_elem, "octave-change")
                octave = int(octave_text) if octave_text else None
                transpose = Transpose(chromatic=chromatic, diatonic=diatonic, octave=octave)
        
        # Check for barline
        barline_elem = self._find_element(measure_elem, "barline")
        if barline_elem is not None:
            barline_style = self._get_text(barline_elem, "bar-style")
            if barline_style:
                barline = barline_style
        
        # TODO: Implement parsing of the measure contents
        # This will be more complex and will be implemented in subsequent phases
                
        # Create measure - Empty list for contents to avoid the IndexError
        measure = Measure(
            contents=[], 
            time_signature=time_signature,
            key=key,
            clef=clef,
            barline=barline,
            number=measure_number,
            transpose=transpose
        )
        
        logger.debug(f"Imported measure: {measure_number}")
        return measure
        

def import_musicxml(file_path: Union[str, Path]) -> Score:
    """
    Import a MusicXML file and return a Score object.
    
    Args:
        file_path: Path to the MusicXML file to import
        
    Returns:
        A Score object representing the imported MusicXML file
    """
    importer = MusicXMLImporter(file_path)
    return importer.import_score() 