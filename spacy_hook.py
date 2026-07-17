import os
import sys
import spacy

def get_spacy_model_path():
    """Get the path to the spaCy model."""
    try:
        # Try to load the model to get its path
        nlp = spacy.load('en_core_web_lg')
        return nlp.path
    except OSError:
        # If model is not found, download it
        spacy.cli.download('en_core_web_lg')
        nlp = spacy.load('en_core_web_lg')
        return nlp.path

# Add the spaCy model path to the system path
spacy_model_path = get_spacy_model_path()
if spacy_model_path not in sys.path:
    sys.path.append(spacy_model_path) 