# oms-service-payment

## Responsibility
Payment processing domain service. Handles payment charges, invoice management, credit notes, cash vouchers, and Freshket coins. Integrates with multiple Thai payment gateways.

## Owns
- Payment transactions (charge lifecycle)
- Invoices
- Credit notes
- Cash vouchers
- Freshket coins (loyalty points as payment)
- Payment gateway integrations

## Does NOT Own
- Order creation (→ oms-services-order)
- Customer billing address (→ cms-services-customer)
- Invoice PDF generation (→ Likely billing service, external)

## APIs
No OpenAPI spec found. Internal API contracts only.

HTTP handlers by domain in `http/handlers/`:
- Charge
- Payment
- Invoice
- Credit Note
- Cash Voucher
- Coin

Auth: Bearer JWT, X-API-Key (internal)

## Events Published
None confirmed. Inferred: may publish `payment.transaction` after processing.

## Events Consumed
| Topic | Handler | Confidence |
|-------|---------|-----------|
| `billing.invoice` | Invoice creation | Confirmed |
| `billing.invoice.updated` | Invoice update | Confirmed |
| `payment.transaction` | Transaction event | Confirmed |
| `billing.credit-note` | Credit note creation | Confirmed |
| `payment.coin` | Coin payment event | Confirmed |
| `billing.cash-voucher` | Cash voucher event | Confirmed |

Consumer entry: `cmd/kafka-consumer/main.go`
Kafka library: segmentio/kafka-go

Note: Producers of `billing.*` topics are **unknown** — no billing service found in this monorepo. Likely a separate repository.

## Database Ownership
- **MySQL** (`nonprod-db-oms.freshket.co:3306/oms_payment_sit`) — primary
  - 32 migration files in `database/`
- **MSSQL** (`freshket-dev-mssql.cth9muhntj72.ap-southeast-1.rds.amazonaws.com:1433/freshketdev`) — legacy

## Dependencies

### Internal Services (HTTP)
| Env Var | Target Service | Usage |
|---------|---------------|-------|
| `APP_JULIANBASEURL` | oms-web (Julian) | Redirect after payment |
| `APP_HRMSURL` | hrms-services-v2 | Staff info |

Payment gateway integrations in `third_party/`:
- Omise (`third_party/omise/`)
- KBank (`third_party/kbank/`)
- KTB (`third_party/ktb/`)
- TTB (`third_party/ttb/`)
- Offline payment handler

## External Integrations
- Omise — Thai payment gateway (primary)
- KBank payment gateway
- KTB payment gateway
- TTB payment gateway
- Offline payment processing

## Important Files
| File | Purpose |
|------|---------|
| `cmd/server/main.go` | HTTP server entry point |
| `cmd/kafka-consumer/main.go` | Kafka consumer entry point |
| `cmd/scheduler/server/server.go` | Scheduled tasks (reconciliation?) |
| `cmd/migrate/main.go` | DB migration runner |
| `internal/services/charge/` | Charge service logic |
| `internal/services/payment/` | Payment service logic |
| `internal/services/invoice/` | Invoice service logic |
| `third_party/` | Payment gateway clients |
| `config/thirdparty/` | Gateway configuration |
| `Taskfile` | Build tool (Task, not Make) |

## Feature Flags
- GrowthBook integration for charge service feature toggling
- TTL: 5 minutes

## Main Flows
1. **Payment Charge**: Receives billing event → selects gateway → processes charge → records transaction
2. **Invoice Processing**: Consumes `billing.invoice` → stores invoice record
3. **Refund via Credit Note**: Consumes `billing.credit-note` → processes refund
4. **Coin Redemption**: Consumes `payment.coin` → deducts loyalty points
5. **Scheduled Reconciliation**: Scheduler reconciles payment status with gateways

## Risks
- **Unknown billing producers**: `billing.*` topics have no known producer in this monorepo — risk of broken event chain if billing service changes
- **Multiple gateway complexity**: 4 payment gateways → high test surface
- **No OpenAPI spec**: No machine-readable contract for this service's REST API

## Suggested Improvements
- Add OpenAPI spec for HTTP endpoints
- Document which payment gateways are used in which environments
- Add AsyncAPI spec for consumed Kafka events
- Identify and document the billing service (separate repo)
