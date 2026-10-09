# FastAPI Docker CI/CD

A containerized application demonstrating an automated **CI/CD pipeline from source code to deployment**, using Docker, Docker Compose, GitHub Actions, GitHub Container Registry (GHCR), PostgreSQL, and Alembic migrations.

The focus of this project is the **DevOps infrastructure, automation, and delivery process**, rather than the application implementation itself.

---

## DevOps Architecture

```text
Developer
    │
    │ git push to main
    ▼
GitHub Repository
    │
    ▼
GitHub Actions — GitHub-hosted runner
    │
    ├── Install dependencies
    ├── Validate application
    └── Build Docker images
             │
             ▼
     GitHub Container Registry
             │
             │ Publish images
             ▼
     Self-hosted GitHub Actions runner
             │
             ├── Authenticate to GHCR
             ├── Pull updated images
             ├── Deploy with Docker Compose
             └── Verify running services
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
         PostgreSQL          Application
                             ┌──────────┐
                             │ Backend  │
                             └────┬─────┘
                                  │
                             ┌────▼─────┐
                             │ Frontend │
                             └──────────┘
```

The pipeline separates **testing, building, publishing, and deploying** application artifacts.

The self-hosted runner executes the deployment job on the local Kali Linux machine, which runs the production-style Docker containers.

---

## Technologies

* Docker and Docker Compose
* GitHub Actions
* GitHub-hosted and self-hosted runners
* GitHub Container Registry (GHCR)
* PostgreSQL
* Alembic
* Nginx
* Python 3.12
* Uvicorn
* Linux / Kali Linux
* Git and GitHub

---

## Repository Structure

```text
fastapi-docker-cicd/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── runner-test.yml
├── backend/
│   ├── Dockerfile
│   ├── start.sh
│   └── ...
├── frontend/
│   ├── Dockerfile
│   └── ...
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
└── .gitignore
```

The two Compose files serve different purposes:

* `docker-compose.yml` builds images from local source code.
* `docker-compose.prod.yml` runs published images pulled from GHCR.

The `.env` file contains local configuration and is excluded from Git.

---

## Container Architecture

The application is divided into three services:

```text
Frontend — Nginx
     │
     ▼
Backend — FastAPI / Uvicorn
     │
     ▼
Database — PostgreSQL
```

The production stack uses Docker Compose to manage the services, their networking, and persistent database storage.

The frontend and backend are published through host ports for local testing. PostgreSQL communicates with the backend through the internal Docker network.

---

## Environment Configuration and Secrets

Sensitive configuration is provided through environment variables.

* `.env` contains local configuration and credentials.
* `.env` is excluded from version control through `.gitignore`.
* `.env.example` documents the required configuration without containing real secrets.
* GitHub Actions uses the automatically provided `GITHUB_TOKEN` to authenticate to GHCR with job-specific permissions.

**Secrets must never be committed to the repository.** If a credential is accidentally exposed, it should be revoked or rotated; deleting it from the latest commit alone may not remove it from Git history.

---

## Database Initialization and Readiness

The backend startup script automatically applies database migrations before starting FastAPI:

```bash
alembic upgrade head
```

The production Compose configuration includes a PostgreSQL health check. The backend waits for the database service to become healthy before starting.

```text
PostgreSQL starts
       ↓
Health check succeeds
       ↓
Backend starts
       ↓
Alembic migrations
       ↓
FastAPI starts
```

The PostgreSQL data is stored in a named Docker volume, allowing it to persist across ordinary container replacements. Persistent volumes are not a substitute for backups.

---

# Continuous Integration (CI)

The CI workflow is triggered by pushes and pull requests targeting `main`.

```text
Git push / Pull request
          ↓
GitHub-hosted runner
          ↓
Checkout repository
          ↓
Set up Python 3.12
          ↓
Install dependencies
          ↓
Validate application
```

The validation step uses Python's `compileall` to check application code for compilation errors.

For trusted pushes to `main`, successful validation allows the pipeline to continue to the image publishing stage.

---

# Docker Image Build and Publishing

After validation succeeds, GitHub Actions builds the backend and frontend Docker images and publishes them to GHCR.

```text
Successful validation
          ↓
Build backend image
          ↓
Build frontend image
          ↓
Tag images
          ↓
Push images to GHCR
```

Published image names:

```text
ghcr.io/rahma-begag-19/fastapi-docker-cicd/backend
ghcr.io/rahma-begag-19/fastapi-docker-cicd/frontend
```

