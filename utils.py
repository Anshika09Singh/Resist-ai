import requests


DEFAULT_LATITUDE = 28.67
DEFAULT_LONGITUDE = 77.21
DEFAULT_LOCATION = "Delhi, India"
REQUEST_TIMEOUT = 10


def get_aqi_category(aqi):
    if aqi is None:
        return "Unavailable"
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    if aqi <= 200:
        return "Unhealthy"
    return "Very Unhealthy"


def get_weather(latitude=DEFAULT_LATITUDE, longitude=DEFAULT_LONGITUDE):
    try:
        url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitude}&longitude={longitude}&current_weather=true"
        )
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        current_weather = data.get("current_weather", {})

        if "temperature" not in current_weather:
            return None

        return {"temp": current_weather["temperature"]}
    except requests.RequestException:
        return None


def get_aqi(latitude=DEFAULT_LATITUDE, longitude=DEFAULT_LONGITUDE):
    try:
        url = (
            "https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={latitude}&longitude={longitude}&current=pm10"
        )
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        current = data.get("current", {})
        pm10 = current.get("pm10")

        if pm10 is None:
            return None

        return int(pm10)
    except requests.RequestException:
        return None


def get_environment_snapshot():
    weather = get_weather()
    aqi = get_aqi()

    return {
        "temp": weather["temp"] if weather else None,
        "aqi": aqi,
        "aqi_category": get_aqi_category(aqi),
        "location": DEFAULT_LOCATION,
    }
