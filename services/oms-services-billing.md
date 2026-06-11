# oms-services-billing

## Responsibility
OMS Billing service. Consumes customer order events from Kafka, generates billing documents (invoices, credit notes, cash vouchers) as PDFs, stores them in S3, and publishes document-lifecycle events consumed by oms-service-payment.

## Owns
- Billing document generation (invoice, credit note, cash voucher)
- PDF rendering via wkhtmltopdf
- Billing document storage (AWS S3)
- Customer order billing event processing

## Does NOT Own
- Payment processing (→ oms-service-payment)
- Order lifecycle (→ oms-services-order)
- Credit limit management (→ cms-services-customer)

## APIs
No OpenAPI spec found. HTTP handlers in `http/`.

Port: 1323 (standard Go service port)
Base URL env (in callers): `APP_BILLINGDSN` (set in oms-services-order)

## Events Consumed
| Env Var | Topic (actual value in env) | Source | Confidence |
|---------|---------------------------|--------|-----------|
| `KAFKA_TOPIC_CUSTOMERORDER_CREATED` | `oms.co.created` | oms-services-order | Confirmed |
| `KAFKA_TOPIC_CUSTOMERORDER_UPDATED` | `oms.co.updated` | oms-services-order | Confirmed |

## Events Published
| Env Var | Topic | Consumers | Confidence |
|---------|-------|-----------|-----------|
| `KAFKA_TOPIC_CUSTOMERORDER_DOCUMENTCREATED` | `billing.invoice` (maps to billing.invoice.sit/prd) | oms-service-payment | Confirmed |
| `KAFKA_TOPIC_CUSTOMERORDER_DOCUMENTUPDATED` | `billing.invoice.updated` | oms-service-payment | Confirmed |
| `KAFKA_TOPIC_CUSTOMERORDER_DOCUMENTGENERATING` | `billing.credit-note` / `billing.cash-voucher` | oms-service-payment | Inferred |

**Gap resolved**: This service is the producer of all `billing.*` Kafka topics consumed by oms-service-payment.

## Database Ownership
- **MySQL** — primary billing data
- Kafka library: Shopify/sarama

## Dependencies

### Internal Services (HTTP)
| Env Var | Target Service | Usage |
|---------|---------------|-------|
| `APP_MCDOCUMENT_DSN` | mc-document service | Document template / owner config |
| `BILLING_DSN` | Billing backend (legacy?) | Additional billing data |

### External
- **AWS S3** (`APP_STORAGE_BUCKET`) — billing document storage
- **wkhtmltopdf** (`github.com/SebastiaanKlippert/go-wkhtmltopdf`) — PDF generation from HTML templates

## Stack
- Go 1.21.3, Echo v4, GORM, Shopify/sarama
- AWS SDK v2 (S3), oapi-codegen

## Important Files
| File | Purpose |
|------|---------|
| `cmd/server/` | HTTP server entry point |
| `cmd/migrate/` | DB migration runner |
| `event/consumer.go` | Kafka consumer setup |
| `event/producer.go` | Billing event producer |
| `config/config.go` | Config struct (KafkaTopic fields) |
| `config/config.yaml` | Default config with Kafka topic mapping |

## Main Flows
1. **Invoice Generation**: `oms.co.created` → fetch order data → render PDF → upload to S3 → publish `billing.invoice`
2. **Document Update**: `oms.co.updated` → re-render document → publish `billing.invoice.updated`
3. **Payment receives**: oms-service-payment consumes billing.* events to track payment state

## Risks
- `event/const/event_const.go` is empty — topic names come from config only, no compile-time constants
- `BILLING_DSN` purpose unclear — may be a legacy finance system endpoint
