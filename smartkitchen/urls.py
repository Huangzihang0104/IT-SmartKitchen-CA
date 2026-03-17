"""
Root URL configuration for the smartkitchen project.

Routes are defined in kitchen/urls.py and included here.
This avoids duplication and keeps URL definitions in one place.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kitchen.urls')),
]
