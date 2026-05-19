<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'

const router = useRouter()
const { get, post, put, del, isLoading, error } = useApi()

const productos = ref([])
const meInfo = ref(null)
const originUrl = window.location.origin

const themes = [
  { id: 'terracotta', name: 'Terracota', color: '#ea580c' },
  { id: 'blue', name: 'Azul Moderno', color: '#3b82f6' },
  { id: 'emerald', name: 'Verde Esmeralda', color: '#10b981' },
  { id: 'violet', name: 'Púrpura Vibrante', color: '#8b5cf6' },
  { id: 'dark', name: 'Gris Premium', color: '#111827' }
]

// Estado del Modal
const mostrarModal = ref(false)
const fileInput = ref(null)
const imagenPrevia = ref(null)
const fileToUpload = ref(null)
const imagenAmpliada = ref(null)
const productoEnEdicion = ref(null)

const nuevoProducto = ref({
  nombre: '',
  precio: '',
  descripcion: '',
  disponible: true
})

const cargarProductos = async () => {
  try {
    // Cargar info del usuario para obtener el slug
    const userData = await get('/api/auth/me')
    if (userData) {
      meInfo.value = userData
    }

    const data = await get('/api/productos/')
    if (data) {
      productos.value = data
    }
  } catch (err) {
    if (err.message.includes('401') || err.message.includes('No se pudo validar')) {
      handleLogout()
    }
  }
}

const diasRestantes = computed(() => {
  if (!meInfo.value || !meInfo.value.comercio.trial_vence) return 0
  const vencimiento = new Date(meInfo.value.comercio.trial_vence)
  const hoy = new Date()
  const diffTime = vencimiento - hoy
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays > 0 ? diffDays : 0
})

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push({ name: 'login' })
}

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

      if (width > 800) {
        height = Math.round((height * 800) / width)
        width = 800
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

const submitProducto = async () => {
  try {
    let imagen_url = null
    
    // Si hay imagen, la subimos primero
    if (fileToUpload.value) {
      const formData = new FormData()
      formData.append('file', fileToUpload.value, 'imagen.webp')
      
      const token = localStorage.getItem('token')
      const response = await fetch('/api/productos/upload-image', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })
      
      if (!response.ok) throw new Error("Error al subir imagen")
      const dataImg = await response.json()
      imagen_url = dataImg.url
    }

    const payload = {
      nombre: nuevoProducto.value.nombre,
      precio: parseFloat(nuevoProducto.value.precio),
      descripcion: nuevoProducto.value.descripcion,
      disponible: nuevoProducto.value.disponible
    }
    
    if (imagen_url) {
      payload.imagen_url = imagen_url
    }

    let data;
    if (productoEnEdicion.value) {
      data = await put(`/api/productos/${productoEnEdicion.value.id}`, payload)
    } else {
      data = await post('/api/productos/', payload)
    }
    
    if (data) {
      await cargarProductos() // Recargar la lista desde el servidor
      cerrarModal()
    }
  } catch (err) {
    console.error("Error al guardar producto:", err)
  }
}

const editarProducto = (prod) => {
  productoEnEdicion.value = prod
  nuevoProducto.value = {
    nombre: prod.nombre,
    precio: prod.precio,
    descripcion: prod.descripcion || '',
    disponible: prod.disponible
  }
  imagenPrevia.value = prod.imagen_url
  fileToUpload.value = null
  mostrarModal.value = true
}

const borrarProducto = async (prod) => {
  if (!confirm(`¿Estás seguro de que deseas borrar "${prod.nombre}"? Esta acción no se puede deshacer.`)) {
    return
  }
  
  try {
    const data = await del(`/api/productos/${prod.id}`)
    if (data) {
      await cargarProductos()
    }
  } catch (err) {
    console.error("Error al borrar producto:", err)
  }
}

const cerrarModal = () => {
  mostrarModal.value = false
  productoEnEdicion.value = null
  nuevoProducto.value = { nombre: '', precio: '', descripcion: '', disponible: true }
  imagenPrevia.value = null
  fileToUpload.value = null
  if (fileInput.value) fileInput.value.value = null
}

const simularPago = async () => {
  try {
    const data = await post('/api/auth/me/simular-pago')
    if (data && data.status === 'success') {
      const userData = await get('/api/auth/me')
      if (userData) {
        meInfo.value = userData
      }
    }
  } catch (err) {
    console.error('Error al simular pago', err)
  }
}

