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
const imagenesProducto = ref([]) // [{ id, url, blob, isExisting }]
const imagenAmpliada = ref(null)
const productoEnEdicion = ref(null)

const nuevoProducto = ref({
  nombre: '',
  precio: '',
  descripcion: '',
  disponible: true
})

const formPerfil = ref({
  nombre: '',
  descripcion: '',
  whatsapp: '',
  email: ''
})
const isUpdatingPerfil = ref(false)
const mensajePerfil = ref('')
const errorPerfil = ref('')
const mostrarPerfilForm = ref(false)

const fileInputLogo = ref(null)
const logoPrevia = ref(null)
const fileLogoToUpload = ref(null)

const fileInputPortada = ref(null)
const portadaPrevia = ref(null)
const filePortadaToUpload = ref(null)

const cargarProductos = async () => {
  try {
    // Cargar info del usuario para obtener el slug
    const userData = await get('/api/auth/me')
    if (userData) {
      meInfo.value = userData
      logoPrevia.value = userData.comercio.logo_url || null
      portadaPrevia.value = userData.comercio.portada_url || null
      formPerfil.value = {
        nombre: userData.comercio.nombre,
        descripcion: userData.comercio.descripcion || '',
        whatsapp: userData.comercio.whatsapp,
        email: userData.email
      }
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

const procesarLogo = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      let width = img.width
      let height = img.height

      if (width > 300) {
        height = Math.round((height * 300) / width)
        width = 300
      }

      canvas.width = width
      canvas.height = height

      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)

      canvas.toBlob((blob) => {
        fileLogoToUpload.value = blob
        logoPrevia.value = URL.createObjectURL(blob)
      }, 'image/webp', 0.8)
    }
    img.src = e.target.result
  }
  reader.readAsDataURL(file)
}

const procesarPortada = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      let width = img.width
      let height = img.height

      if (width > 1200) {
        height = Math.round((height * 1200) / width)
        width = 1200
      }

      canvas.width = width
      canvas.height = height

      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)

      canvas.toBlob((blob) => {
        filePortadaToUpload.value = blob
        portadaPrevia.value = URL.createObjectURL(blob)
      }, 'image/webp', 0.8)
    }
    img.src = e.target.result
  }
  reader.readAsDataURL(file)
}

const guardarPerfil = async () => {
  isUpdatingPerfil.value = true
  mensajePerfil.value = ''
  errorPerfil.value = ''
  try {
    // Si hay un logo nuevo para subir, lo subimos primero
    if (fileLogoToUpload.value) {
      const formData = new FormData()
      formData.append('file', fileLogoToUpload.value, 'logo.webp')
      
      const token = localStorage.getItem('token')
      const response = await fetch('/api/auth/me/logo', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })
      
      if (!response.ok) throw new Error("Error al subir el logo de la tienda")
      const dataLogo = await response.json()
      logoPrevia.value = dataLogo.logo_url
      if (meInfo.value) {
        meInfo.value.comercio.logo_url = dataLogo.logo_url
      }
      fileLogoToUpload.value = null
    }

    if (filePortadaToUpload.value) {
      const formData = new FormData()
      formData.append('file', filePortadaToUpload.value, 'portada.webp')
      
      const token = localStorage.getItem('token')
      const response = await fetch('/api/auth/me/portada', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      })
      
      if (!response.ok) throw new Error("Error al subir la portada de la tienda")
      const dataPortada = await response.json()
      portadaPrevia.value = dataPortada.portada_url
      if (meInfo.value) {
        meInfo.value.comercio.portada_url = dataPortada.portada_url
      }
      filePortadaToUpload.value = null
    }

    const res = await put('/api/auth/me/perfil', formPerfil.value)
    if (res && res.status === 'success') {
      mensajePerfil.value = '¡Perfil de tienda actualizado con éxito!'
      
      // Actualizar localmente la info del usuario/comercio
      meInfo.value.email = res.email
      meInfo.value.comercio.nombre = res.comercio.nombre
      meInfo.value.comercio.slug = res.comercio.slug
      meInfo.value.comercio.whatsapp = res.comercio.whatsapp
      meInfo.value.comercio.descripcion = res.comercio.descripcion
    }
  } catch (err) {
    errorPerfil.value = err.message || 'Error al guardar los cambios'
  } finally {
    isUpdatingPerfil.value = false
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

const abrirNuevoProducto = () => {
  productoEnEdicion.value = null
  nuevoProducto.value = {
    nombre: '',
    precio: '',
    descripcion: '',
    disponible: true
  }
  imagenesProducto.value = []
  mostrarModal.value = true
}

const procesarImagen = (event) => {
  const files = event.target.files
  if (!files || files.length === 0) return

  const espaciosDisponibles = 3 - imagenesProducto.value.length
  const filesToProcess = Array.from(files).slice(0, espaciosDisponibles)

  filesToProcess.forEach((file) => {
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

        canvas.toBlob((blob) => {
          const tempUrl = URL.createObjectURL(blob)
          imagenesProducto.value.push({
            id: Date.now() + Math.random().toString(36).substr(2, 9),
            url: tempUrl,
            blob: blob,
            isExisting: false
          })
        }, 'image/webp', 0.8)
      }
      img.src = e.target.result
    }
    reader.readAsDataURL(file)
  })

  if (fileInput.value) fileInput.value.value = ''
}

