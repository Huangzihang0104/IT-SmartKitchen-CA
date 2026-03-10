from django.contrib import admin
from .models import Ingredient, Inventory, Recipe, RecipeIngredient, Reminder
# Register your models here.
admin.site.register(Ingredient)
admin.site.register(Inventory)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(Reminder)