# crm-customer-services

## Responsibility
CRM lead and customer acquisition service. Manages lead lifecycle, sales management, and 3rd-party CRM integrations (Salesforce, Braze, Freshchat). Runs as both Kubernetes API and AWS Lambda functions.

## Owns
- Lead creation and management
- Customer acquisition pipeline
- Salesforce data synchronization
- CRM-specific customer data (`crm_customer` DB)
- User registration events publication

## Does NOT Own
- Customer profile (KYC, credit limit) (→ cms-services-customer)
- Order data (→ oms-services-order)
- Authentication (→ oms-services-nestjs/authorizer)
- CRM backoffice UI (→ crm-api)

## APIs
No OpenAPI spec. Lambda-native + Echo HTTP API.

Entry points:
- `cmd/api/main.go` — K8s REST API (port 5555)
- `cmd/lambda/main.go` — AWS Lambda (external-facing)
- `cmd/lambda2/main.go` — AWS Lambda (internal-facing)
- `cmd/cronjob/main.go` — Scheduled jobs
- `cmd/kafka-consumer/main.go` — Event consumer

Auth: `AUTHORIZER_PROVIDER_BASE_URL` + `AUTHORIZE_ENDPOINT` — custom authorization provider

## Events Published
| Topic | Trigger | Confidence |
|-------|---------|-----------|
| `crm.customer` (env: `KAFKA_TOPICS_CRM_CUSTOMER`) | Customer data update from CRM | Confirmed |

## Events Consumed
Order/payment topics referenced in serverless configs (currently commented out — Inferred).

## Database Ownership
- **MySQL CRM** (`nonprod-db-crm.freshket.co:3306/crm_customer_sit`) — CRM lead data
- **MySQL User** (`nonprod-db-crm.freshket.co:3306/crm_user`) — User data
- **MSSQL** (`freshket-dev-mssql.cth9muhntj72.ap-southeast-1.rds.amazonaws.com:1433/freshketdev`) — legacy intranet

## Dependencies

### Internal Services (HTTP)
| Env Var | Target Service | Usage |
|---------|---------------|-------|
| `AUTHORIZER_PROVIDER_BASE_URL` | Authorization provider | Token validation |
| `CRM_API` | crm-api | Backoffice data |

## External Integrations
- **Salesforce** (`SALESFORCE_HOST`) — CRM sync via Simpleforce SDK
- **Braze** (`BRAZE_URL`) — Marketing automation
- **Freshchat** (`FRESHCHAT_URL`) — Customer support chat
- **GrowthBook** (`FEATURE_FLAG_URL`) — Feature flags

## Important Files
| File | Purpose |
|------|---------|
| `cmd/api/main.go` | K8s API entry point |
| `cmd/lambda/main.go` | Lambda entry point (external) |
| `cmd/lambda2/main.go` | Lambda entry point (internal) |
| `cmd/cronjob/main.go` | Scheduled jobs |
| `cmd/kafka-consumer/main.go` | Kafka consumer |
| `cmd/data_migrations/main.go` | Data migration tool |
| `internal/domains/` | Domain logic |
| `internal/infra/` | Infrastructure adapters |
| `internal/presentation/` | HTTP handlers |
| `pkg/auth/` | Auth utilities |
| `pkg/authcustomer/` | Customer auth |

## Feature Flags
- GrowthBook: `FEATURE_FLAG_URL=https://growthbook-api.freshket.co/api/features/sdk-OIpztrkhF17JQdB`

## Main Flows
1. **Lead Creation**: Sales staff creates lead → stored in MySQL → published to Salesforce
2. **Customer Conversion**: Lead converts → publishes `crm.customer` event → cms-services-customer picks up
3. **Salesforce Sync**: Bidirectional sync with Salesforce CRM via Simpleforce SDK
4. **Scheduled Jobs**: Cronjob for lead status updates, Salesforce reconciliation
5. **Data Migrations**: `cmd/data_migrations` for one-off data corrections

## Risks
- **Dual deployment mode**: K8s + Lambda adds operational complexity — unclear which mode handles which traffic
- **No OpenAPI spec**: No machine-readable contract
- **Commented-out Kafka consumers**: Suggests events were planned but not yet implemented

## Suggested Improvements
- Clarify K8s vs Lambda traffic routing
- Add OpenAPI spec for REST endpoints
- Document and activate planned Kafka consumers if needed
