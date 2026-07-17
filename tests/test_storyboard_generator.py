import base64
import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image

from src.vision.storyboard_generator import StoryboardGenerator
from src.nlp.script_analyzer import ScriptAnalyzer


class StoryboardGeneratorTests(unittest.TestCase):
    def test_create_storyboard_pdf_creates_output(self):
        with TemporaryDirectory() as tmp_dir:
            image_path = Path(tmp_dir) / "scene_001.png"
            Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8)).save(image_path)

            output_path = Path(tmp_dir) / "storyboard.pdf"
            generator = StoryboardGenerator.__new__(StoryboardGenerator)

            result = generator.create_storyboard_pdf([str(image_path)], str(output_path))

            self.assertEqual(result, str(output_path))
            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 0)

    def test_script_analyzer_falls_back_without_models(self):
        analyzer = ScriptAnalyzer()
        scene = analyzer.analyze_scene("INT. A kitchen. John enters and smiles.")

        self.assertIn(scene.type, {"action", "dialogue"})
        self.assertTrue(scene.emotions)
        self.assertTrue(scene.actions or scene.characters)

    def test_add_storyboard_elements_renders_script_caption(self):
        generator = StoryboardGenerator.__new__(StoryboardGenerator)
        image = np.zeros((256, 256, 3), dtype=np.uint8)
        result = generator.add_storyboard_elements(image, {"id": 1, "type": "action", "content": "INT. A kitchen. Maya walks in and smiles."})

        self.assertFalse(np.array_equal(result, image))

    def test_extract_gemini_image_decodes_payload(self):
        generator = StoryboardGenerator.__new__(StoryboardGenerator)
        image_bytes = BytesIO()
        Image.fromarray(np.zeros((16, 16, 3), dtype=np.uint8)).save(image_bytes, format="PNG")
        payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "inlineData": {
                                    "mimeType": "image/png",
                                    "data": base64.b64encode(image_bytes.getvalue()).decode("ascii")
                                }
                            }
                        ]
                    }
                }
            ]
        }

        image = generator._extract_gemini_image(payload, (16, 16))

        self.assertIsNotNone(image)
        self.assertEqual(image.shape[:2], (16, 16))


if __name__ == "__main__":
    unittest.main()
