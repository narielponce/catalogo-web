<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'

const router = useRouter()
const { get, put, del, isLoading, error } = useApi()

const comercios = ref([])

const handleLogout = () => {
  localStorage.removeItem('token')
  router.push({ name: 'login' })
}

const cargarComercios = async () => {
  try {
    const data = await get('/api/superadmin/comercios')
    if (data) {
      comercios.value = data
    }
  } catch (err) {
    if (err.message.includes('401') || err.message.includes('403')) {
      handleLogout()
    }
  }
}

const toggleActivo = async (comercio) => {
  try {
    const data = await put(`/api/superadmin/comercios/${comercio.id}`, {
      activo: !comercio.activo
    })
    if (data) {
      comercio.activo = data.activo
    }
  } catch (err) {
    console.error("Error al actualizar comercio:", err)
  }
}

const borrarComercio = async (comercio) => {
  if (!confirm(`¿Estás seguro de que deseas borrar DEFINITIVAMENTE el comercio "${comercio.nombre}"? Esto borrará todos sus productos y no se puede deshacer.`)) {
    return
  }
  
  try {
    const data = await del(`/api/superadmin/comercios/${comercio.id}`)
    if (data) {
      await cargarComercios()
    }
  } catch (err) {
    console.error("Error al borrar comercio:", err)
  }
}

onMounted(() => {
  cargarComercios()
})
</script>

<template>
  <div class="admin-dashboard">
    <header class="admin-header glass-header" style="display: flex; justify-content: space-between; align-items: center; background: rgba(139, 92, 246, 0.1); border-bottom: 2px solid var(--color-primary);">
      <h2 style="color: var(--color-primary);">👑 Panel Maestro SaaS</h2>
      <button @click="handleLogout" class="btn-primary" style="width: auto; background: var(--color-text-light)">Cerrar Sesión</button>
    </header>
    
    <div class="admin-content content-wrapper">
      
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
        <h3>Gestión de Clientes</h3>
      </div>

      <div v-if="isLoading" class="loader">Cargando clientes...</div>
      
      <div v-else-if="error" class="error-card">
        {{ error }}
      </div>
      
      <div v-else-if="comercios.length === 0" class="admin-card text-center" style="padding: 3rem;">
        <p style="color: var(--color-text-light); margin-bottom: 1rem;">Aún no hay clientes registrados en la plataforma.</p>
      </div>

      <div v-else style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; background: var(--color-glass); border-radius: var(--radius-md); overflow: hidden; backdrop-filter: blur(10px);">
          <thead>
            <tr style="background: rgba(255,255,255,0.05); text-align: left;">
              <th style="padding: 1rem;">Logo</th>
              <th style="padding: 1rem;">Comercio</th>
              <th style="padding: 1rem;">WhatsApp</th>
              <th style="padding: 1rem;">Slug</th>
              <th style="padding: 1rem;">Estado</th>
              <th style="padding: 1rem;">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="com in comercios" :key="com.id" style="border-top: 1px solid rgba(255,255,255,0.1);">
              <td style="padding: 1rem;">
                <img v-if="com.logo_url" :src="com.logo_url" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover;" />
                <div v-else style="width: 40px; height: 40px; border-radius: 50%; background: var(--color-primary); display: flex; align-items: center; justify-content: center; font-weight: bold;">
                  {{ com.nombre.charAt(0).toUpperCase() }}
                </div>
              </td>
              <td style="padding: 1rem; font-weight: bold;">{{ com.nombre }}</td>
              <td style="padding: 1rem;">{{ com.whatsapp }}</td>
              <td style="padding: 1rem;">
                <a :href="'/' + com.slug" target="_blank" style="color: var(--color-primary);">/{{ com.slug }}</a>
              </td>
              <td style="padding: 1rem;">
                <button 
                  @click="toggleActivo(com)"
                  :style="{
                    background: com.activo ? '#10b981' : '#ef4444',
                    border: 'none',
                    color: 'white',
                    padding: '0.4rem 0.8rem',
                    borderRadius: '20px',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    fontSize: '0.8rem'
                  }"
                >
                  {{ com.activo ? 'ACTIVO' : 'BLOQUEADO' }}
                </button>
              </td>
              <td style="padding: 1rem;">
                <button @click="borrarComercio(com)" style="background: transparent; border: 1px solid #ef4444; color: #ef4444; padding: 0.4rem 0.8rem; border-radius: 4px; cursor: pointer; font-size: 0.8rem;">
                  Eliminar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
