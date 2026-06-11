# oms-promotion-workers

## Responsibility
Promotion worker service. Syncs product SKUs and price-off data between the promotion system and oms-services-product. Listens to order events to update promotion state and manages campaign tray operations. Runs as Kubernetes pods with Kafka consumer, scheduler, and HTTP API.

## Owns
- Bulk SKU sync to promotion system
- Price-off sync from promotion to product service
- Campaign tray management
- Promotion-to-product data synchronization

## Does NOT Own
- Promotion rule definitions (→ oms-services-nestjs/promotion)
- Product catalog (→ oms-services-product)
- Order management (→ oms-services-order)

## APIs
Source: `api/product.openapi.yaml`, `api/campaign-openapi.yaml`

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/admin/bulk_save_skus_to_promotion` | Bulk sync SKUs to promotion system | Staff JWT / Internal |
| POST | `/admin/sync_one_sku_price_off_to_product` | Sync single SKU price-off to product | Staff JWT / Internal |
| GET | `/admin/sync_priceoff_to_product` | Bulk sync all price-off data to product | Staff JWT / Internal |
| POST | `/tray` | Insert tray SKU for campaign | Internal |

## Events Consumed
| Topic | Source | Usage | Confidence |
|-------|--------|-------|-----------|
| `oms.order.created` | oms-services-order | Update promotion counters on order | Confirmed |
| `oms.order.updated` | oms-services-order | Track order state changes | Confirmed |
| `oms.co.created` | oms-services-order | Customer order event processing | Confirmed |

## Events Published
No outbound Kafka events identified.

## Database
- **MySQL** — promotion and product sync data
- Kafka library: Shopify/sarama

## Stack
- Go 1.23.0 (toolchain 1.24.4), Echo v4, GORM, Shopify/sarama
- GrowthBook feature flags, gocron scheduler, AWS Lambda

## Entry Points (`cmd/`)
| Entry Point | Purpose |
|-------------|---------|
| `cmd/server-external/` | External HTTP API |
| `cmd/server-internal/` | Internal HTTP API |
| `cmd/scheduler/` | Cron-based scheduled sync jobs |
| `cmd/kafka-consumer/` | Kafka event consumer |

## Important Files
| File | Purpose |
|------|---------|
| `event/const.go` | Kafka topic constants (`oms.order.created`, etc.) |
| `event/consumer.go` | Kafka consumer setup |
| `event/producer.go` | Event producer (if any outbound events added) |
| `event/processor.go` | Per-topic message processor |
| `event/scheduler.go` | Scheduled sync logic |
| `api/product.openapi.yaml` | Product sync API spec |
| `api/campaign-openapi.yaml` | Campaign management API spec |

## Main Flows
1. **Price-off sync**: Scheduler triggers → read promotion price-off data → call oms-services-product to update SKU prices
2. **Order-driven promotion update**: Kafka consumer receives `oms.order.created` → update promotion usage counters
3. **Bulk SKU sync**: API call → fetch SKU list from promotion → batch upsert to product service

## Risks
- No `.env.example` found — config documentation gap
- Depends on both oms-services-product and promotion system — tight coupling
