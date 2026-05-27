import axios from 'axios'

const API = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 300000
})

export const getCompetitors = () => 
  API.get('/api/competitors')

export const getStats = () => 
  API.get('/api/stats')

export const getLatestBriefing = () => 
  API.get('/api/briefing/latest')

export const generateBriefing = () => 
  API.post('/api/briefing/generate')

export const getCompetitorIntel = (name: string) => 
  API.get(`/api/competitor/${name}`)

export default API