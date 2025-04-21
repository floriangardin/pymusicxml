import os
import tempfile
import pytest
from pymusicxml import (
    Score, Part, Measure, Note, Rest, 
    KeySignature, NonTraditionalKeySignature,
    import_musicxml
)

def test_custom_key_signature_import_export():
    """Test that custom key signatures can be properly imported and exported"""
    
    # Create a score with a custom key signature
    key_signature_str = "d-flat, f#, gx, cbb"
    
    # Create the score
    original_score = Score([
        Part("Test Part", [
            Measure([
                Note("C4", 1),
                Note("D4", 1),
                Note("E4", 1),
                Rest(1)
            ], key=key_signature_str)
        ])
    ])
    
    # Export to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.musicxml', delete=False) as temp:
        temp_path = temp.name
    
    try:
        original_score.export_to_file(temp_path)
        
        # Import and check the key signature
        imported_score = import_musicxml(temp_path)
        
        # Verify the key signature was correctly imported
        measure = imported_score.parts[0].contents[0]
        assert isinstance(measure.key, NonTraditionalKeySignature)
        
        # Verify it has the correct alterations
        alterations = measure.key.step_alteration_tuples
        assert len(alterations) == 4
        
        # Check each alteration
        steps = [t[0] for t in alterations]
        alters = [t[1] for t in alterations]
        
        assert 'D' in steps
        assert 'F' in steps
        assert 'G' in steps
        assert 'C' in steps
        
        # Verify the alterations are correct
        d_index = steps.index('D')
        f_index = steps.index('F')
        g_index = steps.index('G')
        c_index = steps.index('C')
        
        assert alters[d_index] == -1.0  # d-flat
        assert alters[f_index] == 1.0   # f#
        assert alters[g_index] == 2.0   # gx (double sharp)
        assert alters[c_index] == -2.0  # cbb (double flat)
        
        # Export again and reimport to verify round-trip consistency
        with tempfile.NamedTemporaryFile(suffix='.musicxml', delete=False) as temp2:
            temp2_path = temp2.name
            
        imported_score.export_to_file(temp2_path)
        reimported_score = import_musicxml(temp2_path)
        
        # Verify the key signature is still correct
        measure = reimported_score.parts[0].contents[0]
        assert isinstance(measure.key, NonTraditionalKeySignature)
        assert len(measure.key.step_alteration_tuples) == 4
    
    finally:
        # Clean up temporary files
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        if 'temp2_path' in locals() and os.path.exists(temp2_path):
            os.unlink(temp2_path) 