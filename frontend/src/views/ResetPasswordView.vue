<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'

const route = useRoute()
const router = useRouter()
const { post, isLoading, error } = useApi()

const password = ref('')
const confirmPassword = ref('')
const token = ref('')
const message = ref('')
const validationError = ref('')

onMounted(() => {
  token.value = route.query.token || ''
  if (!token.value) {
    validationError.value = 'El token de recuperación no es válido o ha expirado. Por favor, solicita uno nuevo.'
  }
})

const handleResetPassword = async () => {
  validationError.value = ''
  message.value = ''

  if (password.value.length < 6) {
    validationError.value = 'La contraseña debe tener al menos 6 caracteres.'
    return
  }

  if (password.value !== confirmPassword.value) {
    validationError.value = 'Las contraseñas no coinciden.'
    return
  }

  try {
    const data = await post('/api/auth/reset-password', {
      token: token.value,
      password: password.value
    })
    
    message.value = data.message || 'Tu contraseña ha sido restablecida con éxito.'
    setTimeout(() => {
      router.push({ name: 'login' })
    }, 3000)
  } catch (err) {
    console.error('Error al restablecer contraseña', err)
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
    </nav>

    <main class="hero-section" style="padding-top: 6rem; padding-bottom: 2rem; align-items: flex-start;">
      <div class="auth-container" style="background: var(--color-surface); border: 1px solid rgba(0,0,0,0.05); box-shadow: var(--shadow-glass); border-radius: 24px; position: relative; z-index: 10; width: 100%; margin-top: 2rem;">
        <h2 style="font-size: 1.8rem; font-weight: 800; margin-bottom: 1rem; text-align: center;">Nueva Contraseña</h2>
        <p style="text-align: center; color: var(--color-text-light); margin-bottom: 2rem; font-size: 0.95rem;">
          Ingresa y confirma tu nueva contraseña de administrador.
        </p>
        
        <div v-if="error" class="error-card" style="margin-bottom: 1.5rem">
          {{ error }}
        </div>

        <div v-if="validationError" class="error-card" style="margin-bottom: 1.5rem; background-color: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); color: #b91c1c; padding: 1rem; border-radius: 12px; font-weight: 500; font-size: 0.95rem;">
          {{ validationError }}
        </div>

        <div v-if="message" class="success-card" style="margin-bottom: 1.5rem; background-color: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #047857; padding: 1rem; border-radius: 12px; font-weight: 500; font-size: 0.95rem;">
          {{ message }} Redirigiendo a iniciar sesión...
        </div>

        <form v-if="token && !message" @submit.prevent="handleResetPassword">
          <div class="form-group">
            <label>Nueva Contraseña</label>
            <input v-model="password" type="password" class="form-input" required />
          </div>

          <div class="form-group">
            <label>Confirmar Nueva Contraseña</label>
            <input v-model="confirmPassword" type="password" class="form-input" required />
          </div>

          <button type="submit" class="btn-primary" style="padding: 1rem; font-size: 1.1rem; border-radius: 50px; margin-top: 1rem; box-shadow: 0 4px 14px 0 rgba(234, 88, 12, 0.39);" :disabled="isLoading">
            {{ isLoading ? 'Restableciendo...' : 'Guardar Nueva Contraseña' }}
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
