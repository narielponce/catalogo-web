import { ref } from 'vue'

export function useApi() {
  const isLoading = ref(false)
  const error = ref(null)

  const request = async (url, options = {}) => {
    isLoading.value = true
    error.value = null
    
    try {
      const headers = {
        'Content-Type': 'application/json',
        ...options.headers
      }

      const token = localStorage.getItem('token')
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const response = await fetch(url, { ...options, headers })
      
      let data = null
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        data = await response.json()
      } else {
        data = await response.text()
      }

      if (!response.ok) {
        throw new Error(data?.detail || response.statusText || 'Error en la petición')
      }

      return data

    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const get = (url, options = {}) => request(url, { ...options, method: 'GET' })
  const post = (url, body, options = {}) => request(url, { ...options, method: 'POST', body: JSON.stringify(body) })
  const put = (url, body, options = {}) => request(url, { ...options, method: 'PUT', body: JSON.stringify(body) })
  const del = (url, options = {}) => request(url, { ...options, method: 'DELETE' })

  return {
    isLoading,
    error,
    request,
    get,
    post,
    put,
    del
  }
}
