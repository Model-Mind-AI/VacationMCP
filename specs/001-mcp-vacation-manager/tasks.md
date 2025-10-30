# Tasks: MCP Vacation Manager

**Input**: Design documents from `/specs/001-mcp-vacation-manager/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Path Conventions
- Single project: `src/`, `tests/` at repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create project structure per implementation plan
- [X] T002 Initialize Python project and dependencies in requirements.txt
- [X] T003 [P] Create FastAPI app scaffold in src/app.py
- [X] T004 [P] Add health endpoint in src/app.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [X] T005 Configure API key auth middleware in src/middleware/auth.py
- [X] T006 [P] Configure structured logging in src/lib/logging.py
- [X] T007 [P] Create in-memory stores in src/lib/store.py (balances, requests)
- [X] T008 Implement weekday counting utility in src/lib/date_utils.py
- [X] T009 Define Pydantic models in src/models/schemas.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Employee checks vacation balance (Priority: P1) 🎯 MVP

**Goal**: Enable employees to retrieve available vacation balance (0–120 hours)
**Independent Test**: Balance endpoint/tool returns value within [0,120]

### Implementation for User Story 1

- [X] T010 [P] [US1] Implement BalanceService in src/services/balance_service.py
- [X] T011 [US1] Implement GET /balance in src/app.py
- [X] T012 [US1] Add MCP tool `check_vacation_balance` in src/mcp/tools.py
- [X] T013 [US1] Wire auth and logging for balance flow in src/app.py

**Checkpoint**: User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Employee requests vacation (Priority: P2)

**Goal**: Allow full-day, weekdays-only vacation requests validated against balance
**Independent Test**: Valid requests are accepted; invalid requests return clear reason

### Implementation for User Story 2

- [X] T014 [P] [US2] Implement RequestService in src/services/request_service.py
- [X] T015 [US2] Implement POST /vacation-requests in src/app.py
- [X] T016 [US2] Add MCP tool `request_vacation` in src/mcp/tools.py
- [X] T017 [US2] Prevent overlaps and enforce weekdays-only/full-day in src/services/request_service.py

**Checkpoint**: User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Employee reviews pending/approved requests (Priority: P3)

**Goal**: Summarize an employee’s pending and approved requests
**Independent Test**: Returns accurate list scoped to employee

### Implementation for User Story 3

- [X] T018 [P] [US3] Implement listing logic in src/services/request_service.py
- [X] T019 [US3] Implement GET /vacation-requests in src/app.py
- [X] T020 [US3] Add MCP tool `list_vacation_requests` in src/mcp/tools.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T021 [P] Documentation updates in specs/001-mcp-vacation-manger/quickstart.md
- [ ] T022 Code cleanup and refactoring across src/
- [ ] T023 Performance tuning of service hot paths in src/services/
- [X] T024 [P] Add basic unit tests in tests/unit/
- [X] T025 Security hardening (rate limit, header validation) in src/middleware/

---

## Dependencies & Execution Order

### Phase Dependencies
- Setup (Phase 1): No dependencies - can start immediately
- Foundational (Phase 2): Depends on Setup completion - BLOCKS all user stories
- User Stories (Phase 3+): Depend on Foundational completion
  - US1 (P1) → US2 (P2) → US3 (P3)
- Polish (Final): After desired user stories complete

### Parallel Opportunities
- T003 and T004 can run in parallel (different routes in src/app.py)
- T006 and T007 can run in parallel (lib modules)
- Within US1: T010 can proceed in parallel with T011
- Within US2: T014 can proceed in parallel with T015
- Within US3: T018 can proceed in parallel with T019

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Setup + Foundational
2. Implement US1 tasks (T010–T013)
3. Validate and demo

### Incremental Delivery
1. Add US2 tasks (T014–T017) → Validate → Demo
2. Add US3 tasks (T018–T020) → Validate → Demo
3. Polish tasks (T021–T025)
