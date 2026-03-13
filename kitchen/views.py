from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm


def home(request):
    return render(request, 'kitchen/home.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Logged in successfully.')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'kitchen/auth/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'kitchen/auth/register.html', {'form': form})


def dashboard_view(request):
    return render(request, 'kitchen/inventory/dashboard.html')


def recipe_list_view(request):
    return render(request, 'kitchen/recipe/list.html')


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