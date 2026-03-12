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

    # 2. Other Page Routes
    path('', views.home, name='home'),  # 默认打开的首页
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('recipes/', views.recipe_list_view, name='recipe_list'),
    path('recipes/detail/', views.recipe_detail_view, name='recipe_detail'),
    path('ingredient/delete/<int:item_id>/', views.delete_ingredient, name='delete_ingredient'),
    path('recipe/mark_cooked/', views.mark_recipe_cooked, name='mark_recipe_cooked'),
]