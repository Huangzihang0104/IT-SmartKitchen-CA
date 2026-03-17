"""
Views for the SmartKitchen application.

Handles page rendering and AJAX endpoints for:
- User authentication (register, login, logout)
- Inventory dashboard (list, add, edit, delete ingredients)
- Recipe browsing (list, detail, mark-as-cooked)

Design note: Views pass context dictionaries to templates so that
templates can use {% for %} loops and {{ variable }} tags rather
than hard-coding HTML content. This follows Django best practices
for separation of concerns between views and templates.
"""

import json
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm


# ── Helper: compute expiry status from a date string ──

def _expiry_status(expiry_str):
    """Return (css_class, label) based on how close the expiry date is."""
    today = date.today()
    try:
        expiry = date.fromisoformat(expiry_str)
    except (ValueError, TypeError):
        return ('secondary', 'Unknown')

    diff = (expiry - today).days
    if diff < 0:
        return ('danger', 'Expired')
    elif diff <= 3:
        return ('warning', 'Expiring Soon')
    else:
        return ('success', 'Fresh')


# ── Helper: build demo inventory data ──
# TODO: Replace with real database queries once models are populated.
# The template structure ({% for item in inventory_items %}) will
# work identically with either demo data or real QuerySet results.

def _get_demo_inventory():
    """Return a list of demo ingredient dicts for template rendering."""
    today = date.today()
    items = [
        {
            'id': 1,
            'name': 'Milk',
            'quantity': 1,
            'unit': 'bottle',
            'expiry_date': str(today + timedelta(days=2)),
        },
        {
            'id': 2,
            'name': 'Eggs',
            'quantity': 6,
            'unit': 'pcs',
            'expiry_date': str(today + timedelta(days=7)),
        },
        {
            'id': 3,
            'name': 'Spinach',
            'quantity': 200,
            'unit': 'g',
            'expiry_date': str(today - timedelta(days=1)),
        },
        {
            'id': 4,
            'name': 'Pasta',
            'quantity': 500,
            'unit': 'g',
            'expiry_date': str(today + timedelta(days=60)),
        },
        {
            'id': 5,
            'name': 'Mushrooms',
            'quantity': 150,
            'unit': 'g',
            'expiry_date': str(today + timedelta(days=3)),
        },
    ]
    # Enrich each item with computed status fields
    for item in items:
        cls, label = _expiry_status(item['expiry_date'])
        item['status_class'] = cls
        item['status_label'] = label
    return items


def _get_demo_recipes():
    """Return demo recipe data for the recipe list and detail pages."""
    return {
        'featured': {
            'name': 'Creamy Mushroom Pasta',
            'thumb': 'pasta',
            'cook_time': 25,
            'difficulty': 'Easy',
            'dietary': 'Vegetarian',
            'match': 85,
            'description': 'A quick, creamy pasta dish that makes excellent use of mushrooms, garlic, and ingredients already in your kitchen.',
        },
        'recipes': [
            {
                'name': 'Spinach Omelette',
                'thumb': 'omelette',
                'cook_time': 15,
                'difficulty': 'Easy',
                'dietary': 'High Protein',
                'match': 92,
                'label': 'Quick & fresh',
                'description': 'An efficient way to use eggs and spinach before they expire.',
                'badge': 'Spinach expiring',
                'badge_class': 'danger',
                'tags': 'quick protein expiring',
            },
            {
                'name': 'Garlic Fried Rice',
                'thumb': 'rice',
                'cook_time': 20,
                'difficulty': 'Medium',
                'dietary': 'Dairy Free',
                'match': 78,
                'label': 'Pantry friendly',
                'description': 'A flexible recipe ideal for leftover rice and quick weeknight cooking.',
                'badge': 'Good pantry fit',
                'badge_class': 'success',
                'tags': 'quick pantry',
            },
            {
                'name': 'Tomato Pasta Bake',
                'thumb': 'bake',
                'cook_time': 30,
                'difficulty': 'Easy',
                'dietary': 'Vegetarian',
                'match': 74,
                'label': 'Comfort food',
                'description': 'A simple baked pasta dish that works well with staple cupboard ingredients.',
                'badge': 'Great for leftovers',
                'badge_class': 'warning',
                'tags': 'vegetarian pantry',
            },
        ],
    }


