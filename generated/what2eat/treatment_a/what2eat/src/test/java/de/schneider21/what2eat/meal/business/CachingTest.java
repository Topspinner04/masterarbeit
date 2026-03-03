package de.schneider21.what2eat.meal.business;

import de.schneider21.what2eat.meal.caching.MenuServiceCachingDecorator;
import de.schneider21.what2eat.meal.caching.WeatherServiceCachingDecorator;
import de.schneider21.what2eat.meal.data.BasicMeal;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.Collections;

import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class CachingTest {

    @Mock
    private IMenuService menuService;

    @Mock
    private IWeatherService weatherService;

    @Test
    void testMenuServiceCaching() {
        IMenuService cachingDecorator = new MenuServiceCachingDecorator(menuService);

        when(menuService.getMealForDate("2020-03-01")).thenReturn(new BasicMeal("2020-03-01", "Kaviar mit Pommes", new BigDecimal("20.00")));
        when(menuService.getAllAvailableMeals()).thenReturn(Collections.emptyList());

        // First call
        cachingDecorator.getMealForDate("2020-03-01");
        cachingDecorator.getAllAvailableMeals();

        // Second call
        cachingDecorator.getMealForDate("2020-03-01");
        cachingDecorator.getAllAvailableMeals();

        verify(menuService, times(1)).getMealForDate("2020-03-01");
        verify(menuService, times(1)).getAllAvailableMeals();
    }

    @Test
    void testWeatherServiceCaching() {
        IWeatherService cachingDecorator = new WeatherServiceCachingDecorator(weatherService);

        when(weatherService.getTemperatureInCelsius("Kaiserslautern", "DE", "2020-03-01")).thenReturn(20.0);

        // First call
        cachingDecorator.getTemperatureInCelsius("Kaiserslautern", "DE", "2020-03-01");

        // Second call
        cachingDecorator.getTemperatureInCelsius("Kaiserslautern", "DE", "2020-03-01");

        verify(weatherService, times(1)).getTemperatureInCelsius("Kaiserslautern", "DE", "2020-03-01");
    }
}
