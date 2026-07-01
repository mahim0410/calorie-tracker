import os
from fastapi import FastAPI, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from food_search import search_food, get_food_details
from image_analysis import analyze_food_image

load_dotenv()

app = FastAPI(title="CalTracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/search-food")
async def search_food_endpoint(q: str = Query(..., min_length=1)):
    """Search USDA food database by name."""
    try:
        results = search_food(q)
        return {"results": results}
    except Exception as e:
        return {"error": str(e), "results": []}


@app.get("/api/food-details/{fdc_id}")
async def food_details_endpoint(fdc_id: int):
    """Get detailed nutrition info for a specific food."""
    try:
        return get_food_details(fdc_id)
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/analyze-food")
async def analyze_food_endpoint(file: UploadFile = File(...)):
    """Analyze a food photo using Gemini Vision AI."""
    try:
        image_bytes = await file.read()
        if len(image_bytes) > 10 * 1024 * 1024:
            return {"success": False, "error": "Image too large (max 10MB)"}
        analysis = analyze_food_image(image_bytes, file.filename or "image.jpg")
        return analysis
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
