# CalTracker — AI Calorie Counter

Track your daily calories with AI-powered food recognition.  
Search the USDA food database or snap a photo to log meals instantly.

## Stack

- **Frontend:** React + Vite PWA (installable on Android)
- **Backend:** FastAPI (Python 3.11)
- **Food data:** USDA FoodData Central API
- **AI Vision:** Google Gemini 2.0 Flash
- **Storage:** LocalStorage (no account needed)

## Run Locally

### 1. Backend
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# Create .env with your API keys (already done)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### 3. Use it
- Open `http://localhost:5173` in browser
- **On Android:** open the URL in Chrome → menu → "Add to Home Screen"

## Deploy

- **Backend:** Render — connect GitHub repo, root = `backend/`, start command = `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Frontend:** Vercel — connect GitHub repo, root = `frontend/`, framework = Vite

Set `VITE_API_URL` on Vercel to your Render backend URL.
