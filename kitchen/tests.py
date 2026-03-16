from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Ingredient, Inventory, Recipe, RecipeIngredient


class PageTest(TestCase):

    def test_home_page_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)


class RegisterPageTest(TestCase):

    def test_register_page_loads(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )

        self.assertEqual(user.username, "testuser")

class IngredientModelTest(TestCase):

    def test_create_ingredient(self):
        ingredient = Ingredient.objects.create(
            name="Milk",
            unit="ml",
            base_unit_qty=1
        )

        self.assertEqual(ingredient.name, "Milk")


class InventoryModelTest(TestCase):

    def test_inventory_link_user_and_ingredient(self):

        user = User.objects.create_user(
            username="testuser",
            password="password123"
        )

        ingredient = Ingredient.objects.create(
            name="Egg",
            unit="pcs",
            base_unit_qty=1
        )

        inventory = Inventory.objects.create(
            user=user,
            ingredient=ingredient,
            purchase_date="2026-03-01",
            expiry_date="2026-03-10",
            quantity=5
        )

        self.assertEqual(inventory.quantity, 5)
