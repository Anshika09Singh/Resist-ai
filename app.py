import base64
import binascii
import logging
import os
import tempfile

import cv2
import numpy as np
import whisper
from deepface import DeepFace
from flask import Flask, jsonify, render_template, request, session

from model import (
    NEGATIVE_MOODS,
    analyze_mood,
    build_support_plan,
    combine_moods,
    generate_advice,
    interpret_face_emotion,
)
from utils import get_environment_snapshot


app = Flask(__name__)
app.logger.setLevel(logging.INFO)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "realassist-ai-secret")


try:
    WHISPER_MODEL = whisper.load_model("base")
except Exception as exc:
    WHISPER_MODEL = None
    app.logger.exception("Failed to load Whisper model: %s", exc)


def error_response(message, status_code=400, details=None):
    payload = {"success": False, "error": message}
    if details:
        payload["details"] = details
    return jsonify(payload), status_code


def success_response(payload):
    payload["success"] = True
    return jsonify(payload)


def extract_data_url_content(data_url):
    if not data_url or not isinstance(data_url, str):
        raise ValueError("Missing media payload.")
    if "," not in data_url:
        raise ValueError("Invalid media payload format.")
    return data_url.split(",", 1)[1]


def get_data_url_mime_type(data_url):
    if not data_url or not isinstance(data_url, str) or "," not in data_url:
        raise ValueError("Invalid media payload format.")

    header = data_url.split(",", 1)[0]
    if not header.startswith("data:"):
        raise ValueError("Invalid media payload format.")

    mime_type = header[5:].split(";", 1)[0].strip().lower()
    return mime_type or "application/octet-stream"


def get_audio_suffix(audio_data):
    mime_type = get_data_url_mime_type(audio_data)
    mime_to_suffix = {
        "audio/webm": ".webm",
        "audio/mp4": ".mp4",
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/ogg": ".ogg",
        "audio/ogg;codecs=opus": ".ogg",
    }
    return mime_to_suffix.get(mime_type, ".webm")


def decode_audio_data(audio_data):
    encoded_audio = extract_data_url_content(audio_data)
    try:
        return base64.b64decode(encoded_audio)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Audio data could not be decoded.") from exc


def validate_audio_file(audio_path):
    try:
        audio_array = whisper.load_audio(audio_path)
    except Exception as exc:
        raise ValueError("The audio recording could not be read. Please record again and speak for a moment.") from exc

    if audio_array is None or len(audio_array) == 0:
        raise ValueError("The recording looks empty. Please try again and speak clearly for at least 2 seconds.")

    max_amplitude = float(np.max(np.abs(audio_array))) if len(audio_array) else 0.0
    if max_amplitude < 1e-4:
        raise ValueError("The recording is too quiet. Please move closer to the microphone and try again.")

    duration_seconds = len(audio_array) / whisper.audio.SAMPLE_RATE
    if duration_seconds < 1.5:
        raise ValueError("Please record at least 2 seconds of speech before analyzing.")


def transcribe_audio(audio_data):
    if WHISPER_MODEL is None:
        raise RuntimeError("Whisper model is not available on the server.")

    audio_bytes = decode_audio_data(audio_data)
    if not audio_bytes:
        raise ValueError("Audio recording is empty.")

    audio_suffix = get_audio_suffix(audio_data)
    temp_audio_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=audio_suffix) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        validate_audio_file(temp_audio_path)

        try:
            result = WHISPER_MODEL.transcribe(temp_audio_path, fp16=False)
        except RuntimeError as exc:
            if "cannot reshape tensor of 0 elements" in str(exc).lower():
                raise ValueError("The recording was too short or empty for analysis. Please try again and speak for at least 2 seconds.") from exc
            raise

        text = (result.get("text") or "").strip()

        if not text:
            raise ValueError("No speech was detected. Please speak a little louder and try again.")

        return text
    finally:
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except OSError:
                app.logger.warning("Could not remove temp audio file: %s", temp_audio_path)


def decode_image(image_data):
    encoded_image = extract_data_url_content(image_data)

    try:
        image_bytes = base64.b64decode(encoded_image)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("Image data could not be decoded.") from exc

    np_buffer = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_buffer, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Image frame is invalid or empty.")

    return image


def analyze_face(image_data):
    image = decode_image(image_data)

    try:
        result = DeepFace.analyze(
            image,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )
    except Exception as exc:
        raise RuntimeError("Face emotion analysis failed.") from exc

    analysis = result[0] if isinstance(result, list) else result
    dominant_emotion = analysis.get("dominant_emotion")
    emotion_scores = analysis.get("emotion", {})

    if not dominant_emotion:
        raise ValueError("No facial emotion could be detected.")

    display_mood, advice_mood, polarity = interpret_face_emotion(dominant_emotion)
    confidence = round(float(emotion_scores.get(dominant_emotion, 0.0)) / 100, 2)

    return {
        "raw_emotion": dominant_emotion,
        "display_mood": display_mood,
        "advice_mood": advice_mood,
        "polarity": polarity,
        "confidence": confidence,
    }


def build_environment_data():
    environment = get_environment_snapshot()
    return {
        "temp": environment["temp"],
        "aqi": environment["aqi"],
        "aqi_category": environment["aqi_category"],
        "location": environment["location"],
    }


def get_negative_streak(current_mood):
    history = session.get("recent_moods", [])
    normalized_mood = (current_mood or "Neutral").strip().lower()
    history.append(normalized_mood)
    history = history[-5:]
    session["recent_moods"] = history

    streak = 0
    for mood in reversed(history):
        if mood in NEGATIVE_MOODS:
            streak += 1
        else:
            break

    return streak


