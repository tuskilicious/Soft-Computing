import re
from typing import List
from dataclasses import dataclass

try:
    import spacy
except ImportError:  # pragma: no cover - exercised in minimal environments
    spacy = None

try:
    from transformers import pipeline
except ImportError:  # pragma: no cover - exercised in minimal environments
    pipeline = None

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
        self.nlp = None
        if spacy is not None:
            try:
                self.nlp = spacy.load("en_core_web_lg")
            except OSError:
                self.nlp = None

        self.emotion_analyzer = None
        self.scene_classifier = None
        if pipeline is not None:
            try:
                self.emotion_analyzer = pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base"
                )
                self.scene_classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli"
                )
            except Exception:
                self.emotion_analyzer = None
                self.scene_classifier = None

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
        self._last_text = scene_text
        doc = None
        if self.nlp is not None:
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
        """Extract emotions from text using the emotion classifier when available."""
        if self.emotion_analyzer is not None:
            result = self.emotion_analyzer(text)
            return [r['label'] for r in result]

        lower_text = text.lower()
        if any(word in lower_text for word in ["angry", "furious", "upset"]):
            return ["anger"]
        if any(word in lower_text for word in ["happy", "joy", "smile", "laugh"]):
            return ["joy"]
        if any(word in lower_text for word in ["sad", "cry", "tear"]):
            return ["sadness"]
        return ["neutral"]

    def _extract_actions(self, doc) -> List[str]:
        """Extract action verbs and phrases using heuristics when spaCy is unavailable."""
        if doc is None:
            verbs = re.findall(r"\b(?:run|walk|look|speak|smile|cry|laugh|open|close|enter|exit|fight|kiss|hug|sit|stand|hold|drop|throw|go|come)\b", self._last_text.lower())
            return list(dict.fromkeys(verbs))

        actions = []
        for token in doc:
            if token.pos_ == "VERB" and token.dep_ in ["ROOT", "acl"]:
                actions.append(token.text)
        return actions

    def _extract_characters(self, doc) -> List[str]:
        """Extract character names using NER and custom rules."""
        if doc is None:
            names = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b", self._last_text)
            return list(dict.fromkeys(names))

        characters = set()
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                characters.add(ent.text)
        return list(characters)

    def _classify_scene_type(self, text: str) -> str:
        """Classify scene as action or dialogue focused."""
        if self.scene_classifier is not None:
            result = self.scene_classifier(
                text,
                candidate_labels=["action scene", "dialogue scene"],
                hypothesis_template="This is a {}."
            )
            return result['labels'][0].split()[0]  # Returns 'action' or 'dialogue'

        if re.search(r"[?!.]", text) and len(text.split()) < 30:
            return "dialogue"
        return "action"

    def process_script(self, script_text: str) -> List[Scene]:
        """Process entire script and return analyzed scenes."""
        scenes = self.segment_scenes(script_text)
        return [self.analyze_scene(scene) for scene in scenes] 