# Implementation Plan: MCP Vacation Manager

**Branch**: `001-mcp-vacation-manager` | **Date**: 2025-10-30 | **Spec**: specs/001-mcp-vacation-manager/spec.md
**Input**: Feature specification from `/specs/001-mcp-vacation-manager/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a simple vacation manager exposed via MCP for AI tools, with two primary
capabilities: check vacation balance (returns 0–120 hours) and request vacation
(full-day increments, weekdays-only). Provide a minimal Python web service for
Render deployment.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic, Uvicorn  
**Storage**: In-memory (MVP), pluggable later  
**Testing**: pytest  
**Target Platform**: Render web service (Linux container)  
**Project Type**: web  
**Performance Goals**: Balance check p95 < 200ms; request creation p95 < 500ms  
**Constraints**: Balance in [0, 120]; full-day only; weekdays only; employee self-access only  
**Scale/Scope**: Simple example, single service, low concurrency

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates derived from `VacationMCP Constitution`:

- MCP-first interface: Provide MCP tools `check_vacation_balance`, `request_vacation` → PASS (planned)
- Python web service deployable to Render with health endpoints → PASS (planned)
- Deterministic contracts and validation: balance in [0,120]; request validation → PASS (planned)
- Security & privacy: basic auth (API key), minimal logs, no PII leakage → PASS (planned)
- Testing & observability: contract/integration tests, structured logs → PASS (planned)

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: Single project. Use `src/` for service code, `tests/` for
contract/integration/unit tests.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

