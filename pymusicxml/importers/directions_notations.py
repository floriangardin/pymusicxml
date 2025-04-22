"""
Directions and notations importer module.

This module provides functionality for importing directions and notations
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
from typing import Dict, List, Optional, Tuple, Union

import xml.etree.ElementTree as ET

from pymusicxml.directions import Direction, Dynamic, MetronomeMark, TextAnnotation, Harmony, Degree
from pymusicxml.notations import Notation, Fermata, Arpeggiate, NonArpeggiate, Mordent, Turn, Schleifer, TrillMark, Tremolo, UpBow, DownBow, OpenString, Harmonic, Stopped, SnapPizzicato
from pymusicxml.enums import StaffPlacement, ArpeggiationDirection, HairpinType
from pymusicxml.spanners import (
    StartBracket, StopBracket, StartPedal, StopPedal, ChangePedal,
    StartHairpin, StopHairpin, StartDashes, StopDashes
)

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
        
        :param direction_elem: The direction element
        :param find_element: Method to find child elements
        :param get_text: Method to get text content
        :param find_elements: Method to find multiple child elements
        :returns: A Direction object or None if not recognized
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
        voice = int(voice_text) if voice_text else 1
        
        # Process the direction-type elements
        direction_type_elements = find_elements(direction_elem, "direction-type")
        
        # Save text annotation if found for potential bracket start with text
        text_annotation = None
        
        for direction_type_elem in direction_type_elements:
            # Check for dashes elements
            dashes_elem = find_element(direction_type_elem, "dashes")
            if dashes_elem is not None:
                dashes_type = dashes_elem.get("type")
                dashes_number = dashes_elem.get("number", "1")
                
                # Find previous words element for potential text annotation
                words_elems = find_elements(direction_type_elem, "words")
                if words_elems:
                    words_text = words_elems[0].text
                    if words_text:
                        text_annotation = TextAnnotation(
                            text=words_text,
                            placement=placement or "above",
                            staff=staff,
                            voice=voice
                        )
                
                if dashes_type == "start":
                    # Get dash-length and space-length
                    dash_length_str = dashes_elem.get("dash-length")
                    space_length_str = dashes_elem.get("space-length")
                    
                    dash_length = float(dash_length_str) if dash_length_str else None
                    space_length = float(space_length_str) if space_length_str else None
                    
                    return StartDashes(
                        label=dashes_number,
                        dash_length=dash_length,
                        space_length=space_length,
                        text=text_annotation,
                        placement=placement or "above",
                        voice=voice,
                        staff=staff
                    )
                elif dashes_type == "stop":
                    return StopDashes(
                        label=dashes_number,
                        text=text_annotation,
                        placement=placement or "above",
                        voice=voice,
                        staff=staff
                    )
            
            # Check for hairpin elements (wedge)
            wedge_elem = find_element(direction_type_elem, "wedge")
            if wedge_elem is not None:
                wedge_type = wedge_elem.get("type")
                wedge_number = wedge_elem.get("number", "1")
                
                # Get spread attribute
                spread_str = wedge_elem.get("spread")
                spread = float(spread_str) if spread_str else None
                
                # Get niente attribute
                niente = wedge_elem.get("niente") == "yes"
                
                if wedge_type == "crescendo":
                    return StartHairpin(
                        hairpin_type=HairpinType.crescendo,
                        label=wedge_number,
                        spread=spread,
                        placement=placement or "below",
                        niente=niente,
                        voice=voice,
                        staff=staff
                    )
                elif wedge_type == "diminuendo":
                    return StartHairpin(
                        hairpin_type=HairpinType.diminuendo,
                        label=wedge_number,
                        spread=spread,
                        placement=placement or "below",
                        niente=niente,
                        voice=voice,
                        staff=staff
                    )
                elif wedge_type == "stop":
                    return StopHairpin(
                        label=wedge_number,
                        spread=spread,
                        placement=placement or "below",
                        voice=voice,
                        staff=staff
                    )
            
            # Check for pedal elements
            pedal_elem = find_element(direction_type_elem, "pedal")
            if pedal_elem is not None:
                pedal_type = pedal_elem.get("type")
                pedal_number = pedal_elem.get("number", "1")
                
                # Get sign and line attributes
                sign = pedal_elem.get("sign") != "no"  # Default is yes for sign
                line = pedal_elem.get("line") != "no"  # Default is yes for line
                
                if pedal_type == "start":
                    return StartPedal(
                        label=pedal_number,
                        sign=sign,
                        line=line,
                        placement=placement or "below",
                        voice=voice,
                        staff=staff
                    )
                elif pedal_type == "stop":
                    return StopPedal(
                        label=pedal_number,
                        sign=sign,
                        line=line,
                        placement=placement or "below",
                        voice=voice,
                        staff=staff
                    )
                elif pedal_type == "change":
                    return ChangePedal(
                        label=pedal_number,
                        sign=sign,
                        line=line,
                        placement=placement or "below",
                        voice=voice,
                        staff=staff
                    )
            
            # Check for dynamics
            dynamics_elem = find_element(direction_type_elem, "dynamics")
            if dynamics_elem is not None:
                # Find the first dynamic mark (e.g., f, p, mf, etc.)
                for dynamic_type in Dynamic.STANDARD_TYPES:
                    if find_element(dynamics_elem, dynamic_type) is not None:
                        return Dynamic(dynamic_text=dynamic_type, 
                                      placement=placement or "below", 
                                      staff=staff, 
                                      voice=voice)
                
                # Check for other-dynamics
                other_dynamics = get_text(dynamics_elem, "other-dynamics")
                if other_dynamics:
                    return Dynamic(dynamic_text=other_dynamics, 
                                  placement=placement or "below", 
                                  staff=staff, 
                                  voice=voice)
                
                # If no recognized dynamic was found
                logger.warning("Unrecognized dynamic marking")
                return None
                
            # Check for metronome marks
            metronome_elem = find_element(direction_type_elem, "metronome")
            if metronome_elem is not None:
                beat_unit = get_text(metronome_elem, "beat-unit")
                beat_unit_dot = find_element(metronome_elem, "beat-unit-dot")
                per_minute = get_text(metronome_elem, "per-minute")
                
                if per_minute and beat_unit:
                    try:
                        bpm = float(per_minute)
                        # Convert beat unit to beat length
                        beat_unit_map = {
                            "whole": 4.0,
                            "half": 2.0, 
                            "quarter": 1.0,
                            "eighth": 0.5,
                            "16th": 0.25,
                            "32nd": 0.125,
                            "64th": 0.0625,
                            "128th": 0.03125
                        }
                        
                        beat_length = beat_unit_map.get(beat_unit, 1.0)  # Default to quarter note
                        
                        # Apply dot if present
                        if beat_unit_dot is not None:
                            beat_length *= 1.5  # A dotted note is 1.5x the original length
                        
                        # Create other attributes dict for additional properties
                        other_attrs = {}
                        if metronome_elem.get("parentheses") == "yes":
                            other_attrs["parentheses"] = "yes"
                            
                        return MetronomeMark(
                            beat_length=beat_length,
                            bpm=bpm,
                            placement=placement or "above",
                            staff=staff,
                            voice=voice,
                            **other_attrs
                        )
                    except ValueError:
                        logger.warning(f"Invalid BPM value: {per_minute}")
                
                return None
                
            # Check for text annotations
            words_elem = find_element(direction_type_elem, "words")
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
                
                # Extract any additional attributes
                other_attrs = {}
                for attr_name, attr_value in words_elem.attrib.items():
                    if attr_name not in ["font-size", "font-style", "font-weight"]:
                        other_attrs[attr_name] = attr_value
                
                text_annotation = TextAnnotation(
                    text=text,
                    font_size=font_size,
                    italic=italic,
                    bold=bold,
                    placement=placement or "above",
                    staff=staff,
                    voice=voice,
                    **other_attrs
                )
                
                # Store text annotation for potential bracket, but also return it if no bracket is found
                continue
                
            # Check for brackets
            bracket_elem = find_element(direction_type_elem, "bracket")
            if bracket_elem is not None:
                bracket_type = bracket_elem.get("type")
                number = bracket_elem.get("number", "1")
                
                if bracket_type == "start":
                    line_type = bracket_elem.get("line-type", "dashed")
                    line_end = bracket_elem.get("line-end")
                    end_length = bracket_elem.get("end-length")
                    
                    if end_length is not None:
                        try:
                            end_length = float(end_length)
                        except ValueError:
                            end_length = None
                            
                    return StartBracket(
                        label=number,
                        line_type=line_type,
                        line_end=line_end,
                        end_length=end_length,
                        text=text_annotation,
                        placement=placement or "above",
                        voice=voice,
                        staff=staff
                    )
                    
                elif bracket_type == "stop":
                    line_end = bracket_elem.get("line-end")
                    end_length = bracket_elem.get("end-length")
                    
                    if end_length is not None:
                        try:
                            end_length = float(end_length)
                        except ValueError:
                            end_length = None
                            
                    return StopBracket(
                        label=number,
                        line_end=line_end,
                        end_length=end_length,
                        text=text_annotation,
                        placement=placement or "above",
                        voice=voice,
                        staff=staff
                    )
        
        # If we've gotten here and have a text annotation but no bracket, return the text annotation
        if text_annotation is not None:
            return text_annotation
                
        # Check for harmony element (which is not inside direction-type)
        harmony_elem = find_element(direction_elem, "harmony")
        if harmony_elem is not None:
            # Extract root information
            root_step = get_text(find_element(harmony_elem, "root"), "root-step")
            root_alter_text = get_text(find_element(harmony_elem, "root"), "root-alter", "0")
            
            try:
                root_alter = int(float(root_alter_text))
            except ValueError:
                root_alter = 0
                logger.warning(f"Invalid root alteration: {root_alter_text}, defaulting to 0")
            
            # Extract kind information
            kind_text = get_text(harmony_elem, "kind")
            if kind_text and root_step:
                # Check if kind is valid
                if kind_text not in Harmony.KINDS:
                    # Check if any version with different casing matches
                    found_kind = False
                    for valid_kind in Harmony.KINDS:
                        if kind_text.lower() == valid_kind.lower():
                            kind_text = valid_kind
                            found_kind = True
                            break
                            
                    if not found_kind:
                        logger.warning(f"Unknown harmony kind: {kind_text}, defaulting to 'major'")
                        kind_text = "major"
                
                # Check for use-symbols attribute
                kind_elem = find_element(harmony_elem, "kind")
                use_symbols = kind_elem is not None and kind_elem.get("use-symbols") == "yes"
                
                # Extract degrees if present
                degrees = []
                for degree_elem in find_elements(harmony_elem, "degree"):
                    value_text = get_text(degree_elem, "degree-value")
                    alter_text = get_text(degree_elem, "degree-alter", "0")
                    type_text = get_text(degree_elem, "degree-type", "alter")
                    
                    if value_text:
                        try:
                            value = int(value_text)
                            alter = int(float(alter_text))
                            
                            # Validate degree type
                            if type_text not in Degree.DEGREE_TYPES:
                                logger.warning(f"Unknown degree type: {type_text}, defaulting to 'alter'")
                                type_text = "alter"
                                
                            print_object = degree_elem.get("print-object") != "no"
                            
                            degrees.append(Degree(
                                value=value,
                                alter=alter,
                                degree_type=type_text,
                                print_object=print_object
                            ))
                        except ValueError:
                            logger.warning(f"Invalid degree value/alter: {value_text}/{alter_text}")
                
                return Harmony(
                    root_letter=root_step,
                    root_alter=root_alter,
                    kind=kind_text,
                    use_symbols=use_symbols,
                    degrees=degrees,
                    placement=placement or "above"
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
    def import_notation(notation_elem, find_element, get_text, find_elements) -> Optional[Union[Notation, List[Notation]]]:
        """
        Import a notation element.
        
        :param notation_elem: The notation element
        :param find_element: Method to find child elements
        :param get_text: Method to get text content
        :param find_elements: Method to find multiple child elements
        :returns: A Notation object, a list of Notation objects, or None if not recognized
        """
        notations = []
        
        # Check for fermata
        fermata_elem = find_element(notation_elem, "fermata")
        if fermata_elem is not None:
            inverted = fermata_elem.get("type") == "inverted"
            notations.append(Fermata(inverted=inverted))
            
        # Check for arpeggiate
        arpeggiate_elem = find_element(notation_elem, "arpeggiate")
        if arpeggiate_elem is not None:
            direction_text = arpeggiate_elem.get("direction")
            direction = None
            
            if direction_text == "up":
                direction = ArpeggiationDirection.UP
            elif direction_text == "down":
                direction = ArpeggiationDirection.DOWN
                
            notations.append(Arpeggiate(direction=direction))
            
        # Check for non-arpeggiate
        non_arpeggiate_elem = find_element(notation_elem, "non-arpeggiate")
        if non_arpeggiate_elem is not None:
            notations.append(NonArpeggiate())
            
        # Check for ornaments
        ornaments_elem = find_element(notation_elem, "ornaments")
        if ornaments_elem is not None:
            # Extract placement (for all ornaments)
            placement_str = ornaments_elem.get("placement", "above")
            try:
                placement = StaffPlacement(placement_str)
            except ValueError:
                logger.warning(f"Unknown placement value: {placement_str}, defaulting to 'above'")
                placement = StaffPlacement.ABOVE
            
            # Check for mordent
            mordent_elem = find_element(ornaments_elem, "mordent")
            if mordent_elem is not None:
                notations.append(Mordent(inverted=False, placement=placement))
                
            # Check for inverted mordent
            inverted_mordent_elem = find_element(ornaments_elem, "inverted-mordent")
            if inverted_mordent_elem is not None:
                notations.append(Mordent(inverted=True, placement=placement))
                
            # Check for turn
            turn_elem = find_element(ornaments_elem, "turn")
            if turn_elem is not None:
                notations.append(Turn(inverted=False, delayed=False, placement=placement))
                
            # Check for inverted turn
            inverted_turn_elem = find_element(ornaments_elem, "inverted-turn")
            if inverted_turn_elem is not None:
                notations.append(Turn(inverted=True, delayed=False, placement=placement))
                
            # Check for delayed turn
            delayed_turn_elem = find_element(ornaments_elem, "delayed-turn")
            if delayed_turn_elem is not None:
                notations.append(Turn(inverted=False, delayed=True, placement=placement))
                
            # Check for delayed inverted turn
            delayed_inverted_turn_elem = find_element(ornaments_elem, "delayed-inverted-turn")
            if delayed_inverted_turn_elem is not None:
                notations.append(Turn(inverted=True, delayed=True, placement=placement))
                
            # Check for schleifer (horizontal grace)
            schleifer_elem = find_element(ornaments_elem, "schleifer")
            if schleifer_elem is not None:
                notations.append(Schleifer(placement=placement))
                
            # Check for trill-mark
            trill_mark_elem = find_element(ornaments_elem, "trill-mark")
            if trill_mark_elem is not None:
                notations.append(TrillMark(placement=placement))
                
            # Check for tremolo
            tremolo_elem = find_element(ornaments_elem, "tremolo")
            if tremolo_elem is not None:
                # Get tremolo type (default to 'single' if not specified)
                tremolo_type = tremolo_elem.get("type", "single")
                
                # For both tremolo with type attribute and without
                # Get the number of lines (marks) from text content
                tremolo_text = tremolo_elem.text
                num_lines = 3  # Default
                if tremolo_text:
                    try:
                        num_lines = int(tremolo_text)
                    except ValueError:
                        logger.warning(f"Invalid tremolo lines value: {tremolo_text}, defaulting to 3")
                notations.append(Tremolo(num_lines=num_lines))
        
        # Check for technical notations
        technical_elem = find_element(notation_elem, "technical")
        if technical_elem is not None:
            # Collect all technical notations within this single technical element
            # This ensures we don't lose any technical notations when multiple are present
            technical_notations = []
            
            # Check for up-bow
            if find_element(technical_elem, "up-bow") is not None:
                technical_notations.append(UpBow())
                
            # Check for down-bow
            if find_element(technical_elem, "down-bow") is not None:
                technical_notations.append(DownBow())
                
            # Check for open-string
            if find_element(technical_elem, "open-string") is not None:
                technical_notations.append(OpenString())
                
            # Check for harmonic
            if find_element(technical_elem, "harmonic") is not None:
                technical_notations.append(Harmonic())
                
            # Check for stopped
            if find_element(technical_elem, "stopped") is not None:
                technical_notations.append(Stopped())
                
            # Check for snap-pizzicato
            if find_element(technical_elem, "snap-pizzicato") is not None:
                technical_notations.append(SnapPizzicato())
            
            # Add all technical notations to the main list
            notations.extend(technical_notations)
        
        # Return based on the number of notations found
        if len(notations) == 0:
            return None
        elif len(notations) == 1:
            return notations[0]
        else:
            return notations 