const isUpdatingTheme = ref(false)
const cambiarTema = async (temaId) => {
  if (isUpdatingTheme.value || !meInfo.value) return
  isUpdatingTheme.value = true
  try {
    const res = await put('/api/auth/me/tema', { tema: temaId })
    if (res && res.status === 'success') {
      meInfo.value.comercio.tema = res.tema
    }
  } catch (err) {
    console.error('Error al cambiar tema', err)
  } finally {
    isUpdatingTheme.value = false
  }
}

onMounted(() => {
  cargarProductos()
})
</script>

<template>
  <div class="admin-dashboard">
    <header class="admin-header glass-header" style="display: flex; justify-content: space-between; align-items: center;">
      <h2>Panel de Control</h2>
      <button @click="handleLogout" class="btn-primary" style="width: auto; background: var(--color-text-light)">Cerrar Sesión</button>
    </header>
    
    <div class="admin-content content-wrapper">
      
      <!-- PAYWALL SIMULADO (TRIAL FINALIZADO O SIN SUSCRIPCIÓN) -->
      <div v-if="meInfo && !meInfo.comercio.activo" class="admin-card text-center" style="padding: 4rem 2rem; max-width: 600px; margin: 4rem auto; border: 2px solid var(--color-primary);">
        <h2 style="margin-bottom: 1rem; font-size: 2rem;">Período de Prueba Finalizado 🔒</h2>
        <p style="color: var(--color-text-light); font-size: 1.1rem; margin-bottom: 2rem;">
          Tu catálogo ha sido pausado. Para reactivarlo y seguir vendiendo sin límites, suscríbete a nuestro plan premium mensual.
        </p>
        <button @click="simularPago" class="btn-primary" style="font-size: 1.2rem; padding: 1rem; background: #009ee3; box-shadow: 0 10px 25px -5px rgba(0, 158, 227, 0.4);" :disabled="isLoading">
          {{ isLoading ? 'Procesando...' : 'Pagar Suscripción (Mercado Pago)' }}
        </button>
      </div>

      <!-- DASHBOARD ACTIVO -->
      <template v-else-if="meInfo && meInfo.comercio.activo">
        
        <!-- BANNER DE TRIAL -->
        <div v-if="meInfo.comercio.trial_vence && diasRestantes > 0 && diasRestantes <= 14" class="admin-card" style="margin-bottom: 2rem; background: rgba(234, 88, 12, 0.1); border: 2px solid var(--color-primary); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
          <div>
            <h3 style="color: var(--color-primary); margin-bottom: 0.25rem;">Estás en tu período de prueba (Quedan {{ diasRestantes }} días)</h3>
            <p style="color: var(--color-text-light); font-size: 0.95rem;">Tu catálogo está 100% operativo. Suscríbete antes de que termine para no perder ventas.</p>
          </div>
          <button @click="simularPago" class="btn-primary" style="width: auto; background: #009ee3; box-shadow: 0 4px 14px 0 rgba(0, 158, 227, 0.4);" :disabled="isLoading">
            Suscribirse Ahora
          </button>
        </div>

        <div class="admin-card" style="margin-bottom: 2rem; background: rgba(234, 88, 12, 0.05); border-color: rgba(234, 88, 12, 0.1);">
          <h3>¡Tu catálogo está en vivo! 🚀</h3>
          <p style="margin-top: 0.5rem; color: var(--color-text-light);">Comparte este enlace con tus clientes:</p>
          <a :href="'/' + meInfo.comercio.slug" target="_blank" style="display: block; margin-top: 0.5rem; font-weight: bold; color: var(--color-primary); word-break: break-all;">
            {{ originUrl }}/{{ meInfo.comercio.slug }}
          </a>
        </div>

        <div class="admin-card" style="margin-bottom: 2rem;">
          <h3 style="margin-bottom: 1rem;">Personaliza tu Tienda 🎨</h3>
          <p style="color: var(--color-text-light); margin-bottom: 1rem; font-size: 0.9rem;">Elige el color principal de tu catálogo público.</p>
          <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
            <button 
              v-for="tema in themes" 
              :key="tema.id"
              @click="cambiarTema(tema.id)"
              :disabled="isUpdatingTheme"
              style="width: 40px; height: 40px; border-radius: 50%; cursor: pointer; transition: transform 0.2s; position: relative;"
              :style="{ 
                backgroundColor: tema.color,
                border: meInfo.comercio.tema === tema.id ? '3px solid var(--color-text)' : '2px solid transparent',
                transform: meInfo.comercio.tema === tema.id ? 'scale(1.1)' : 'scale(1)'
              }"
              :title="tema.name"
            >
              <span v-if="meInfo.comercio.tema === tema.id" style="color: white; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 1rem;">✓</span>
            </button>
          </div>
        </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
        <h3>Mis Productos</h3>
        <button @click="mostrarModal = true" class="btn-primary" style="width: auto;">+ Nuevo Producto</button>
      </div>

      <div v-if="isLoading" class="loader">Cargando productos...</div>
      
      <div v-else-if="error" class="error-card">
        {{ error }}
      </div>
      
      <div v-else-if="productos.length === 0" class="admin-card text-center" style="padding: 3rem;">
        <p style="color: var(--color-text-light); margin-bottom: 1rem;">Aún no tienes productos en tu catálogo.</p>
        <p>¡Añade tu primer producto para empezar a vender!</p>
      </div>

      <div v-else class="product-grid">
        <div v-for="prod in productos" :key="prod.id" class="product-card">
          <img v-if="prod.imagen_url" :src="prod.imagen_url" class="product-image-real" alt="Producto" @click="imagenAmpliada = prod.imagen_url" />
          <div v-else class="product-image-placeholder"></div>
          <div class="product-info">
            <div style="display: flex; justify-content: space-between; align-items: start;">
              <h3 style="margin: 0; margin-bottom: 0.25rem;">{{ prod.nombre }}</h3>
              <span v-if="!prod.disponible" style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold;">Inactivo</span>
            </div>
            <p>${{ prod.precio }}</p>
            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
              <button @click="editarProducto(prod)" class="btn-primary" style="background: var(--color-text-light); padding: 0.5rem; font-size: 0.8rem;">Editar</button>
              <button @click="borrarProducto(prod)" class="btn-primary" style="background: #ef4444; padding: 0.5rem; font-size: 0.8rem;">Borrar</button>
            </div>
          </div>
        </div>
      </div>
      </template>
    </div>

    <!-- Modal Nuevo/Editar Producto -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <h3 style="margin-bottom: 1.5rem;">{{ productoEnEdicion ? 'Editar Producto' : 'Crear Nuevo Producto' }}</h3>
        
        <form @submit.prevent="submitProducto">
          
          <div class="form-group text-center" style="margin-bottom: 1.5rem;">
            <label style="display: block; margin-bottom: 0.5rem;">Foto del Producto (Opcional)</label>
            <img v-if="imagenPrevia" :src="imagenPrevia" style="width: 100%; max-width: 200px; height: 200px; object-fit: cover; border-radius: var(--radius-md); margin-bottom: 1rem;" />
            <div style="position: relative;">
              <input 
                ref="fileInput"
                type="file" 
                accept="image/*" 
                capture="environment" 
                @change="procesarImagen"
                style="display: none;"
                id="file-upload"
              />
              <label for="file-upload" class="btn-primary" style="display: inline-block; cursor: pointer; width: auto; background: var(--color-glass); color: var(--color-text);">
                📸 Tomar o Elegir Foto
              </label>
            </div>
          </div>

          <div class="form-group">
            <label>Nombre del Producto</label>
            <input v-model="nuevoProducto.nombre" type="text" class="form-input" required />
          </div>
          
          <div class="form-group">
            <label>Precio ($)</label>
            <input v-model="nuevoProducto.precio" type="number" step="0.01" class="form-input" required />
          </div>

          <div class="form-group">
            <label>Descripción corta (Opcional)</label>
            <textarea v-model="nuevoProducto.descripcion" class="form-input" rows="3"></textarea>
          </div>

          <div class="form-group" style="display: flex; align-items: center; gap: 0.75rem; background: rgba(0,0,0,0.05); padding: 1rem; border-radius: var(--radius-md);">
            <input type="checkbox" id="disponible" v-model="nuevoProducto.disponible" style="width: 20px; height: 20px;" />
            <label for="disponible" style="margin: 0; cursor: pointer; font-weight: bold;">
              Producto Visible al Público
            </label>
          </div>

          <div style="display: flex; gap: 1rem; margin-top: 2rem;">
            <button type="button" @click="cerrarModal" class="btn-primary" style="background: var(--color-text-light);">Cancelar</button>
            <button type="submit" class="btn-primary" :disabled="isLoading">
              {{ isLoading ? 'Guardando...' : 'Guardar Producto' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Imagen Ampliada -->
    <div v-if="imagenAmpliada" class="modal-overlay" @click.self="imagenAmpliada = null" style="background: rgba(0,0,0,0.85); z-index: 2000; padding: 2rem;">
      <button @click="imagenAmpliada = null" style="position: absolute; top: 1.5rem; right: 1.5rem; background: rgba(255,255,255,0.1); border: none; color: white; font-size: 2rem; cursor: pointer; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(4px);">&times;</button>
      <img :src="imagenAmpliada" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: var(--radius-md); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);" />
    </div>
  </div>
</template>
