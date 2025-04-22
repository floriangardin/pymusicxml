"""
Base importer module with core XML parsing functionality.

This module provides the base MusicXMLImporter class with fundamental methods
for parsing MusicXML files.
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
import xml.etree.ElementTree as ET
from typing import Dict, Optional, Sequence, Union, Any
from pathlib import Path
import re
import zipfile
import tempfile
import os

# Set up logging
logger = logging.getLogger(__name__)


class MusicXMLImporter:
    """
    Base class for importing MusicXML files and converting them to pymusicxml objects.
    
    This class handles the core XML parsing functionality and provides utility methods
    for navigating and extracting data from MusicXML files.
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
        if self.file_path.suffix in [".mxl"]:
            self.parse_mxl()
        elif self.file_path.suffix in [".musicxml", ".xml"]:
            self.parse_musicxml()
        else:
            raise ValueError(f"Unsupported file extension: {self.file_path.suffix}")

    def parse_mxl(self):
        """Parse the compressed MusicXML file and extract the root element."""
        try:
            # Create a temporary directory to extract files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract the MXL file (which is a ZIP archive)
                with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Look for container.xml which points to the main MusicXML file
                container_path = os.path.join(temp_dir, "META-INF", "container.xml")
                if os.path.exists(container_path):
                    # Parse container.xml to find the main MusicXML file
                    container_tree = ET.parse(container_path)
                    container_root = container_tree.getroot()
                    
                    # Find the rootfile element which contains the path to the main MusicXML file
                    rootfile_element = container_root.find(".//*[@full-path]")
                    if rootfile_element is not None:
                        main_file_path = rootfile_element.get("full-path")
                        musicxml_path = os.path.join(temp_dir, main_file_path)
                    else:
                        raise ValueError("Could not find main MusicXML file in container.xml")
                else:
                    # If container.xml doesn't exist, look for a .musicxml or .xml file
                    xml_files = [f for f in os.listdir(temp_dir) 
                                if f.endswith('.musicxml') or f.endswith('.xml')]
                    if xml_files:
                        musicxml_path = os.path.join(temp_dir, xml_files[0])
                    else:
                        raise ValueError("Could not find MusicXML file in the archive")
                
                # Parse the main MusicXML file
                tree = ET.parse(musicxml_path)
                self.root = tree.getroot()
                # Extract namespaces if present
                self._extract_namespaces()
                logger.info(f"Successfully parsed compressed MusicXML file: {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to parse compressed MusicXML file: {self.file_path}")
            logger.error(f"Error: {str(e)}")
            raise
            
    def parse_musicxml(self):
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
    
    def _get_text(self, parent, tag, default=None, index=None) -> str:
        """
        Get the text content of an element within the parent.
        
        Args:
            parent: Parent element to search in
            tag: Tag name to search for
            default: Default value to return if element not found
            index: Index for selecting a specific element when multiple elements exist with the same tag
            
        Returns:
            Text content of the element or default if not found
        """
        if index is not None:
            elements = self._find_elements(parent, tag)
            if elements and 0 <= index < len(elements):
                return elements[index].text if elements[index].text is not None else default
            return default
        
        element = self._find_element(parent, tag)
        return element.text if element is not None and element.text is not None else default 