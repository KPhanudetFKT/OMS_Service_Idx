# cms-services-kyc-workflow

## Responsibility
Customer KYC (Know Your Customer) verification and credit management workflow service. Manages customer verification requests, approval/rejection workflows, credit term requests, and credit limit requests. Deployed as AWS Lambda functions.

## Owns
- Customer verification request lifecycle (submit → review → approve/reject)
- Credit term request lifecycle
- Credit limit request lifecycle
- KYC document uploads (S3)
- Admin approval/rejection workflows

## Does NOT Own
- Customer profile source of truth (→ cms-services-customer)
- Payment processing (→ oms-service-payment)
- Order management (→ oms-services-order)

## APIs
Source: `api/customer.open-api.yaml` (28 endpoints)
Base path: `cms/kyc-workflow`
Deployed as Lambda via `serverless-external.yml`

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/customers/request-verifications` | Submit customer verification request | Customer JWT |
| GET | `/customers` | Get customer verification info | Customer JWT |
| GET | `/resources/customers` | Search customers by keyword | Staff JWT |
| GET | `/resources/customers/verifications` | List verifications (paginated, filterable) | Staff JWT |
| GET | `/resources/customers/verifications/{guid}` | Verification detail | Staff JWT |
| POST | `/resources/customers/verifications/{guid}/approve` | Approve verification | Staff JWT |
| POST | `/resources/customers/verifications/{guid}/reject` | Reject with reason | Staff JWT |
| POST | `/resources/customers/request-credit-term` | Submit credit term request | Customer JWT |
| PUT | `/resources/customers/request-credit-term/{guid}` | Edit credit term request | Staff JWT |
| POST | `/resources/customers/request-credit-limit` | Submit credit limit request | Customer JWT |
| PUT | `/resources/customers/request-credit-limit/{guid}` | Edit credit limit request | Staff JWT |
| GET | `/resources/customers/request-credit-terms` | List credit term requests (paginated) | Staff JWT |
| GET | `/resources/customers/request-credit-terms/{guid}` | Credit term detail | Staff JWT |
| DELETE | `/resources/customers/request-credit-terms/{guid}` | Delete credit term request | Staff JWT |
| POST | `/resources/customers/request-credit-terms/{guid}/approve` | Approve credit term | Staff JWT |
| POST | `/resources/customers/request-credit-terms/{guid}/reject` | Reject credit term | Staff JWT |
| GET | `/resources/my/customers/request-credit-terms` | Own credit term requests | Customer JWT |
| GET | `/resources/my/customers/request-credit-terms/{guid}` | Own credit term detail | Customer JWT |
| GET | `/customers/invoice-upload-permissions` | Check invoice upload permission | Customer JWT |

Auth: Customer JWT (customer routes), Staff JWT via Auth0 adapter (staff routes)

## Events
No Kafka events produced or consumed. This service is purely HTTP-driven.

## Database Ownership
- **MySQL** (`freshket-nonprod-cms.cth9muhntj72.ap-southeast-1.rds.amazonaws.com`) — primary
  - Databases: `cms_kyc_workflow_*`, `cms_*`
  - Migrations in `cmd/migrate/`
- **MSSQL** — legacy read
- **AWS S3** (`cms-kyc-workflow-*`) — document uploads (KYC documents, invoices)

## Dependencies

### Internal Services (HTTP)
| Env Var | Target Service | Usage |
|---------|---------------|-------|
| `APP_CUSTOMERDSN` | cms-services-customer | Customer profile lookup |
| `APP_CRM_CUSTOMERDSN` | crm-customer-services | CRM customer data |
| `APP_NOTIFICATIONDSN` | shared-notification-service | Send KYC status notifications |
| `APP_ORDERDSN` | oms-services-order | Order data for credit checks |
| `APP_LEGACYWEBDSN` | oms-api | Legacy web operations |
| `APP_HRMSDSN` | hrms-services-v2 | Staff info for approvals |

## Stack
- Go 1.21, Echo v4, GORM (MySQL), AWS Lambda
- AWS SDK v2 (S3), oapi-codegen, uber-go/zap

## Entry Points (`cmd/`)
| Entry Point | Purpose |
|-------------|---------|
| `cmd/server/` | HTTP server (local dev / K8s) |
| `cmd/migrate/` | DB migration runner |

Deployed as Lambda via `serverless-external.yml`.

## Important Files
| File | Purpose |
|------|---------|
| `api/customer.open-api.yaml` | Full OpenAPI 3.0 spec (28 endpoints) |
| `config/config.go` | Config struct with all env vars |
| `config/config.yaml` | Default config |
| `environment/dev-external.yaml` | Lambda environment variable mapping |
| `service/` | Business logic services |
| `domain/` | Domain interfaces |
| `infrastructure/` | Repository implementations |

## Main Flows
1. **Customer Verification**: Customer submits docs → staff reviews in backoffice → approve/reject → notify customer via shared-notification-service
2. **Credit Term**: Customer requests credit terms → staff reviews history → approve/reject → update credit in cms-services-customer
3. **Credit Limit**: Customer requests higher limit → staff reviews → approve/reject

## Risks
- Maximum credit limit hard-coded default: `APP_MAXIMUM_CREDIT_LIMIT=2500000`
- Depends on oms-api (legacy) for some operations — migration target
