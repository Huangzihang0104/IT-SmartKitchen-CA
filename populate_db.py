import os
import django


# 1. Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartkitchen.settings')
django.setup()

from kitchen.models import Recipe, Ingredient, RecipeIngredient

def populate():
    print("Starting to enter recipe data...")


    recipes_data = [ 
        {
            "name": "Kung Pao Chicken (宫保鸡丁)",
            "time": 25,
            "diff": "medium",
            "img": "https://images.unsplash.com/photo-1525755662778-989d0524087e?w=800",
            "desc": "1. Dice chicken and marinate with soy sauce.\n2. Fry peanuts until crunchy.\n3. Stir-fry chicken with dried chili and sichuan pepper.\n4. Add sauce and peanuts, toss together.",
            "ingredients": [
                {"name": "Chicken Breast", "qty": 300, "unit": "g"},
                {"name": "Peanuts", "qty": 50, "unit": "g"},
                {"name": "Dried Chili", "qty": 10, "unit": "pcs"},
                {"name": "Soy Sauce", "qty": 20, "unit": "ml"}
            ]
        },
        {
            "name": "Mapo Tofu (麻婆豆腐)",
            "time": 20,
            "diff": "medium",
            "img": "https://images.openai.com/static-rsc-3/-SFgY-Dra0gCT6rFYS2KL2UefCPHqjJ0FJd9ogW8pwIfV3vsk06kV5pnerb4KSCa7hCxT2a7ILEGpki5VrIrXPpVunnstQhpIRo91UAYtLQ?purpose=fullsize&v=1",
            "desc": "1. Cut tofu into cubes and blanch in salty water.\n2. Fry minced beef until brown.\n3. Add Doubanjiang (chili bean paste) and stir until red oil appears.\n4. Add tofu and simmer for 5 mins.\n5. Thicken with starch and sprinkle Sichuan pepper powder.",
            "ingredients": [
                {"name": "Soft Tofu", "qty": 1, "unit": "block"},
                {"name": "Minced Beef", "qty": 100, "unit": "g"},
                {"name": "Doubanjiang", "qty": 2, "unit": "spoons"},
                {"name": "Spring Onion", "qty": 1, "unit": "stalk"}
            ]
        },
        {
            "name": "Tomato Scrambled Eggs (番茄炒蛋)",
            "time": 10,
            "diff": "easy",
            "img": "https://images.unsplash.com/photo-1598103442097-8b74394b95c6?w=800",
            "desc": "1. Beat eggs and fry until just set, then remove.\n2. Stir-fry tomato wedges until soft and juicy.\n3. Put eggs back, add salt and a pinch of sugar.\n4. Mix well and serve.",
            "ingredients": [
                {"name": "Egg", "qty": 3, "unit": "pcs"},
                {"name": "Tomato", "qty": 2, "unit": "pcs"},
                {"name": "Sugar", "qty": 5, "unit": "g"}
            ]
        },
        {
            "name": "Stir-fried Broccoli with Beef (西兰花炒牛肉)",
            "time": 20,
            "diff": "medium",
            "img": "https://images.unsplash.com/photo-1534939561126-755ecf1588b0?w=800",
            "desc": "1. Thinly slice beef and marinate with cornstarch.\n2. Blanch broccoli for 2 mins.\n3. Stir-fry beef until no longer pink.\n4. Add broccoli and garlic, season with oyster sauce.",
            "ingredients": [
                {"name": "Beef Flank", "qty": 200, "unit": "g"},
                {"name": "Broccoli", "qty": 1, "unit": "head"},
                {"name": "Garlic", "qty": 3, "unit": "cloves"},
                {"name": "Oyster Sauce", "qty": 15, "unit": "ml"}
            ]
        },
        {
            "name": "Egg Fried Rice (蛋炒饭)",
            "time": 15,
            "diff": "easy",
            "img": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800",
            "desc": "1. Use leftover cold rice.\n2. Fry eggs and break into small pieces.\n3. Add rice and toss on high heat.\n4. Add soy sauce, salt, and lots of chopped spring onions.",
            "ingredients": [
                {"name": "Cooked Rice", "qty": 2, "unit": "bowls"},
                {"name": "Egg", "qty": 2, "unit": "pcs"},
                {"name": "Spring Onion", "qty": 2, "unit": "stalks"}
            ]
        },
        {
            "name": "Classic Beef Stew",
            "time": 90,
            "diff": "medium",
            "img": "https://images.unsplash.com/photo-1547592166-23ac45744acd?w=800",
            "desc": "1. Brown beef cubes in a large pot.\n2. Add chopped potatoes, carrots, and onions.\n3. Pour in beef broth and herbs.\n4. Simmer on low heat for 90 minutes until tender.",
            "ingredients": [
                {"name": "Beef Flank", "qty": 500, "unit": "g"},
                {"name": "Potato", "qty": 2, "unit": "pcs"},
                {"name": "Carrot", "qty": 1, "unit": "pc"},
                {"name": "Onion", "qty": 1, "unit": "pc"}
            ]
        },
        {
            "name": "Honey Garlic Salmon",
            "time": 20,
            "diff": "easy",
            "img": "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=800",
            "desc": "1. Season salmon with salt and pepper.\n2. Pan-fry salmon for 5 mins on each side.\n3. Add honey, garlic, and soy sauce to the pan to glaze.\n4. Serve with steamed broccoli.",
            "ingredients": [
                {"name": "Salmon Fillet", "qty": 200, "unit": "g"},
                {"name": "Honey", "qty": 1, "unit": "spoon"},
                {"name": "Garlic", "qty": 2, "unit": "cloves"}
            ]
        },
        {
            "name": "Avocado Toast",
            "time": 10,
            "diff": "easy",
            "img": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=800",
            "desc": "1. Toast the sourdough bread until golden.\n2. Mash avocado with lemon juice and salt.\n3. Spread on toast and top with a poached egg.\n4. Sprinkle chili flakes.",
            "ingredients": [
                {"name": "Bread", "qty": 1, "unit": "slice"},
                {"name": "Avocado", "qty": 0.5, "unit": "pc"},
                {"name": "Egg", "qty": 1, "unit": "pc"}
            ]
        },
        {
            "name": "Mushroom Risotto",
            "time": 40,
            "diff": "medium",
            "img": "https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=800",
            "desc": "1. Sauté onions and mushrooms in butter.\n2. Add Arborio rice and toast for 2 mins.\n3. Gradually add warm stock one ladle at a time, stirring constantly.\n4. Finish with parmesan cheese.",
            "ingredients": [
                {"name": "Arborio Rice", "qty": 100, "unit": "g"},
                {"name": "Mushroom", "qty": 150, "unit": "g"},
                {"name": "Vegetable Stock", "qty": 300, "unit": "ml"}
            ]
        },
        {
            "name": "Berry Pancake",
            "time": 15,
            "diff": "easy",
            "img": "https://images.unsplash.com/photo-1506084868730-342b1f894491?w=800",
            "desc":"1. Mix flour, milk, and egg into a smooth batter.\n2. Heat a pan and pour small circles.\n3. Cook until bubbles form, then flip.\n4. Top with fresh berries and maple syrup.",
            "ingredients": [
                {"name": "Flour", "qty": 100, "unit": "g"},
                {"name": "Milk", "qty": 150, "unit": "ml"},
                {"name": "Blueberries", "qty": 30, "unit": "g"},
                {"name": "Egg", "qty": 1, "unit": "pc"}
            ]
        }
    ]

    for data in recipes_data:
        # 1. crate recipes
        recipe, created = Recipe.objects.get_or_create(
            name=data["name"],
            defaults={
                "cook_time": data["time"],
                "difficulty": data["diff"],
                "image_url": data["img"],
                "instructions": data["desc"]
            }
        )
        
        # 2. Handling related ingredients
        for ing_item in data["ingredients"]:
            # Obtain or prepare basic ingredients
            ingredient, _ = Ingredient.objects.get_or_create(
                name=ing_item["name"],
                defaults={"unit": ing_item["unit"]}
            )
            # Create a join using a temporary table
            RecipeIngredient.objects.get_or_create(
                recipe=recipe,
                ingredient=ingredient,
                defaults={"quantity_required": ing_item["qty"]}
            )

    print("Complete！")

if __name__ == '__main__':
    populate()