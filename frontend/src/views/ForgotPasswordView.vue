<script setup>
import { ref } from 'vue'
import { useApi } from '../composables/useApi'

const { post, isLoading, error } = useApi()

const email = ref('')
const message = ref('')
const debugLink = ref('')

const handleForgotPassword = async () => {
  try {
    message.value = ''
    debugLink.value = ''
    
    const data = await post('/api/auth/forgot-password', {
      email: email.value
    })
    
    message.value = data.message || 'Se ha enviado un correo con instrucciones para restablecer tu contraseña.'
    if (data.debug_link) {
      debugLink.value = data.debug_link
    }
  } catch (err) {
    console.error('Error al solicitar recuperación', err)
  }
}
</script>

<template>
  <div class="landing-page">
    <nav class="landing-nav" style="position: absolute;">
      <router-link to="/" class="logo-container" style="text-decoration: none; color: var(--color-text);">
        <span class="logo-icon">🛍️</span>
        <span class="logo-text">TuPedido.ar</span>
      </router-link>
      <div class="nav-actions">
        <router-link to="/login" class="nav-link">Iniciar Sesión</router-link>
      </div>
    </nav>

    <main class="hero-section" style="padding-top: 6rem; padding-bottom: 2rem; align-items: flex-start;">
      <div class="auth-container" style="background: var(--color-surface); border: 1px solid rgba(0,0,0,0.05); box-shadow: var(--shadow-glass); border-radius: 24px; position: relative; z-index: 10; width: 100%; margin-top: 2rem;">
        <h2 style="font-size: 1.8rem; font-weight: 800; margin-bottom: 1rem; text-align: center;">Recuperar Contraseña</h2>
        <p style="text-align: center; color: var(--color-text-light); margin-bottom: 2rem; font-size: 0.95rem;">
          Ingresa tu correo electrónico y te enviaremos un enlace para restablecer tu contraseña.
        </p>
        
        <div v-if="error" class="error-card" style="margin-bottom: 1.5rem">
          {{ error }}
        </div>

        <div v-if="message" class="success-card" style="margin-bottom: 1.5rem; background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #047857; padding: 1rem; border-radius: 12px; font-weight: 500; font-size: 0.95rem;">
          {{ message }}
        </div>

        <div v-if="debugLink" class="debug-card" style="margin-bottom: 1.5rem; background-color: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); color: #1d4ed8; padding: 1rem; border-radius: 12px; font-size: 0.9rem;">
          <p style="margin: 0 0 0.5rem 0; font-weight: 700;">🔧 Enlace de Depuración (Local):</p>
          <a :href="debugLink" style="word-break: break-all; color: #2563eb; font-weight: 600; text-decoration: underline;">
            Restablecer Contraseña Directamente
          </a>
        </div>

        <form v-if="!message" @submit.prevent="handleForgotPassword">
          <div class="form-group">
            <label>Email del Comercio</label>
            <input v-model="email" type="email" class="form-input" required />
          </div>

          <button type="submit" class="btn-primary" style="padding: 1rem; font-size: 1.1rem; border-radius: 50px; margin-top: 1rem; box-shadow: 0 4px 14px 0 rgba(234, 88, 12, 0.39);" :disabled="isLoading">
            {{ isLoading ? 'Enviando...' : 'Enviar Enlace' }}
          </button>
        </form>
        
        <p class="text-center" style="margin-top: 2rem; color: var(--color-text-light);">
          ¿Recordaste tu contraseña? <router-link to="/login" class="link" style="font-weight: 700;">Inicia sesión aquí</router-link>
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
