#!/usr/bin/env python
"""
Basic example demonstrating how to import a MusicXML file.

This example shows how to use the pymusicxml library to import a MusicXML file,
access its components, and modify it if needed.
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

def main():
    """Example of importing a MusicXML file and accessing its components."""
    file_path = Path(__file__).parent.parent / "DirectExampleAllFeatures.musicxml"
    
    if not file_path.exists():
        print(f"Error: Example file {file_path} does not exist.")
        return
    
    print(f"Importing MusicXML file: {file_path}")
    
    # Import the MusicXML file
    score = import_musicxml(file_path)
    
    # Print some basic information about the score
    print(f"Score title: {score.title}")
    print(f"Composer: {score.composer}")
    print(f"Number of parts: {len(score.parts)}")
    
    # Print information about each part
    for i, part in enumerate(score.parts):
        print(f"\nPart {i+1}: {part.part_name}")
        print(f"  Instrument: {part.instrument_name}")
        print(f"  Number of measures: {len(part.measures)}")
        
        # Print information about the first measure
        if part.measures:
            measure = part.measures[0]
            print(f"  First measure elements: {len(measure.contents)}")
            
            # Print information about the first few elements
            for j, element in enumerate(measure.contents[:5]):
                if j >= 5:
                    print("  ...")
                    break
                print(f"    Element {j+1}: {type(element).__name__}")
    
    print("\nImport successful!")

if __name__ == "__main__":
    main() 