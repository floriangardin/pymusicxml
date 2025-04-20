"""
Module for importing MusicXML files into pymusicxml object hierarchy.

This module provides convenience functions for importing MusicXML files
and serves as the main entry point for the import functionality.
"""

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