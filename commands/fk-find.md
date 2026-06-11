# fk-find — Find which Freshket service owns a capability

Given: $ARGUMENTS

## Steps

1. If `docs/ai/ownership/domain-ownership.md` exists in the current project, read it.
2. If `docs/ai/service-map.md` exists, read it too.
3. If neither exists, explore the codebase: look for relevant packages in `pkg/`, `service/`, `apps/`, `internal/` directories to infer ownership.

## Answer these questions

- **Which service owns this capability?** State the service name and repo path.
- **Why?** Cite the domain boundary or ownership rule.
- **Key files to modify**: List the specific files/packages within that service where the change would go.
- **Does NOT own warning**: Name any services that might seem related but should NOT implement this (with reason).
- **Impacted neighbors**: Other services that may need to be notified or updated.

## Output format

```
## Service Ownership: <capability>

**Owner**: `<service-name>` (<repo-directory>)
**Reason**: <domain boundary rationale>

### Key Files
- `<service>/pkg/<domain>/<domain>_service.go` — business logic
- `<service>/pkg/<domain>/<domain>_repository.go` — data layer
- `<service>/api/<service>-openapi.yaml` — if API change needed

### Does NOT Own
- `<other-service>` — <why not>

### Neighbors to Notify
- `<service>` — <what they need to know>
```
