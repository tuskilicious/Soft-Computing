# Script-to-Storyboard Generation System

An AI-powered system that converts film scripts into visual storyboards using NLP, Computer Vision, and Deep Learning.

## Features

- Script parsing and scene segmentation
- Emotion and action analysis
- Scene classification (action/dialogue)
- Visual storyboard generation
- Cloud API integration

## Project Structure

```
script2storyboard/
├── src/
│   ├── nlp/              # NLP processing modules
│   ├── vision/           # Computer vision and image generation
│   ├── models/           # ML models and training code
│   └── api/              # API endpoints and services
├── examples/             # Example scripts and outputs
├── tests/               # Unit tests
└── config/              # Configuration files
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy model:
```bash
python -m spacy download en_core_web_lg
```

## Usage

1. Process a script:
```bash
python src/main.py --script path/to/script.txt
```

2. Generate storyboard:
```bash
python src/main.py --generate --script path/to/script.txt
```

## API Documentation

The system provides RESTful APIs for:
- Script analysis
- Scene segmentation
- Storyboard generation
- Scene classification

## License

MIT License 