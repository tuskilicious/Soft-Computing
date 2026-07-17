import spacy
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from transformers import pipeline

@dataclass
class Scene:
    id: int
    content: str
    type: str  # 'action' or 'dialogue'
    emotions: List[str]
    actions: List[str]
    characters: List[str]

class ScriptAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.emotion_analyzer = pipeline("text-classification", 
                                      model="j-hartmann/emotion-english-distilroberta-base")
        self.scene_classifier = pipeline("zero-shot-classification",
                                       model="facebook/bart-large-mnli")

    def segment_scenes(self, script_text: str) -> List[str]:
        """Segment script into individual scenes using fuzzy logic."""
        # Split by scene markers (INT, EXT, etc.)
        scene_markers = ["INT.", "EXT.", "INT/EXT.", "INT -", "EXT -"]
        scenes = []
        current_scene = []
        
        for line in script_text.split('\n'):
            if any(marker in line.upper() for marker in scene_markers):
                if current_scene:
                    scenes.append('\n'.join(current_scene))
                current_scene = [line]
            else:
                current_scene.append(line)
        
        if current_scene:
            scenes.append('\n'.join(current_scene))
        
        return scenes

    def analyze_scene(self, scene_text: str) -> Scene:
        """Analyze a single scene for emotions, actions, and type."""
        doc = self.nlp(scene_text)
        
        # Extract emotions
        emotions = self._extract_emotions(scene_text)
        
        # Extract actions
        actions = self._extract_actions(doc)
        
        # Extract characters
        characters = self._extract_characters(doc)
        
        # Classify scene type
        scene_type = self._classify_scene_type(scene_text)
        
        return Scene(
            id=hash(scene_text) % 10000,  # Simple hash for ID
            content=scene_text,
            type=scene_type,
            emotions=emotions,
            actions=actions,
            characters=characters
        )

    def _extract_emotions(self, text: str) -> List[str]:
        """Extract emotions from text using the emotion classifier."""
        result = self.emotion_analyzer(text)
        return [r['label'] for r in result]

    def _extract_actions(self, doc) -> List[str]:
        """Extract action verbs and phrases."""
        actions = []
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ in ["ROOT", "acl"]:
                actions.append(token.text)
        return actions

    def _extract_characters(self, doc) -> List[str]:
        """Extract character names using NER and custom rules."""
        characters = set()
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                characters.add(ent.text)
        return list(characters)

    def _classify_scene_type(self, text: str) -> str:
        """Classify scene as action or dialogue focused."""
        result = self.scene_classifier(
            text,
            candidate_labels=["action scene", "dialogue scene"],
            hypothesis_template="This is a {}."
        )
        return result['labels'][0].split()[0]  # Returns 'action' or 'dialogue'

    def process_script(self, script_text: str) -> List[Scene]:
        """Process entire script and return analyzed scenes."""
        scenes = self.segment_scenes(script_text)
        return [self.analyze_scene(scene) for scene in scenes] 