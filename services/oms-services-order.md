# oms-services-order

## Responsibility
Core order domain service. Manages the full lifecycle of customer orders: shopping cart creation, order placement, order calculations (pricing, discounts, service fees), bulk orders, delivery scheduling, and promotions application.

## Owns
- Shopping cart state
- Customer Orders (CO) and Purchase Orders (PO — legacy)
- Bulk order management
- Order calculation engine (price, tax, rebate, service fee)
- Delivery time slot and date management
- Order special messages (multi-language)
- Delivery task coordination

## Does NOT Own
- Product pricing source of truth (→ oms-services-product)
- Promotion rules (→ oms-services-nestjs/promotion)
- Payment processing (→ oms-service-payment)
- Customer profile / credit limit (→ cms-services-customer)
- Delivery fulfillment tracking (→ LMS service, external)

## APIs
Source: `api/*.yaml` (6 specs, oapi-codegen generated)

| Spec | Base Path | Key Endpoints |
|------|-----------|---------------|
| order-openapi.yaml | /orders, /admin, /resources/orders | CRUD orders, cancellations, PVP validate, rebate programs, service fees |
| shoppingcart-openapi.yaml | /shopping-cart | Cart CRUD, recommendations |
| bulkorder-openapi.yaml | /bulk-orders | Bulk order management |
| calculation-openapi.yaml | /calculation | Order price calculation |
| delivery-openapi.yaml | /delivery | Time slots, dates, base times |
| health-openapi.yaml | /health | Health check |

Auth: Bearer JWT (customer), Staff JWT, X-API-Key (internal)

## Events Published
| Topic | Trigger | Confidence |
|-------|---------|-----------|
| `oms.order.created` | New order placed | Confirmed |
| `oms.order.updated` | Order status changed | Confirmed |
| `oms.co.created` | Customer Order created | Confirmed |
| `oms.co.updated` | Customer Order updated | Confirmed |
| `oms.legacy-po.created` | Legacy PO created | Confirmed |
| `oms.order.updated.co-created` | Order updated + CO created event | Confirmed |
| `oms.gps-order-tracker` | GPS tracking update | Likely |

## Events Consumed
| Topic | Handler | Confidence |
|-------|---------|-----------|
| `lms.delivery-task` | Delivery task status update | Inferred |

## Database Ownership
- **MySQL** (`nonprod-db-oms.freshket.co:3306`) — primary
  - 73 migration files in `database/migration/`
  - Tables: shopping_cart, orders, order_special_message_languages, delivery_tasks, etc.
- **MSSQL** (`freshket-dev-mssql.cth9muhntj72.ap-southeast-1.rds.amazonaws.com:1433/freshketdev`) — legacy read

## Dependencies

### Internal Services (HTTP)
| Env Var | Target Service | Usage |
|---------|---------------|-------|
| `APP_PRODUCTDSN` | oms-services-product | SKU pricing, product info |
| `APP_PROMOTIONDSN` | oms-services-nestjs/promotion | Promotion validation |
| `APP_RECOMMENDDSN` | oms-services-recommendation | Cart recommendations |
| `APP_CUSTOMERDSN` | cms-services-customer | Customer credit check |
| `APP_FULFILLMENTDSN` | LMS fulfillment | Delivery fulfillment |
| `APP_ORDERADAPTERDSN` | oms-services-nestjs/orderadapter | Order data sync |
| `APP_LEGACYWEBMVCDSN` | oms-api | Legacy OMS operations |
| `APP_BILLINGDSN` | billing service | Invoice reference |
| `APP_HRMSURL` | hrms-services-v2 | Staff info lookup |

HTTP clients in: `thirdparty/productapi/`, `thirdparty/promotionapi/`, `thirdparty/fulfillmentapi/`, `thirdparty/customerapi/`, `thirdparty/recommendapi/`, `thirdparty/order_adapter_api/`, `thirdparty/legacywebmvcapi/`, `thirdparty/lmsapi/`

## External Integrations
- Line Notify API (order notifications)
- Payment Coins API

## Important Files
| File | Purpose |
|------|---------|
| `cmd/server/main.go` | HTTP server entry point |
| `cmd/job/main.go` | Kafka consumer entry point |
| `cmd/scheduler/main.go` | Scheduled jobs entry point |
| `cmd/migrate/main.go` | DB migration runner |
| `event/const/event_const.go` | Canonical Kafka topic name constants |
| `http/middleware/authorized.go` | Customer JWT middleware |
| `http/middleware/authorized_staff.go` | Staff JWT middleware |
| `http/middleware/authorized_internal.go` | Internal HMAC auth middleware |
| `config/config.yaml` | Service DSN and Kafka configuration |
| `.env.example` | Environment variable reference |
| `api/order-openapi.yaml` | Primary API spec |

## Feature Flags
- GrowthBook: `APP_GROWTHBOOKURL` + `APP_GROWTHBOOKKEY`
- Used for: mass rebate logic, promotional feature rollouts

## Main Flows
1. **Cart to Order**: Customer adds items to cart → calculates price (calls product + promotion) → places order → emits `oms.order.created`
2. **Order Calculation**: Calls product service for pricing, promotion service for discounts, applies service fees and rebates
3. **Delivery Scheduling**: Customer selects delivery time slot, assigns delivery task
4. **Bulk Orders**: B2B large-quantity orders with separate management

## Risks
- **High fan-out**: Calls 8+ services synchronously during order creation — latency risk
- **Dual database**: MySQL + MSSQL creates operational complexity
- **Legacy coupling**: Direct dependency on `oms-api` (legacy .NET) for some operations

## Suggested Improvements
- Add circuit breaker / retry for thirdparty HTTP calls
- Document which operations require MSSQL vs MySQL
- Add AsyncAPI spec for Kafka events
