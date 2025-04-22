"""
Module for importing MusicXML files into pymusicxml object hierarchy.

This module provides convenience functions for importing MusicXML files
and serves as the main entry point for the import functionality.
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


from typing import Union
from pathlib import Path

from pymusicxml.score_components import Score
from pymusicxml.importers.score_importer import import_musicxml as _import_musicxml

def import_musicxml(file_path: Union[str, Path]) -> Score:
    """
    Import a MusicXML file and return a Score object.
    
    Args:
        file_path: Path to the MusicXML file to import
        
    Returns:
        A Score object representing the imported MusicXML file
    """
    return _import_musicxml(file_path)

# For backwards compatibility
from pymusicxml.importers.base_importer import MusicXMLImporter 