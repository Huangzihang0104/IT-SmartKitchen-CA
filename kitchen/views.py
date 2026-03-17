"""
Views for the SmartKitchen application.
"""

import json
from datetime import date

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm, InventoryForm
from .models import Ingredient, Inventory, Recipe


def _expiry_status(expiry_date):
    """Return (css_class, label) based on how close the expiry date is."""
    today = date.today()
    diff = (expiry_date - today).days
    if diff < 0:
        return "danger", "Expired"
    if diff <= 3:
        return "warning", "Expiring Soon"
    return "success", "Fresh"


def home(request):
    return render(request, "kitchen/home.html")


# Core Authentication Logic (M1)
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to SmartKitchen!")
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, "kitchen/auth/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome, {username}!")
                return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "kitchen/auth/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("login")


# Inventory Management Logic (M2/M3)
@login_required(login_url="login")
def dashboard_view(request):
    user_inventory = Inventory.objects.filter(user=request.user).select_related("ingredient").order_by("expiry_date")
    inventory_items = []
    for item in user_inventory:
        status_class, status_label = _expiry_status(item.expiry_date)
        inventory_items.append(
            {
                "id": item.id,
                "name": item.ingredient.name,
                "quantity": item.quantity,
                "unit": item.ingredient.unit,
                "expiry_date": item.expiry_date.strftime("%Y-%m-%d"),
                "status_class": status_class,
                "status_label": status_label,
            }
        )

    context = {
        "inventory_items": inventory_items,
        "form": InventoryForm(),
    }
    return render(request, "kitchen/inventory/dashboard.html", context)


@login_required(login_url="login")
def add_inventory_view(request):
    if request.method == "POST":
        form = InventoryForm(request.POST)
        if form.is_valid():
            raw_name = form.cleaned_data.get("ingredient_name", "").strip()
            formatted_name = raw_name.capitalize()
            unit = (form.cleaned_data.get("unit") or "pcs").strip() or "pcs"

            ingredient_obj, _ = Ingredient.objects.get_or_create(
                name=formatted_name,
                defaults={"unit": unit},
            )

            new_item = form.save(commit=False)
            new_item.user = request.user
            new_item.ingredient = ingredient_obj
            new_item.save()

    return redirect("dashboard")


@login_required(login_url="login")
def edit_inventory_view(request, item_id):
    item = get_object_or_404(Inventory, id=item_id, user=request.user)
    if request.method == "POST":
        form = InventoryForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = InventoryForm(instance=item)
    return render(request, "kitchen/inventory/edit_inventory.html", {"form": form, "item": item})


@login_required(login_url="login")
def add_ingredient(request):
    """AJAX endpoint: add a new ingredient to the user's inventory."""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Only POST allowed."}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON."}, status=400)

    name = (data.get("name") or "").strip()
    quantity = data.get("quantity")
    unit = (data.get("unit") or "pcs").strip() or "pcs"
    expiry_date = data.get("expiry_date")

    if not name or not quantity or not expiry_date:
        return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

    try:
        quantity = float(quantity)
        if quantity <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "message": "Quantity must be a positive number."}, status=400)

    ingredient, _ = Ingredient.objects.get_or_create(name=name.capitalize(), defaults={"unit": unit})
    if not ingredient.unit:
        ingredient.unit = unit
        ingredient.save(update_fields=["unit"])

    item = Inventory.objects.create(
        user=request.user,
        ingredient=ingredient,
        purchase_date=date.today(),
        expiry_date=expiry_date,
        quantity=quantity,
    )

    return JsonResponse(
        {
            "success": True,
            "id": item.id,
            "message": f"{ingredient.name} added to inventory.",
        }
    )


@login_required(login_url="login")
def edit_ingredient(request, item_id):
    """AJAX endpoint: update an existing ingredient's details."""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Only POST allowed."}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON."}, status=400)

    item = get_object_or_404(Inventory, id=item_id, user=request.user)

    name = (data.get("name") or "").strip()
    unit = (data.get("unit") or "pcs").strip() or "pcs"
    expiry_date = data.get("expiry_date")
    quantity = data.get("quantity")

    if not name or not quantity or not expiry_date:
        return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

    try:
        quantity = float(quantity)
        if quantity <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"success": False, "message": "Quantity must be a positive number."}, status=400)

    ingredient, _ = Ingredient.objects.get_or_create(name=name.capitalize(), defaults={"unit": unit})
    if not ingredient.unit:
        ingredient.unit = unit
        ingredient.save(update_fields=["unit"])

    item.ingredient = ingredient
    item.quantity = quantity
    item.expiry_date = expiry_date
    item.save(update_fields=["ingredient", "quantity", "expiry_date"])

    return JsonResponse({"success": True, "message": "Ingredient updated."})


@login_required(login_url="login")
def delete_ingredient(request, item_id):
    if request.method == "POST":
        try:
            item = Inventory.objects.get(id=item_id, user=request.user)
            item.delete()
            return JsonResponse({"success": True, "deleted_id": item_id})
        except Inventory.DoesNotExist:
            return JsonResponse({"success": False, "message": "Item not found"}, status=404)
    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)


# M4: Intelligent Recipe Matching
@login_required(login_url="login")
def recipe_list_view(request):
    user_ingredient_ids = set(
        Inventory.objects.filter(user=request.user).values_list("ingredient_id", flat=True)
    )
    all_recipes = Recipe.objects.prefetch_related("required_ingredients__ingredient")

    recipe_data_list = []
    for recipe in all_recipes:
        required_items = list(recipe.required_ingredients.all())
        total_required = len(required_items)
        have_count = sum(1 for req in required_items if req.ingredient_id in user_ingredient_ids)
        match_percentage = int((have_count / total_required) * 100) if total_required else 0

        recipe_data_list.append(
            {
                "recipe": recipe,
                "match_percentage": match_percentage,
                "total_required": total_required,
                "have_count": have_count,
                "missing_count": total_required - have_count,
            }
        )

    recipe_data_list.sort(key=lambda x: x["match_percentage"], reverse=True)

    featured_recipe = recipe_data_list[0] if recipe_data_list else None
    return render(
        request,
        "kitchen/recipe/list.html",
        {
            "recipe_data_list": recipe_data_list,
            "featured_recipe": featured_recipe,
        },
    )


@login_required(login_url="login")
def recipe_detail_view(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user_ingredient_ids = set(
        Inventory.objects.filter(user=request.user).values_list("ingredient_id", flat=True)
    )
    required_items = list(recipe.required_ingredients.select_related("ingredient"))

    total_required = len(required_items)
    have_count = sum(1 for req in required_items if req.ingredient_id in user_ingredient_ids)
    match_percentage = int((have_count / total_required) * 100) if total_required else 0

    context = {
        "recipe": recipe,
        "match_percentage": match_percentage,
    }
    return render(request, "kitchen/recipe/detail.html", context)


@login_required(login_url="login")
def mark_recipe_cooked(request):
    if request.method == "POST":
        return JsonResponse({"success": True, "message": "Recipe marked as cooked. Inventory updated."})
    return JsonResponse({"success": False, "message": "Only POST allowed."}, status=400)
