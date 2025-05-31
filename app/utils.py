import requests

def geocode_city(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": city_name,
        "count": 5,
        "language": "ru",
        "format": "json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('results', [])

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relativehumidity_2m,apparent_temperature,precipitation_probability,weathercode,windspeed_10m",
        "timezone": "auto",
        "forecast_days": 1
    }
    response = requests.get(url, params=params)
    return response.json()

def weathercode_to_description(code):
    weather_codes = {
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Туман с инеем",
        51: "Морось: слабая",
        53: "Морось: умеренная",
        55: "Морось: сильная",
        56: "Ледяная морось: слабая",
        57: "Ледяная морось: сильная",
        61: "Дождь: слабый",
        63: "Дождь: умеренный",
        65: "Дождь: сильный",
        66: "Ледяной дождь: слабый",
        67: "Ледяной дождь: сильный",
        71: "Снег: слабый",
        73: "Снег: умеренный",
        75: "Снег: сильный",
        77: "Снежные зерна",
        80: "Ливень: слабый",
        81: "Ливень: умеренный",
        82: "Ливень: сильный",
        85: "Снегопад: слабый",
        86: "Снегопад: сильный",
        95: "Гроза: слабая или умеренная",
        96: "Гроза с мелким градом",
        99: "Гроза с крупным градом"
    }
    return weather_codes.get(code, "Неизвестно")