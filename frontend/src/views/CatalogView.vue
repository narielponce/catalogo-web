<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '../composables/useApi'

const route = useRoute()
const slug = route.params.slug
const { get, isLoading, error } = useApi()

const comercio = ref(null)
const productos = ref([])
const imagenAmpliadaInfo = ref(null)

// --- Estado del Carrito ---
const carrito = ref([])
const mostrarCarrito = ref(false)

const cantidadTotal = computed(() => {
  return carrito.value.reduce((total, item) => total + item.cantidad, 0)
})

const precioTotal = computed(() => {
  return carrito.value.reduce((total, item) => total + (item.producto.precio * item.cantidad), 0)
})

const obtenerCantidad = (producto) => {
  const item = carrito.value.find(i => i.producto.id === producto.id)
  return item ? item.cantidad : 0
}

const agregarAlCarrito = (producto) => {
  carrito.value.push({ producto, cantidad: 1 })
}

const modificarCantidad = (producto, delta) => {
  const index = carrito.value.findIndex(i => i.producto.id === producto.id)
  if (index !== -1) {
    const nuevaCantidad = carrito.value[index].cantidad + delta
    if (nuevaCantidad <= 0) {
      carrito.value.splice(index, 1) // Eliminar si llega a 0
    } else {
      carrito.value[index].cantidad = nuevaCantidad
    }
  }
}

