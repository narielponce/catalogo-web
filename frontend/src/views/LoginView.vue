<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'

const router = useRouter()
const { request, get, isLoading, error } = useApi()

const email = ref('')
const password = ref('')

const handleLogin = async () => {
  try {
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    // OAuth2 espera application/x-www-form-urlencoded
    const data = await request('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    if (data && data.access_token) {
      localStorage.setItem('token', data.access_token)
      
      // Consultar rol para redirección
      const userData = await get('/api/auth/me')
      if (userData && userData.is_superuser) {
        router.push({ name: 'superadmin' })
      } else {
        router.push({ name: 'admin' })
      }
    }
  } catch (err) {
    console.error('Error de Login', err)
  }
}
</script>

<template>
  <div class="landing-page">
    <nav class="landing-nav" style="position: absolute;">
      <router-link to="/" class="logo-container" style="text-decoration: none; color: var(--color-text);">
        <span class="logo-icon">🛍️</span>
        <span class="logo-text">CatálogoSaaS</span>
      </router-link>
      <div class="nav-actions">
        <router-link to="/register" class="nav-link">Crear Catálogo</router-link>
      </div>
    </nav>

    <main class="hero-section" style="padding-top: 6rem; padding-bottom: 2rem; align-items: flex-start;">
      <div class="auth-container" style="background: var(--color-surface); border: 1px solid rgba(0,0,0,0.05); box-shadow: var(--shadow-glass); border-radius: 24px; position: relative; z-index: 10; width: 100%; margin-top: 2rem;">
        <h2 style="font-size: 1.8rem; font-weight: 800; margin-bottom: 1.5rem; text-align: center;">Iniciar Sesión</h2>
        
        <div v-if="error" class="error-card" style="margin-bottom: 1.5rem">
          {{ error }}
        </div>

        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label>Email del Comercio</label>
            <input v-model="email" type="email" class="form-input" required />
          </div>
          
          <div class="form-group">
            <label>Contraseña</label>
            <input v-model="password" type="password" class="form-input" required />
          </div>

          <button type="submit" class="btn-primary" style="padding: 1rem; font-size: 1.1rem; border-radius: 50px; margin-top: 1rem; box-shadow: 0 4px 14px 0 rgba(234, 88, 12, 0.39);" :disabled="isLoading">
            {{ isLoading ? 'Conectando...' : 'Entrar al Panel' }}
          </button>
        </form>
        
        <p class="text-center" style="margin-top: 2rem; color: var(--color-text-light);">
          ¿No tienes tu catálogo aún? <router-link to="/register" class="link" style="font-weight: 700;">Regístrate aquí</router-link>
        </p>
      </div>
      
      <!-- Background Blobs -->
      <div class="glow-blob blob-1" style="opacity: 0.1;"></div>
      <div class="glow-blob blob-2" style="opacity: 0.1;"></div>
    </main>
  </div>
</template>

<style scoped>
.landing-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg);
  color: var(--color-text);
  overflow-x: hidden;
  position: relative;
}

.landing-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 5%;
  width: 100%;
  z-index: 100;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.nav-link {
  color: var(--color-text-light);
  text-decoration: none;
  font-weight: 500;
}

.hero-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.glow-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  pointer-events: none;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: #ea580c;
  top: 0;
  left: -100px;
}

.blob-2 {
  width: 300px;
  height: 300px;
  background: #f59e0b;
  bottom: 0;
  right: -50px;
}
</style>
