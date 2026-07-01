import React, { useState } from 'react'
import { searchFood } from '../api'

export default function FoodSearch({ apiBase, onAddMeal }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [grams, setGrams] = useState({})

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    try {
      const data = await searchFood(apiBase, query)
      setResults(data.results || [])
      if (data.error) setError(data.error)
      if (data.results?.length === 0) setError('No foods found. Try a different search term.')
    } catch {
      setError('Backend not responding. Make sure the API server is running.')
    } finally {
      setLoading(false)
    }
  }

  const logFood = (food) => {
    const g = parseFloat(grams[food.fdc_id]) || 100
    const factor = g / 100
    onAddMeal({
      name: food.name,
      brand: food.brand,
      calories: Math.round((food.calories || 0) * factor),
      protein: food.protein ? Math.round(food.protein * factor * 10) / 10 : null,
      carbs: food.carbs ? Math.round(food.carbs * factor * 10) / 10 : null,
      fat: food.fat ? Math.round(food.fat * factor * 10) / 10 : null,
      grams: g,
      source: 'search',
    })
  }

  return (
    <div className="food-search">
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search food (e.g. 'chicken breast')"
          className="search-input"
          autoFocus
        />
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? '⏳' : '🔍'}
        </button>
      </form>

      {error && <p className="error-msg">{error}</p>}

      {results.length > 0 && (
        <div className="search-results">
          <h3>Results <span className="count">({results.length})</span></h3>
          {results.map(food => (
            <div key={food.fdc_id} className="food-card">
              <div className="food-info">
                <strong className="food-name">{food.name}</strong>
                {food.brand && <span className="brand"> — {food.brand}</span>}
                <div className="food-macros">
                  {food.calories && <span className="macro-chip">🔥 {Math.round(food.calories)}</span>}
                  {food.protein && <span className="macro-chip protein">🥩 {food.protein}g</span>}
                  {food.carbs && <span className="macro-chip carbs">🍚 {food.carbs}g</span>}
                  {food.fat && <span className="macro-chip fat">🧈 {food.fat}g</span>}
                </div>
                <span className="per-serving">per 100g</span>
              </div>
              <div className="food-actions">
                <div className="serving-input">
                  <input
                    type="number"
                    value={grams[food.fdc_id] || 100}
                    onChange={e => setGrams({...grams, [food.fdc_id]: e.target.value})}
                    min={1}
                  />
                  <span className="unit">g</span>
                </div>
                <button className="btn btn-add" onClick={() => logFood(food)}>+ Log</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}