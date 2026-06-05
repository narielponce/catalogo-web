# AGENTS.md - Catálogo Web API & Frontend

## 1. Project Overview

**Project Name:** catalogo-web  
**Description:** SaaS platform for businesses to create, manage, and share digital product catalogs. It includes multi-tenant architecture, product management, and automated subscription renewal integrated via n8n (e.g., Mercado Pago).  
**Type:** Full-stack web application (FastAPI + Vue 3)

## 2. Technology Stack

### Backend
- **Framework:** FastAPI
- **ORM:** SQLAlchemy (async)
- **Database:** PostgreSQL (via asyncpg)
- **Migrations:** Alembic
- **Runtime:** Python 3.x

### Frontend
- **Framework:** Vue 3 (Composition API)
- **Build Tool:** Vite
- **Router:** Vue Router 4

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Database Service:** PostgreSQL 15 (Alpine)
- **CI/CD:** GitHub Actions & GHCR (GitHub Container Registry)

## 3. Project Structure

```
catalogo-web/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── api/                 # API Routers (auth, productos, public, superadmin, n8n)
│   │   ├── core/                # Core configuration & settings
│   │   ├── db/                  # Database connection and session management
│   │   └── schemas/             # Pydantic validation schemas
│   ├── uploads/                 # Uploaded images (auto-created)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.vue
│   │   ├── main.js
│   │   ├── router/index.js      # Vue Router config
│   │   ├── assets/              # Static assets
│   │   ├── components/          # Vue components
│   │   ├── composables/         # Vue composables (e.g., shared state/logic)
│   │   └── views/               # Page views (Admin, Catalog, Landing, Login, etc.)
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml           # Local dev/docker environment
├── docker-compose.prod.yml      # Production environment overrides
├── docker-compose.override.yml  
└── AGENT.md                     # CI/CD deployment documentation
```

## 4. API Endpoints (Logical Groupings)

Based on the FastAPI routers included in `main.py`:

- **`/auth`**: Authentication endpoints (login, register, token generation)
- **`/productos`**: Product management CRUD for authenticated business users
- **`/public`**: Public catalog read access for customers
- **`/superadmin`**: Administrative endpoints for managing tenants (businesses)
- **`/n8n`**: Webhook endpoints for external integrations like n8n and Mercado Pago (subscriptions/reactivation)
- **`/health`**: System and database health check

## 5. Data Models

### Comercio (Tenant)
- `id` (UUID), `nombre`, `slug` (unique), `descripcion`, `logo_url`, `portada_url`, `whatsapp`, `tema`, `activo`, `trial_vence`, `created_at`
- **Relations:** Has many `usuarios`, Has many `productos`

### Usuario
- `id` (UUID), `comercio_id` (ForeignKey), `email` (unique), `hashed_password`, `is_active`, `is_superuser`
- **Relations:** Belongs to `comercio`

### Producto
- `id` (UUID), `comercio_id` (ForeignKey), `nombre`, `descripcion`, `precio`, `imagen_url`, `disponible`, `categoria`, `created_at`
- **Relations:** Belongs to `comercio`
- *Note:* Contains compound indexes (`comercio_id`, `disponible`, `categoria`) to optimize public catalog loading.

## 6. Environment Variables

Expected variables for `.env` or Docker environment:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=catalogo_db
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/catalogo_db
JWT_SECRET=your-super-secret-key
N8N_SECRET=your-super-secret-n8n-key
```

## 7. Frontend Routes

| Path | Component | Auth Required | Description |
|------|-----------|---------------|-------------|
| `/` | LandingView | No | Main landing page for the SaaS |
| `/login` | LoginView | No | Authentication |
| `/register` | RegisterView | No | Tenant registration |
| `/admin` | AdminView | Yes | Dashboard for business owners |
| `/superadmin` | SuperAdminView | Yes | Dashboard for platform administrators |
| `/:slug` | CatalogView | No | Public catalog for a specific business |

## 8. Key Features
- **Multi-tenant SaaS Architecture:** A single backend serves multiple businesses, separated by `comercio_id`.
- **Custom Slugs:** Businesses get their own shareable URLs (e.g., `/misitio`).
- **Subscription Management:** Automated handling via `n8n` webhooks for Mercado Pago renewals.
- **Image Handling:** Supports cover photos, logos, and product images (typically saved locally in `/uploads` mapped via volume).
- **Public Catalog Optimization:** Custom database indices tailored for fast public menu access.
