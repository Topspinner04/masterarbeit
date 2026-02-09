package de.schneider21.what2eat.meal.business;

import de.schneider21.what2eat.meal.data.BasicMeal;
import de.schneider21.what2eat.meal.data.ExtendedMeal;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MealServiceCached implements IMealService {

    private final IMealService mealService;
    private final Map<String, ExtendedMeal> extendedMealCache = new HashMap<>();
    private final Map<String, Long> extendedMealCacheTimestamp = new HashMap<>();
    private List<BasicMeal> allAvailableMealsCache;
    private long allAvailableMealsCacheTimestamp;

    public MealServiceCached(IMealService mealService) {
        this.mealService = mealService;
    }

    @Override
    public List<BasicMeal> getAllAvailableMeals() {
        if (allAvailableMealsCache != null && System.currentTimeMillis() - allAvailableMealsCacheTimestamp < 10000) {
            return allAvailableMealsCache;
        }
        allAvailableMealsCache = mealService.getAllAvailableMeals();
        allAvailableMealsCacheTimestamp = System.currentTimeMillis();
        return allAvailableMealsCache;
    }

    @Override
    public ExtendedMeal getExtendedMealForDate(String dateString) {
        if (extendedMealCache.containsKey(dateString) && System.currentTimeMillis() - extendedMealCacheTimestamp.get(dateString) < 10000) {
            return extendedMealCache.get(dateString);
        }
        ExtendedMeal extendedMeal = mealService.getExtendedMealForDate(dateString);
        extendedMealCache.put(dateString, extendedMeal);
        extendedMealCacheTimestamp.put(dateString, System.currentTimeMillis());
        return extendedMeal;
    }

    @Override
    public int calculateColdBowlProbabilityInPercent(Double temperature) {
        return mealService.calculateColdBowlProbabilityInPercent(temperature);
    }
}
