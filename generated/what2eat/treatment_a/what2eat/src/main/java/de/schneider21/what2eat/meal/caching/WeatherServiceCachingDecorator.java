package de.schneider21.what2eat.meal.caching;

import de.schneider21.what2eat.meal.business.IWeatherService;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;

public class WeatherServiceCachingDecorator implements IWeatherService {

    private IWeatherService weatherService;
    private Map<String, Double> temperatureCache = new ConcurrentHashMap<>();

    public WeatherServiceCachingDecorator(IWeatherService weatherService) {
        this.weatherService = weatherService;
    }

    @Override
    public Double getTemperatureInCelsius(String city, String countryCode, String dateString) {
        String key = city + countryCode + dateString;
        return temperatureCache.computeIfAbsent(key, s -> weatherService.getTemperatureInCelsius(city, countryCode, dateString));
    }
}
