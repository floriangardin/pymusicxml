# pymusicxml

_pymusicxml_ is a simple python library for exporting and importing MusicXML files, modelling 
them in a hierarchical and musically logical way. Although MusicXML can simply be created using `xml.etree.ElementTree`,
it is a confusing process: for instance, objects like tuplets and chords are created using note attributes in the 
MusicXML standard. In _pymusicxml_, they are modelled as containers.

## Installation

```
pip install pymusicxml
```

## Usage

### Creating and Exporting MusicXML

See the examples folder for examples of explicitly created and exported scores, as well as algorithmically 
created and exported scores.

```python
from pymusicxml import *

# Create a simple score
score = Score(title="Hello World")
part = Part(part_name="Piano")
score.append(part)

# Add a measure with some notes
measure = Measure()
measure.append(Note(pitch=Pitch("C", 4), duration=1))
measure.append(Note(pitch=Pitch("E", 4), duration=1))
measure.append(Note(pitch=Pitch("G", 4), duration=1))
measure.append(Rest(duration=1))
part.append(measure)

# Export to MusicXML
score.export_to_file("hello_world.musicxml")
```

### Importing MusicXML

_pymusicxml_ now supports importing MusicXML files, creating the same object hierarchy used for exporting. This enables round-trip compatibility where a file can be imported, modified, and exported again.

```python
from pymusicxml import import_musicxml

# Import a MusicXML file
score = import_musicxml("existing_score.musicxml")

# Access score components
print(f"Title: {score.title}")
print(f"Parts: {len(score.parts)}")

# Modify the score
score.title = "Modified Score"

# Export the modified score
score.export_to_file("modified_score.musicxml")
```

See the `examples/import` directory for more detailed examples of importing and modifying MusicXML files.

## Development

_pymusicxml_ is part of [scamp](https://sr.ht/~marcevanstein/scamp/), a Suite for Computer-Assisted Music in Python.