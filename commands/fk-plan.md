# fk-plan — End-to-end feature implementation plan for Freshket

Given: $ARGUMENTS

## Steps

Read all relevant docs/ai/ files if present:
1. `docs/ai/service-map.md`
2. `docs/ai/ownership/domain-ownership.md`
3. `docs/ai/architecture-principles.md`
4. `docs/ai/events/event-catalog.md`
5. `docs/ai/apis/api-catalog.md`
6. Relevant `docs/ai/services/<service>.md` files
7. Relevant `docs/ai/flows/*.md` if touching an existing flow

If docs/ai/ is absent: explore the codebase to discover service ownership and patterns.

## Answer for every feature

- Which service owns the core business logic?
- Which services need async event notification?
- Which services need sync HTTP calls?
- Does this change any existing API contracts?
- Are new Kafka events needed? What naming convention?
- Does this require a DB migration?
- Does this affect the frontend? Which app(s)?
- Is a feature flag needed? (GrowthBook — default OFF)
- Does this touch any oms-api legacy endpoints?
- What are the auth requirements?

## Output format

```
## Feature Plan: <feature name>

**Summary**: <1-2 sentences>

### 1. Service Ownership
**Primary owner**: `<service>` — <reason>
**Supporting services**: <list with roles>

### 2. API Changes

#### New Endpoints
| Service | Method | Path | Auth | Purpose |
|---------|--------|------|------|---------|

#### Modified Endpoints (additive only)
| Service | Endpoint | Change |
|---------|---------|--------|

#### OpenAPI Spec Files to Update
- `<service>/api/<service>-openapi.yaml`

### 3. Kafka Events

#### New Events to Publish
| Topic | Producer | Consumers | When |
|-------|----------|-----------|------|

#### Existing Events Affected
| Topic | Change |
|-------|--------|

### 4. Database Changes
| Service | Migration | Type |
|---------|-----------|------|

Migration file: `<service>/database/migration/<N>_<description>.go`

### 5. Frontend Changes
| App | Change | BFF needed? |
|----|--------|------------|

### 6. Feature Flag
- Flag name: `<kebab-case-name>`
- Provider: GrowthBook (`sdk-OIpztrkhF17JQdB`)
- Rollout: <phased plan>
- Implementation: `thirdparty/growth_book/` in `<service>`

### 7. Implementation Order (PR Sequence)
1. DB migration
2. Service logic + endpoint
3. Event publisher/consumer
4. Frontend
5. Enable flag in SIT

### 8. Test Plan
- [ ] Unit: <logic under test>
- [ ] Integration: <endpoint + DB + event>
- [ ] E2E: <full user journey>
- [ ] Regression: <existing flows>

### 9. Risks & Dependencies
- <dependency that must land first>
- Feature flag must default to OFF
```
