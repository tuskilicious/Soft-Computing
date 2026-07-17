import cv2
import numpy as np
import torch
from PIL import Image
from transformers import pipeline
from typing import List, Tuple
import os
from diffusers import StableDiffusionPipeline

class StoryboardGenerator:
    def __init__(self):
        self.image_generator = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")
        # Use diffusers for Stable Diffusion
        self.text_to_image = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float32
        )
        self.text_to_image = self.text_to_image.to("cpu")  # Use CPU
        
    def generate_storyboard_frame(self, scene_description: str, 
                                size: Tuple[int, int] = (512, 512)) -> np.ndarray:
        """Generate a storyboard frame from scene description."""
        # Generate image from text
        image = self.text_to_image(scene_description).images[0]
        image = image.resize(size)
        return np.array(image)

    def add_storyboard_elements(self, image: np.ndarray, 
                              scene_info: dict) -> np.ndarray:
        """Add storyboard elements like arrows, text, etc."""
        # Create a copy of the image
        result = image.copy()
        
        # Add scene number
        cv2.putText(result, f"Scene {scene_info.get('id', '')}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add scene type
        cv2.putText(result, scene_info.get('type', '').upper(), 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        return result

    def generate_storyboard(self, scenes: List[dict], 
                          output_dir: str = "output") -> List[str]:
        """Generate complete storyboard from list of scenes."""
        os.makedirs(output_dir, exist_ok=True)
        output_paths = []
        
        for i, scene in enumerate(scenes):
            # Generate base image
            image = self.generate_storyboard_frame(scene['content'])
            
            # Add storyboard elements
            image = self.add_storyboard_elements(image, scene)
            
            # Save image
            output_path = os.path.join(output_dir, f"scene_{i+1:03d}.png")
            cv2.imwrite(output_path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            output_paths.append(output_path)
            
        return output_paths

    def create_storyboard_pdf(self, image_paths: List[str], 
                            output_path: str) -> str:
        """Create a PDF from storyboard images."""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        for i, img_path in enumerate(image_paths):
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Calculate scaling to fit page
            scale = min(width/img_width, height/img_height) * 0.8
            img_width *= scale
            img_height *= scale
            
            # Center image on page
            x = (width - img_width) / 2
            y = (height - img_height) / 2
            
            c.drawImage(img_path, x, y, width=img_width, height=img_height)
            c.showPage()
        
        c.save()
        return output_path 