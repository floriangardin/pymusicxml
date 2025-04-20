"""
Directions and notations importer module.

This module provides functionality for importing directions and notations
from MusicXML files.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union

import xml.etree.ElementTree as ET

from pymusicxml.directions import Direction, Dynamic, MetronomeMark, TextAnnotation, Harmony, Degree
from pymusicxml.notations import Notation, Fermata, Arpeggiate, NonArpeggiate
from pymusicxml.enums import StaffPlacement, ArpeggiationDirection

# Set up logging
logger = logging.getLogger(__name__)


class DirectionsImporter:
    """
    Class for importing musical directions from MusicXML files.
    
    This class provides methods for importing dynamics, metronome marks,
    text annotations, harmonies, and other direction elements.
    """
    
    @staticmethod
    def import_direction(direction_elem, find_element, get_text, find_elements) -> Optional[Direction]:
        """
        Import a direction element.
        
        Args:
            direction_elem: The direction element
            find_element: Method to find child elements
            get_text: Method to get text content
            find_elements: Method to find multiple child elements
            
        Returns:
            A Direction object or None if not recognized
        """
        # Get placement
        placement_str = direction_elem.get("placement")
        placement = None
        if placement_str:
            try:
                placement = StaffPlacement(placement_str)
            except ValueError:
                logger.warning(f"Unknown placement value: {placement_str}")
        
        # Get staff and voice
        staff_text = get_text(direction_elem, "staff")
        staff = int(staff_text) if staff_text else None
        
        voice_text = get_text(direction_elem, "voice")
        voice = int(voice_text) if voice_text else None
        
        # Check for dynamics
        dynamics_elem = find_element(direction_elem, "dynamics")
        if dynamics_elem is not None:
            # Find the first dynamic mark (e.g., f, p, mf, etc.)
            for dynamic_type in ["p", "pp", "ppp", "pppp", "ppppp", "pppppp", 
                                "f", "ff", "fff", "ffff", "fffff", "ffffff",
                                "mp", "mf", "sf", "sfz", "sff", "sfp", "sfpp", "fp", "rf", "rfz"]:
                if find_element(dynamics_elem, dynamic_type) is not None:
                    return Dynamic(dynamic_text=dynamic_type, placement=placement, staff=staff, voice=voice)
            
            # If no recognized dynamic was found
            logger.warning("Unrecognized dynamic marking")
            return None
            
        # Check for metronome marks
        metronome_elem = find_element(direction_elem, "metronome")
        if metronome_elem is not None:
            beat_unit = get_text(metronome_elem, "beat-unit", "quarter")
            per_minute = get_text(metronome_elem, "per-minute")
            
            if per_minute:
                try:
                    bpm = float(per_minute)
                    return MetronomeMark(
                        beat_length=beat_unit,
                        bpm=bpm,
                        placement=placement,
                        staff=staff,
                        voice=voice
                    )
                except ValueError:
                    logger.warning(f"Invalid BPM value: {per_minute}")
            
            return None
            
        # Check for text annotations
        words_elem = find_element(direction_elem, "words")
        if words_elem is not None:
            text = words_elem.text or ""
            
            # Get text formatting attributes
            font_size = None
            font_size_str = words_elem.get("font-size")
            if font_size_str:
                try:
                    font_size = float(font_size_str)
                except ValueError:
                    pass
                    
            italic = words_elem.get("font-style") == "italic"
            bold = words_elem.get("font-weight") == "bold"
            
            return TextAnnotation(
                text=text,
                font_size=font_size,
                italic=italic,
                bold=bold,
                placement=placement,
                staff=staff,
                voice=voice
            )
            
        # Handle other direction types as needed
        return None


class NotationsImporter:
    """
    Class for importing musical notations from MusicXML files.
    
    This class provides methods for importing articulations, ornaments,
    technical notations, and other notation elements.
    """
    
    @staticmethod
    def import_notation(notation_elem, find_element, get_text, find_elements) -> Optional[Notation]:
        """
        Import a notation element.
        
        Args:
            notation_elem: The notation element
            find_element: Method to find child elements
            get_text: Method to get text content
            find_elements: Method to find multiple child elements
            
        Returns:
            A Notation object or None if not recognized
        """
        # Check for fermata
        fermata_elem = find_element(notation_elem, "fermata")
        if fermata_elem is not None:
            inverted = fermata_elem.get("type") == "inverted"
            return Fermata(inverted=inverted)
            
        # Check for arpeggiate
        arpeggiate_elem = find_element(notation_elem, "arpeggiate")
        if arpeggiate_elem is not None:
            direction_text = arpeggiate_elem.get("direction")
            direction = None
            
            if direction_text == "up":
                direction = ArpeggiationDirection.UP
            elif direction_text == "down":
                direction = ArpeggiationDirection.DOWN
                
            return Arpeggiate(direction=direction)
            
        # Check for non-arpeggiate
        non_arpeggiate_elem = find_element(notation_elem, "non-arpeggiate")
        if non_arpeggiate_elem is not None:
            return NonArpeggiate()
            
        # Handle other notation types as needed
        
        return None 