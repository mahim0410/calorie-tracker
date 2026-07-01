import React, { useState, useEffect } from 'react'
import FoodSearch from './components/FoodSearch'
import CameraCapture from './components/CameraCapture'
import DailyLog from './components/DailyLog'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [activeTab, setActiveTab] = useState('log')
  const [meals, setMeals] = useState([])
  const [backendOk, setBackendOk] = useState(null)

  useEffect(() => {
    const saved = localStorage.getItem('caltracker_meals')
    if (saved) {
      try { setMeals(JSON.parse(saved)) } catch {}
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('caltracker_meals', JSON.stringify(meals))
  }, [meals])

  // Health check for backend (non-blocking)
  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then(r => setBackendOk(r.ok))
      .catch(() => setBackendOk(false))
  }, [])

  const addMeal = (meal) => {
    const newMeal = {
      ...meal,
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
    }
    setMeals(prev => [newMeal, ...prev])
  }

  const deleteMeal = (id) => {
    setMeals(prev => prev.filter(m => m.id !== id))
  }

  const clearToday = () => {
    if (confirm('Clear all meals for today?')) {
      const today = new Date().toDateString()
      setMeals(prev => prev.filter(m => new Date(m.timestamp).toDateString() !== today))
    }
  }

  const todayMeals = meals.filter(m =>
    new Date(m.timestamp).toDateString() === new Date().toDateString()
  )
  const todayCalories = todayMeals.reduce((s, m) => s + (m.calories || 0), 0)
  const todayProtein = todayMeals.reduce((s, m) => s + (m.protein || 0), 0)
  const dailyGoal = 2000

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-top">
          <h1>🍽️ CalTrack</h1>
          {backendOk === false && (
            <span className="offline-badge" title="Backend offline — AI features won't work">⚡ Offline</span>
          )}
        </div>
        <div className="calorie-ring">
          <svg viewBox="0 0 120 120" className="ring-svg">
            <circle cx="60" cy="60" r="52" fill="none" stroke="#1e293b" strokeWidth="10" />
            <circle
              cx="60" cy="60" r="52" fill="none" stroke="#10b981"
              strokeWidth="10" strokeLinecap="round"
              strokeDasharray={`${(todayCalories / dailyGoal) * 327} 327`}
              transform="rotate(-90 60 60)"
              style={{ transition: 'stroke-dasharray 0.5s ease' }}
            />
            <text x="60" y="52" textAnchor="middle" fill="#e2e8f0" fontSize="28" fontWeight="bold">
              {todayCalories}
            </text>
            <text x="60" y="72" textAnchor="middle" fill="#94a3b8" fontSize="11">
              of {dailyGoal} cal
            </text>
          </svg>
        </div>
        {todayMeals.length > 0 && (
          <div className="macro-strip">
            <span>🥩 {Math.round(todayProtein)}g protein</span>
          </div>
        )}
      </header>

      <main className="app-main">
        {activeTab === 'log' && (
          <DailyLog meals={todayMeals} onDelete={deleteMeal} onClear={clearToday} />
        )}
        {activeTab === 'search' && (
          <FoodSearch apiBase={API_BASE} onAddMeal={addMeal} />
        )}
        {activeTab === 'camera' && (
          <CameraCapture apiBase={API_BASE} onAddMeal={addMeal} />
        )}
      </main>

      <nav className="app-nav">
        <button className={`nav-btn ${activeTab === 'log' ? 'active' : ''}`} onClick={() => setActiveTab('log')}>
          📋 Log
        </button>
        <button className={`nav-btn ${activeTab === 'search' ? 'active' : ''}`} onClick={() => setActiveTab('search')}>
          🔍 Search
        </button>
        <button className={`nav-btn ${activeTab === 'camera' ? 'active' : ''}`} onClick={() => setActiveTab('camera')}>
          📸 Camera
        </button>
      </nav>
    </div>
  )
}

export default App