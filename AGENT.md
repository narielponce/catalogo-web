# Guía de Arquitectura de CI/CD para Despliegues Automáticos con Docker y GitHub Actions

Esta guía describe el esquema de Integración y Despliegue Continuo (CI/CD) implementado en este proyecto, diseñado para ser rápido, modular, seguro y de muy bajo mantenimiento. Puedes replicar este mismo modelo en cualquier otro desarrollo.

---

## 1. Concepto de la Arquitectura

```mermaid
graph TD
    A[PC Local: git push] -->|Trigger| B[GitHub Actions]
    B -->|Job 1: Compilar y Subir| C[GitHub Container Registry - GHCR]
    B -->|Job 2: SSH Deploy| D[Droplet VPS / Servidor]
    D -->|Autenticación| C
    D -->|docker compose pull| D
    D -->|docker compose up -d| D
```

1. **PC Local:** Solo haces `git push origin main`. No necesitas scripts locales ni conectarte al servidor manualmente.
2. **GitHub Actions (Compilación):** GitHub crea una máquina virtual temporal, compila tus aplicaciones (Frontend, Backend, etc.) y genera **Imágenes Docker**.
3. **GitHub Container Registry (GHCR):** Las imágenes Docker se suben y guardan en el registro privado de paquetes de GitHub.
4. **Droplet VPS (Despliegue):** GitHub se conecta por SSH a tu servidor y le da órdenes para:
   * Hacer un `git pull` rápido para sincronizar archivos de configuración (como `docker-compose.yml`).
   * Descargar las nuevas imágenes Docker compiladas desde GHCR.
   * Reiniciar solo los contenedores cuyas imágenes cambiaron (cero o mínimo tiempo de inactividad).
   * Limpiar imágenes antiguas no utilizadas (`docker image prune`).

---

## 2. Configuración en GitHub (Secrets)

Para replicar esto en otro repositorio, debes ingresar a la configuración de tu repositorio en GitHub: **Settings -> Secrets and variables -> Actions**, y crear los siguientes **Repository Secrets**:

| Secret Name | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `VPS_IP` | La dirección IP pública de tu Droplet/servidor | `159.203.18.25` |
| `VPS_USER` | El usuario SSH con privilegios de Docker en el servidor | `devops` |
| `VPS_SSH_KEY` | Tu llave privada SSH (la que corresponde a la llave pública autorizada en el VPS) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `GHCR_PAT` | Un token de acceso personal de GitHub (Personal Access Token) con permisos `read:packages` y `write:packages` | `ghp_L1A9K...` |

> [!TIP]
> Puedes generar un **Personal Access Token (PAT)** desde tu cuenta de GitHub en: *Settings -> Developer Settings -> Personal Access Tokens (Tokens classic)*.

---

## 3. Estructura del Archivo de Workflow (`.github/workflows/deploy.yml`)

Crea esta estructura de carpetas en tu nuevo proyecto: `.github/workflows/deploy.yml` y copia esta plantilla:

```yaml
name: Build and Deploy

on:
  push:
    branches:
      - main # O la rama por defecto de tu proyecto

permissions:
  contents: read
  packages: write

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      # Modifica estos bloques según las carpetas y nombres de tus servicios
      - name: Build and push Backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ghcr.io/${{ github.repository_owner }}/nombre-app-backend:latest

      - name: Build and push Frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: true
          tags: ghcr.io/${{ github.repository_owner }}/nombre-app-frontend:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to VPS via SSH
      uses: appleboy/ssh-action@v1.0.3
      with:
        host: ${{ secrets.VPS_IP }}
        username: ${{ secrets.VPS_USER }}
        key: ${{ secrets.VPS_SSH_KEY }}
        script: |
          # 1. Ruta absoluta de la aplicación en el servidor
          cd /home/devops/apps/nombre-app
          
          # 2. Autenticarse en GHCR en el VPS
          echo "${{ secrets.GHCR_PAT }}" | docker login ghcr.io -u ${{ github.actor }} --password-stdin
          
          # 3. Traer cambios de configuración (ej: docker-compose.yml actualizados)
          git pull origin main
          
          # 4. Descargar imágenes nuevas de los contenedores
          docker compose pull
          
          # 5. Recrear y encender contenedores en segundo plano
          docker compose up -d
          
          # 6. Borrar imágenes residuales anteriores (libera espacio en disco)
          docker image prune -f
```

---

## 4. Configuración Inicial Única en el Servidor (VPS)

En cada aplicación nueva que crees, debes hacer lo siguiente en tu Droplet por única vez:

1. **Clonar el Repositorio:**
   Ve a la carpeta donde agrupas tus aplicaciones (ej: `/home/devops/apps/`) y clona el proyecto con Git:
   ```bash
   git clone https://github.com/tu-usuario/tu-repositorio.git nombre-app
   ```
2. **Crear archivo `.env`:**
   Entra a la carpeta clonada y crea el archivo `.env` para las variables de producción:
   ```bash
   cd nombre-app
   touch .env
   # Llena el .env con las variables de base de datos, contraseñas y llaves JWT correspondientes
   ```
3. **Configurar Traefik (si utilizas proxy inverso):**
   Añade las `labels` correctas de Traefik en el `docker-compose.yml` de producción para mapear tu dominio al puerto expuesto de tu contenedor de Frontend o Backend.

---

## 5. Ventajas de este Esquema

* **Seguridad:** El servidor no necesita acceso SSH a tu PC local, y GitHub solo interactúa a través de SSH con comandos controlados de Docker.
* **Cero Scripts de Despliegue en el VPS:** No necesitas mantener scripts pesados `.sh` en tu servidor. Toda la inteligencia reside en el archivo YAML de GitHub de tu código.
* **Eficiencia:** Las imágenes Docker se compilan en las máquinas ultra rápidas de GitHub, no en los recursos limitados de tu Droplet. Tu Droplet solo descarga la imagen final optimizada, previniendo cuelgues del CPU al compilar.
