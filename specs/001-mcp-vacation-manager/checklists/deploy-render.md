# Render Deployment Checklist: MCP Vacation Manager

**Purpose**: Guide deployment of the VacationMCP service to Render using Docker
**Created**: 2025-10-30
**Feature**: ../spec.md

## Pre-requisites

- [ ] Git remote configured (GitHub/GitLab/Bitbucket)
- [ ] Render account created and logged in
- [ ] Repository contains `Dockerfile`, `render.yaml`, `requirements.txt`, `src/`

## Local validation (optional but recommended)

- [ ] Create a virtual environment and install deps
- [ ] Set `API_KEY` env var locally (e.g., `devkey`)
- [ ] Start server: `uvicorn src.app:app --host 0.0.0.0 --port 8000`
- [ ] Verify `GET /health` returns `{ "status": "ok" }`
- [ ] Verify `GET /balance` with headers `X-API-Key: devkey` and `X-Employee-Id: alice`
- [ ] Verify `POST /vacation-requests` with `X-API-Key: devkey` accepts/declines per balance

## Configure Render Web Service

- [ ] Push branch `001-mcp-vacation-manager` to your Git host
- [ ] In Render, "New +" → Web Service → Connect repository
- [ ] Confirm Render detects `render.yaml` (env: docker)
- [ ] Service name: `vacation-mcp` (or preferred)
- [ ] Region: `oregon` (or preferred)
- [ ] Health Check Path: `/health`
- [ ] Auto deploy: enabled

## Environment Variables

- [ ] Set env var `API_KEY` (value: your secret key)
- [ ] Save changes and trigger deploy

## Post-deploy validation

- [ ] Check service events → build succeeded
- [ ] Health check passes at `/health`
- [ ] Test `GET /balance` with headers:
  - [ ] `X-API-Key: <API_KEY>`
  - [ ] `X-Employee-Id: alice`
- [ ] Test `POST /vacation-requests` using seeded accounts

## MCP Tools (optional integration test)

- [ ] From an AI tool supporting MCP, call:
  - [ ] `check_vacation_balance(employee_id="alice")` → returns 0..120
  - [ ] `request_vacation(employee_id, start_date, end_date)` → returns status/id
  - [ ] `list_vacation_requests(employee_id)` → returns list

## Rollback and Updates

- [ ] To update, push to the connected branch; Render auto-deploys
- [ ] To rollback, select a previous successful deploy in Render

## Notes

- Demo balances are seeded on startup: `alice=80`, `bob=16`
- Rate limiting: 60 req/min per API key
