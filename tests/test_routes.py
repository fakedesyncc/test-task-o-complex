import pytest
from app import create_app, database
from unittest.mock import patch

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Прогноз погоды' in response.data.decode()

@patch('app.utils.geocode_city')
def test_autocomplete(mock_geocode, client):
    mock_geocode.return_value = [
        {'name': 'Moscow', 'admin1': 'Moscow', 'country': 'Russia', 'latitude': 55.75, 'longitude': 37.61}
    ]
    
    response = client.get('/autocomplete?query=mos')
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]['name'] == 'Moscow, Moscow, Russia'

@patch('app.utils.get_weather')
@patch('app.utils.geocode_city')
def test_get_weather(mock_geocode, mock_weather, client):
    mock_geocode.return_value = [
        {'name': 'Moscow', 'latitude': 55.75, 'longitude': 37.61}
    ]
    
    mock_weather.return_value = {
        'current_weather': {
            'temperature': 20.5,
            'windspeed': 10.2,
            'weathercode': 1
        },
        'hourly': {
            'time': ['2023-01-01T00:00', '2023-01-01T01:00'],
            'temperature_2m': [19.0, 18.5],
            'apparent_temperature': [18.0, 17.5],
            'relativehumidity_2m': [65, 70],
            'precipitation_probability': [10, 20],
            'weathercode': [1, 2],
            'windspeed_10m': [5.0, 6.0]
        }
    }
    
    with client:
        response = client.get('/weather?city=Moscow&lat=55.75&lon=37.61')
        data = response.get_json()
        
        assert response.status_code == 200
        assert data['city'] == 'Moscow'
        assert data['current']['temperature'] == 20.5
        
        # Проверяем, что запрос сохранился в БД
        with client.session_transaction() as session:
            user_id = session.get('user_id')
            assert user_id is not None
        
        # Проверяем историю
        history = database.get_search_history(user_id)
        assert len(history) > 0
        assert history[0][0] == 'Moscow'

def test_stats(client):
    # Сначала добавляем данные
    database.log_search('test_user', 'Moscow')
    database.log_search('test_user', 'London')
    database.log_search('test_user', 'Moscow')
    
    response = client.get('/stats')
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data) >= 2
    assert any(city['city'] == 'Moscow' and city['count'] >= 2 for city in data)