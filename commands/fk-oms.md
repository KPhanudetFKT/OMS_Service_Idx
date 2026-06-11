# fk-oms — oms-api endpoint migration plan

Given: $ARGUMENTS (e.g. `baseApi/Payments/Paid` or `api/authorize/intranet`)

## Steps

1. If `docs/ai/services/oms-api-caller-map.md` exists, read it — find the exact endpoint and all known callers.
2. If `docs/ai/services/oms-api.md` exists, read it — check migration readiness classification.
3. If `docs/ai/ownership/domain-ownership.md` exists, read it — identify the target modern service.
4. If docs/ai/ is absent: grep the codebase for the endpoint path to find callers.

## Migration Readiness Classification

- **P0** — active microservice callers (must migrate before decommission, highest urgency)
- **P1** — no callers or superseded by new service (safe to remove)
- **P2** — unknown callers (mobile, browser, cron) — verify before removing

## Output format

```
## Migration Plan: `<endpoint>`

**Endpoint**: <method> <path>
**Classification**: <P0/P1/P2> — <reason>
**Current .NET handler**: <Controller>.cs → <Action>()

### Current Callers
| Caller | Repo | File | Purpose |
|--------|------|------|---------|

### Target Service
**Service**: `<service-name>`
**Reason**: <domain ownership rationale>

### Implementation Plan

**Step 1**: Add endpoint to `<target-service>`
- Handler file: `http/handlers/<handler>.go`
- Business logic: `internal/services/<domain>/<domain>_service.go`
- Auth: <Internal X-API-Key / Staff JWT / Customer JWT>
- OpenAPI spec: `api/<service>-openapi.yaml`

**Step 2**: Update callers
- `<caller-service>/<file>` — change base URL from `APP_LEGACYWEBMVCDSN` to `APP_<SERVICE>DSN`

**Step 3**: Remove from oms-api
- `FreshKetApi/Controllers/<Controller>.cs` — remove or mark [Obsolete]

### PR Sequence
1. PR in `freshket/<target-service>` — add new endpoint
2. Deploy to SIT — verify with curl/Postman
3. PR in `freshket/<caller>` — update to call new service
4. Deploy to SIT — verify end-to-end
5. Deploy both to UAT — full regression
6. Deploy to PROD
7. PR in `freshket/oms-api` — remove handler

### Risk
- <concurrency/downtime risk during migration window>
- Recommend: feature flag in caller to toggle between legacy and new endpoint

### Validation Checklist
- [ ] New endpoint returns same response shape as legacy
- [ ] Auth header accepted correctly
- [ ] SIT smoke test passes
- [ ] End-to-end verified in UAT
- [ ] Rollback plan documented
```