def build_result_payload(
    text=None,
    mood=None,
    polarity=0.0,
    face_mood=None,
    source="text",
    confidence_score=0.0,
    support_mood=None,
):
    environment = build_environment_data()
    advice_seed = face_mood or mood or "Neutral"
    streak = get_negative_streak(support_mood or mood or face_mood or "Neutral")
    support_plan = build_support_plan(support_mood or advice_seed, negative_streak=streak)
    advice = generate_advice(
        mood=advice_seed,
        polarity=polarity,
        aqi=environment["aqi"],
        temp=environment["temp"],
    )

    return {
        "source": source,
        "text": text,
        "mood": mood,
        "face_mood": face_mood,
        "detected_emotion": support_mood or mood or face_mood,
        "confidence_score": round(float(confidence_score or 0.0) * 100, 1),
        "advice": advice,
        "suggestions": support_plan["suggestions"],
        "daily_action": support_plan["daily_action"],
        "mental_health_check": support_plan["mental_health_check"],
        "environment": environment,
    }


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/analyze/text")
def analyze_text_route():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()

    if not text:
        return error_response("Please enter some text before analyzing.")

    try:
        mood, polarity, confidence = analyze_mood(text)
        response = build_result_payload(
            text=text,
            mood=mood,
            polarity=polarity,
            source="text",
            confidence_score=confidence,
            support_mood=mood,
        )
        return success_response(response)
    except Exception as exc:
        app.logger.exception("Text analysis failed: %s", exc)
        return error_response("Text analysis failed. Please try again.", 500)


@app.post("/analyze/voice")
def analyze_voice_route():
    payload = request.get_json(silent=True) or {}
    audio = payload.get("audio")

    if not audio:
        return error_response("Please record your voice before submitting.")

    try:
        text = transcribe_audio(audio)
        mood, polarity, confidence = analyze_mood(text)
        response = build_result_payload(
            text=text,
            mood=mood,
            polarity=polarity,
            source="voice",
            confidence_score=confidence,
            support_mood=mood,
        )
        return success_response(response)
    except ValueError as exc:
        return error_response(str(exc))
    except RuntimeError as exc:
        app.logger.exception("Voice analysis runtime error: %s", exc)
        return error_response(str(exc), 500)
    except Exception as exc:
        app.logger.exception("Voice analysis failed: %s", exc)
        return error_response("Voice analysis failed. Please try again.", 500)


@app.post("/analyze/face")
def analyze_face_route():
    payload = request.get_json(silent=True) or {}
    image = payload.get("image")

    if not image:
        return error_response("Please capture a camera frame before analyzing.")

    try:
        face_result = analyze_face(image)
        response = build_result_payload(
            text=None,
            mood=face_result["display_mood"],
            polarity=face_result["polarity"],
            face_mood=face_result["display_mood"],
            source="face",
            confidence_score=face_result["confidence"],
            support_mood=face_result["advice_mood"],
        )
        response["raw_face_emotion"] = face_result["raw_emotion"]
        return success_response(response)
    except ValueError as exc:
        return error_response(str(exc))
    except RuntimeError as exc:
        app.logger.exception("Face analysis runtime error: %s", exc)
        return error_response(str(exc), 500)
    except Exception as exc:
        app.logger.exception("Face analysis failed: %s", exc)
        return error_response("Face analysis failed. Please try again.", 500)


@app.post("/analyze/combo")
def analyze_combo_route():
    payload = request.get_json(silent=True) or {}
    audio = payload.get("audio")
    image = payload.get("image")

    if not audio and not image:
        return error_response("Please provide voice or camera input for combo analysis.")

    try:
        spoken_text = None
        voice_mood = None
        polarity = 0.0
        voice_confidence = 0.0
        face_result = None

        if audio:
            spoken_text = transcribe_audio(audio)
            voice_mood, polarity, voice_confidence = analyze_mood(spoken_text)

        if image:
            face_result = analyze_face(image)

        final_mood = combine_moods(voice_mood, face_result["display_mood"] if face_result else None)
        advice_mood = voice_mood or (face_result["advice_mood"] if face_result else "Neutral")
        advice_polarity = polarity if spoken_text else (face_result["polarity"] if face_result else 0.0)
        confidence_values = [score for score in [voice_confidence, face_result["confidence"] if face_result else 0.0] if score]
        combo_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0

        response = build_result_payload(
            text=spoken_text,
            mood=final_mood,
            polarity=advice_polarity,
            face_mood=face_result["display_mood"] if face_result else None,
            source="combo",
            confidence_score=combo_confidence,
            support_mood=advice_mood,
        )
        response["voice_mood"] = voice_mood
        response["raw_face_emotion"] = face_result["raw_emotion"] if face_result else None
        response["advice"] = generate_advice(
            mood=advice_mood,
            polarity=advice_polarity,
            aqi=response["environment"]["aqi"],
            temp=response["environment"]["temp"],
        )
        return success_response(response)
    except ValueError as exc:
        return error_response(str(exc))
    except RuntimeError as exc:
        app.logger.exception("Combo analysis runtime error: %s", exc)
        return error_response(str(exc), 500)
    except Exception as exc:
        app.logger.exception("Combo analysis failed: %s", exc)
        return error_response("Combo analysis failed. Please try again.", 500)


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
