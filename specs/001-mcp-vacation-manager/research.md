# Research: MCP Vacation Manager

## Decisions

- Decision: Use FastAPI for the web service
- Rationale: Async-first, built-in OpenAPI generation, strong Pydantic validation
- Alternatives considered: Flask (simpler but less typing/validation), Django (heavier)

- Decision: Use API key authentication via header for MVP
- Rationale: Simple to configure and adequate for a demo; minimizes scope
- Alternatives considered: OAuth2 (overkill for MVP), session auth (not needed)

- Decision: In-memory storage for balances and requests
- Rationale: Keeps example simple; can be replaced with DB later
- Alternatives considered: SQLite/PostgreSQL (adds setup complexity)

- Decision: Weekdays-only counting and full-day increments
- Rationale: Matches clarified policy; ensures deterministic validation
- Alternatives considered: Partial-day support (out of scope for MVP)

## Best Practices

- FastAPI: Pydantic models for request/response; explicit error models
- Auth: Use `Authorization: Bearer <API_KEY>` or `X-API-Key` header consistently
- Logging: Structured logs with correlation IDs; avoid PII in logs
- Testing: Contract tests against OpenAPI; integration tests for flows

## Patterns

- OpenAPI-first contracts drive implementation
- Validation layer ensures hours within [0, 120] and no overlaps
- Separate domain logic from transport (MCP vs REST share services)
