export async function searchFood(apiBase, query) {
  const res = await fetch(`${apiBase}/api/search-food?q=${encodeURIComponent(query)}`)
  if (!res.ok) throw new Error('Search failed')
  return res.json()
}

export async function analyzeFoodImage(apiBase, file) {
  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(`${apiBase}/api/analyze-food`, {
    method: 'POST',
    body: formData,
  })
  if (!res.ok) throw new Error('Analysis failed')
  return res.json()
}

export async function healthCheck(apiBase) {
  try {
    const res = await fetch(`${apiBase}/api/health`)
    return res.ok
  } catch {
    return false
  }
}