const eliminarImagen = (index) => {
  const img = imagenesProducto.value[index]
  if (!img.isExisting && img.url) {
    URL.revokeObjectURL(img.url)
  }
  imagenesProducto.value.splice(index, 1)
}

const submitProducto = async () => {
  try {
    isLoading.value = true
    const urlsFinales = []
    
    for (let img of imagenesProducto.value) {
      if (img.isExisting) {
        urlsFinales.push(img.url)
      } else if (img.blob) {
        const formData = new FormData()
        formData.append('file', img.blob, 'imagen.webp')
        
        const token = localStorage.getItem('token')
        const response = await fetch('/api/productos/upload-image', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` },
          body: formData
        })
        
        if (!response.ok) throw new Error("Error al subir una de las imágenes")
        const dataImg = await response.json()
        urlsFinales.push(dataImg.url)
      }
    }

    const payload = {
      nombre: nuevoProducto.value.nombre,
      precio: parseFloat(nuevoProducto.value.precio),
      descripcion: nuevoProducto.value.descripcion,
      disponible: nuevoProducto.value.disponible,
      imagen_url: urlsFinales.join(',')
    }

    let data;
    if (productoEnEdicion.value) {
      data = await put(`/api/productos/${productoEnEdicion.value.id}`, payload)
    } else {
      data = await post('/api/productos/', payload)
    }
    
    if (data) {
      await cargarProductos()
      cerrarModal()
    }
  } catch (err) {
    console.error("Error al guardar producto:", err)
  } finally {
    isLoading.value = false
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
  
  const urls = prod.imagen_url ? prod.imagen_url.split(',') : []
  imagenesProducto.value = urls.map((url, index) => ({
    id: index,
    url: url,
    blob: null,
    isExisting: true
  }))
  
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
  
  imagenesProducto.value.forEach((img) => {
    if (!img.isExisting && img.url) {
      URL.revokeObjectURL(img.url)
    }
  })
  imagenesProducto.value = []
  
  if (fileInput.value) fileInput.value.value = ''
}

const simularPago = async () => {
  try {
    isLoading.value = true
    const data = await post('/api/auth/me/crear-preferencia')
    if (data && data.init_point) {
      window.location.href = data.init_point
    }
  } catch (err) {
    console.error('Error al generar link de pago', err)
  } finally {
    isLoading.value = false
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

const formatearPrecio = (valor) => {
  return new Intl.NumberFormat('es-AR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(valor)
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

        <div class="admin-card theme-card" style="margin-bottom: 2rem;">
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
        <button @click="abrirNuevoProducto" class="btn-primary" style="width: auto;">+ Nuevo Producto</button>
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
          <img v-if="prod.imagen_url" :src="prod.imagen_url.split(',')[0]" class="product-image-real" alt="Producto" @click="imagenAmpliada = prod.imagen_url.split(',')[0]" />
          <div v-else class="product-image-placeholder"></div>
          <div class="product-info">
            <div style="display: flex; justify-content: space-between; align-items: start;">
              <h3 style="margin: 0; margin-bottom: 0.25rem;">{{ prod.nombre }}</h3>
              <span v-if="!prod.disponible" style="background: #ef4444; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: bold;">Inactivo</span>
            </div>
            <p>${{ formatearPrecio(prod.precio) }}</p>
            <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
              <button @click="editarProducto(prod)" class="btn-primary" style="background: var(--color-text-light); padding: 0.5rem; font-size: 0.8rem;">Editar</button>
              <button @click="borrarProducto(prod)" class="btn-primary" style="background: #ef4444; padding: 0.5rem; font-size: 0.8rem;">Borrar</button>
            </div>
          </div>
        </div>
      </div>

        <!-- Sección Colapsable para Editar Datos de la Tienda -->
        <div class="admin-card" style="margin-top: 3rem;">
          <div @click="mostrarPerfilForm = !mostrarPerfilForm" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none;">
            <h3 style="margin: 0; display: flex; align-items: center; gap: 0.5rem;">
              Editar Datos de la Tienda 📝
            </h3>
            <span style="font-size: 1.2rem; transition: transform 0.2s;" :style="{ transform: mostrarPerfilForm ? 'rotate(180deg)' : 'rotate(0)' }">
              ▼
            </span>
          </div>

          <div v-show="mostrarPerfilForm" style="margin-top: 1.5rem; border-top: 1px solid rgba(128,128,128,0.1); padding-top: 1.5rem;">
            <p style="color: var(--color-text-light); margin-bottom: 1.5rem; font-size: 0.9rem;">
              Actualiza el nombre, descripción y datos de contacto de tu negocio.
              <span style="display: block; margin-top: 0.5rem; font-weight: bold; color: var(--color-primary);" v-if="formPerfil.nombre !== meInfo.comercio.nombre">
                ⚠️ Nota: Cambiar el nombre modificará tu enlace de catálogo.
              </span>
            </p>

            <!-- LOGO DE LA TIENDA -->
            <div style="display: flex; align-items: center; gap: 1.5rem; margin-bottom: 2rem; background: rgba(128,128,128,0.05); padding: 1rem; border-radius: var(--radius-lg);">
              <div style="position: relative; width: 80px; height: 80px;">
                <img v-if="logoPrevia" :src="logoPrevia" alt="Logo Previo" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid var(--color-primary);" />
                <div v-else style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover)); display: flex; justify-content: center; align-items: center; color: white; font-size: 2.2rem;">
                  🛍️
                </div>
              </div>
              <div>
                <label class="btn-primary" style="width: auto; display: inline-block; cursor: pointer; padding: 0.5rem 1rem; font-size: 0.85rem; background: var(--color-text-light);">
                  Subir nuevo logo
                  <input ref="fileInputLogo" type="file" accept="image/*" @change="procesarLogo" style="display: none;" />
                </label>
                <p style="font-size: 0.75rem; color: var(--color-text-light); margin-top: 0.4rem;">Formatos recomendados: PNG, JPG, WEBP. Tamaño max: 300x300px.</p>
              </div>
            </div>

            <!-- PORTADA DE LA TIENDA -->
            <div style="display: flex; flex-direction: column; gap: 1rem; margin-bottom: 2rem; background: rgba(128,128,128,0.05); padding: 1rem; border-radius: var(--radius-lg);">
              <label style="font-weight: 500; color: var(--color-text-light);">Portada de la Tienda</label>
              <div style="position: relative; width: 100%; height: 120px; border-radius: var(--radius-md); overflow: hidden; background: linear-gradient(135deg, rgba(128,128,128,0.1), rgba(128,128,128,0.2));">
                <img v-if="portadaPrevia" :src="portadaPrevia" alt="Portada Previa" style="width: 100%; height: 100%; object-fit: cover;" />
                <div v-else style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; color: var(--color-text-light);">
                  Sin imagen de portada
                </div>
              </div>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <label class="btn-primary" style="width: auto; display: inline-block; cursor: pointer; padding: 0.5rem 1rem; font-size: 0.85rem; background: var(--color-text-light);">
                  Subir nueva portada
                  <input ref="fileInputPortada" type="file" accept="image/*" @change="procesarPortada" style="display: none;" />
                </label>
                <p style="font-size: 0.75rem; color: var(--color-text-light); margin: 0;">Recomendado: 1200x400px.</p>
              </div>
            </div>
            
            <form @submit.prevent="guardarPerfil">
              <div class="form-group">
                <label>Nombre del Negocio</label>
                <input v-model="formPerfil.nombre" type="text" class="form-input" required />
              </div>
              
              <div class="form-group">
                <label>Descripción / Eslogan</label>
                <textarea v-model="formPerfil.descripcion" class="form-input" rows="2" style="resize: vertical; font-family: inherit;"></textarea>
              </div>
              
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                <div class="form-group" style="margin-bottom: 0;">
                  <label>WhatsApp (con código de país)</label>
                  <input v-model="formPerfil.whatsapp" type="text" class="form-input" placeholder="ej: 5491122334455" required />
                </div>
                <div class="form-group" style="margin-bottom: 0;">
                  <label>Email de contacto</label>
                  <input v-model="formPerfil.email" type="email" class="form-input" required />
                </div>
              </div>

              <div v-if="mensajePerfil" class="success-card" style="margin-bottom: 1.5rem; color: #10b981; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); padding: 0.75rem; border-radius: var(--radius-md); text-align: center; font-weight: 500;">
                {{ mensajePerfil }}
              </div>
              <div v-if="errorPerfil" class="error-card" style="margin-bottom: 1.5rem; padding: 0.75rem;">
                {{ errorPerfil }}
              </div>

              <button type="submit" class="btn-primary" style="width: auto; padding: 0.75rem 2rem;" :disabled="isUpdatingPerfil">
                {{ isUpdatingPerfil ? 'Guardando...' : 'Guardar Cambios' }}
              </button>
            </form>
          </div>
        </div>
      </template>
    </div>

    <!-- Modal Nuevo/Editar Producto -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="cerrarModal">
      <div class="modal-content">
        <h3 style="margin-bottom: 1.5rem;">{{ productoEnEdicion ? 'Editar Producto' : 'Crear Nuevo Producto' }}</h3>
        
        <form @submit.prevent="submitProducto">
          
          <div class="form-group" style="margin-bottom: 1.5rem;">
            <label style="display: block; margin-bottom: 0.75rem; font-weight: bold;">Fotos del Producto (Máx. 3)</label>
            
            <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem;">
              <!-- Miniaturas de imágenes cargadas -->
              <div v-for="(img, idx) in imagenesProducto" :key="img.id" style="position: relative; width: 80px; height: 80px; border-radius: var(--radius-md); overflow: hidden; border: 2px solid var(--color-primary);">
                <img :src="img.url" style="width: 100%; height: 100%; object-fit: cover;" />
                <button type="button" @click="eliminarImagen(idx)" style="position: absolute; top: 4px; right: 4px; background: rgba(239, 68, 68, 0.9); color: white; border: none; border-radius: 50%; width: 20px; height: 20px; display: flex; justify-content: center; align-items: center; cursor: pointer; font-size: 0.7rem; font-weight: bold; line-height: 1; border-color: transparent;">
                  ✕
                </button>
              </div>

              <!-- Slot vacío/botón para agregar -->
              <div v-if="imagenesProducto.length < 3" style="position: relative; width: 80px; height: 80px;">
                <input 
                  ref="fileInput"
                  type="file" 
                  accept="image/*" 
                  multiple
                  @change="procesarImagen"
                  style="display: none;"
                  id="file-upload-multiple"
                />
                <label for="file-upload-multiple" style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: center; align-items: center; border: 2px dashed rgba(128,128,128,0.3); border-radius: var(--radius-md); cursor: pointer; background: rgba(128,128,128,0.05); transition: background 0.2s; margin: 0;">
                  <span style="font-size: 1.5rem; color: var(--color-text-light);">+</span>
                  <span style="font-size: 0.65rem; color: var(--color-text-light);">Subir foto</span>
                </label>
              </div>
            </div>
            <p style="font-size: 0.75rem; color: var(--color-text-light);">Formatos recomendados: PNG, JPG, WEBP. Se optimizarán automáticamente al subir.</p>
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

<style scoped>
.theme-card {
  background: rgba(255, 255, 255, 0.9) !important;
  border: 1px solid rgba(0, 0, 0, 0.05) !important;
}
@media (prefers-color-scheme: dark) {
  .theme-card {
    background: rgba(255, 255, 255, 0.15) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
  }
}
</style>
