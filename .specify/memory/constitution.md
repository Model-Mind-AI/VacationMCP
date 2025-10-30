<!--
Sync Impact Report
- Version change: N/A → 1.0.0
- Modified principles: Template placeholders → concrete MCP server principles
- Added sections: Additional Constraints; Development Workflow
- Removed sections: None
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated (Constitution Check remains generic)
  - .specify/templates/spec-template.md ✅ aligned (no changes required)
  - .specify/templates/tasks-template.md ✅ aligned (paths and phases compatible)
  - .specify/templates/checklist-template.md ✅ aligned (generic)
  - .specify/templates/agent-file-template.md ✅ aligned (generic)
- Follow-up TODOs:
  - TODO(RATIFICATION_DATE): Provide original adoption date for the constitution
-->

# VacationMCP Constitution

## Core Principles

### I. MCP-First, AI-Tool Compatible Interface
The project MUST expose functionality via Model Context Protocol (MCP) so AI tools
can reliably discover and call capabilities. Capabilities include: `check_vacation_balance`
and `request_vacation`. Contracts MUST be documented and versioned.

### II. Web Service in Python, Deployable to Render
Implementation MUST be Python-based (e.g., FastAPI or equivalent), packaged as a
web server suitable for Render deployment. Health/readiness endpoints MUST exist.

### III. Deterministic Contracts and Validation (NON-NEGOTIABLE)
`check_vacation_balance` MUST return a numeric value in hours within [0, 120].
`request_vacation` MUST validate input (dates, hours requested, balance checks) and
return a structured result with status and reason on failure. All inputs/outputs
MUST be schema-validated and documented.

### IV. Security, Privacy, and Access Control
The service MUST protect employee data. At minimum, use API key or auth mechanism,
apply basic rate limiting, and avoid logging sensitive identifiers. Error messages
MUST not leak PII.

### V. Testing, Observability, and Versioning Discipline
Contract and integration tests for both capabilities are REQUIRED. Structured logging
and request correlation IDs SHOULD be included. Breaking changes MUST bump MAJOR,
additive changes MINOR, and fixes PATCH, following semver.

## Additional Constraints

- Language: Python 3.11+; Framework: FastAPI (or equivalent ASGI)
- Deployment: Render web service with a Dockerfile or Render native build
- Interfaces: MCP tools for AI use; REST endpoints for web deployment
- Data: In-memory store acceptable for MVP; pluggable persistence allowed later
- Performance: Target p95 < 200ms for balance checks under typical load

## Development Workflow

- Define and freeze contracts first (OpenAPI + MCP tool schemas)
- Write contract tests, then implement endpoints and MCP tools
- Add integration tests for request flows and edge cases
- Configure CI to run tests and linting on every change
- Prepare Render service configuration and deployment checklist

## Governance

- This constitution governs implementation and review. Any deviations REQUIRE
  explicit justification recorded in the plan and approved in review.
- Amendments MUST update this file, increment version per semver, and record the
  amendment date.
- Reviews MUST verify: contract bounds ([0, 120] for balance), input validation,
  auth controls, logging scope, and test coverage for core flows.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2025-10-30
