import base64
import json
import os
import sqlite3
from datetime import date, datetime
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Calorie Tracker")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "calories.db"
SETTINGS_PATH = BASE_DIR / "settings.json"
FOOD_DB_PATH = BASE_DIR / "food_db.json"


# ── Database ──────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                food_name TEXT NOT NULL,
                calories INTEGER NOT NULL,
                protein REAL DEFAULT 0,
                carbs REAL DEFAULT 0,
                fat REAL DEFAULT 0,
                portion TEXT DEFAULT '',
                image_path TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)


init_db()


# ── Settings ──────────────────────────────────────────────
def load_settings():
    if SETTINGS_PATH.exists():
        return json.loads(SETTINGS_PATH.read_text())
    return {"api_key": "", "daily_goal": 2200}


def save_settings(data):
    SETTINGS_PATH.write_text(json.dumps(data, indent=2))


# ── Food database for offline estimates ───────────────────
def load_food_db():
    if FOOD_DB_PATH.exists():
        return json.loads(FOOD_DB_PATH.read_text())
    # Default food database with approximate calories per 100g
    defaults = {
        "rice": {"cal_per_100g": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
        "white rice": {"cal_per_100g": 130, "protein": 2.7, "carbs": 28, "fat": 0.3},
        "biriyani": {"cal_per_100g": 190, "protein": 8, "carbs": 25, "fat": 6},
        "biryani": {"cal_per_100g": 190, "protein": 8, "carbs": 25, "fat": 6},
        "chicken": {"cal_per_100g": 165, "protein": 31, "carbs": 0, "fat": 3.6},
        "chicken breast": {"cal_per_100g": 165, "protein": 31, "carbs": 0, "fat": 3.6},
        "chicken curry": {"cal_per_100g": 180, "protein": 18, "carbs": 6, "fat": 10},
        "beef": {"cal_per_100g": 250, "protein": 26, "carbs": 0, "fat": 15},
        "beef curry": {"cal_per_100g": 220, "protein": 20, "carbs": 5, "fat": 14},
        "fish": {"cal_per_100g": 140, "protein": 20, "carbs": 0, "fat": 6},
        "fish curry": {"cal_per_100g": 160, "protein": 18, "carbs": 5, "fat": 8},
        "dal": {"cal_per_100g": 110, "protein": 8, "carbs": 19, "fat": 0.5},
        "daal": {"cal_per_100g": 110, "protein": 8, "carbs": 19, "fat": 0.5},
        "lentils": {"cal_per_100g": 116, "protein": 9, "carbs": 20, "fat": 0.4},
        "roti": {"cal_per_100g": 297, "protein": 9, "carbs": 62, "fat": 1.2},
        "chapati": {"cal_per_100g": 297, "protein": 9, "carbs": 62, "fat": 1.2},
        "paratha": {"cal_per_100g": 350, "protein": 7, "carbs": 45, "fat": 16},
        "naan": {"cal_per_100g": 262, "protein": 9, "carbs": 46, "fat": 5},
        "bread": {"cal_per_100g": 265, "protein": 9, "carbs": 49, "fat": 3.2},
        "egg": {"cal_per_100g": 155, "protein": 13, "carbs": 1.1, "fat": 11},
        "omelette": {"cal_per_100g": 180, "protein": 13, "carbs": 2, "fat": 13},
        "vegetables": {"cal_per_100g": 40, "protein": 2, "carbs": 6, "fat": 0.3},
        "salad": {"cal_per_100g": 25, "protein": 1.5, "carbs": 4, "fat": 0.2},
        "banana": {"cal_per_100g": 89, "protein": 1.1, "carbs": 23, "fat": 0.3},
        "apple": {"cal_per_100g": 52, "protein": 0.3, "carbs": 14, "fat": 0.2},
        "orange": {"cal_per_100g": 47, "protein": 0.9, "carbs": 12, "fat": 0.1},
        "mango": {"cal_per_100g": 60, "protein": 0.8, "carbs": 15, "fat": 0.4},
        "milk": {"cal_per_100g": 42, "protein": 3.4, "carbs": 5, "fat": 1},
        "tea": {"cal_per_100g": 30, "protein": 0, "carbs": 5, "fat": 0},
        "coffee": {"cal_per_100g": 2, "protein": 0.1, "carbs": 0, "fat": 0},
        "pizza": {"cal_per_100g": 266, "protein": 11, "carbs": 33, "fat": 10},
        "burger": {"cal_per_100g": 295, "protein": 17, "carbs": 30, "fat": 14},
        "pasta": {"cal_per_100g": 131, "protein": 5, "carbs": 25, "fat": 1.1},
        "noodles": {"cal_per_100g": 138, "protein": 4.5, "carbs": 25, "fat": 2},
        "sandwich": {"cal_per_100g": 250, "protein": 12, "carbs": 30, "fat": 10},
        "idli": {"cal_per_100g": 70, "protein": 2, "carbs": 14, "fat": 0.2},
        "dosa": {"cal_per_100g": 210, "protein": 4, "carbs": 35, "fat": 6},
        "sambar": {"cal_per_100g": 55, "protein": 3, "carbs": 9, "fat": 1},
        "paneer": {"cal_per_100g": 265, "protein": 18, "carbs": 1.2, "fat": 21},
        "yogurt": {"cal_per_100g": 61, "protein": 3.5, "carbs": 4.7, "fat": 3.3},
        "ice cream": {"cal_per_100g": 207, "protein": 3.5, "carbs": 24, "fat": 11},
        "chocolate": {"cal_per_100g": 546, "protein": 4.9, "carbs": 61, "fat": 31},
        "cake": {"cal_per_100g": 350, "protein": 5, "carbs": 50, "fat": 15},
        "french fries": {"cal_per_100g": 312, "protein": 3.4, "carbs": 41, "fat": 15},
        "samosa": {"cal_per_100g": 280, "protein": 6, "carbs": 30, "fat": 16},
        "pakora": {"cal_per_100g": 350, "protein": 5, "carbs": 25, "fat": 26},
        "haleem": {"cal_per_100g": 160, "protein": 12, "carbs": 16, "fat": 6},
        "nihari": {"cal_per_100g": 180, "protein": 15, "carbs": 3, "fat": 12},
        "shrimp": {"cal_per_100g": 99, "protein": 24, "carbs": 0.2, "fat": 0.3},
        "mutton": {"cal_per_100g": 230, "protein": 25, "carbs": 0, "fat": 14},
    }
    FOOD_DB_PATH.write_text(json.dumps(defaults, indent=2))
    return defaults


food_db = load_food_db()


def estimate_from_db(food_name: str, portion_g: int = 300) -> dict:
    """Try to match food name with local database."""
    name_lower = food_name.lower().strip()
    # Try exact match first
    if name_lower in food_db:
        item = food_db[name_lower]
        factor = portion_g / 100
        return {
            "food_name": food_name,
            "calories": round(item["cal_per_100g"] * factor),
            "protein": round(item["protein"] * factor, 1),
            "carbs": round(item["carbs"] * factor, 1),
            "fat": round(item["fat"] * factor, 1),
            "portion": f"~{portion_g}g",
            "source": "local_db",
        }
    # Partial match
    for key, item in food_db.items():
        if key in name_lower or name_lower in key:
            factor = portion_g / 100
            return {
                "food_name": food_name,
                "calories": round(item["cal_per_100g"] * factor),
                "protein": round(item["protein"] * factor, 1),
                "carbs": round(item["carbs"] * factor, 1),
                "fat": round(item["fat"] * factor, 1),
                "portion": f"~{portion_g}g",
                "source": "local_db",
            }
    return None


# ── API: Analyze food image ───────────────────────────────
@app.post("/api/analyze")
async def analyze_food(image: UploadFile = File(...)):
    settings = load_settings()
    api_key = settings.get("api_key", "")

    if not api_key:
        raise HTTPException(status_code=400, detail="API key not set. Go to Settings and add your OpenRouter API key.")

    # Read and encode image
    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    content_type = image.content_type or "image/jpeg"

    # Call OpenRouter vision API
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Calorie Tracker",
            },
            json={
                "model": "google/gemini-2.5-flash",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "Analyze this food image. Return ONLY a valid JSON object (no markdown, no code blocks) with these exact fields:\n"
                                    '{"food_name": "what food(s) you see", "total_calories": an_integer,\n'
                                    '"protein_g": a_number, "carbs_g": a_number, "fat_g": a_number,\n'
                                    '"portion_estimate": "e.g. ~300g or 1 plate"}\n\n'
                                    "IMPORTANT: total_calories must be an integer. protein_g, carbs_g, fat_g can have 1 decimal.\n"
                                    "For Bangladeshi/South Asian food, use these reference values:\n"
                                    "- 1 plate rice (300g) = ~390 cal\n"
                                    "- 1 medium piece fish curry = ~160 cal\n"
                                    "- 1 chicken leg piece curry = ~200 cal\n"
                                    "- 1 cup dal = ~150 cal\n"
                                    "- 1 roti/chapati = ~100 cal\n"
                                    "- 1 plate biryani = ~600 cal\n"
                                    "- 1 serving vegetables = ~50 cal\n"
                                    "- 1 egg = ~80 cal\n"
                                    "- 1 banana = ~100 cal\n"
                                    "- 1 cup milk tea = ~60 cal\n"
                                    "Estimate total calories realistically. Most meals are 400-800 calories."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{content_type};base64,{image_b64}"},
                            },
                        ],
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.1,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    # Parse response
    content = data["choices"][0]["message"]["content"].strip()
    # Handle possible markdown code blocks
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from response
        import re
        match = re.search(r'\{[^{}]*\}', content)
        if match:
            result = json.loads(match.group())
        else:
            result = {"food_name": "Unknown", "total_calories": 400, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "portion_estimate": "unknown"}

    # If AI gives 0 or very low calories, try local DB fallback
    if result.get("total_calories", 0) < 20:
        food_name = result.get("food_name", "")
        local = estimate_from_db(food_name)
        if local:
            result["total_calories"] = local["calories"]
            result["protein_g"] = local["protein"]
            result["carbs_g"] = local["carbs"]
            result["fat_g"] = local["fat"]
            result["portion_estimate"] = local["portion"]
            result["source"] = "local_db_fallback"

    result["source"] = result.get("source", "ai_vision")

    # Check cost
    cost = data.get("usage", {})
    result["_cost"] = round(cost.get("total_cost", 0) or 0, 4)

    return result


