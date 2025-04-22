#!/usr/bin/env python
"""
Example demonstrating how to import, modify, and re-export a MusicXML file.

This example shows how to use pymusicxml to:
1. Import an existing MusicXML file
2. Modify the imported score (add notes, change dynamics, transpose, etc.)
3. Export the modified score to a new MusicXML file
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

import os
import sys
from pathlib import Path

# Ensure the pymusicxml package is in the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pymusicxml import import_musicxml
from pymusicxml import Note, Pitch, Rest, Dynamic, Measure

def main():
    """Example of importing, modifying, and re-exporting a MusicXML file."""
    # The path to the example MusicXML file
    file_path = Path(__file__).parent.parent.parent / "tests" / "data" / "main.musicxml"
    
    if not file_path.exists():
        print(f"Error: Example file {file_path} does not exist.")
        return
    
    print(f"Importing MusicXML file: {file_path}")
    
    # Import the MusicXML file
    score = import_musicxml(file_path)
    
    # Modify the score metadata
    score.title = "Modified Score"
    score.composer = "Modified by pymusicxml"
    
    # Add a new dynamic marking to the first part's first measure
    if score.parts and score.parts[0].measures:
        first_measure = score.parts[0].measures[0]
        # Add a forte dynamic at the beginning of the measure
        first_measure.directions_with_displacements.insert(0, (Dynamic("f"), 0))
        print("Added dynamic marking to first measure")
    
    
    # Add a new measure to the first part
    for idx, part in enumerate(score.parts):
        if idx != 0:
            part.measures.append(Measure([Rest(4)]))
            continue
        
        # Create a new measure with some notes
        new_measure_elements = [
            Note(pitch=Pitch("C", 4), duration=1),
            Note(pitch=Pitch("E", 4), duration=1),
            Note(pitch=Pitch("G", 4), duration=1),
            Rest(duration=1)
        ]
        
        # Add the new measure
        part.measures.append(Measure(contents=new_measure_elements))
        print("Added new measure to first part")

    # Export the modified score to a new MusicXML file
    output_path = Path(__file__).parent / "modified_score.musicxml"
    score.export_to_file(output_path)
    
    print(f"\nModified score exported to: {output_path}")

if __name__ == "__main__":
    main() 