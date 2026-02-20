package de.schneider21.what2eat.meal.caching;

import de.schneider21.what2eat.meal.business.IMenuService;
import de.schneider21.what2eat.meal.data.BasicMeal;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

public class MenuServiceCachingDecorator implements IMenuService {

    private IMenuService menuService;
    private Map<String, BasicMeal> mealForDateCache = new ConcurrentHashMap<>();
    private List<BasicMeal> allAvailableMealsCache;


    public MenuServiceCachingDecorator(IMenuService menuService) {
        this.menuService = menuService;
    }

    @Override
    public List<BasicMeal> getAllAvailableMeals() {
        if (allAvailableMealsCache == null) {
            allAvailableMealsCache = menuService.getAllAvailableMeals();
        }
        return allAvailableMealsCache;
    }

    @Override
    public BasicMeal getMealForDate(String dateString) {
        return mealForDateCache.computeIfAbsent(dateString, menuService::getMealForDate);
    }
}
