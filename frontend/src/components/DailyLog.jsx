import React from 'react'

export default function DailyLog({ meals, onDelete, onClear }) {
  if (meals.length === 0) {
    return (
      <div className="daily-log">
        <div className="empty-state">
          <span className="empty-icon">🍽️</span>
          <p className="empty-title">No meals logged yet</p>
          <p className="empty-hint">Search for food in the 🔍 tab,<br />or take a 📸 photo to analyze</p>
        </div>
      </div>
    )
  }

  // Group by meal time period
  const now = new Date()
  const hour = now.getHours()
  let greeting = 'Good evening'
  if (hour < 12) greeting = 'Good morning'
  else if (hour < 17) greeting = 'Good afternoon'

  return (
    <div className="daily-log">
      <div className="log-header">
        <h3>{greeting}</h3>
        <button className="btn-link" onClick={onClear}>Clear</button>
      </div>
      <div className="meal-list">
        {meals.map(meal => (
          <div key={meal.id} className="meal-card">
            <div className="meal-info">
              <div className="meal-name-row">
                <strong>{meal.name}</strong>
                <span className="meal-cal">🔥 {meal.calories}</span>
              </div>
              {meal.portion && <span className="portion-text">{meal.portion}</span>}
              {meal.grams && <span className="portion-text">{meal.grams}g</span>}
              {(meal.protein || meal.carbs || meal.fat) && (
                <div className="meal-macros">
                  {meal.protein != null && <span>🥩 {meal.protein}g</span>}
                  {meal.carbs != null && <span>🍚 {meal.carbs}g</span>}
                  {meal.fat != null && <span>🧈 {meal.fat}g</span>}
                </div>
              )}
              <span className="meal-time">
                {new Date(meal.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                {meal.source === 'camera' && ' 📸'}
              </span>
            </div>
            <button className="btn-delete" onClick={() => onDelete(meal.id)}>✕</button>
          </div>
        ))}
      </div>
    </div>
  )
}