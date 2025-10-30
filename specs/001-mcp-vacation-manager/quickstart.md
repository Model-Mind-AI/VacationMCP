# Quickstart: MCP Vacation Manager

1. Review contracts in `contracts/openapi.yaml`.
2. Implement service endpoints in `src/` following contracts.
3. Add MCP tools for `check_vacation_balance` and `request_vacation`.
4. Write tests in `tests/` (contract + integration).
5. Provide health endpoint and basic API key auth.
6. Prepare Render deployment configuration (Dockerfile and render.yaml).

## Run locally

```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
set API_KEY=devkey  # PowerShell: $env:API_KEY='devkey'
uvicorn src.app:app --host 0.0.0.0 --port 8000
```

- Check health: GET http://localhost:8000/health
- Get balance: GET http://localhost:8000/balance with headers:
  - `X-API-Key: devkey`
  - `X-Employee-Id: alice`
- Create request: POST http://localhost:8000/vacation-requests (JSON body `{ "employeeId": "alice", "startDate": "2025-11-03", "endDate": "2025-11-04" }`) with header `X-API-Key: devkey`

## Deploy to Render

1. Push to GitHub/GitLab.
2. In Render, create a new Web Service from this repo.
3. Render will detect `render.yaml` and provision the service.
4. Set Environment Variable `API_KEY` in Render dashboard.
5. Deploy; health check should pass at `/health`.