const formatearPrecio = (valor) => {
  return new Intl.NumberFormat('es-AR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(valor)
}

const activeImageIndices = ref({})

const obtenerImagenesDetalle = (imagenUrl) => {
  if (!imagenUrl) return []
  return imagenUrl.split(',').map(item => {
    const parts = item.split('|')
    return {
      highres: parts[0],
      thumb: parts[1] || parts[0]
    }
  })
}

const getActiveIndex = (prodId) => {
  return activeImageIndices.value[prodId] || 0
}

const setActiveIndex = (prodId, index) => {
  activeImageIndices.value[prodId] = index
}

const enviarPedidoPorWhatsApp = () => {
  if (!comercio.value || carrito.value.length === 0) return
  
  const numero = comercio.value.whatsapp
  let mensaje = `Hola! Quiero hacer este pedido:\n`
  
  carrito.value.forEach(item => {
    mensaje += `- ${item.cantidad}x ${item.producto.nombre} ($${formatearPrecio(item.producto.precio * item.cantidad)})\n`
  })
  
  mensaje += `\nTotal a pagar: $${formatearPrecio(precioTotal.value)}`
  
  const url = `https://wa.me/${numero}?text=${encodeURIComponent(mensaje)}`
  window.open(url, '_blank')
}
// --------------------------

onMounted(async () => {
  try {
    // 1. Obtener datos del comercio
    const comercioData = await get(`/api/public/comercios/${slug}`)
    if (comercioData) {
      comercio.value = comercioData
    }
    
    // 2. Obtener productos de este comercio
    const productosData = await get(`/api/public/comercios/${slug}/productos`)
    if (productosData) {
      productos.value = productosData
    }
    
    // Aplicar tema si existe
    if (comercio.value && comercio.value.tema) {
      const themes = {
        'terracotta': {
          primary: '#ea580c',
          primaryHover: '#c2410c',
          bg: '#fffbf7',
          text: '#292524',
          textLight: '#78716c',
          surface: 'rgba(255, 255, 255, 0.75)',
          surfaceHover: 'rgba(255, 255, 255, 0.9)'
        },
        'blue': {
          primary: '#2563eb',
          primaryHover: '#1d4ed8',
          bg: '#f8fafc',
          text: '#0f172a',
          textLight: '#64748b',
          surface: 'rgba(255, 255, 255, 0.8)',
          surfaceHover: 'rgba(255, 255, 255, 0.95)'
        },
        'emerald': {
          primary: '#059669',
          primaryHover: '#047857',
          bg: '#f0fdf4',
          text: '#064e3b',
          textLight: '#374151',
          surface: 'rgba(255, 255, 255, 0.8)',
          surfaceHover: 'rgba(255, 255, 255, 0.95)'
        },
        'violet': {
          primary: '#7c3aed',
          primaryHover: '#6d28d9',
          bg: '#faf5ff',
          text: '#3b0764',
          textLight: '#4b5563',
          surface: 'rgba(255, 255, 255, 0.8)',
          surfaceHover: 'rgba(255, 255, 255, 0.95)'
        },
        'dark': {
          primary: '#f97316',
          primaryHover: '#ea580c',
          bg: '#0c0a09',
          text: '#fafaf9',
          textLight: '#a8a29e',
          surface: 'rgba(28, 25, 23, 0.7)',
          surfaceHover: 'rgba(41, 37, 36, 0.9)'
        }
      }
      const theme = themes[comercio.value.tema] || themes['terracotta']
      
      document.documentElement.style.setProperty('--color-primary', theme.primary)
      document.documentElement.style.setProperty('--color-primary-hover', theme.primaryHover)
      document.documentElement.style.setProperty('--color-bg', theme.bg)
      document.documentElement.style.setProperty('--color-text', theme.text)
      document.documentElement.style.setProperty('--color-text-light', theme.textLight)
      document.documentElement.style.setProperty('--color-surface', theme.surface)
      document.documentElement.style.setProperty('--color-surface-hover', theme.surfaceHover)
    }
  } catch (err) {
    console.error('Catálogo no encontrado', err)
  }
})

onUnmounted(() => {
  // Restaurar los colores del sistema (para Landing y Panel de Control)
  document.documentElement.style.removeProperty('--color-primary')
  document.documentElement.style.removeProperty('--color-primary-hover')
  document.documentElement.style.removeProperty('--color-bg')
  document.documentElement.style.removeProperty('--color-text')
  document.documentElement.style.removeProperty('--color-text-light')
  document.documentElement.style.removeProperty('--color-surface')
  document.documentElement.style.removeProperty('--color-surface-hover')
})

// Eliminamos la función comprarPorWhatsApp vieja, ya no se usa.
</script>

<template>
  <main class="catalog-container">
    <header v-if="comercio" style="position: relative; background: var(--color-surface); margin-bottom: 2rem; border-bottom-left-radius: var(--radius-lg); border-bottom-right-radius: var(--radius-lg); box-shadow: var(--shadow-glass); overflow: hidden;">
      <!-- Portada -->
      <div class="portada-container">
        <img v-if="comercio.portada_url" :src="comercio.portada_url" alt="Portada" class="portada-img" />
        <div v-else class="portada-img" style="background: linear-gradient(135deg, rgba(128,128,128,0.1), rgba(128,128,128,0.2));"></div>
      </div>

      <!-- Contenido Solapado -->
      <div class="header-content text-center" style="padding: 0 1.5rem 2rem 1.5rem; display: flex; flex-direction: column; align-items: center;">
        <!-- Logo solapado -->
        <div class="logo-wrapper">
          <img v-if="comercio.logo_url" :src="comercio.logo_url" alt="Logo" class="logo-img" />
          <div v-else class="logo-img placeholder-logo">
            🛍️
          </div>
        </div>
        
        <!-- Textos -->
        <div style="margin-top: 1rem;">
          <h1 style="margin-bottom: 0.25rem; font-size: 2rem;">{{ comercio.nombre }}</h1>
          <p v-if="comercio.descripcion" style="color: var(--color-text-light); font-size: 1.1rem; max-width: 600px; margin: 0 auto;">{{ comercio.descripcion }}</p>
        </div>
      </div>
    </header>

    <div class="content-wrapper">
      <div v-if="isLoading" class="loader">Cargando catálogo...</div>
      
      <div v-else-if="error" class="error-card text-center" style="padding: 3rem;">
        <h3>Ups...</h3>
        <p>No pudimos encontrar este catálogo.</p>
        <p>Revisa que la URL sea la correcta.</p>
      </div>

      <div v-else-if="comercio" class="product-grid">
        <div v-if="productos.length === 0" style="grid-column: 1 / -1; text-align: center; color: var(--color-text-light);">
          Este negocio aún no tiene productos publicados.
        </div>
        
        <div v-for="prod in productos" :key="prod.id" class="product-card">
          <div v-if="prod.imagen_url" style="position: relative; width: 100%; height: 250px; overflow: hidden; background: rgba(0,0,0,0.03); border-top-left-radius: inherit; border-top-right-radius: inherit;">
            <!-- Imagen actual -->
            <img 
              :src="obtenerImagenesDetalle(prod.imagen_url)[getActiveIndex(prod.id)]?.thumb" 
              class="product-image-real" 
              alt="Producto" 
              @click="imagenAmpliadaInfo = { urls: obtenerImagenesDetalle(prod.imagen_url).map(img => img.highres), currentIndex: getActiveIndex(prod.id) }"
              style="width: 100%; height: 100%; object-fit: cover; cursor: pointer; transition: opacity 0.3s ease; border-radius: 0;"
            />
            
            <!-- Flechas de navegación (si hay más de 1 imagen) -->
            <template v-if="obtenerImagenesDetalle(prod.imagen_url).length > 1">
              <button 
                @click.stop="setActiveIndex(prod.id, (getActiveIndex(prod.id) - 1 + obtenerImagenesDetalle(prod.imagen_url).length) % obtenerImagenesDetalle(prod.imagen_url).length)"
                style="position: absolute; left: 8px; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,0.5); color: white; border: none; border-radius: 50%; width: 32px; height: 32px; display: flex; justify-content: center; align-items: center; cursor: pointer; font-size: 1.2rem; font-weight: bold; backdrop-filter: blur(4px); z-index: 10; border-color: transparent;"
              >
                ‹
              </button>
              <button 
                @click.stop="setActiveIndex(prod.id, (getActiveIndex(prod.id) + 1) % obtenerImagenesDetalle(prod.imagen_url).length)"
                style="position: absolute; right: 8px; top: 50%; transform: translateY(-50%); background: rgba(0,0,0,0.5); color: white; border: none; border-radius: 50%; width: 32px; height: 32px; display: flex; justify-content: center; align-items: center; cursor: pointer; font-size: 1.2rem; font-weight: bold; backdrop-filter: blur(4px); z-index: 10; border-color: transparent;"
              >
                ›
              </button>
              
              <!-- Puntos de paginación abajo -->
              <div style="position: absolute; bottom: 12px; left: 50%; transform: translateX(-50%); display: flex; gap: 6px; z-index: 10;">
                <span 
                  v-for="(img, idx) in obtenerImagenesDetalle(prod.imagen_url)" 
                  :key="idx"
                  @click.stop="setActiveIndex(prod.id, idx)"
                  style="width: 8px; height: 8px; border-radius: 50%; cursor: pointer; transition: all 0.2s;"
                  :style="{ 
                    background: idx === getActiveIndex(prod.id) ? 'var(--color-primary)' : 'rgba(255,255,255,0.6)',
                    transform: idx === getActiveIndex(prod.id) ? 'scale(1.2)' : 'scale(1)'
                  }"
                ></span>
              </div>
            </template>
          </div>
          <div v-else class="product-image-placeholder"></div>
          <div class="product-info">
            <h3>{{ prod.nombre }}</h3>
            <p v-if="prod.descripcion" style="font-size: 0.9rem; color: var(--color-text-light); margin-bottom: 0.5rem; font-weight: normal;">
              {{ prod.descripcion }}
            </p>
            <p>${{ formatearPrecio(prod.precio) }}</p>
            
            <div v-if="obtenerCantidad(prod) > 0" style="display: flex; align-items: center; justify-content: space-between; background: rgba(128,128,128,0.1); border-radius: var(--radius-md); padding: 0.5rem; margin-top: auto;">
              <button @click="modificarCantidad(prod, -1)" class="btn-primary" style="width: 32px; height: 32px; padding: 0; border-radius: 50%; background: var(--color-text-light);">-</button>
              <span style="font-weight: bold; font-size: 1.1rem;">{{ obtenerCantidad(prod) }}</span>
              <button @click="modificarCantidad(prod, 1)" class="btn-primary" style="width: 32px; height: 32px; padding: 0; border-radius: 50%;">+</button>
            </div>
            
            <button v-else @click="agregarAlCarrito(prod)" class="btn-primary" style="margin-top: auto;">
              Añadir al Carrito 🛒
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Imagen Ampliada -->
    <div v-if="imagenAmpliadaInfo" class="modal-overlay" @click.self="imagenAmpliadaInfo = null" style="background: rgba(0,0,0,0.85); z-index: 2000; padding: 2rem;">
      <button @click="imagenAmpliadaInfo = null" style="position: absolute; top: 1.5rem; right: 1.5rem; background: rgba(255,255,255,0.1); border: none; color: white; font-size: 2rem; cursor: pointer; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(4px);">&times;</button>
      
      <button v-if="imagenAmpliadaInfo.urls.length > 1" @click.stop="imagenAmpliadaInfo.currentIndex = (imagenAmpliadaInfo.currentIndex - 1 + imagenAmpliadaInfo.urls.length) % imagenAmpliadaInfo.urls.length" style="position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); background: rgba(255,255,255,0.2); color: white; border: none; border-radius: 50%; width: 50px; height: 50px; display: flex; justify-content: center; align-items: center; cursor: pointer; font-size: 2rem; backdrop-filter: blur(4px); z-index: 2010;">
        ‹
      </button>

      <img :src="imagenAmpliadaInfo.urls[imagenAmpliadaInfo.currentIndex]" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: var(--radius-md); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);" />

      <button v-if="imagenAmpliadaInfo.urls.length > 1" @click.stop="imagenAmpliadaInfo.currentIndex = (imagenAmpliadaInfo.currentIndex + 1) % imagenAmpliadaInfo.urls.length" style="position: absolute; right: 1rem; top: 50%; transform: translateY(-50%); background: rgba(255,255,255,0.2); color: white; border: none; border-radius: 50%; width: 50px; height: 50px; display: flex; justify-content: center; align-items: center; cursor: pointer; font-size: 2rem; backdrop-filter: blur(4px); z-index: 2010;">
        ›
      </button>
      
      <!-- Puntos de paginación -->
      <div v-if="imagenAmpliadaInfo.urls.length > 1" style="position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%); display: flex; gap: 8px;">
        <span v-for="(img, idx) in imagenAmpliadaInfo.urls" :key="idx" @click.stop="imagenAmpliadaInfo.currentIndex = idx" style="width: 10px; height: 10px; border-radius: 50%; cursor: pointer; transition: all 0.2s;" :style="{ background: idx === imagenAmpliadaInfo.currentIndex ? 'var(--color-primary)' : 'rgba(255,255,255,0.5)', transform: idx === imagenAmpliadaInfo.currentIndex ? 'scale(1.2)' : 'scale(1)' }"></span>
      </div>
    </div>

    <!-- Botón flotante del Carrito -->
    <button 
      v-if="cantidadTotal > 0" 
      @click="mostrarCarrito = true" 
      class="cart-floating-btn"
    >
      <span class="cart-badge">{{ cantidadTotal }}</span>
      🛒 Ver Carrito - ${{ formatearPrecio(precioTotal) }}
    </button>

    <!-- Modal del Carrito -->
    <div v-if="mostrarCarrito" class="modal-overlay" @click.self="mostrarCarrito = false" style="z-index: 3000;">
      <div class="modal-content" style="max-width: 450px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
          <h3 style="margin: 0;">Tu Pedido</h3>
          <button @click="mostrarCarrito = false" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--color-text);">&times;</button>
        </div>
        
        <div v-if="carrito.length === 0" style="text-align: center; color: var(--color-text-light); padding: 2rem 0;">
          El carrito está vacío.
        </div>
        
        <div v-else>
          <div v-for="item in carrito" :key="item.producto.id" style="display: flex; justify-content: space-between; align-items: center; padding: 1rem 0; border-bottom: 1px solid rgba(128,128,128,0.2);">
            <div style="flex: 1; padding-right: 1rem;">
              <h4 style="margin: 0; font-size: 1rem; margin-bottom: 0.25rem;">{{ item.producto.nombre }}</h4>
              <div style="display: flex; gap: 0.5rem; align-items: center;">
                <button @click="modificarCantidad(item.producto, -1)" style="background: var(--color-text-light); color: white; border: none; border-radius: 4px; width: 24px; height: 24px; cursor: pointer;">-</button>
                <span style="font-weight: bold;">{{ item.cantidad }}</span>
                <button @click="modificarCantidad(item.producto, 1)" style="background: var(--color-primary); color: white; border: none; border-radius: 4px; width: 24px; height: 24px; cursor: pointer;">+</button>
              </div>
            </div>
            <div style="font-weight: bold; font-size: 1.1rem; color: var(--color-primary);">
              ${{ formatearPrecio(item.producto.precio * item.cantidad) }}
            </div>
          </div>
          
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; font-size: 1.3rem; font-weight: bold;">
            <span>Total:</span>
            <span>${{ formatearPrecio(precioTotal) }}</span>
          </div>
          
          <button @click="enviarPedidoPorWhatsApp" class="btn-primary" style="margin-top: 2rem; background-color: #25D366; padding: 1rem; font-size: 1.1rem;">
            WhatsApp - Enviar Pedido
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.portada-container {
  width: 100%;
  height: 150px;
}
.portada-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.logo-wrapper {
  margin-top: -50px;
  position: relative;
  z-index: 2;
}
.logo-img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid var(--color-surface);
  box-shadow: var(--shadow-md);
  background: var(--color-surface);
}
.placeholder-logo {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover));
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  font-size: 3rem;
}
@media (min-width: 768px) {
  .portada-container {
    height: 260px;
  }
  .logo-wrapper {
    margin-top: -60px;
  }
  .logo-img {
    width: 120px;
    height: 120px;
    border-width: 5px;
  }
}
</style>
