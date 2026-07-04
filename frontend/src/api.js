import axios from 'axios'

export const API_BASE_URL = 'http://127.0.0.1:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
})

export async function getSnapshot() {
  const response = await api.get('/snapshot/')
  return response.data
}
