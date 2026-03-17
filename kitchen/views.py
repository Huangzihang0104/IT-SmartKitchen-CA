from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Inventory, Ingredient, Recipe
from .forms import CustomUserCreationForm, InventoryForm




# Core Authentication Logic (M1)
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to SmartKitchen!")')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'kitchen/auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome, {username}!")
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'kitchen/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('login')

def home(request):
    return render(request, 'kitchen/home.html')

# 2. Inventory Management Logic M2/M3
# (Read) - Take a look inside own fridge
@login_required(login_url='login')
def dashboard_view(request):
    user_inventory = Inventory.objects.filter(user=request.user).order_by('expiry_date')
    form = InventoryForm() 
    return render(request, 'kitchen/inventory/dashboard.html', {'inventory_list': user_inventory, 'form': form})

# (Create) - Add ingredients to the fridge
@login_required(login_url='login')
def add_inventory_view(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            # 1.  When receive the names of ingredients entered by the user, automatically capitalize the first letter
            raw_name = form.cleaned_data.get('ingredient_name').strip()
            formatted_name = raw_name.capitalize() 
            unit = form.cleaned_data.get('unit').strip() if form.cleaned_data.get('unit') else ""

            # 2. Look it up in the dictionary; if it’s not there, create a new entry.
            ingredient_obj, created = Ingredient.objects.get_or_create(
                name=formatted_name,
                defaults={'unit': unit}
            )

            # 3. Save this ingredient and quantity to the user's fridge
            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.ingredient = ingredient_obj 
            new_item.save()
            
            return redirect('dashboard')
    return redirect('dashboard')

# (Update) - Change the quantity or date of the ingredients
@login_required(login_url='login')
def edit_inventory_view(request, item_id):
    item = get_object_or_404(Inventory, id=item_id, user=request.user)
    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = InventoryForm(instance=item)
    return render(request, 'kitchen/inventory/edit_inventory.html', {'form': form, 'item': item})

# (Delete) - Throw away expired food
@login_required(login_url='login')
def delete_ingredient(request, item_id):
    if request.method == 'POST':
        try:
            item = Inventory.objects.get(id=item_id, user=request.user)
            item.delete()
            return JsonResponse({'success': True, 'deleted_id': item_id})
        except Inventory.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)

# 3. M4: Intelligent Recipe Matching
@login_required(login_url='login')
def recipe_list_view(request):
    # 1. Get the list of base IDs for all ingredients in the current user's refrigerator
    user_inventory = Inventory.objects.filter(user=request.user)
    user_ingredient_ids = user_inventory.values_list('ingredient_id', flat=True)

    # 2.Retrieve all the recipes from the database
    all_recipes = Recipe.objects.all()

    recipe_data_list = []

    # 3. Rate the recipe 
    for recipe in all_recipes:
        required_items = recipe.required_ingredients.all()
        total_required = required_items.count()

        if total_required == 0:
            match_percentage = 0
            have_count = 0
        else:
            have_count = 0
            # Check if the user has all the ingredients needed for this dish in their refrigerator.
            for req in required_items:
                if req.ingredient.id in user_ingredient_ids:
                    have_count += 1

            # Calculate the percentage and convert it to a whole number
            match_percentage = int((have_count / total_required) * 100)
        # Bundle the information about this dish, its match rate, and the quantity needed
        recipe_data_list.append({
            'recipe' : recipe,
            'match_percentage' : match_percentage,
            'total_required' : total_required,
            'have_count' : have_count,
            'missing_count' : total_required - have_count
        })

    # 4. Sort by relevance from highest to lowest
    recipe_data_list.sort(key=lambda x : x['match_percentage'], reverse=True)

    return render(request, 'kitchen/recipe/list.html', {'recipe_data_list': recipe_data_list})


@login_required(login_url='login')
def recipe_detail_view(request, recipe_id):
    # Retrieve this dish from the database using its ID
    recipe = get_object_or_404(Recipe, id=recipe_id)
    # pack the ingredients needed for this dish
    ingredients = recipe.required_ingredients.all()
    return render(request, 'kitchen/recipe/detail.html', {'recipe': recipe, 'ingredients': ingredients})

def delete_ingredient(request, item_id):
    if request.method == 'POST':
        return JsonResponse({'success': True, 'deleted_id': item_id})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


def mark_recipe_cooked(request):
    if request.method == 'POST':
        return JsonResponse({'success': True, 'message': 'Recipe marked as cooked.'})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)