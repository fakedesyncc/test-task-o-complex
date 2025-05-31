from flask import Blueprint, request, jsonify, render_template, make_response
import uuid
from . import database
from . import utils

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    user_id = request.cookies.get('user_id', str(uuid.uuid4()))
    history = database.get_search_history(user_id)
    
    resp = make_response(render_template('index.html', history=history))
    if not request.cookies.get('user_id'):
        resp.set_cookie('user_id', user_id, max_age=60*60*24*30)  # 30 дней
    return resp

@bp.route('/autocomplete')
def autocomplete():
    query = request.args.get('query', '')
    results = utils.geocode_city(query)
    suggestions = [{
        'name': f"{res['name']}, {res.get('admin1', '')}, {res.get('country', '')}",
        'latitude': res['latitude'],
        'longitude': res['longitude']
    } for res in results]
    return jsonify(suggestions)

@bp.route('/weather')
def get_weather():
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    if not city or not lat or not lon:
        return jsonify({'error': 'Missing parameters'}), 400
    
    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    weather_data = utils.get_weather(lat, lon)
    
    if 'error' in weather_data:
        return jsonify(weather_data), 400
    
    # Логируем запрос
    user_id = request.cookies.get('user_id')
    if user_id:
        database.log_search(user_id, city)
    
    # Форматируем данные
    current = weather_data['current_weather']
    hourly = weather_data['hourly']
    
    # Берем прогноз на ближайшие 6 часов
    forecast = []
    for i in range(6):
        forecast.append({
            'time': hourly['time'][i],
            'temperature': hourly['temperature_2m'][i],
            'apparent_temperature': hourly['apparent_temperature'][i],
            'humidity': hourly['relativehumidity_2m'][i],
            'precipitation_probability': hourly['precipitation_probability'][i],
            'weather_description': utils.weathercode_to_description(hourly['weathercode'][i]),
            'wind_speed': hourly['windspeed_10m'][i]
        })
    
    return jsonify({
        'city': city,
        'current': {
            'temperature': current['temperature'],
            'windspeed': current['windspeed'],
            'weathercode': current['weathercode'],
            'weather_description': utils.weathercode_to_description(current['weathercode'])
        },
        'forecast': forecast
    })

@bp.route('/stats')
def stats():
    stats_data = database.get_search_stats()
    return jsonify([{'city': row[0], 'count': row[1]} for row in stats_data])