# ── Page views ──

def home(request):
    """Landing page — adapts hero content based on authentication state."""
    inventory = _get_demo_inventory()
    context = {
        'total_ingredients': len(inventory),
        'total_recipes': len(_get_demo_recipes()['recipes']),
    }
    return render(request, 'kitchen/home.html', context)


def register_view(request):
    """User registration with custom form that includes email field."""
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


def login_view(request):
    """User login using Django's built-in AuthenticationForm."""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, 'Logged in successfully.')
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'kitchen/auth/login.html', {'form': form})


@require_POST
def logout_view(request):
    """Logout: only accepts POST requests (CSRF-protected)."""
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Inventory dashboard — passes ingredient list to template for rendering."""
    context = {
        'inventory_items': _get_demo_inventory(),
    }
    return render(request, 'kitchen/inventory/dashboard.html', context)


def recipe_list_view(request):
    """Recipe recommendations — passes recipe list and featured recipe to template."""
    data = _get_demo_recipes()
    context = {
        'featured_recipe': data['featured'],
        'recipes': data['recipes'],
    }
    return render(request, 'kitchen/recipe/list.html', context)


def recipe_detail_view(request):
    """Recipe detail page — shows ingredients, instructions, and cook action."""
    context = {
        'recipe': {
            'name': 'Creamy Mushroom Pasta',
            'thumb': 'pasta',
            'cook_time': 25,
            'difficulty': 'Easy',
            'match': 80,
            'ingredients': [
                {'name': 'Pasta', 'quantity': 200, 'unit': 'g', 'status': 'In Stock', 'status_class': 'success'},
                {'name': 'Mushrooms', 'quantity': 150, 'unit': 'g', 'status': 'In Stock', 'status_class': 'success'},
                {'name': 'Cream', 'quantity': 100, 'unit': 'ml', 'status': 'Missing', 'status_class': 'danger'},
                {'name': 'Garlic', 'quantity': 2, 'unit': 'cloves', 'status': 'In Stock', 'status_class': 'success'},
            ],
            'steps': [
                'Boil the pasta until al dente.',
                'Sauté garlic and mushrooms in a pan.',
                'Add cream and stir until smooth.',
                'Mix in the cooked pasta and serve hot.',
            ],
        },
    }
    return render(request, 'kitchen/recipe/detail.html', context)


# ── AJAX endpoints ──

@login_required
def add_ingredient(request):
    """AJAX endpoint: add a new ingredient to the user's inventory."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)

        name = data.get('name', '').strip()
        quantity = data.get('quantity')
        unit = data.get('unit', 'pcs')
        expiry_date = data.get('expiry_date')

        # Basic server-side validation
        if not name or not quantity or not expiry_date:
            return JsonResponse({'success': False, 'message': 'All fields are required.'}, status=400)

        # TODO: Save to database via Inventory.objects.create(...)
        # For now, return success with a generated ID
        return JsonResponse({
            'success': True,
            'id': 'new-' + str(hash(name) % 10000),
            'message': name + ' added to inventory.',
        })

    return JsonResponse({'success': False, 'message': 'Only POST allowed.'}, status=405)


@login_required
def edit_ingredient(request, item_id):
    """AJAX endpoint: update an existing ingredient's details."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)

        # TODO: Lookup Inventory object by item_id and update fields
        return JsonResponse({
            'success': True,
            'message': 'Ingredient updated.',
        })

    return JsonResponse({'success': False, 'message': 'Only POST allowed.'}, status=405)


@login_required
def delete_ingredient(request, item_id):
    """AJAX endpoint: delete an ingredient from inventory."""
    if request.method == 'POST':
        # TODO: Lookup and delete Inventory object by item_id
        return JsonResponse({'success': True, 'deleted_id': item_id})
    return JsonResponse({'success': False, 'message': 'Only POST allowed.'}, status=400)


@login_required
def mark_recipe_cooked(request):
    """AJAX endpoint: mark a recipe as cooked, decrement inventory quantities."""
    if request.method == 'POST':
        # TODO: Decrement ingredient quantities in Inventory based on recipe
        return JsonResponse({
            'success': True,
            'message': 'Recipe marked as cooked. Inventory updated.',
        })
    return JsonResponse({'success': False, 'message': 'Only POST allowed.'}, status=400)
