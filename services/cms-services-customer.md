# cms-services-customer (CIMS)

## Responsibility
Customer Information Management System (CIMS). Manages customer profiles, KYC verification, credit limit management, and customer notifications. Acts as the system of record for customer identity and financial eligibility.

## Owns
- Customer profile data
- KYC (Know Your Customer) verification status
- Credit limit management
- Customer notification preferences
- External → internal customer ID mapping

## Does NOT Own
- Lead / acquisition data (→ crm-customer-services, crm-api)
- Order history (→ oms-services-order)
- Payment methods (→ oms-service-payment)
- Authentication tokens (→ oms-services-nestjs/authorizer)

## APIs
Source: `api/customer-openapi.yaml` (1 spec)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/info` | GET | Customer profile info |
| `/kyc` | GET/POST | KYC verification status |
| `/credit-limit/check` | GET | Credit limit check |

Two HTTP servers:
- **Internal server** (`cmd/server-internal/main.go`) — for service-to-service calls
- **External server** (`cmd/server-external/main.go`) — for customer-facing requests via API Gateway

Auth: Bearer JWT (external), X-API-Key (internal)

## Events Published
| Topic | Trigger | Confidence |
|-------|---------|-----------|
| `cms.customer` (env: `KAFKA_TOPIC_CMS_CUSTOMER`) | Customer profile update | Confirmed |

## Events Consumed
| Topic | Handler | Confidence |
|-------|---------|-----------|
| `crm.user.registered.sit` (env: `KAFKA_TOPIC_CRM_USER_REGISTERED`) | New user registration → create customer record | Confirmed |
| `crm.customer` (env: `KAFKA_TOPIC_CRM_CUSTOMER`) | CRM customer update → sync profile | Confirmed |

Consumer entry: `cmd/kafka-consumer/main.go`
Kafka library: segmentio/kafka-go

## Database Ownership
- **MySQL** (`nonprod-db-crm.freshket.co:3306/oms_customer`) — primary
  - 8 migration files in `migration/`
- **MSSQL Master** (`freshket-dev-mssql.cth9muhntj72.ap-southeast-1.rds.amazonaws.com:1433/freshketdev`) — legacy
- **MSSQL Replica** — same host, separate credentials

## Dependencies

### Internal Services (HTTP)
| Env Var | Target Service | Usage |
|---------|---------------|-------|
| `INTERNALCRM_DNS` | crm-api | Internal CRM data |
| `CRM_DNS` | crm-api (Lambda) | CRM Lambda API |
| `CRM_KUB_DNS` | crm-customer-services (K8s) | CRM K8s API |
| `CRM_CUSTOMER_INFO` | crm-customer-services | Customer info endpoint |
| `HRMS_HOST` | hrms-services-v2 | Staff info |

HTTP clients in: `infrastructure/api/order/`, `infrastructure/api/crm/`

## External Integrations
- **MOEngage** (`MOENGAGE_HOST`) — customer engagement / marketing automation
- **Line Bot SDK** — LINE messaging notifications
- **Firebase** — (inferred from dependencies)

## Important Files
| File | Purpose |
|------|---------|
| `cmd/server-internal/main.go` | Internal HTTP server |
| `cmd/server-external/main.go` | External HTTP server (API Gateway) |
| `cmd/kafka-consumer/main.go` | Kafka consumer |
| `cmd/migration/main.go` | DB migration runner |
| `service/customer/` | Core customer service logic |
| `service/customer-notification/` | Notification service |
| `infrastructure/api/crm/` | CRM HTTP client |
| `infrastructure/api/moengage/` | MOEngage client |
| `libs/auth/auth.go` | JWT verification |
| `domain/` | Service and repository interfaces |
| `app/middleware/` | HTTP middleware |

## Feature Flags
- GrowthBook: `FEATURE_FLAG_HOST=https://growthbook-api.freshket.co/api/features/sdk-OIpztrkhF17JQdB`
- TTL: 5 minutes (`FEATURE_FLAG_TTL`)

## Main Flows
1. **Customer Registration**: `crm.user.registered` event → create customer record in MySQL
2. **Profile Sync**: `crm.customer` event → update customer profile from CRM data
3. **KYC Verification**: External server endpoint → update KYC status → publish `cms.customer`
4. **Credit Limit Check**: Order service calls `/credit-limit/check` before order placement
5. **Customer Notification**: LINE messaging for account/KYC status updates

## Architecture Notes
- Uses uber-go/fx for dependency injection (unique among Go services)
- Clean architecture: `domain/` interfaces → `service/` implementations → `infrastructure/` adapters
- Dual database design: MySQL (primary business data) + MSSQL (legacy read)

## Risks
- **Multiple CRM endpoints**: 4 different CRM-related env vars (`INTERNALCRM_DNS`, `CRM_DNS`, `CRM_KUB_DNS`, `CRM_CUSTOMER_INFO`) — unclear which is authoritative
- **Unknown `cms.customer` consumers**: Who consumes `cms.customer` topic is not documented

## Suggested Improvements
- Clarify and consolidate CRM endpoint configuration (4 vars → 1–2)
- Document consumers of `cms.customer` topic
- Add AsyncAPI spec for Kafka events