Each image is published with two tags:

* `latest` — a convenient reference to the most recently published image.
* `<commit-sha>` — identifies the source commit associated with the image.

The commit-based tag improves traceability between source code and published artifacts.

---

# Continuous Deployment (CD)

The deployment stage runs on a **self-hosted GitHub Actions runner** installed on the Kali Linux machine.

It is configured to deploy only for pushes to `main`, after the image publishing job succeeds.

```text
Images published to GHCR
          ↓
Self-hosted runner receives job
          ↓
Authenticate to GHCR
          ↓
Validate deployment configuration
          ↓
Pull updated backend and frontend images
          ↓
Docker Compose updates services
          ↓
PostgreSQL readiness check
          ↓
Backend migrations and startup
          ↓
Verify deployment status
```

The deployment workflow:

1. Authenticates to GitHub Container Registry.
2. Checks that the deployment configuration is valid.
3. Pulls the published application images.
4. Updates the production-style Compose stack.
5. Checks the resulting container status.

PostgreSQL uses persistent storage so that replacing application containers does not ordinarily remove database data.

The deployment uses the existing Compose project name to retain the intended production stack and its associated volume.

---

## Self-Hosted GitHub Actions Runner

A self-hosted runner allows GitHub Actions to execute selected workflow jobs on a machine we control.

In this project, the runner executes the deployment commands locally on Kali Linux.

The runner can be started from its installation directory:

```bash
./run.sh
```

When running interactively, its terminal must remain open to accept jobs. Press `Ctrl+C` to stop it.

The runner was tested using a dedicated workflow that reports the execution environment, including the runner's username, hostname, operating system, and Docker version.

### Security considerations

A self-hosted runner has access to resources on its host machine. Therefore:

* Do not run untrusted pull-request workflows on the personal runner.
* Restrict deployment to trusted branches and workflows.
* Use least-privilege permissions for workflow tokens.
* Keep private keys, tokens, and `.env` credentials out of Git.
* Stop the runner when it is not needed.
* Review workflow changes before allowing them to execute on the host.

The old SSH-based deployment key is not required for the current local self-hosted deployment approach, provided no other workflow or service still depends on it.

---

# Deployment and Access

The production-style stack can be managed with Docker Compose.

Pull the published images:

```bash
docker compose -f docker-compose.prod.yml pull
```

Start or update the services:

```bash
docker compose -f docker-compose.prod.yml up -d
```

Check service status:

```bash
docker compose -f docker-compose.prod.yml ps
```

View backend logs:

```bash
docker compose -f docker-compose.prod.yml logs backend
```

View database logs:

```bash
docker compose -f docker-compose.prod.yml logs db
```

The frontend is available locally at:

```text
http://localhost:5500
```

The backend API documentation is available locally at:

```text
http://localhost:8080/docs
```

These addresses assume the corresponding host-port mappings are enabled in the active Compose configuration.

---

# Development vs Production-Style Deployment

### Local development

```text
Source code
    ↓
docker-compose.yml
    ↓
Build images locally
    ↓
Run containers
```

The development Compose file uses `build:` to create images from local source code.

### Automated deployment

```text
Git push to main
    ↓
CI validation
    ↓
Build and publish images
    ↓
GHCR
    ↓
Self-hosted deployment runner
    ↓
Pull images
    ↓
Docker Compose
    ↓
Updated containers
```

The production Compose file uses published `image:` references instead of building application images from source.

This separates image creation from deployment and allows the deployment environment to consume artifacts produced by CI.

---

# What This Project Demonstrates

From a DevOps perspective, this project demonstrates:

* Containerizing an application with Docker.
* Orchestrating services with Docker Compose.
* Managing configuration through environment variables.
* Keeping secrets out of version control.
* Persisting database data with Docker volumes.
* Managing schema changes with Alembic.
* Using health checks for service readiness.
* Automating validation with GitHub Actions.
* Building and publishing images to GHCR.
* Tagging images with commit identifiers.
* Using a self-hosted runner to execute deployment jobs.
* Automating deployment after a successful push to `main`.
* Pulling and running published artifacts.
* Verifying deployment status and reviewing container logs.
* Understanding the security implications of self-hosted CI/CD runners.

The project demonstrates an automated path from a Git commit to a running containerized application, with CI, artifact publishing, deployment automation, and host-security considerations.
