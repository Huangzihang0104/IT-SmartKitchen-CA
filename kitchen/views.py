from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages


# 1. register
def register_view(request):
    # if users clicked "create"
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to SmartKitchen!")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'kitchen/auth/register.html', {'form': form})

# 2. LOGIN 
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome, {username}! ")
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'kitchen/auth/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('login')


def home(request):
    return render(request, 'kitchen/home.html')



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




