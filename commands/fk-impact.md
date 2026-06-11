# fk-impact — Blast radius analysis for a Freshket change

Given: $ARGUMENTS

## Steps

1. If `docs/ai/apis/api-catalog.md` exists, read it — find HTTP callers of the affected endpoint or service.
2. If `docs/ai/events/event-catalog.md` exists, read it — find Kafka consumers/producers.
3. If `docs/ai/services/<service>.md` exists, read it — get dependency map.
4. If `docs/ai/services/portal-web.md` exists, read it — check frontend impact.
5. If docs/ai/ is absent: run grep across the codebase for the service name, endpoint path, or env var DSN to find callers manually.

## For each change, check all four dimensions

### 1. HTTP Callers (sync impact)
Which services or frontend apps call this endpoint? Check `thirdparty/` directories in Go services.

### 2. Kafka Dependents (async impact)
Which services consume events this service publishes? Which events does this service consume that may change?

### 3. Database Impact
Does this change a migration that affects deploy order? Flag any cross-service DB access (violation).

### 4. Frontend Impact
Which portal-web apps call this service (directly or via BFF)?

## Output format

```
## Impact Analysis: <change description>

**Change**: <what is changing>
**Service**: `<service-name>`

### HTTP Callers — Impacted
| Caller | File | Endpoint | Impact |
|--------|------|----------|--------|

### Kafka Dependents — Impacted
| Service | Topic | Impact |
|---------|-------|--------|

### Frontend — Impacted
| App | Page/Component | Impact |
|----|---------------|--------|

### No Impact Confirmed
- `<service>` — does not call this service

### Test Scope
- [ ] <test>

### Deploy Order (if breaking)
1. <step>

**Confidence**: Confirmed / Likely / Inferred (mark unknowns)
```
