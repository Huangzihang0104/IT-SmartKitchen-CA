from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('recipe/', views.recipe_list_view, name='recipe_list'),
    path('recipe/detail/', views.recipe_detail_view, name='recipe_detail'),

    path('ingredients/delete/<int:item_id>/', views.delete_ingredient, name='delete_ingredient'),
    path('recipe/mark-cooked/', views.mark_recipe_cooked, name='mark_recipe_cooked'),
]