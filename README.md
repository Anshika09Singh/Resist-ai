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
    A[User Input<br>Text / Voice / Camera] --> B[Preprocessing]

    B --> B1[Speech to Text - Whisper]
    B --> B2[Face Emotion Detection - DeepFace]
    B --> B3[Text Processing]

    B1 --> C[Text Mood Analysis]
    B3 --> C
    B2 --> D[Facial Emotion Mapping]

    C --> E[Multimodal Fusion]
    D --> E

    E --> F[Advice Engine]
    G[Environment Data<br>AQI and Temperature] --> F

    F --> H[Output<br>Mood, Confidence, Suggestions]
