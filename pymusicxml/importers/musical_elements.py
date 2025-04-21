"""
Musical elements importer module for importing notes, rests, and other basic musical elements.

This module provides functionality for importing notes, rests, chords, pitches,
and other basic musical elements from MusicXML files.
"""

import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Sequence

import xml.etree.ElementTree as ET

from pymusicxml.score_components import (
    Note, Rest, BarRest, Chord, GraceNote, GraceChord,
    Pitch, Duration, Notehead, BeamedGroup, BarRestDuration, Tuplet
)
from pymusicxml.notations import (
    StartGliss, StopGliss, StartMultiGliss, StopMultiGliss
)

# Set up logging
logger = logging.getLogger(__name__)


class MusicalElementsImporter:
    """
    Class for importing basic musical elements from MusicXML files.
    
    This class provides methods for importing notes, rests, chords, pitches,
    and other basic musical elements.
    """
    
    @staticmethod
    def import_pitch(note_elem, find_element, get_text) -> Optional[Pitch]:
        """
        Import a pitch element from a note element.
        
        Args:
            note_elem: The note element
            find_element: Method to find child elements
            get_text: Method to get text content
            
        Returns:
            A Pitch object or None if the note has no pitch
        """
        pitch_elem = find_element(note_elem, "pitch")
        if pitch_elem is None:
            return None
            
        step = get_text(pitch_elem, "step", "C")
        octave = int(get_text(pitch_elem, "octave", "4"))
        
        alter_text = get_text(pitch_elem, "alter")
        alter = float(alter_text) if alter_text is not None else 0.0
        
        return Pitch(step=step, octave=octave, alteration=alter)
    
    @staticmethod
    def import_duration(note_elem, find_element, get_text) -> Duration:
        """
        Import duration information from a note element.
        
        Args:
            note_elem: The note element
            find_element: Method to find child elements
            get_text: Method to get text content
            
        Returns:
            A Duration object
        """
        # Get the note type
        note_type = get_text(note_elem, "type", "quarter")
        
        # Check for dots
        dot_elements = find_element(note_elem, "dot")
        num_dots = len(dot_elements) if isinstance(dot_elements, list) else (1 if dot_elements is not None else 0)
        
        # Check for tuplet
        time_modification = find_element(note_elem, "time-modification")
        tuplet_ratio = None
        if time_modification is not None:
            actual_notes = int(get_text(time_modification, "actual-notes", "1"))
            normal_notes = int(get_text(time_modification, "normal-notes", "1"))
            if actual_notes != normal_notes:
                tuplet_ratio = (actual_notes, normal_notes)
        
        return Duration(note_type=note_type, num_dots=num_dots, tuplet_ratio=tuplet_ratio)
    
    @staticmethod
    def import_notehead(note_elem, find_element, get_text) -> Optional[Notehead]:
        """
        Import notehead information from a note element.
        
        Args:
            note_elem: The note element
            find_element: Method to find child elements
            get_text: Method to get text content
            
        Returns:
            A Notehead object or None if no notehead is specified
        """
        notehead_elem = find_element(note_elem, "notehead")
        if notehead_elem is None:
            return None
            
        # Get the notehead type from the element text
        notehead_type = notehead_elem.text.strip().lower() if notehead_elem.text else "normal"
        
        # Make sure the notehead type is valid
        if notehead_type not in Notehead.valid_xml_types:
            logger.warning(f"Unknown notehead type: {notehead_type}, defaulting to 'normal'")
            notehead_type = "normal"
        
        # Get the filled attribute
        filled_attr = notehead_elem.get("filled")
        filled = None
        
        if filled_attr is not None:
            if filled_attr.lower() == "yes":
                filled = True
            elif filled_attr.lower() == "no":
                filled = False
        
        # Create the notehead
        return Notehead(notehead_name=notehead_type, filled=filled)
    
    @staticmethod
    def import_notations(note_elem, find_element, find_elements) -> List[Any]:
        """
        Import notations from a note element.
        
        Args:
            note_elem: The note element
            find_element: Method to find child elements
            find_elements: Method to find multiple child elements
            
        Returns:
            A list of notation objects
        """
        notations = []
        notations_elem = find_element(note_elem, "notations")
        
        if notations_elem is None:
            return notations
            
        # Handle glissandos
        glissando_elems = find_elements(notations_elem, "glissando") or []
        slide_elems = find_elements(notations_elem, "slide") or []
        
        # Process all glissando and slide elements
        for gliss in glissando_elems + slide_elems:
            gliss_type = gliss.get("type")
            number = gliss.get("number", "1")
            
            if gliss_type == "start":
                notations.append(StartGliss(number=number))
            elif gliss_type == "stop":
                notations.append(StopGliss(number=number))
        
        # TODO: Add more notation types (articulations, ornaments, technical, etc.)
        
        return notations
    
    @staticmethod
    def import_ties(note_elem, find_elements) -> List[str]:
        """
        Import tie information from a note element.
        
        Args:
            note_elem: The note element
            find_elements: Method to find multiple child elements
            
        Returns:
            A list of tie types ("start", "stop")
        """
        ties = []
        tie_elems = find_elements(note_elem, "tie") or []
        
        for tie in tie_elems:
            tie_type = tie.get("type")
            if tie_type:
                ties.append(tie_type)
                
        return ties
    
    @staticmethod
    def import_note(note_elem, find_element, get_text, find_elements) -> Optional[Union[Note, Rest, GraceNote]]:
        """
        Import a note element.
        
        Args:
            note_elem: The note element
            find_element: Method to find child elements
            get_text: Method to get text content
            find_elements: Method to find multiple child elements
            
        Returns:
            A Note, GraceNote, Rest, or BarRest object, or None if the note is part of a chord
        """
        # Check if this note is part of a chord
        is_chord = find_element(note_elem, "chord") is not None
        if is_chord:
            # This note is part of a chord, will be handled by the chord importer
            return None
            
        # Check if this is a grace note
        is_grace = find_element(note_elem, "grace") is not None
            
        # Check if this is a rest
        is_rest = find_element(note_elem, "rest") is not None
        
        # Extract voice information
        voice_text = get_text(note_elem, "voice")
        voice = int(voice_text) if voice_text is not None else None
        
        # Extract staff information
        staff_text = get_text(note_elem, "staff")
        staff = int(staff_text) if staff_text is not None else None
        
        if is_rest:
            # Handle rest
            duration = MusicalElementsImporter.import_duration(note_elem, find_element, get_text)
            
            # Check if it's a whole measure rest
            rest_elem = find_element(note_elem, "rest")
            is_measure_rest = rest_elem is not None and rest_elem.get("measure") == "yes"
            
            if is_measure_rest:
                # This is a whole measure rest
                bar_length_duration = BarRestDuration(length=duration.true_length)
                rest = BarRest(bar_length=bar_length_duration)
                
                # Set voice and staff attributes
                if voice is not None:
                    rest.voice = voice
                if staff is not None:
                    rest.staff = staff
                    
                return rest
            else:
                # This is a regular rest
                # Import notations
                notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
                
                # Import directions (to be implemented)
                directions = []
                
                rest = Rest(duration=duration, notations=notations, directions=directions)
                
                # Set voice and staff attributes
                if voice is not None:
                    rest.voice = voice
                if staff is not None:
                    rest.staff = staff
                    
                return rest
        else:
            # Handle note
            pitch = MusicalElementsImporter.import_pitch(note_elem, find_element, get_text)
            if pitch is None:
                logger.warning("Note element has no pitch")
                return None
            
            # Import ties
            ties = MusicalElementsImporter.import_ties(note_elem, find_elements)
            tie_value = None
            if "start" in ties and "stop" in ties:
                tie_value = "both"
            elif "start" in ties:
                tie_value = "start"
            elif "stop" in ties:
                tie_value = "stop"
            
            # Import notations
            notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
            
            # Import notehead
            notehead = MusicalElementsImporter.import_notehead(note_elem, find_element, get_text)
            
            # Import directions (to be implemented)
            directions = []
            
            # Import stem direction
            stemless = False
            stem = find_element(note_elem, "stem")
            if stem is not None and stem.text == "none":
                stemless = True
                
            if is_grace:
                # This is a grace note
                duration = MusicalElementsImporter.import_duration(note_elem, find_element, get_text)
                grace_note = GraceNote(
                    pitch=pitch,
                    duration=duration,
                    ties=tie_value,
                    notations=notations,
                    notehead=notehead,
                    directions=directions,
                    stemless=stemless
                )
                
                # Set voice and staff attributes
                if voice is not None:
                    grace_note.voice = voice
                if staff is not None:
                    grace_note.staff = staff
                    
                return grace_note
            else:
                # This is a regular note
                duration = MusicalElementsImporter.import_duration(note_elem, find_element, get_text)
                note = Note(
                    pitch=pitch,
                    duration=duration,
                    ties=tie_value,
                    notations=notations,
                    notehead=notehead,
                    directions=directions,
                    stemless=stemless
                )
                
                # Set voice and staff attributes
                if voice is not None:
                    note.voice = voice
                if staff is not None:
                    note.staff = staff
                    
                return note
            
    @staticmethod
    def import_chord(first_note_elem, chord_notes, find_element, get_text, find_elements) -> Optional[Union[Chord, GraceChord]]:
        """
        Import a chord from a list of note elements.
        
        Args:
            first_note_elem: The first note element of the chord
            chord_notes: List of note elements in the chord
            find_element: Method to find child elements
            get_text: Method to get text content
            find_elements: Method to find multiple child elements
            
        Returns:
            A Chord or GraceChord object
        """
        pitches = []
        
        # Check if this is a grace chord
        is_grace = find_element(first_note_elem, "grace") is not None
        
        # Get the first note's duration (all chord notes share the same duration)
        duration = MusicalElementsImporter.import_duration(first_note_elem, find_element, get_text)
        
        # Get all pitches in the chord
        for note_elem in chord_notes:
            pitch = MusicalElementsImporter.import_pitch(note_elem, find_element, get_text)
            if pitch is not None:
                pitches.append(pitch)
        
        if not pitches:
            logger.warning("Chord has no pitches")
            return None
        
        # Import ties from the first note
        ties = MusicalElementsImporter.import_ties(first_note_elem, find_elements)
        tie_value = None
        if "start" in ties and "stop" in ties:
            tie_value = "both"
        elif "start" in ties:
            tie_value = "start"
        elif "stop" in ties:
            tie_value = "stop"
        
        # Collect notations from all notes in the chord
        all_notations = []
        for note_elem in chord_notes:
            notations = MusicalElementsImporter.import_notations(note_elem, find_element, find_elements)
            all_notations.extend(notations)
        
        # Process multi-gliss notations
        multi_gliss_start = {}
        multi_gliss_stop = {}
        
        for notation in all_notations:
            if isinstance(notation, StartGliss):
                multi_gliss_start[notation.number] = notation
            elif isinstance(notation, StopGliss):
                multi_gliss_stop[notation.number] = notation
        
        # Replace individual glisses with multi-gliss if needed
        notations = []
        if len(multi_gliss_start) > 1:
            notations.append(StartMultiGliss(numbers=list(multi_gliss_start.keys())))
        elif len(multi_gliss_start) == 1:
            notations.append(next(iter(multi_gliss_start.values())))
            
        if len(multi_gliss_stop) > 1:
            notations.append(StopMultiGliss(numbers=list(multi_gliss_stop.keys())))
        elif len(multi_gliss_stop) == 1:
            notations.append(next(iter(multi_gliss_stop.values())))
        
        # Add all other notations
        for notation in all_notations:
            if not (isinstance(notation, StartGliss) or isinstance(notation, StopGliss)):
                notations.append(notation)
        
        # Import noteheads from multiple notes
        # Chord takes noteheads, not notehead
        noteheads = []
        for note_elem in chord_notes:
            notehead = MusicalElementsImporter.import_notehead(note_elem, find_element, get_text)
            if notehead is not None:
                noteheads.append(notehead)
        
        # Import directions (to be implemented)
        directions = []
        
        # Import stem direction
        stemless = False
        stem = find_element(first_note_elem, "stem")
        if stem is not None and stem.text == "none":
            stemless = True
        
        # Extract voice and staff information from the first note
        voice_text = get_text(first_note_elem, "voice")
        voice = int(voice_text) if voice_text is not None else None
        
        staff_text = get_text(first_note_elem, "staff")
        staff = int(staff_text) if staff_text is not None else None
        
        if is_grace:
            # Check if it's a slashed grace chord
            slashed = False
            grace_elem = find_element(first_note_elem, "grace")
            if grace_elem is not None and grace_elem.get("slash") == "yes":
                slashed = True
                
            grace_chord = GraceChord(
                pitches=pitches,
                duration=duration,
                ties=tie_value,
                notations=notations,
                noteheads=noteheads if noteheads else None,
                directions=directions,
                stemless=stemless,
                slashed=slashed
            )
            
            # Set voice and staff attributes
            if voice is not None:
                grace_chord.voice = voice
            if staff is not None:
                grace_chord.staff = staff
                
            return grace_chord
        else:
            chord = Chord(
                pitches=pitches,
                duration=duration,
                ties=tie_value,
                notations=notations,
                noteheads=noteheads if noteheads else None,
                directions=directions,
                stemless=stemless
            )
            
            # Set voice and staff attributes
            if voice is not None:
                chord.voice = voice
            if staff is not None:
                chord.staff = staff
                
            return chord
    
    @staticmethod
    def import_beamed_group(measure_elem, find_element, find_elements, get_text, start_idx, end_idx) -> Optional[BeamedGroup]:
        """
        Import a beamed group of notes from measure elements.
        
        Args:
            measure_elem: The measure element
            find_element: Method to find child elements
            find_elements: Method to find multiple child elements
            get_text: Method to get text content
            start_idx: Starting index of the beamed group
            end_idx: Ending index of the beamed group
            
        Returns:
            A BeamedGroup object or None if no beamed group is found
        """
        note_elems = find_elements(measure_elem, "note")
        if not note_elems or start_idx >= len(note_elems) or end_idx >= len(note_elems):
            return None
            
        # Import notes in the beamed group
        contents = []
        current_idx = start_idx
        while current_idx <= end_idx:
            note_elem = note_elems[current_idx]
            
            # Check if this is part of a chord
            is_chord = find_element(note_elem, "chord") is not None
            
            if is_chord:
                # Skip chord notes, they will be handled as part of the chord
                current_idx += 1
                continue
                
            # Check if this note is the start of a chord
            chord_notes = [note_elem]
            next_idx = current_idx + 1
            while next_idx < len(note_elems) and next_idx <= end_idx and find_element(note_elems[next_idx], "chord") is not None:
                chord_notes.append(note_elems[next_idx])
                next_idx += 1
                
            if len(chord_notes) > 1:
                # This is a chord
                chord = MusicalElementsImporter.import_chord(note_elem, chord_notes, find_element, get_text, find_elements)
                if chord:
                    contents.append(chord)
                current_idx = next_idx
            else:
                # This is a regular note or rest
                note = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
                if note:
                    contents.append(note)
                current_idx += 1
        
        if not contents:
            return None
            
        # Create and return the BeamedGroup
        return BeamedGroup(contents=contents)
    
    @staticmethod
    def import_tuplet(measure_elem, find_element, find_elements, get_text, start_idx, end_idx) -> Optional[Tuplet]:
        """
        Import a tuplet from measure elements.
        
        Args:
            measure_elem: The measure element
            find_element: Method to find child elements
            find_elements: Method to find multiple child elements
            get_text: Method to get text content
            start_idx: Starting index of the tuplet
            end_idx: Ending index of the tuplet
            
        Returns:
            A Tuplet object or None if no tuplet is found
        """
        note_elems = find_elements(measure_elem, "note")
        if not note_elems or start_idx >= len(note_elems) or end_idx >= len(note_elems):
            return None
        
        # First, create a beamed group with the contents
        beamed_group = MusicalElementsImporter.import_beamed_group(
            measure_elem, find_element, find_elements, get_text, start_idx, end_idx
        )
        
        if not beamed_group or not beamed_group.contents:
            return None
        
        # Extract the tuplet ratio from the first note
        first_note_elem = note_elems[start_idx]
        time_modification = find_element(first_note_elem, "time-modification")
        if time_modification is None:
            logger.warning("Tuplet missing time-modification element")
            return None
        
        actual_notes = int(get_text(time_modification, "actual-notes", "1"))
        normal_notes = int(get_text(time_modification, "normal-notes", "1"))
        
        if actual_notes == normal_notes:
            logger.warning("Invalid tuplet ratio: actual notes equals normal notes")
            return None
        
        ratio = (actual_notes, normal_notes)
        
        # Create the tuplet
        return Tuplet(contents=beamed_group.contents, ratio=ratio)
    
    @staticmethod
    def identify_groups_in_measure(measure_elem, find_element, find_elements, get_text) -> List[Union[Note, Rest, Chord, BeamedGroup, Tuplet]]:
        """
        Identify and process beamed groups and tuplets in a measure.
        
        Args:
            measure_elem: The measure element
            find_element: Method to find child elements
            find_elements: Method to find multiple child elements
            get_text: Method to get text content
            
        Returns:
            A list of musical elements, with beamed groups and tuplets properly grouped
        """
        note_elems = find_elements(measure_elem, "note")
        if not note_elems:
            return []
        
        # Find all forward elements in the measure
        # We don't directly create musical elements for forward/backup elements
        # These are implicit in the MusicXML and handled by position tracking in ScoreImporter
        forward_elems = find_elements(measure_elem, "forward")
        backup_elems = find_elements(measure_elem, "backup")
        
        # Log the presence of forward/backup elements for debugging
        if forward_elems:
            logger.debug(f"Found {len(forward_elems)} forward elements in measure")
            
        if backup_elems:
            logger.debug(f"Found {len(backup_elems)} backup elements in measure")
            
        # Dictionary to store groups with their starting positions
        element_positions = {}
        processed_indices = set()
        
        # First, identify tuplet groups
        tuplet_groups = []
        current_tuplet = None
        
        for i, note_elem in enumerate(note_elems):
            if i in processed_indices:
                continue
                
            # Skip chord members - they'll be processed with their parent
            if find_element(note_elem, "chord") is not None:
                processed_indices.add(i)
                continue
                
            # Check for tuplet notation
            notations_elem = find_element(note_elem, "notations")
            tuplet_elem = None
            if notations_elem is not None:
                tuplet_elem = find_element(notations_elem, "tuplet")
                
            # Check for time modification (required for tuplets)
            time_modification = find_element(note_elem, "time-modification")
            
            # Process tuplet start
            if tuplet_elem is not None and tuplet_elem.get("type") == "start":
                current_tuplet = {"start": i, "end": None}
            
            # Process tuplet stop
            if tuplet_elem is not None and tuplet_elem.get("type") == "stop":
                if current_tuplet is not None:
                    current_tuplet["end"] = i
                    tuplet_groups.append(current_tuplet)
                    current_tuplet = None
            
            # If we have a time modification but no tuplet notation,
            # this note is part of a tuplet
            if time_modification is not None and current_tuplet is None:
                # This is a tuplet without proper start/stop marks
                # Try to infer the tuplet grouping based on time modification
                actual_notes = int(get_text(time_modification, "actual-notes", "1"))
                normal_notes = int(get_text(time_modification, "normal-notes", "1"))
                
                if actual_notes != normal_notes:
                    # Look ahead for notes with the same time modification
                    tuplet_start = i
                    tuplet_end = i
                    for j in range(i + 1, len(note_elems)):
                        next_time_mod = find_element(note_elems[j], "time-modification")
                        if next_time_mod is not None:
                            next_actual = int(get_text(next_time_mod, "actual-notes", "1"))
                            next_normal = int(get_text(next_time_mod, "normal-notes", "1"))
                            if next_actual == actual_notes and next_normal == normal_notes:
                                tuplet_end = j
                            else:
                                break
                        else:
                            break
                    
                    if tuplet_end > tuplet_start:
                        tuplet_groups.append({"start": tuplet_start, "end": tuplet_end})
        
        # Create tuplets for identified groups and store with position
        for group in tuplet_groups:
            tuplet = MusicalElementsImporter.import_tuplet(
                measure_elem, find_element, find_elements, get_text, 
                group["start"], group["end"]
            )
            if tuplet:
                element_positions[group["start"]] = tuplet
                # Mark all indices in this group as processed
                processed_indices.update(range(group["start"], group["end"] + 1))
        
        # Now identify beamed groups among remaining notes
        beam_groups = []
        current_beam = None
        
        for i, note_elem in enumerate(note_elems):
            if i in processed_indices:
                continue
                
            # Skip chord members - they'll be processed with their parent
            if find_element(note_elem, "chord") is not None:
                processed_indices.add(i)
                continue
            
            # Look for beam elements
            beam_elems = find_elements(note_elem, "beam") or []
            
            # Process beam start
            for beam in beam_elems:
                if beam.text == "begin":
                    current_beam = {"start": i, "end": None}
                    break
            
            # Process beam end
            for beam in beam_elems:
                if beam.text == "end":
                    if current_beam is not None:
                        current_beam["end"] = i
                        beam_groups.append(current_beam)
                        current_beam = None
                    break
        
        # Create beamed groups for identified groups and store with position
        for group in beam_groups:
            beamed_group = MusicalElementsImporter.import_beamed_group(
                measure_elem, find_element, find_elements, get_text, 
                group["start"], group["end"]
            )
            if beamed_group:
                element_positions[group["start"]] = beamed_group
                # Mark all indices in this group as processed
                processed_indices.update(range(group["start"], group["end"] + 1))
        
        # Process remaining notes individually
        for i, note_elem in enumerate(note_elems):
            if i in processed_indices:
                continue
                
            # Skip chord members - they'll be processed with their parent
            if find_element(note_elem, "chord") is not None:
                processed_indices.add(i)
                continue
                
            # Check if this note is the start of a chord
            chord_notes = [note_elem]
            j = i + 1
            while j < len(note_elems) and find_element(note_elems[j], "chord") is not None:
                chord_notes.append(note_elems[j])
                processed_indices.add(j)
                j += 1
                
            if len(chord_notes) > 1:
                # This is a chord
                chord = MusicalElementsImporter.import_chord(note_elem, chord_notes, find_element, get_text, find_elements)
                if chord:
                    element_positions[i] = chord
            else:
                # This is a regular note or rest
                note = MusicalElementsImporter.import_note(note_elem, find_element, get_text, find_elements)
                if note:
                    element_positions[i] = note
            
            processed_indices.add(i)
        
        # Sort elements by their position in the original MusicXML
        sorted_result = []
        for pos in sorted(element_positions.keys()):
            sorted_result.append(element_positions[pos])
            
        return sorted_result 