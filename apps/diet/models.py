from django.db import models
from django.conf import settings


class NutritionGoal(models.Model):
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
        ('endurance', 'Endurance'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='nutrition_goal')
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    daily_calories = models.PositiveIntegerField(default=2000)
    protein_g = models.PositiveIntegerField(default=150)
    carbs_g = models.PositiveIntegerField(default=200)
    fat_g = models.PositiveIntegerField(default=65)
    water_ml = models.PositiveIntegerField(default=2500)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.goal}"


class FoodItem(models.Model):
    CATEGORY_CHOICES = [
        ('protein', 'Protein'),
        ('carbs', 'Carbohydrates'),
        ('fat', 'Healthy Fats'),
        ('vegetable', 'Vegetables'),
        ('fruit', 'Fruits'),
        ('dairy', 'Dairy'),
        ('supplement', 'Supplements'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES)
    calories_per_100g = models.FloatField()
    protein_per_100g = models.FloatField(default=0)
    carbs_per_100g = models.FloatField(default=0)
    fat_per_100g = models.FloatField(default=0)
    fiber_per_100g = models.FloatField(default=0)
    image = models.ImageField(upload_to='food/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.calories_per_100g} cal/100g)"


class Meal(models.Model):
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
        ('pre_workout', 'Pre-Workout'),
        ('post_workout', 'Post-Workout'),
    ]

    name = models.CharField(max_length=100)
    meal_type = models.CharField(max_length=15, choices=MEAL_TYPE_CHOICES)
    description = models.TextField(blank=True)
    prep_time_minutes = models.PositiveIntegerField(default=15)
    instructions = models.TextField(blank=True)
    image = models.ImageField(upload_to='meals/', blank=True, null=True)
    food_items = models.ManyToManyField(FoodItem, through='MealIngredient')

    @property
    def total_calories(self):
        total = 0
        for ing in self.ingredients.all():
            total += (ing.food_item.calories_per_100g * ing.amount_g) / 100
        return round(total)

    def __str__(self):
        return self.name


class MealIngredient(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='ingredients')
    food_item = models.ForeignKey(FoodItem, on_delete=models.PROTECT)
    amount_g = models.FloatField()

    def __str__(self):
        return f"{self.food_item.name} - {self.amount_g}g"


class DietPlan(models.Model):
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('maintenance', 'Maintenance'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    duration_weeks = models.PositiveIntegerField(default=4)
    daily_calories = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_diet_plans'
    )
    assigned_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True,
        related_name='assigned_diet_plans'
    )
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.goal})"


class DietDay(models.Model):
    plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='days')
    day_number = models.PositiveIntegerField()
    title = models.CharField(max_length=100, blank=True)
    meals = models.ManyToManyField(Meal, blank=True)

    class Meta:
        ordering = ['day_number']
        unique_together = ['plan', 'day_number']

    def __str__(self):
        return f"{self.plan.title} - Day {self.day_number}"


class FoodLog(models.Model):
    """Daily food intake tracking."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='food_logs')
    date = models.DateField()
    meal_type = models.CharField(max_length=15, choices=Meal.MEAL_TYPE_CHOICES)
    food_item = models.ForeignKey(FoodItem, on_delete=models.PROTECT)
    amount_g = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'meal_type']

    @property
    def calories(self):
        return round((self.food_item.calories_per_100g * self.amount_g) / 100, 1)

    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.food_item.name}"
