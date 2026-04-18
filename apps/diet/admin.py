from django.contrib import admin
from .models import FoodItem, Meal, MealIngredient, DietPlan, DietDay, FoodLog, NutritionGoal


class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 1


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'calories_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['name', 'meal_type', 'prep_time_minutes', 'total_calories']
    list_filter = ['meal_type']
    inlines = [MealIngredientInline]


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'goal', 'duration_weeks', 'daily_calories', 'is_active']
    list_filter = ['goal', 'is_active']
    filter_horizontal = ['assigned_users']


@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'meal_type', 'food_item', 'amount_g']
    list_filter = ['date', 'meal_type']
    search_fields = ['user__email']
    date_hierarchy = 'date'


@admin.register(NutritionGoal)
class NutritionGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'goal', 'daily_calories', 'protein_g', 'carbs_g', 'fat_g']
