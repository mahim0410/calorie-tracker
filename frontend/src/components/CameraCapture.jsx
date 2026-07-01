import React, { useRef, useState } from 'react'
import { analyzeFoodImage } from '../api'

export default function CameraCapture({ apiBase, onAddMeal }) {
  const fileInputRef = useRef(null)
  const [preview, setPreview] = useState(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handleFile = (e) => {
    const file = e.target.files[0]
    if (!file) return
    setPreview(URL.createObjectURL(file))
    setError('')
    setResult(null)
    analyzeImage(file)
  }

  const analyzeImage = async (file) => {
    setAnalyzing(true)
    try {
      const data = await analyzeFoodImage(apiBase, file)
      setResult(data)
      if (!data.success) setError(data.error || 'Could not analyze image')
    } catch {
      setError('Backend offline. Make sure the API server is running.')
    } finally {
      setAnalyzing(false)
    }
  }

  const logResult = () => {
    if (!result || result.food_name === 'unknown') return
    onAddMeal({
      name: result.food_name,
      calories: result.estimated_calories || 0,
      protein: result.protein_g,
      carbs: result.carbs_g,
      fat: result.fat_g,
      portion: result.portion_description,
      source: 'camera',
    })
    resetCapture()
  }

  const resetCapture = () => {
    setPreview(null)
    setResult(null)
    setError('')
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  return (
    <div className="camera-capture">
      <input
        type="file"
        accept="image/*"
        capture="environment"
        ref={fileInputRef}
        onChange={handleFile}
        className="file-input"
        id="camera-input"
      />
      <label htmlFor="camera-input" className="camera-label">
        {preview ? (
          <span>📷 Take another photo</span>
        ) : (
          <>
            <span className="camera-icon">📸</span>
            <span>Take a photo of your food</span>
            <span className="camera-hint">Or tap to upload from gallery</span>
          </>
        )}
      </label>

      {error && <p className="error-msg">{error}</p>}

      {preview && (
        <div className="preview-section">
          <img src={preview} alt="Food" className="food-preview" />

          {analyzing && (
            <div className="analyzing">
              <div className="pulse-dot" />
              <span>Analyzing your food...</span>
            </div>
          )}

          {result && result.food_name && result.food_name !== 'unknown' && (
            <div className="analysis-result">
              <h3>{result.food_name}</h3>
              {result.confidence && (
                <span className={`confidence confidence-${result.confidence}`}>
                  {result.confidence} confidence
                </span>
              )}
              <div className="analysis-grid">
                <div className="analysis-item cal">
                  <span className="analysis-value">{result.estimated_calories}</span>
                  <span className="analysis-label">calories</span>
                </div>
                {result.protein_g != null && (
                  <div className="analysis-item">
                    <span className="analysis-value">{result.protein_g}g</span>
                    <span className="analysis-label">protein</span>
                  </div>
                )}
                {result.carbs_g != null && (
                  <div className="analysis-item">
                    <span className="analysis-value">{result.carbs_g}g</span>
                    <span className="analysis-label">carbs</span>
                  </div>
                )}
                {result.fat_g != null && (
                  <div className="analysis-item">
                    <span className="analysis-value">{result.fat_g}g</span>
                    <span className="analysis-label">fat</span>
                  </div>
                )}
              </div>
              {result.portion_description && (
                <p className="portion-text">{result.portion_description}</p>
              )}
              <button className="btn btn-primary btn-big" onClick={logResult}>
                ✓ Log This Meal
              </button>
            </div>
          )}

          {result && result.food_name === 'unknown' && (
            <div className="analysis-result error">
              <p>🤔 Could not identify the food. Try a clearer photo.</p>
              <button className="btn" onClick={resetCapture}>Try Again</button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}