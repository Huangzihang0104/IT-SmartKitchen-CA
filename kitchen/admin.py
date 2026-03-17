from django.contrib import admin
from .models import Ingredient, Inventory, Recipe, RecipeIngredient, Reminder

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'cook_time', 'difficulty')
    fields = ('name', 'cook_time', 'difficulty', 'instructions', 'image_url')

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(Inventory)
admin.site.register(RecipeIngredient)
admin.site.register(Reminder)