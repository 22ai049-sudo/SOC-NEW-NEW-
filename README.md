# NEXUS SOC Command Center

Production-ready AI-driven SOC automation platform with FastAPI backend, React frontend, WebSocket live feed, JWT/RBAC, multi-tenant isolation, SIEM connectors, playbook orchestration, and deployment artifacts.

## Architecture
- **Backend:** FastAPI async APIs (`backend/app/main_api.py`)
- **Frontend:** React + Vite (`frontend/src`)
- **Queue/Bus:** Redis (service provisioned)
- **LLM:** Ollama endpoint + RAG simulation components
- **Realtime:** `/ws/live` WebSocket

## Backend module coverage
All requested modules are present under `backend/app/services/` including ingestion, detection, RAG/LLM, MITRE mapping, threat intel, scoring, agents, playbooks, case management, SLA, tenant, SIEM, memory, audit, orchestration.

## How to run this project

### Option A — Run with Docker (recommended)
1. Start all services:
   ```bash
   docker compose up --build
   ```
2. Open the UI:
   - Frontend: `http://localhost:3000`
   - Backend OpenAPI docs: `http://localhost:8000/docs`
3. Login with default credentials:
   - `admin/admin123`
   - `manager/manager123`
   - `analyst/analyst123`

### Option B — Run locally (without Docker)
1. Start backend:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main_api:app --reload --host 0.0.0.0 --port 8000
   ```
2. In a new terminal, start frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
3. Open:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`

### Verify the backend quickly
```bash
curl http://localhost:8000/health
```
Expected response:
```json
{"status":"ok","service":"NEXUS SOC Command Center"}
```

## Pipeline flow
`Log ingestion -> detection -> LLM + RAG -> MITRE -> threat enrichment -> risk scoring -> playbook generation -> validation/execution -> case mgmt -> SLA -> audit`

## API highlights
- `POST /api/ingest/manual`
- `POST /api/ingest/dataset/start`
- `POST /api/ingest/scheduler/toggle`
- `GET /api/dashboard/metrics`
- `GET /api/incidents`, `GET /api/incidents/{id}`
- `POST /api/mitigation/approve|reject|execute`
- `GET/POST/PUT /api/cases`
- `GET /api/sla/status`
- `GET /api/audit`
- `GET /api/agents/activity`
- `GET /api/siem/status`
- `POST /api/auth/login`, `GET /api/auth/me`
- `POST /api/tenant/switch`

## Ports
- frontend `3000`
- backend `8000`
- redis `6379`
- ollama `11434`

## Ollama setup
```bash
ollama pull mistral:7b
```
Set backend `ollama_url` in `backend/app/core/config.py` or via env injection.

## Run backend tests
```bash
cd backend
PYTHONPATH=. python -m unittest discover -s tests -v
```

## Kubernetes deployment
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/ollama-deployment.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/ingress.yaml
```

## Troubleshooting

### Frontend install/build fails with `403 Forbidden`
If `npm install` or `npm run build` fails with a registry/proxy `403`, check and clear local npm proxy settings:

```bash
npm config get proxy
npm config get https-proxy
npm config delete proxy
npm config delete https-proxy
```

Then retry:

```bash
cd frontend
npm install
npm run build
```

If your environment requires a corporate proxy, set valid proxy values instead of deleting them.

### Playwright screenshot shows `ERR_EMPTY_RESPONSE`
This usually means the frontend server is not running. Start frontend first:

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 3000
```

Then open `http://localhost:3000` and rerun screenshot tooling.

### Backend startup/auth hashing issue in Python 3.12
The backend now uses `pbkdf2_sha256` as the primary hashing scheme to avoid bcrypt runtime incompatibilities in some Python 3.12 images. Rebuild the backend image after pulling latest changes:

```bash
docker compose build backend --no-cache
docker compose up backend
```
