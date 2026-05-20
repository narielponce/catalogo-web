<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '../composables/useApi'

const route = useRoute()
const slug = route.params.slug
const { get, isLoading, error } = useApi()

const comercio = ref(null)
const productos = ref([])
const imagenAmpliada = ref(null)

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
        'terracotta': '#ea580c',
        'blue': '#3b82f6',
        'emerald': '#10b981',
        'violet': '#8b5cf6',
        'dark': '#111827'
      }
      const colorHex = themes[comercio.value.tema] || '#ea580c'
      document.documentElement.style.setProperty('--color-primary', colorHex)
      // Opcional: Generar un color hover oscureciendo un poco
      document.documentElement.style.setProperty('--color-primary-hover', colorHex + 'dd')
    }
  } catch (err) {
    console.error('Catálogo no encontrado', err)
  }
})

onUnmounted(() => {
  // Restaurar los colores del sistema (para Landing y Panel de Control)
  document.documentElement.style.removeProperty('--color-primary')
  document.documentElement.style.removeProperty('--color-primary-hover')
})

// Eliminamos la función comprarPorWhatsApp vieja, ya no se usa.
</script>

<template>
  <main class="catalog-container">
    <header class="glass-header text-center" v-if="comercio" style="padding: 2rem 1.5rem;">
      <div style="display: flex; flex-direction: column; align-items: center; gap: 1rem;">
        <img v-if="comercio.logo_url" :src="comercio.logo_url" alt="Logo" style="width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid var(--color-primary); box-shadow: var(--shadow-md);" />
        <div v-else style="width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, var(--color-primary), var(--color-primary-hover)); display: flex; justify-content: center; align-items: center; color: white; font-size: 2.5rem; box-shadow: var(--shadow-md);">
          🛍️
        </div>
        <div>
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
          <img v-if="prod.imagen_url" :src="prod.imagen_url" class="product-image-real" alt="Producto" @click="imagenAmpliada = prod.imagen_url" />
          <div v-else class="product-image-placeholder"></div>
          <div class="product-info">
            <h3>{{ prod.nombre }}</h3>
            <p v-if="prod.descripcion" style="font-size: 0.9rem; color: var(--color-text-light); margin-bottom: 0.5rem; font-weight: normal;">
              {{ prod.descripcion }}
            </p>
            <p>${{ formatearPrecio(prod.precio) }}</p>
            
            <div v-if="obtenerCantidad(prod) > 0" style="display: flex; align-items: center; justify-content: space-between; background: rgba(128,128,128,0.1); border-radius: var(--radius-md); padding: 0.5rem; margin-top: 1rem;">
              <button @click="modificarCantidad(prod, -1)" class="btn-primary" style="width: 32px; height: 32px; padding: 0; border-radius: 50%; background: var(--color-text-light);">-</button>
              <span style="font-weight: bold; font-size: 1.1rem;">{{ obtenerCantidad(prod) }}</span>
              <button @click="modificarCantidad(prod, 1)" class="btn-primary" style="width: 32px; height: 32px; padding: 0; border-radius: 50%;">+</button>
            </div>
            
            <button v-else @click="agregarAlCarrito(prod)" class="btn-primary" style="margin-top: 1rem;">
              Añadir al Carrito 🛒
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Imagen Ampliada -->
    <div v-if="imagenAmpliada" class="modal-overlay" @click.self="imagenAmpliada = null" style="background: rgba(0,0,0,0.85); z-index: 2000; padding: 2rem;">
      <button @click="imagenAmpliada = null" style="position: absolute; top: 1.5rem; right: 1.5rem; background: rgba(255,255,255,0.1); border: none; color: white; font-size: 2rem; cursor: pointer; border-radius: 50%; width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; backdrop-filter: blur(4px);">&times;</button>
      <img :src="imagenAmpliada" style="max-width: 100%; max-height: 100%; object-fit: contain; border-radius: var(--radius-md); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);" />
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
