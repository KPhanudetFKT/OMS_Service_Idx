# oms-services (Monorepo)

## Responsibility
General-purpose OMS services monorepo for functionality that doesn't belong to a single domain service. Moved from Lambda to Kubernetes. Contains multiple sub-services: product sync, fulfillment/delivery slots, frontend request logging, GPS order tracking, recommendation refresh, mission programs, notifications, and promo codes.

## Sub-Services
| Sub-service | Purpose |
|-------------|---------|
| `product-sync-worker` | Syncs products from Legacy (oms-api) to OMS |
| `fulfillment-service` | Delivery time slot management |
| `log` | Logs frontend HTTP requests (solves C# log gap) |
| `gps-order-tracker` | GPS tracking for orders |
| `refresh-recommendation` | Triggers recommendation refresh at 6:00 AM UTC+7 Mon |
| `notification` | Internal notification service |
| `mission-program` | Mission/promotion program logic |
| `promo-code` | Promotional code service |
| `postal-code` | Postal code lookups |

## Owns
- Product sync from legacy to OMS
- Delivery time slot and date management (fulfillment-service)
- Frontend request logging
- GPS order tracking state
- Mission program logic

## Does NOT Own
- Order lifecycle (→ oms-services-order)
- Product catalog source of truth (→ oms-services-product)
- Promotion rules (→ oms-services-nestjs/promotion)

## APIs
Source: `api/product.openapi.yaml`, `api/delivery-openapi.yaml`, `api/log.openapi.yaml`

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/product-sync` | Sync product from Legacy | Internal |
| GET | `/delivery/delivery-dates` | Available delivery dates | Customer JWT |
| GET | `/delivery/delivery-time-slots` | Time slots for a date | Customer JWT |
| POST | `/delivery/refresh-data` | Force refresh delivery data | Internal |
| GET | `/delivery/base-time-slots` | Base delivery time slot config | Staff JWT |
| POST | `/public/logs/requests` | Save frontend request log | Public / Internal |

## Events Consumed
| Env Var | Topic | Source | Confidence |
|---------|-------|--------|-----------|
| `KAFKA_OMS_ORDER_DELIVERED_UPDATED_TOPIC` | `oms.order-delivered-updated.sit` | oms-services-order | Confirmed |
| `KAFKA_OMS_MISSION_PROGRAM_TOPIC` | `oms.mission_program.sit` | Unknown producer | Unknown |
| `KAFKA_OMS_ORDER_TRACKER_TOPIC` | `oms.gps-order-tracker.sit` | oms-services-order / GPS device | Confirmed |

## Events Published
No outbound Kafka events identified. Uses SQS for internal product-sync queue.

## Database
- **MySQL** — primary (via GORM)
- **MSSQL** — legacy read (SQL Server)
- **Redis** — caching
- **Elasticsearch / OpenSearch** — search indexing
- **AWS SQS** — product-sync message queue
- Kafka library: segmentio/kafka-go

## Stack
- Go 1.22, Echo v4, GORM, segmentio/kafka-go
- Redis, Elasticsearch, AWS SDK (SQS + Lambda), Jaeger/OpenTracing, GrowthBook

## Entry Points (`cmd/`)
| Entry Point | Purpose |
|-------------|---------|
| `cmd/server-external/` | External HTTP server |
| `cmd/server-internal/` | Internal HTTP server |
| `cmd/kafka-consumer/` | Kafka event consumer |
| `cmd/sqs-consumer/` | AWS SQS consumer (product sync) |
| `cmd/cronjob/` | Scheduled jobs (recommendation refresh) |

## Dependencies
| Env Var | Target Service | Usage |
|---------|---------------|-------|
| `APP_LEGACYWEBMVCDSN` | oms-api | Product sync source |
| `APP_RECOMMENDDSN` | oms-services-recommendation | Trigger recommendation refresh |

## Important Files
| File | Purpose |
|------|---------|
| `services/fulfillment/` | Delivery slot service |
| `services/gps-order-tracker/` | GPS tracking logic |
| `services/log/` | Frontend request logging |
| `services/product/` | Product sync logic |
| `services/refresh-recommendation/` | Recommendation refresh cron |
| `services/mission-program/` | Mission program logic |
| `kafka/module.go` | Kafka consumer module |
| `cmd/sqs-consumer/receive_message.go` | SQS message handler |

## Notes
- Config repo moved to `fkt-platform-charts` (chart: `oms/product-sync-worker`)
- "Don't use Lambda anymore" — all sub-services run on Kubernetes
- Consumer group ID: `oms.services.sit`
- DLQ failures alert to Slack via webhook

## Risks
- Monorepo with mixed concerns — unclear ownership boundaries
- `oms.mission_program` producer identity unknown
