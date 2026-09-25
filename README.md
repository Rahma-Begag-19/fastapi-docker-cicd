# FastAPI Docker CI/CD

A containerized application demonstrating a complete **CI/CD workflow from source code to a running deployment environment**, with Docker, GitHub Actions, GitHub Container Registry (GHCR), PostgreSQL, Alembic migrations, and Docker Compose.

The focus of this project is the **DevOps infrastructure and delivery process**, rather than the application implementation itself.

---

## DevOps Architecture

```text
Developer
    │
    │ git push
    ▼
GitHub Repository
    │
    ▼
GitHub Actions
    │
    ├── Install dependencies
    ├── Validate application
    ├── Build Docker images
    └── Push images to GHCR
              │
              ▼
      GitHub Container Registry
              │
              │ docker compose pull
              ▼
       Production Compose
              │
       ┌──────┴──────┐
       │             │
       ▼             ▼
   PostgreSQL     Backend
                     │
                     ├── Alembic migrations
                     │
                     └── FastAPI
       │
       ▼
    Frontend
```

The workflow separates **building images** from **running those images**.

---

## Technologies

* Docker
* Docker Compose
* GitHub Actions
* GitHub Container Registry (GHCR)
* PostgreSQL
* Alembic
* Nginx
* Python 3.12
* Uvicorn

---

## Repository Structure

```text
fastapi-docker-cicd/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── backend/
│   ├── Dockerfile
│   ├── start.sh
│   └── ...
│
├── frontend/
│   ├── Dockerfile
│   └── ...
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── .gitignore
```

The two Compose files have different purposes:

* `docker-compose.yml` — builds images from the local source code.
* `docker-compose.prod.yml` — pulls already-built images from GHCR.

This separation allows the same Docker images produced by CI to be used during deployment.

---

## Docker

The application is divided into separate containers:

```text
┌─────────────────────┐
│      Frontend       │
│       Nginx         │
│       :80           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       Backend       │
│      Uvicorn        │
│       :8000         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     PostgreSQL      │
│       :5432         │
└─────────────────────┘
```

Host ports:

```text
Frontend  → localhost:5500
Backend   → localhost:8080
PostgreSQL → internal Docker network
```

PostgreSQL does not need to be exposed to the host because the backend communicates with it through the Docker network.

---

## Environment Configuration

Sensitive configuration is provided through environment variables.


The `.env` file is excluded from Git using `.gitignore`.

Secrets should not be committed to the repository.

---

## Database Initialization

A PostgreSQL container can start successfully even when the application tables do not exist.

To avoid requiring a manual migration command during deployment, the backend container automatically runs:

```bash
alembic upgrade head
```

before starting FastAPI.

The startup flow is:

```text
Backend container starts
        │
        ▼
Run Alembic migrations
        │
        ▼
Database schema reaches latest revision
        │
        ▼
Start Uvicorn
```

The backend startup script is responsible for this sequence.

This means a new environment can initialize its database schema automatically.

---

## PostgreSQL Health Check

The production Compose configuration includes a PostgreSQL health check.

The backend depends on PostgreSQL being healthy:

```yaml
depends_on:
  db:
    condition: service_healthy
```

This prevents the backend from immediately attempting database migrations before PostgreSQL is ready to accept connections.

The deployment sequence is therefore:

```text
PostgreSQL starts
       ↓
Health check
       ↓
PostgreSQL becomes healthy
       ↓
Backend starts
       ↓
Alembic migrations
       ↓
FastAPI starts
```

---

# CI Pipeline

The CI pipeline is implemented with GitHub Actions.

It is triggered by pushes and pull requests targeting `main`.

```text
Git push
   ↓
GitHub Actions
   ↓
Checkout repository
   ↓
Set up Python
   ↓
Install dependencies
   ↓
Validate application
   ↓
Build Docker images
   ↓
Push images to GHCR
```

The pipeline contains two main stages:

### 1. Test

The test job:

* checks out the repository
* installs Python 3.12
* installs backend dependencies
* validates the application with `compileall`

### 2. Docker Build & Publish

After the test job succeeds:

```text
test
  ↓
docker-build
  ↓
Build backend image
  ↓
Build frontend image
  ↓
Push images to GHCR
```

The Docker build job depends on the successful completion of the test job.

---

# GitHub Container Registry

Docker images are published to GitHub Container Registry.

The images are stored as:

