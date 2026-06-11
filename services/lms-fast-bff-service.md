# lms-fast-bff-service

## Responsibility
Backend-for-Frontend (BFF) API gateway for Freshket LMS (Logistics Management System). Proxies and aggregates requests to internal transport/hub delivery services and third-party APIs. Provides delivery-related endpoints consumed by the LMS frontend. Handles Firebase authentication for riders/drivers.

## Owns
- LMS frontend API aggregation
- Delivery service proxy / aggregation
- Rider attendance management
- Firebase-authenticated rider endpoints
- S3 document uploads for LMS

## Does NOT Own
- Delivery fulfillment logic (→ internal delivery service via `THIRDPARTY_DELIVERY_BASE_URI`)
- Order management (→ oms-services-order)
- Product catalog (→ oms-services-product)

## APIs
Source: Swagger generated (`make swag-api` → `docs/`)
Swagger UI: `http://localhost:8081/swagger/index.html`
Port: `API_PORT` (default 8081)

Endpoint domains (from `internal/application/handlers/`):
- Delivery routes (time slots, dates)
- Rider attendance
- Document uploads (S3)
- Health check

Auth: Firebase JWT (external), `X-Api-Key` (internal)

## Events
No Kafka events. HTTP-only service.

## Database
- **Redis** (`THIRDPARTY_REDIS_*`) — caching
- No persistent database — BFF pattern, data from downstream services

## Stack
- Go 1.26, Echo v4, Firebase Go SDK, Redis
- AWS SDK v2 (S3), OpenTelemetry (OTLP), GrowthBook feature flags

## Entry Points
| Entry Point | Purpose |
|-------------|---------|
| `cmd/api/main.go` | Single HTTP server entry point |

## Dependencies
| Env Var | Target | Usage |
|---------|--------|-------|
| `THIRDPARTY_DELIVERY_BASE_URI` | Internal delivery service | Delivery slots, task data |
| `AUTH_BASE_URL` | Auth service | Token validation |
| `AWS_UPLOAD_BUCKET` | AWS S3 | Document uploads |
| Firebase config | Firebase | Rider JWT auth |

## Important Files
| File | Purpose |
|------|---------|
| `cmd/api/main.go` | Entry point, wires DI |
| `config/config.go` | Env-based config struct |
| `external/` | External service client implementations |
| `internal/application/handlers/` | Echo route handlers |
| `internal/domain/usecase/` | Use case implementations |
| `internal/infrastructure/repositories/` | Repository layer |
| `pkg/` | Shared utilities (cache, middleware, tracing, validator) |

## Architecture
Clean Architecture: Handler → Usecase → Repository → External Client
- OpenTelemetry spans at every layer
- Table-driven unit tests with testify mocks co-located with interface files

## Risks
- No Kafka — purely sync HTTP BFF; LMS event flows happen in the core LMS service (separate repo)
- Firebase auth is unique among Freshket Go services — operational distinction
