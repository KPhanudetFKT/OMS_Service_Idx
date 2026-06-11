# shared-notification-service

## Responsibility
Shared notification platform. Receives notification-trigger events via Kafka, persists notifications to PostgreSQL, pushes real-time updates to clients via WebSocket (backed by Redis Pub/Sub), and sends transactional emails (SMTP + S3-hosted templates). Produces backwards-compatible `billing.email.*` events for legacy billing consumers.

## Owns
- In-app notification persistence and delivery
- Real-time WebSocket push notifications
- Transactional email sending (SMTP via S3 templates)
- Notification read/unread state (Redis-cached unread counts)
- `notification.email.sent` / `billing.email.*` event production

## Does NOT Own
- Notification trigger logic (callers publish `notification.trigger` events)
- LINE / push notifications (→ oms-services-nestjs/notification for older channels)
- SMS / OTP (→ oms-services-nestjs/otp)

## APIs
Source: Swagger generated (`make swag-api` → `docs/`)

Two boundaries (configured via `BOUNDARY` env var):
- **external** — Auth0 JWT, customer-facing
- **internal** — `X-Api-Key`, service-to-service

Port: `API_PORT` (default 8080)

Key endpoint domains (from clean-arch handler structure):
- Notifications CRUD (list, mark read, unread count)
- WebSocket connection endpoint for real-time push
- Email send/status endpoints

## Events Consumed
| Env Var | Topic | Source | Confidence |
|---------|-------|--------|-----------|
| `KAFKA_TOPIC_NOTIFICATION` | `notification.trigger` | Any service that triggers notifications | Confirmed |

## Events Published
| Env Var | Topic | Consumers | Confidence |
|---------|-------|-----------|-----------|
| `KAFKA_TOPIC_EMAIL_SENT` | `billing.email.sit` / `billing.email.prd` | billing/finance consumers | Confirmed |

Note: `KAFKA_TOPIC_EMAIL_SENT` is named `billing.email.<env>` to maintain backwards compatibility with existing finance consumers. This service **produces** that topic.

## Internal Event Types (constants)
| Constant | Value |
|----------|-------|
| `EventTypeNotificationTrigger` | `notification.trigger` |
| `EventTypeEmailSend` | `notification.email.send` |
| `EventTypeEmailSent` | `notification.email.sent` |

## Database Ownership
- **PostgreSQL** (`THIRDPARTY_POSTGRES_*`) — notification store (not MySQL — unique among Freshket Go services)
  - Migrations in `migrations/`
- **Redis** (`THIRDPARTY_REDIS_*`) — unread count cache + WebSocket Pub/Sub channel

## Stack
- Go 1.26, Echo v4, GORM (postgres driver), IBM/sarama
- gorilla/websocket, Redis, OpenTelemetry (OTLP), AWS S3 (email templates)

## Entry Points (`cmd/`)
| Entry Point | Purpose |
|-------------|---------|
| `cmd/api/` | Echo HTTP server (REST + WebSocket) |
| `cmd/consumer/` | Kafka consumer → DB write → Redis Pub/Sub publish |
| `cmd/adapter/` | WebSocket Hub — Redis subscriber → push to connected clients |

## Dependencies
| Env Var | Target | Usage |
|---------|--------|-------|
| `EMAIL_TEMPLATE_S3_BUCKET` | AWS S3 | Email HTML template storage |
| `EMAIL_PROVIDER_HOST/PORT/USER/PASSWORD` | SMTP provider | Transactional email delivery |
| `AUTH_BASE_URL` | Auth0 | JWT verification for external routes |

## Important Files
| File | Purpose |
|------|---------|
| `cmd/api/main.go` | HTTP server + WebSocket entry |
| `cmd/consumer/main.go` | Kafka consumer entry |
| `cmd/adapter/main.go` | WebSocket adapter / Redis subscriber |
| `constants/constants.go` | Event type constants |
| `config/config.go` | Full config struct with all env var mappings |
| `pkg/ws/` | WebSocket infrastructure |

## Main Flows
1. **In-app notification**: Caller publishes `notification.trigger` → consumer writes to PostgreSQL → publishes to Redis channel → WebSocket adapter pushes to connected browser
2. **Email notification**: `notification.trigger` with email type → consumer sends via SMTP → publishes `notification.email.sent` (= `billing.email.*`)
3. **Unread count**: Redis-cached; TTL 30s

## Risks
- PostgreSQL (not MySQL) — different ops setup from other Go services
- `billing.email.*` topic name is set by callers' env — must match finance consumer config in each env