```text
ghcr.io/rahma-begag-19/fastapi-docker-cicd/backend
ghcr.io/rahma-begag-19/fastapi-docker-cicd/frontend
```

The registry acts as the bridge between CI and deployment.

```text
GitHub Actions
      │
      │ build
      ▼
Docker images
      │
      │ push
      ▼
     GHCR
      │
      │ pull
      ▼
Deployment environment
```

---

# Image Tagging

Each image is published with two tags:

```text
latest
```

and:

```text
<commit-sha>
```

For example:

```text
backend:latest
backend:<commit-sha>
```

The `latest` tag provides a convenient reference to the most recent published image.

The commit SHA tag provides an immutable reference to the exact source revision that produced the image.

This gives us both:

```text
latest
   ↓
convenient deployment reference
```

and:

```text
commit SHA
   ↓
exact version identification
```

---

# Production Deployment

The production Compose file does **not** build the application locally.

Instead, it pulls the images produced by CI:

```yaml
backend:
  image: ghcr.io/rahma-begag-19/fastapi-docker-cicd/backend:latest

frontend:
  image: ghcr.io/rahma-begag-19/fastapi-docker-cicd/frontend:latest
```

This creates a separation between:

```text
CI
→ builds and publishes artifacts
```

and:

```text
Deployment
→ consumes those artifacts
```

---

## Deploying the Published Images

Pull the latest images:

```bash
sudo docker compose -f docker-compose.prod.yml pull
```

Start the production stack:

```bash
sudo docker compose -f docker-compose.prod.yml up -d
```

Check the running containers:

```bash
sudo docker compose -f docker-compose.prod.yml ps
```

Check backend logs:

```bash
sudo docker compose -f docker-compose.prod.yml logs backend
```

The backend startup logs should show the migration process followed by Uvicorn starting.

---

# Local Development vs Production

### Development

```text
Source code
    ↓
docker-compose.yml
    ↓
Docker build
    ↓
Local containers
```

The development Compose file uses:

```yaml
build:
```

so Docker builds images from the local source.

### Production-style deployment

```text
GHCR
  ↓
docker-compose.prod.yml
  ↓
Pull published images
  ↓
Run containers
```

The production Compose file uses:

```yaml
image:
```

instead of `build:`.

This ensures the deployment runs the same Docker artifacts that were built and published by CI.

---

# CI/CD Workflow

The complete workflow is:

```text
                  CI
                  │
Developer ──push──► GitHub Actions
                       │
                       ▼
                    Validate
                       │
                       ▼
                  Build images
                       │
                       ▼
                    Push GHCR
                       │
                       ▼
                  ─────────────
                       │
                  Deployment
                       │
                       ▼
                 Pull images
                       │
                       ▼
               Start PostgreSQL
                       │
                       ▼
                Health check
                       │
                       ▼
              Start backend
                       │
                       ▼
              Run migrations
                       │
                       ▼
               Start FastAPI
                       │
                       ▼
               Start frontend
```

This project demonstrates **Continuous Integration and Continuous Delivery** using containerized artifacts.

The deployment step is currently triggered manually with Docker Compose rather than automatically after every successful GitHub Actions run.

---

# Useful Commands

### Development stack

```bash
sudo docker compose up -d
```

Check containers:

```bash
sudo docker compose ps
```

View logs:

```bash
sudo docker compose logs
```

Stop the stack:

```bash
sudo docker compose down
```

### Production-style stack

Pull published images:

```bash
sudo docker compose -f docker-compose.prod.yml pull
```

Start:

```bash
sudo docker compose -f docker-compose.prod.yml up -d
```

Check status:

```bash
sudo docker compose -f docker-compose.prod.yml ps
```

View backend logs:

```bash
sudo docker compose -f docker-compose.prod.yml logs backend
```

Stop:

```bash
sudo docker compose -f docker-compose.prod.yml down
```

---

# What This Project Demonstrates

From a DevOps perspective, this project demonstrates:

* Containerizing an application
* Separating application services into containers
* Managing services with Docker Compose
* Managing configuration through environment variables
* Keeping secrets outside the Git repository
* Managing database schema changes with Alembic
* Handling database readiness with health checks
* Automating validation with GitHub Actions
* Building Docker images in CI
* Publishing images to a container registry
* Using immutable commit-based image tags
* Separating CI artifacts from deployment
* Deploying published images with Docker Compose
* Automatically applying database migrations during container startup

The resulting workflow provides a reproducible path from a Git commit to a running containerized application.
