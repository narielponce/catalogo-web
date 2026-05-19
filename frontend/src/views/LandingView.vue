<script setup>
</script>

<template>
  <div class="landing-page">
    <!-- Navbar Minimalista -->
    <nav class="landing-nav">
      <div class="logo-container">
        <span class="logo-icon">🛍️</span>
        <span class="logo-text">CatálogoSaaS</span>
      </div>
      <div class="nav-actions">
        <router-link to="/login" class="nav-link">Iniciar Sesión</router-link>
        <router-link to="/register" class="btn-primary nav-btn">Empezar</router-link>
      </div>
    </nav>

    <!-- Hero Section -->
    <main class="hero-section">
      <div class="hero-content">
        <div class="badge">Vende más, más rápido ⚡</div>
        <h1 class="hero-title">Tu tienda online,<br/>directo a WhatsApp.</h1>
        <p class="hero-subtitle">
          Crea un catálogo digital profesional en menos de 5 minutos. Sin comisiones, sin intermediarios y optimizado para que tus clientes compren desde su celular.
        </p>
        
        <div class="hero-cta">
          <router-link to="/register" class="btn-primary cta-main">Crear mi Catálogo Gratis</router-link>
          <!-- <button class="btn-secondary cta-demo">Ver Tienda Demo</button> -->
        </div>
      </div>
      
      <!-- Decoración de fondo suave -->
      <div class="glow-blob blob-1"></div>
      <div class="glow-blob blob-2"></div>
    </main>

    <!-- Features Section -->
    <section class="features-section">
      <div class="feature-card">
        <div class="feature-icon">📱</div>
        <h3 class="feature-title">Pedidos a WhatsApp</h3>
        <p class="feature-desc">Tus clientes arman su carrito y te envían el pedido detallado directamente a tu chat.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <h3 class="feature-title">Gestión en tiempo real</h3>
        <p class="feature-desc">Sube fotos, edita precios y oculta productos sin stock al instante desde tu teléfono.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">💎</div>
        <h3 class="feature-title">Identidad de Marca</h3>
        <p class="feature-desc">Personaliza tu catálogo con el logo y descripción de tu negocio para lucir profesional.</p>
      </div>
    </section>

    <!-- Footer Simple -->
    <footer class="landing-footer">
      <p>© 2026 CatálogoSaaS. Diseñado para emprendedores.</p>
    </footer>
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

/* Navbar */
.landing-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 5%;
  position: fixed;
  top: 0;
  width: 100%;
  z-index: 100;
  background: var(--color-surface);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.logo-icon {
  font-size: 1.5rem;
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
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: var(--color-text);
}

.nav-btn {
  width: auto;
  padding: 0.5rem 1.25rem;
  font-size: 0.9rem;
  border-radius: 50px;
}

/* Hero Section */
.hero-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8rem 5% 4rem;
  position: relative;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  background: rgba(234, 88, 12, 0.1);
  color: var(--color-primary);
  border: 1px solid rgba(234, 88, 12, 0.2);
  border-radius: 50px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 2rem;
}

.hero-title {
  font-size: clamp(2.5rem, 6vw, 4.5rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -1px;
  margin-bottom: 1.5rem;
  background: linear-gradient(135deg, var(--color-text) 0%, var(--color-text-light) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: var(--color-text-light);
  line-height: 1.6;
  max-width: 600px;
  margin-bottom: 2.5rem;
}

.hero-cta {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.cta-main {
  width: auto;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  border-radius: 50px;
  box-shadow: 0 10px 25px -5px rgba(234, 88, 12, 0.4);
}

.btn-secondary {
  background: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
  padding: 1rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--color-text-light);
}

/* Decoraciones de fondo (Blobs) */
.glow-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  z-index: 0;
  opacity: 0.15;
  pointer-events: none;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: #ea580c;
  top: -100px;
  left: -100px;
}

.blob-2 {
  width: 300px;
  height: 300px;
  background: #f59e0b;
  bottom: -50px;
  right: -50px;
}

/* Features Section */
.features-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  padding: 4rem 5% 6rem;
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
  z-index: 10;
}

.feature-card {
  background: var(--color-surface);
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-shadow: var(--shadow-glass);
  padding: 2rem;
  border-radius: 24px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  background: rgba(234, 88, 12, 0.1);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}

.feature-desc {
  color: var(--color-text-light);
  line-height: 1.5;
  font-size: 0.95rem;
}

/* Footer */
.landing-footer {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-light);
  font-size: 0.85rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  margin-top: auto;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .nav-actions {
    gap: 1rem;
  }
  .nav-link {
    display: none; /* Hide login link on very small screens to save space */
  }
  .hero-section {
    padding-top: 7rem;
  }
  .hero-cta {
    flex-direction: column;
    width: 100%;
  }
  .cta-main, .btn-secondary {
    width: 100%;
  }
  .glow-blob {
    opacity: 0.1;
  }
  
  .features-section {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    padding: 2rem 5%;
  }
  .feature-card {
    width: 100%;
    max-width: 100%;
  }
}
</style>
