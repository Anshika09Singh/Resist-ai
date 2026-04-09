from textblob import TextBlob


FACE_EMOTION_MAP = {
    "angry": ("Angry", "Angry", -0.7),
    "disgust": ("Stressed", "Stressed", -0.5),
    "fear": ("Stressed", "Stressed", -0.6),
    "happy": ("Happy", "Happy", 0.8),
    "sad": ("Sad", "Sad", -0.8),
    "surprise": ("Surprised", "Neutral", 0.1),
    "neutral": ("Neutral", "Neutral", 0.0),
}

STRESS_KEYWORDS = {
    "stressed",
    "stress",
    "overwhelmed",
    "burned out",
    "burnt out",
    "anxious",
    "anxiety",
    "pressure",
    "tired",
    "exhausted",
    "worried",
}

ANGER_KEYWORDS = {
    "angry",
    "mad",
    "furious",
    "annoyed",
    "frustrated",
    "upset",
    "irritated",
}

NEGATIVE_MOODS = {"sad", "angry", "stressed", "anxious", "discomfort"}


def analyze_mood(text):
    cleaned_text = (text or "").strip()

    if not cleaned_text:
        return "Neutral", 0.0, 0.0

    lowered_text = cleaned_text.lower()
    analysis = TextBlob(cleaned_text)
    polarity = analysis.sentiment.polarity

    if any(keyword in lowered_text for keyword in ANGER_KEYWORDS):
        mood = "Angry"
    elif any(keyword in lowered_text for keyword in STRESS_KEYWORDS):
        mood = "Stressed"
    elif polarity > 0.3:
        mood = "Happy"
    elif polarity < -0.3:
        mood = "Sad"
    else:
        mood = "Neutral"

    confidence = estimate_confidence(mood, polarity)
    return mood, polarity, confidence


def interpret_face_emotion(emotion):
    normalized = (emotion or "neutral").strip().lower()
    return FACE_EMOTION_MAP.get(normalized, ("Neutral", "Neutral", 0.0))


def combine_moods(voice_mood, face_mood):
    if voice_mood and face_mood:
        return f"Voice: {voice_mood} | Face: {face_mood}"
    return voice_mood or face_mood or "Neutral"


def estimate_confidence(mood, polarity):
    normalized_mood = (mood or "Neutral").strip().lower()
    base = min(abs(polarity or 0.0), 1.0)

    if normalized_mood in {"stressed", "angry"}:
        return 0.82

    if normalized_mood == "neutral":
        return 0.6

    return round(min(0.98, 0.58 + (base * 0.4)), 2)


def build_support_plan(mood, negative_streak=0):
    normalized_mood = (mood or "Neutral").strip().lower()

    if normalized_mood == "sad":
        suggestions = [
            {
                "title": "Gentle motivation",
                "description": "You are allowed to take things one small step at a time. A hard moment does not define your whole day.",
            },
            {
                "title": "Positive affirmation",
                "description": "Remind yourself: I am trying, I am learning, and I can handle one next step.",
            },
        ]
        daily_action = "Take a 10-minute walk or sit near fresh air for a short reset."
    elif normalized_mood in {"stressed", "angry", "anxious", "discomfort"}:
        suggestions = [
            {
                "title": "Breathing exercise",
                "description": "Try box breathing: inhale for 4 seconds, hold for 4, exhale for 4, and pause for 4. Repeat 4 times.",
            },
            {
                "title": "Calming tip",
                "description": "Step away for a minute, loosen your shoulders, and focus only on the very next small task.",
            },
        ]
        daily_action = "Drink water, relax your shoulders, and restart with one easy task."
    elif normalized_mood == "happy":
        suggestions = [
            {
                "title": "Use the momentum",
                "description": "This is a good time to start an important task, review a goal, or finish something small that has been waiting.",
            },
            {
                "title": "Growth idea",
                "description": "Capture one win from today and turn that energy into your next focused step.",
            },
        ]
        daily_action = "Start one small task you have been postponing for 10 focused minutes."
    else:
        suggestions = [
            {
                "title": "Stay steady",
                "description": "Your mood looks fairly balanced. Keep your day simple and consistent.",
            },
            {
                "title": "Light productivity tip",
                "description": "Pick one manageable task and finish it before switching to something else.",
            },
        ]
        daily_action = "Drink water and complete one simple task before taking your next break."

    mental_health_check = None
    if negative_streak >= 2 and normalized_mood in NEGATIVE_MOODS:
        mental_health_check = "Consider taking a break or talking to someone you trust."

    return {
        "suggestions": suggestions,
        "daily_action": daily_action,
        "mental_health_check": mental_health_check,
    }


def generate_advice(mood, polarity, aqi, temp):
    normalized_mood = (mood or "Neutral").strip().lower()
    stress = abs(polarity or 0.0) * 10

    if aqi is not None and aqi > 150 and normalized_mood in {"sad", "angry", "anxious"}:
        return "Air quality is poor and you seem tense. Stay indoors if possible, hydrate, and try a short breathing exercise."

    if normalized_mood == "happy" and aqi is not None and aqi < 100:
        return "You seem to be in a good space and the air looks fairly clean. A short walk or outdoor break could feel great."

    if stress > 5:
        return "You sound a bit mentally overloaded. Take a short pause, breathe slowly, and reset before the next task."

    if temp is not None and temp > 35:
        return "It is quite warm right now. Keep water nearby and avoid long periods in direct heat."

    if normalized_mood in NEGATIVE_MOODS:
        return "Try a calmer next step: water, fresh air if safe, or talking through what is bothering you."

    return "Your signals look fairly balanced right now. Keep a steady routine with rest, hydration, and a little movement."
