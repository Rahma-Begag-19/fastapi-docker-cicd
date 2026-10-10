# FastAPI Docker CI/CD

A containerized application demonstrating an automated **CI/CD pipeline and monitoring stack** using Docker, GitHub Actions, GHCR, and Prometheus.

## Architecture

```text
Git Push to main
       ↓
GitHub Actions (CI)
       ↓
Build & Publish Docker Images
       ↓
GitHub Container Registry
       ↓
Self-Hosted Runner (CD)
       ↓
Docker Compose Deployment
       ↓
Frontend · FastAPI · PostgreSQL
       ↓
Prometheus · Grafana · Alertmanager
```

## Tech Stack

* **Application:** FastAPI, Python, PostgreSQL, Nginx
* **Containers:** Docker, Docker Compose
* **CI/CD:** GitHub Actions, self-hosted runner, GHCR
* **Database migrations:** Alembic
* **Monitoring & alerting:** Prometheus, Grafana, Alertmanager, Node Exporter, cAdvisor, PostgreSQL Exporter

## Key Features

* Automated CI validation, Docker image builds, and publishing to GHCR.
* Automated deployment to a local Linux host using a self-hosted GitHub Actions runner.
* PostgreSQL persistence, health checks, and database migrations.
* Infrastructure and container monitoring with Prometheus and Grafana.
* Alert rules and Gmail email notifications through Alertmanager.
* Environment-based configuration and secret management.

## Run the Application

Requirements: Docker and Docker Compose.

1. Clone the repository.
2. Configure your environment using `.env.example`.
3. Start the development stack:

```bash
docker compose up -d --build
```

## Access

* **Frontend:** http://localhost:5500
* **Backend API docs:** http://localhost:8080/docs
* **Prometheus:** http://localhost:9090
* **Grafana:** http://localhost:3000

Monitoring interfaces are bound to localhost in the configured monitoring stack.

## What I Learned

This project demonstrates containerization, CI/CD automation, image publishing, deployment orchestration, database management, monitoring, alerting, and secure handling of configuration and secrets.
