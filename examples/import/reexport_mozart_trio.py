from pymusicxml import import_musicxml
from pathlib import Path

path = Path(__file__).parent / "MozartTrio.mxl"
score = import_musicxml(path)

# Reexport the score for testing
score.export_to_file(Path(__file__).parent / "MozartTrio_exported.musicxml")

