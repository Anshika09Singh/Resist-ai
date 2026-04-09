# Resist AI – Multimodal Mental Health Assistant

A practical, human-centered AI system that understands user emotions from text, voice, and facial expressions, and provides supportive, context-aware guidance.

---

## What is Resist AI?

Resist AI is a multimodal emotion understanding system. It combines:

* Text sentiment (what the user writes)
* Voice cues (speech patterns and tone)
* Facial expressions (visual emotion detection)
* Environment context (AQI and temperature)

By integrating these signals, the system produces a more reliable mood estimate and generates helpful recommendations.

---

## Key Capabilities

* Text Analysis – detects mood and polarity from user input
* Voice Analysis – converts speech to text (Whisper) and evaluates mood
* Face Analysis – extracts dominant emotion from camera frames (DeepFace)
* Multimodal Fusion – combines multiple signals for improved accuracy
* Context-Aware Advice – adapts suggestions using AQI and temperature
* Support Plan – generates short, actionable steps and daily check-ins

---

## System Architecture

Below is a simplified view of how data flows through the system.

```mermaid
flowchart LR
    A[User Input\n(Text / Voice / Camera)] --> B[Preprocessing]
    B --> B1[Speech → Text (Whisper)]
    B --> B2[Image → Emotion (DeepFace)]
    B --> B3[Clean & Normalize Text]

    B1 --> C[NLP Mood Analysis]
    B2 --> D[Face Emotion Mapping]
    B3 --> C

    C --> E[Multimodal Fusion]
    D --> E

    E --> F[Advice Engine]
    G[Environment (AQI, Temp)] --> F

    F --> H[Output\nMood • Confidence • Suggestions]
```

Note: If GitHub does not render Mermaid diagrams, include the PNG diagram below as a fallback.

---

## Architecture Diagram (PNG Fallback)

Save the following image as `architecture.png` and reference it below. (You can quickly export from draw.io / diagrams.net using the same blocks.)

![Architecture Diagram](docs/architecture.png)

---

## Project Structure

```
resist-ai/
├── app.py
├── model.py
├── utils.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── docs/
│   └── architecture.png
├── requirements.txt
├── .gitignore
└── README.md
```

---

## How It Works (End-to-End)

1. **Input** – user provides text, records voice, or captures a face frame
2. **Preprocessing**

   * Voice → text using Whisper
   * Image → emotion probabilities using DeepFace
   * Text cleaned for NLP
3. **Analysis**

   * Text/voice text → mood, polarity, confidence
   * Face → dominant emotion + confidence
4. **Fusion**

   * Combine signals to produce a final mood estimate
5. **Advice Engine**

   * Uses mood + AQI + temperature to generate guidance
6. **Output**

   * Mood, confidence score, suggestions, daily action

---

## Tech Stack

**Backend**

* Python, Flask

**AI/ML**

* Whisper (speech-to-text)
* DeepFace (facial emotion)
* Custom NLP utilities (mood, polarity, fusion)

**Frontend**

* HTML, CSS, JavaScript

**Utilities**

* OpenCV, NumPy

---

## API Endpoints

* `GET /` – UI
* `POST /analyze/text` – text → mood
* `POST /analyze/voice` – audio → transcription → mood
* `POST /analyze/face` – image → emotion → mood
* `POST /analyze/combo` – voice + face → fused mood

---

## Getting Started

### 1) Clone

```bash
git clone https://github.com/Anshika09Singh/Resist-ai.git
cd Resist-ai
```

### 2) Install

```bash
pip install -r requirements.txt
```

### 3) Run

```bash
python app.py
```

Open: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Configuration

Create a `.env` file (do not commit it):

```
FLASK_SECRET_KEY=your-secret-key
```

---

## Screenshots

Add your UI images inside `static/images/` and reference them here:

```
![Home](static/images/home.png)
![Voice](static/images/voice.png)
![Face](static/images/face.png)
```

---

## Example Output

* **Mood:** Calm / Stressed / Happy
* **Confidence:** 82.5%
* **Suggestions:** short, practical steps
* **Daily Action:** 1–2 minute task
* **Environment:** AQI, temperature context

---

## Limitations

* Low‑light images can reduce face accuracy
* Very short/quiet audio may fail validation
* Heuristic fusion (can be improved with learned fusion)

---

## Future Work

* LLM integration for conversational support
* Learned multimodal fusion (late/early fusion with weights)
* Real‑time streaming (WebRTC)
* Deployment (Render / AWS) and mobile UI

---

## Author

**Anshika Singh**

---

## License

MIT License (recommended)
