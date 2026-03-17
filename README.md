SmartKitchen Project

A Django-based smart kitchen application for managing recipes and ingredients.

## Quick Start (For Team Members)

To ensure everyone is working with the same data and UI, follow these steps:

## 1. Sync the Latest Code
```bash
git pull origin main
```
## 2. Environment Setup
Make sure you have your virtual environment activated:

## 3. Database & Data Synchronization 
If you see an empty page or "0/0 Ingredients", run the following to load the pre-configured recipes:

Bash
### Step 1: Apply any new database migrations
```bash
python manage.py migrate
```
### Step 2: Load seed data (Recipes & Ingredients)
```bash
python manage.py loaddata initial_data.json
```
Alternatively, you can run
```bash
python populate_db.py to generate the data
```
via script.

# Project Structure：
kitchen/: Main app logic

models.py: Database schema (Recipe, Ingredient, RecipeIngredient)

views.py: Logic for filtering and matching recipes

templates/: HTML templates

populate_db.py: Automation script for data entry

initial_data.json: Database seed data
