from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.
# 1. ingredient
class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    shelf_life = models.IntegerField(help_text="Default shelf life in days", null=True, blank=True)
    category = models.CharField(max_length=64, null=True, blank=True)
    unit = models.CharField(max_length=16, verbose_name="Unit (e.g. , g, ml)")
    base_unit_qty = models.FloatField(default=1.0)
    image_url = models.CharField(max_length=256, null=True, blank=True)

    def __str__(self):
        return self.name 
    
# 2. inventory
class Inventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventories')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    purchase_date = models.DateField()
    expiry_date = models.DateField()
    quantity = models.FloatField()
    is_notified = models.BooleanField(default=False)

    @property
    def name(self):
        return self.ingredient.name
    
    @property
    def unit(self):
        return self.ingredient.unit

    @property
    def status_label(self):
        today = date.today()
        if self.expiry_date < today:
            return "Expired"
        days_left = (self.expiry_date - today).days
        if days_left <= 3:
            return "Expiring Soon"
        return "Fresh"
    
    @property
    def status_class(self):
        today = date.today()
        if self.expiry_date < today:
            return "danger"
        days_left = (self.expiry_date - today).days
        if days_left <= 3:
            return "warning"
        return "success"

    def __str__(self):
        return f"{self.user.username}'s {self.ingredient.name}"
    
# 3. recipe
class Recipe(models.Model):
    name = models.CharField(max_length=128)
    instructions = models.TextField()
    difficulty = models.CharField(max_length=32, null=True, blank=True)
    cook_time = models.IntegerField(help_text="Cook time in minutes")
    image_url = models.URLField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return self.name

# 4. RecipeIngredient 
class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='required_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity_required = models.FloatField()

    def __str__(self):
        return f"{self.recipe.name} requires {self.quantity_required} of {self.ingredient.name}"

# 5. Reminder 表 
class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()

    def __str__(self):
        return f"Reminder for {self.user.username}: {self.inventory.ingredient.name}"