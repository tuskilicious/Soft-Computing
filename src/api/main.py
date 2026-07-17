from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
from typing import List
import json

from ..nlp.script_analyzer import ScriptAnalyzer
from ..vision.storyboard_generator import StoryboardGenerator

app = FastAPI(title="Script-to-Storyboard API")

# Initialize components
script_analyzer = ScriptAnalyzer()
storyboard_generator = StoryboardGenerator()

@app.post("/analyze-script")
async def analyze_script(file: UploadFile = File(...)):
    """Analyze a script file and return scene analysis."""
    try:
        # Read script content
        content = await file.read()
        script_text = content.decode()
        
        # Process script
        scenes = script_analyzer.process_script(script_text)
        
        # Convert scenes to dict for JSON serialization
        scene_dicts = [
            {
                "id": scene.id,
                "content": scene.content,
                "type": scene.type,
                "emotions": scene.emotions,
                "actions": scene.actions,
                "characters": scene.characters
            }
            for scene in scenes
        ]
        
        return {"scenes": scene_dicts}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-storyboard")
async def generate_storyboard(file: UploadFile = File(...)):
    """Generate storyboard from script file."""
    try:
        # Create temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Read and analyze script
            content = await file.read()
            script_text = content.decode()
            scenes = script_analyzer.process_script(script_text)
            
            # Convert scenes to dict format
            scene_dicts = [
                {
                    "id": scene.id,
                    "content": scene.content,
                    "type": scene.type
                }
                for scene in scenes
            ]
            
            # Generate storyboard images
            image_paths = storyboard_generator.generate_storyboard(
                scene_dicts, 
                output_dir=temp_dir
            )
            
            # Create PDF
            pdf_path = os.path.join(temp_dir, "storyboard.pdf")
            storyboard_generator.create_storyboard_pdf(image_paths, pdf_path)
            
            # Return PDF file
            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename="storyboard.pdf"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"} 