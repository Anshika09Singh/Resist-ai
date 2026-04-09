# Resist AI – Multimodal Mental Health Assistant

A practical, human-centered AI system that understands user emotions from text, voice, and facial expressions, and provides supportive, context-aware guidance.

---

## What is Resist AI?

Resist AI is a multimodal emotion understanding system. It combines:

- Text sentiment (what the user writes)
- Voice cues (speech patterns and tone)
- Facial expressions (visual emotion detection)
- Environment context (AQI and temperature)

By integrating these signals, the system produces a more reliable mood estimate and generates helpful recommendations.

---

## Key Capabilities

- Text Analysis – detects mood and polarity from user input  
- Voice Analysis – converts speech to text (Whisper) and evaluates mood  
- Face Analysis – extracts dominant emotion from camera frames (DeepFace)  
- Multimodal Fusion – combines multiple signals for improved accuracy  
- Context-Aware Advice – adapts suggestions using AQI and temperature  
- Support Plan – generates short, actionable steps and daily check-ins  

---

## System Architecture

Below is a simplified view of how data flows through the system.

### Architecture Diagram

![Architecture](architecture.png)

---

## Project Structure

```
resist-ai/
├── app.py                 # Main Flask application
├── model.py               # AI logic (mood analysis, fusion)
├── utils.py               # Helper functions (environment, utilities)
│
├── templates/             # HTML templates
│   └── index.html
│
├── static/                # Static assets
│   ├── css/
│   ├── js/
│   └── images/
│
├── architecture.png       # System architecture diagram
├── requirements.txt       # Python dependencies
├── .gitignore             # Ignored files
└── READM
```
## How It Works (End-to-End)

1. **User Input**
   - The user provides input in the form of text, voice, or facial image.

2. **Preprocessing**
   - Voice input is converted to text using Whisper.
   - Facial image is processed using DeepFace for emotion detection.
   - Text input is cleaned and normalized for analysis.

3. **Analysis**
   - Text and transcribed voice are analyzed to detect mood, sentiment polarity, and confidence score.
   - Facial data is used to identify dominant emotion.

4. **Multimodal Fusion**
   - Results from text, voice, and facial analysis are combined.
   - A final mood is determined using fusion logic.

5. **Context Integration**
   - Environmental data such as AQI and temperature is incorporated.
   - This helps generate more personalized recommendations.

6. **Advice Generation**
   - The system generates:
     - Mood assessment
     - Personalized suggestions
     - Daily actionable steps
     - Mental health check insights

7. **Final Output**
   - The user receives a complete response including:
     - Detected mood
     - Confidence score
     - Suggestions and guidance
     - Environmental context

## Tech Stack

### Backend
- Python  
- Flask  

### AI / Machine Learning
- Whisper – Speech-to-text processing  
- DeepFace – Facial emotion detection  
- Custom NLP – Mood analysis and sentiment detection  

### Frontend
- HTML  
- CSS  
- JavaScript  

### Libraries & Tools
- OpenCV – Image processing  
- NumPy – Numerical computations  
