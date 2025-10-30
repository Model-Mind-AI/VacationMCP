# Data Model: MCP Vacation Manager

## Entities

### Employee
- id: string (unique)
- name: string (optional for MVP display)

### VacationBalance
- employeeId: string (FK -> Employee.id)
- hoursAvailable: integer [0..120]
- lastUpdated: datetime

### VacationRequest
- id: string (unique)
- employeeId: string (FK -> Employee.id)
- startDate: date (weekday-only counting)
- endDate: date (inclusive; weekdays only)
- totalDays: integer (derived)
- totalHours: integer (derived: totalDays * 8)
- status: enum [Pending, Approved, Declined]
- reason: string (on decline)
- createdAt: datetime

## Rules
- Balance hours must remain within [0,120]
- Requests must be full-day increments; no partial-day
- Count only weekdays between start and end dates
- No overlapping requests per employee
- Only employee can view their own data (MVP)
