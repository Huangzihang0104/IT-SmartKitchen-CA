from django.http import JsonResponse
from django.shortcuts import render

def home(request):
    return render(request, 'kitchen/home.html')

def login_view(request):
    return render(request, 'kitchen/auth/login.html')

def register_view(request):
    return render(request, 'kitchen/auth/register.html')

def dashboard_view(request):
    return render(request, 'kitchen/inventory/dashboard.html')

def recipe_detail_view(request):
    return render(request, 'kitchen/recipe/detail.html')

def delete_ingredient(request, item_id):
    if request.method == 'POST':
        return JsonResponse({'success': True, 'deleted_id': item_id})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

def mark_recipe_cooked(request):
    if request.method == 'POST':
        return JsonResponse({'success': True, 'message': 'Recipe marked as cooked.'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)