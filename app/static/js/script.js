document.addEventListener('DOMContentLoaded', function() {
    const cityInput = document.getElementById('city-input');
    const autocompleteResults = document.getElementById('autocomplete-results');
    const weatherForm = document.getElementById('weather-form');
    const weatherResults = document.getElementById('weather-results');
    const historyList = document.getElementById('history-list');
    const historySection = document.getElementById('history-section');
    
    // Загрузка истории
    loadHistory();
    
    // Автодополнение
    cityInput.addEventListener('input', function() {
        const query = cityInput.value.trim();
        
        if (query.length < 2) {
            autocompleteResults.innerHTML = '';
            return;
        }
        
        fetch(`/autocomplete?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                autocompleteResults.innerHTML = '';
                data.forEach(item => {
                    const div = document.createElement('div');
                    div.textContent = item.name;
                    div.addEventListener('click', function() {
                        cityInput.value = item.name;
                        autocompleteResults.innerHTML = '';
                        getWeather(item.name, item.latitude, item.longitude);
                    });
                    autocompleteResults.appendChild(div);
                });
            });
    });
    
    // Отправка формы
    weatherForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const query = cityInput.value.trim();
        
        if (query) {
            fetch(`/autocomplete?query=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.length > 0) {
                        getWeather(data[0].name, data[0].latitude, data[0].longitude);
                    } else {
                        showError('Город не найден');
                    }
                });
        }
    });
    
    // Получение погоды
    function getWeather(city, lat, lon) {
        fetch(`/weather?city=${encodeURIComponent(city)}&lat=${lat}&lon=${lon}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    displayWeather(data);
                    loadHistory();
                }
            })
            .catch(error => {
                showError('Ошибка при получении данных');
            });
    }
    
    // Отображение погоды
    function displayWeather(data) {
        weatherResults.innerHTML = `
            <div class="weather-card mt-4">
                <div class="weather-header">
                    <h2>${data.city}</h2>
                    <div class="d-flex align-items-center">
                        <h1 class="display-4 me-3">${data.current.temperature}°C</h1>
                        <div>
                            <h5>${data.current.weather_description}</h5>
                            <div>Ветер: ${data.current.windspeed} км/ч</div>
                        </div>
                    </div>
                </div>
                
                <div class="weather-body">
                    <h4 class="mb-3">Прогноз на ближайшие 6 часов:</h4>
                    <div class="row text-center">
                        ${data.forecast.map(hour => `
                            <div class="col forecast-item">
                                <div class="fw-bold">${hour.time.split('T')[1].substring(0, 5)}</div>
                                <div class="fs-5">${hour.temperature}°C</div>
                                <div>${hour.weather_description}</div>
                                <div>💧 ${hour.precipitation_probability}%</div>
                                <div>🌬️ ${hour.wind_speed} км/ч</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        cityInput.value = '';
        autocompleteResults.innerHTML = '';
    }
    
    // Показать ошибку
    function showError(message) {
        weatherResults.innerHTML = `
            <div class="alert alert-danger mt-4">${message}</div>
        `;
    }
    
    // Загрузка истории
    function loadHistory() {
        fetch('/stats')
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    historyList.innerHTML = data.map(item => `
                        <button class="history-btn" 
                                onclick="getWeatherForHistory('${item.city}')">
                            ${item.city} (${item.count})
                        </button>
                    `).join('');
                    historySection.style.display = 'block';
                } else {
                    historySection.style.display = 'none';
                }
            });
    }
    
    // Получить погоду для города из истории
    window.getWeatherForHistory = function(city) {
        cityInput.value = city;
        weatherForm.dispatchEvent(new Event('submit'));
    };
});