# ── API: Log entry ────────────────────────────────────────
@app.post("/api/log")
async def log_entry(
    food_name: str = Form(...),
    calories: int = Form(...),
    protein: float = Form(0),
    carbs: float = Form(0),
    fat: float = Form(0),
    portion: str = Form(""),
):
    today = str(date.today())
    now = datetime.now().strftime("%I:%M %p")

    with get_db() as db:
        db.execute(
            "INSERT INTO entries (date, time, food_name, calories, protein, carbs, fat, portion) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (today, now, food_name, calories, protein, carbs, fat, portion),
        )
    return {"status": "ok"}


# ── API: Get today's entries ──────────────────────────────
@app.get("/api/entries")
def get_entries(d: str = ""):
    target = d if d else str(date.today())
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM entries WHERE date = ? ORDER BY id DESC", (target,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── API: Delete entry ─────────────────────────────────────
@app.delete("/api/entries/{entry_id}")
def delete_entry(entry_id: int):
    with get_db() as db:
        db.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    return {"status": "ok"}


# ── API: Daily summary ────────────────────────────────────
@app.get("/api/summary")
def get_summary(d: str = ""):
    target = d if d else str(date.today())
    with get_db() as db:
        row = db.execute(
            "SELECT SUM(calories) as total_cal, SUM(protein) as total_protein, SUM(carbs) as total_carbs, SUM(fat) as total_fat, COUNT(*) as meals FROM entries WHERE date = ?",
            (target,),
        ).fetchone()
    settings = load_settings()
    goal = settings.get("daily_goal", 2200)
    total = row["total_cal"] or 0
    return {
        "date": target,
        "total_calories": total,
        "total_protein": round(row["total_protein"] or 0, 1),
        "total_carbs": round(row["total_carbs"] or 0, 1),
        "total_fat": round(row["total_fat"] or 0, 1),
        "meals": row["meals"],
        "goal": goal,
        "remaining": goal - total,
        "percent": round((total / goal) * 100) if goal else 0,
    }


# ── API: Weekly history ───────────────────────────────────
@app.get("/api/weekly")
def get_weekly():
    with get_db() as db:
        rows = db.execute("""
            SELECT date, SUM(calories) as total_cal, COUNT(*) as meals
            FROM entries
            WHERE date >= date('now', '-7 days')
            GROUP BY date
            ORDER BY date DESC
        """).fetchall()
    return [dict(r) for r in rows]


# ── API: Settings ─────────────────────────────────────────
@app.get("/api/settings")
def get_settings():
    s = load_settings()
    # Mask API key for security
    key = s.get("api_key", "")
    s["api_key_masked"] = key[:4] + "..." + key[-4:] if len(key) > 8 else ("***" if key else "")
    return s


@app.post("/api/settings")
async def save_settings_endpoint(api_key: str = Form(""), daily_goal: int = Form(2200)):
    settings_data = {"api_key": api_key.strip() if api_key else "", "daily_goal": daily_goal}
    save_settings(settings_data)
    return {"status": "ok"}


# ── Static files ──────────────────────────────────────────
@app.get("/")
def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


# ── Run ───────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
