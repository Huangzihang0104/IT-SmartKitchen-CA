"""
URL configuration for the kitchen app.

All URLs use named routes so templates can reference them via
{% url 'route_name' %} instead of hard-coded paths.
"""

from django.urls import path

from . import views

urlpatterns = [
    # Home page
    path('', views.home, name='home'),

    # Authentication
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Inventory dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Recipes
    path('recipes/', views.recipe_list_view, name='recipe_list'),
    path('recipes/detail/', views.recipe_detail_view, name='recipe_detail'),

    # AJAX endpoints for inventory CRUD
    path('ingredients/add/', views.add_ingredient, name='add_ingredient'),
    path('ingredients/edit/<int:item_id>/', views.edit_ingredient, name='edit_ingredient'),
    path('ingredients/delete/<int:item_id>/', views.delete_ingredient, name='delete_ingredient'),

    # AJAX endpoint for recipe actions
    path('recipe/mark-cooked/', views.mark_recipe_cooked, name='mark_recipe_cooked'),
]
