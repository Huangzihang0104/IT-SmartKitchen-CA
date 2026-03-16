from django.contrib import admin
from django.urls import include, path
from kitchen import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kitchen.urls')),


    # 1. User Authentication Module
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 2. M2/M3 Inventory Management Core Routing
    path('', views.home, name='home'),  # open the default home page
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('inventory/add/', views.add_inventory_view, name='add_inventory'), # Add Ingredients page
    path('inventory/edit/<int:item_id>/', views.edit_inventory_view, name='edit_inventory'), # Edit Ingredients Page
    path('ingredient/delete/<int:item_id>/', views.delete_ingredient, name='delete_ingredient'),

    # Other page routes
    path('recipes/', views.recipe_list_view, name='recipe_list'),
    path('recipes/detail/', views.recipe_detail_view, name='recipe_detail'),
    path('recipe/mark_cooked/', views.mark_recipe_cooked, name='mark_recipe_cooked'),
]