<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'

const router = useRouter()
const { post, isLoading, error } = useApi()

const comercioNombre = ref('')
const descripcion = ref('')
const whatsapp = ref('')
const email = ref('')
const password = ref('')

const fileInput = ref(null)
const imagenPrevia = ref(null)
const fileToUpload = ref(null)

const procesarImagen = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      let width = img.width
      let height = img.height

      if (width > 400) {
        height = Math.round((height * 400) / width)
        width = 400
      }

      canvas.width = width
      canvas.height = height

      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)

      // Comprimir a WebP 80%
      canvas.toBlob((blob) => {
        fileToUpload.value = blob
        imagenPrevia.value = URL.createObjectURL(blob)
      }, 'image/webp', 0.8)
    }
    img.src = e.target.result
  }
  reader.readAsDataURL(file)
}

const handleRegister = async () => {
  try {
    const payload = {
      comercio: {
        nombre: comercioNombre.value,
        whatsapp: whatsapp.value,
        descripcion: descripcion.value
      },
      usuario: {
        email: email.value,
        password: password.value
      }
    }

    await post('/api/auth/register', payload)
    
    // Si el registro fue exitoso, hacemos login automáticamente
    const { request } = useApi()
    const formData = new URLSearchParams()
    formData.append('username', email.value)
    formData.append('password', password.value)

    const loginData = await request('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    })
    
    if (loginData && loginData.access_token) {
      localStorage.setItem('token', loginData.access_token)
      
      // Subir logo si fue seleccionado
      if (fileToUpload.value) {
        const logoFormData = new FormData()
        logoFormData.append('file', fileToUpload.value, 'logo.webp')
        
        try {
          await fetch('/api/auth/me/logo', {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${loginData.access_token}` },
            body: logoFormData
          })
        } catch (logoErr) {
          console.error('Error subiendo el logo', logoErr)
        }
      }
      
      router.push({ name: 'admin' })
    }
  } catch (err) {
    console.error('Error de Registro', err)
  }
}
</script>

<template>
  <div class="google-style-page">
    <div class="google-container">
      
      <!-- Left side: Headers and Logo Upload -->
      <div class="google-left">
        <router-link to="/" class="logo-text">
          <span class="logo-icon">🛍️</span> CatálogoSaaS
        </router-link>
        
        <h1 class="main-title">Crea tu Catálogo</h1>
        <p class="subtitle">Ingresa los datos de tu emprendimiento para comenzar a vender por WhatsApp.</p>
        
        <div class="logo-upload-section">
          <img v-if="imagenPrevia" :src="imagenPrevia" class="preview-img" />
          <div v-else class="preview-img-placeholder">
            <span>🖼️</span>
          </div>
          <div class="upload-controls">
            <label class="upload-label">Logo de tu negocio (Opcional)</label>
            <input 
              ref="fileInput"
              type="file" 
              accept="image/*" 
              @change="procesarImagen"
              style="display: none;"
              id="logo-upload"
            />
            <label for="logo-upload" class="btn-text-primary">
              Seleccionar imagen
            </label>
          </div>
        </div>
      </div>

      <!-- Right side: Form fields -->
      <div class="google-right">
        <div v-if="error" class="error-msg">
          {{ error }}
        </div>

        <form @submit.prevent="handleRegister" class="google-form">
          <!-- Row 1 -->
          <div class="form-row">
            <div class="google-input-group">
              <input v-model="comercioNombre" type="text" class="google-input" placeholder=" " required />
              <label class="google-label">Nombre del Negocio</label>
            </div>
          </div>
          
          <!-- Row 2 -->
          <div class="form-row">
            <div class="google-input-group">
              <input v-model="descripcion" type="text" class="google-input" placeholder=" " maxlength="200" />
              <label class="google-label">Breve Descripción (Opcional)</label>
            </div>
          </div>

          <!-- Row 3 -->
          <div class="form-row">
            <div class="google-input-group">
              <input v-model="whatsapp" type="text" class="google-input" placeholder=" " required />
              <label class="google-label">WhatsApp (ej: 5491100000000)</label>
            </div>
          </div>

          <!-- Row 4 -->
          <div class="form-row split-row">
            <div class="google-input-group">
              <input v-model="email" type="email" class="google-input" placeholder=" " required />
              <label class="google-label">Email</label>
            </div>
            <div class="google-input-group">
              <input v-model="password" type="password" class="google-input" placeholder=" " required minlength="6" />
              <label class="google-label">Contraseña</label>
            </div>
          </div>
          
          <div class="form-actions">
            <router-link to="/login" class="btn-text-primary">Acceder en su lugar</router-link>
            <button type="submit" class="btn-google-primary" :disabled="isLoading">
              {{ isLoading ? 'Creando...' : 'Siguiente' }}
            </button>
          </div>
        </form>
      </div>

    </div>
  </div>
</template>

<style scoped>
.google-style-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg);
  padding: 2rem;
  color: #202124;
}

.google-container {
  display: flex;
  max-width: 1040px;
  width: 100%;
  gap: 4rem;
  background: transparent;
}

/* LEFT SIDE */
.google-left {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.logo-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
  margin-bottom: 3rem;
}

.main-title {
  font-size: 2.5rem;
  font-weight: 400;
  line-height: 1.2;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.subtitle {
  font-size: 1rem;
  color: var(--color-text-light);
  line-height: 1.5;
  margin-bottom: 3rem;
}

.logo-upload-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-top: auto;
}

.preview-img {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 1px solid #dadce0;
}

.preview-img-placeholder {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: #f1f3f4;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  border: 1px dashed #dadce0;
}

.upload-controls {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.25rem;
}

.upload-label {
  font-size: 0.85rem;
  color: var(--color-text-light);
}

/* RIGHT SIDE */
.google-right {
  flex: 1.2;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.google-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  width: 100%;
}

.split-row {
  display: flex;
  gap: 1rem;
}

.split-row .google-input-group {
  flex: 1;
}

/* Floating label inputs (Google style) */
.google-input-group {
  position: relative;
  width: 100%;
}

.google-input {
  width: 100%;
  padding: 13px 15px;
  font-size: 1rem;
  border: 1px solid #dadce0;
  border-radius: 4px;
  background: transparent;
  color: var(--color-text);
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.google-input:focus {
  border-color: #ea580c;
  border-width: 2px;
  padding: 12px 14px; /* Adjust padding to prevent jumping when border becomes 2px */
}

.google-label {
  position: absolute;
  top: 50%;
  left: 12px;
  transform: translateY(-50%);
  background: var(--color-bg);
  padding: 0 4px;
  color: var(--color-text-light);
  font-size: 1rem;
  transition: 0.2s ease all;
  pointer-events: none;
}

/* When input is focused OR has value (placeholder=" " hack) */
.google-input:focus ~ .google-label,
.google-input:not(:placeholder-shown) ~ .google-label {
  top: 0;
  font-size: 0.75rem;
  color: #ea580c;
}

.google-input:not(:focus):not(:placeholder-shown) ~ .google-label {
  color: var(--color-text-light);
}

/* Buttons */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2rem;
}

.btn-text-primary {
  color: #ea580c;
  font-weight: 600;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.5rem 0.5rem;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.95rem;
  transition: background 0.2s;
}

.btn-text-primary:hover {
  background: rgba(234, 88, 12, 0.04);
}

.btn-google-primary {
  background: #ea580c;
  color: white;
  border: none;
  padding: 0.6rem 1.5rem;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s, box-shadow 0.2s;
}

.btn-google-primary:hover {
  background: #c2410c;
  box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
}

.btn-google-primary:disabled {
  background: #e0e0e0;
  color: #9e9e9e;
  cursor: not-allowed;
  box-shadow: none;
}

.error-msg {
  color: #d93025;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 768px) {
  .google-style-page {
    padding: 1.5rem;
    align-items: flex-start;
  }
  .google-container {
    flex-direction: column;
    gap: 2rem;
  }
  .split-row {
    flex-direction: column;
    gap: 1.5rem;
  }
  .main-title {
    font-size: 2rem;
  }
  .logo-text {
    margin-bottom: 1.5rem;
  }
  .subtitle {
    margin-bottom: 1.5rem;
  }
  .logo-upload-section {
    margin-top: 0;
  }
}
</style>
