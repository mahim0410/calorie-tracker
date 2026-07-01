import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

PROMPT = (
    "Analyze this food image. Return ONLY a raw JSON object with no markdown, no code fences, no extra text:\n"
    '{\n'
    '  "food_name": "detailed name of the food dish/item",\n'
    '  "estimated_calories": <number>,\n'
    '  "confidence": "high"|"medium"|"low",\n'
    '  "portion_description": "approximate portion size",\n'
    '  "protein_g": <number or null>,\n'
    '  "carbs_g": <number or null>,\n'
    '  "fat_g": <number or null>\n'
    '}\n'
    'If you truly cannot identify any food, return '
    '{\"food_name\": \"unknown\", \"estimated_calories\": 0, \"confidence\": \"low\", '
    '\"portion_description\": \"\", \"protein_g\": null, \"carbs_g\": null, \"fat_g\": null}'
)


def analyze_food_image(image_bytes: bytes, filename: str = "image.jpg"):
    """Send a food image to Gemini Vision and parse the nutritional analysis."""
    try:
        mime_type = _get_mime_type(filename)
        response = model.generate_content([
            PROMPT,
            {"mime_type": mime_type, "data": image_bytes},
        ])
        text = response.text.strip()

        # Strip any code fences the model might wrap around
        text = text.removeprefix("```json").removeprefix("```JSON").removeprefix("```").removesuffix("```").strip()

        result = json.loads(text)
        result["success"] = True
        return result

    except json.JSONDecodeError:
        return {
            "success": False,
            "food_name": "unknown",
            "estimated_calories": 0,
            "confidence": "low",
            "error": f"Failed to parse AI response: {text if 'text' in dir() else ''}",
            "raw_response": text if 'text' in dir() else "",
        }
    except Exception as e:
        return {
            "success": False,
            "food_name": "unknown",
            "estimated_calories": 0,
            "confidence": "low",
            "error": str(e),
        }


def _get_mime_type(filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "jpg"
    mimes = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
        "heic": "image/heic",
        "heif": "image/heif",
    }
    return mimes.get(ext, "image/jpeg")
