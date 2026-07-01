import os
import requests
from dotenv import load_dotenv

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"


def search_food(query: str, page_size: int = 10):
    """Search USDA FoodData Central for foods matching the query."""
    url = f"{USDA_BASE_URL}/foods/search"
    params = {
        "api_key": USDA_API_KEY,
        "query": query,
        "pageSize": page_size,
        "dataType": ["Foundation", "SR Legacy", "Branded"],
        "requireAllWords": "true",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for food in data.get("foods", []):
        nutrients = {}
        for nutrient in food.get("foodNutrients", []):
            name = nutrient.get("nutrientName") or nutrient.get("name", "")
            value = nutrient.get("value")
            unit_name = nutrient.get("unitName", "")

            # Normalize common nutrient names
            if "Energy" in name and "kcal" not in name:
                name = "Energy (kcal)"
            if "Total lipid" in name or "Total Fat" in name:
                name = "Total Fat"
            if "Carbohydrate, by difference" in name:
                name = "Total Carbohydrate"

            if name and value is not None:
                nutrients[name] = {"value": value, "unit": unit_name}

        def get_nutrient(*names):
            for n in names:
                if n in nutrients:
                    return nutrients[n]["value"]
            return None

        results.append({
            "fdc_id": food.get("fdcId"),
            "name": food.get("description", "Unknown"),
            "brand": food.get("brandName") or "",
            "calories": get_nutrient("Energy (kcal)", "Energy"),
            "protein": get_nutrient("Protein"),
            "carbs": get_nutrient("Total Carbohydrate", "Carbohydrate, by difference"),
            "fat": get_nutrient("Total Fat", "Total lipid (fat)"),
            "serving_size": (
                f"{food.get('servingSize', '')} {food.get('servingSizeUnit', 'g')}"
                if food.get("servingSize")
                else "per 100g"
            ),
            "nutrients": nutrients,
        })

    return results


def get_food_details(fdc_id: int):
    """Get full details for a food by its FDC ID."""
    url = f"{USDA_BASE_URL}/food/{fdc_id}"
    params = {"api_key": USDA_API_KEY}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()
