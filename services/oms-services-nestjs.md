# oms-services-nestjs

## Responsibility
NestJS-based serverless microservices deployed as AWS Lambda functions. Houses multiple independent apps: promotion engine, notification delivery, order adapter, authorizers, OTP, and PDPA consent management.

## Apps

| App | Purpose | Deploy Mode |
|-----|---------|-------------|
| **promotion** | Promotion lifecycle management — creates, activates, deactivates promotions | Lambda + K8s |
| **notification** | Notification delivery (push, email, LINE) | Lambda |
| **orderadapter** | Order data transformation and downstream system sync | Lambda |
| **authorizer** | Customer JWT validation (API Gateway custom authorizer) | Lambda |
| **authorizer-staff** | Staff JWT/JWKS validation (API Gateway) | Lambda |
| **authorizer-internal** | Internal API key validation (API Gateway) | Lambda |
| **otp** | One-time password generation and verification | Lambda |
| **pdpa** | Privacy/consent management (Thai PDPA law) | Lambda |

## Owns
- Promotion lifecycle (create → activate → deactivate → full)
- Notification dispatch logic
- JWT/JWKS token validation (all three auth levels)
- OTP generation and verification
- PDPA/consent state

## Does NOT Own
- Promotion application to orders (→ oms-services-order calculation)
- Customer profile (→ cms-services-customer)
- Order data (→ oms-services-order)

## APIs
No OpenAPI spec (Lambda event-driven). API Gateway routes defined in `serverless-*.yml`.

Serverless configs:
- `serverless-internal.yml` — internal Lambda functions
- `serverless-internal-nonprod.yml` — nonprod variant
- `serverless-external.yml` — external-facing Lambda functions
- `serverless-external-nonprod.yml` — nonprod external variant
- `serverless-internal-container.yml` — K8s container mode
- `serverless-external-container.yml` — K8s container mode

## Events Published (promotion app)
| Topic | Trigger | Confidence |
|-------|---------|-----------|
| `oms.promotion.created` | Promotion created via API | Confirmed |
| `oms.promotion.updated` | Promotion updated | Confirmed |
| `oms.promotion.activated` | Promotion activated | Confirmed |
| `oms.promotion.deactivated` | Promotion deactivated | Confirmed |
| `oms.promotion.fulled` | Promotion quota reached | Confirmed |

## Events Consumed
| Topic | App | Confidence |
|-------|-----|-----------|
| `oms.order.created` | promotion | Confirmed |
| `oms.order.updated` | promotion | Confirmed |
| `oms.legacy-po.created` | orderadapter | Confirmed |
| `oms.co.created` (CO_CREATE_ORDER) | orderadapter | Confirmed |
| `oms.co.updated` (CO_UPDATE_ORDER) | orderadapter | Confirmed |
| `payment.transaction` | orderadapter | Confirmed |
| `oms.inv.created` (INV_CREATED) | promotion | Inferred |
| `lms.delivery-task` (DELIVERY_TASK) | promotion | Confirmed |
| `oms.order.updated.co-created` | notification | Confirmed |
| user consent topics | pdpa | Confirmed |

Kafka library: kafkajs
Lambda Kafka integration: `libs/lambdakafka/`

## Database Ownership
- **MySQL** — used by promotion app
- No direct DB access for authorizer apps (stateless token validation)

## Dependencies

### Shared Libraries (libs/)
- `bootstraper` — Lambda bootstrap logic
- `lambdakafka` — Kafka integration for Lambda
- `auth` — Authentication utilities
- `identity-header-middleware` — Request identity propagation
- `otel-logging` — OpenTelemetry logging

### External Services Called
- `APP_PRODUCTDSN` → oms-services-product (promotion needs product data)

## External Integrations
- AWS Lambda runtime
- API Gateway (custom authorizers)
- Notification channels (push, email, LINE — via notification app)

## Important Files
| File | Purpose |
|------|---------|
| `apps/promotion/` | Promotion domain logic |
| `apps/notification/` | Notification delivery |
| `apps/orderadapter/` | Order adapter logic |
| `apps/authorizer/` | Customer JWT authorizer |
| `apps/authorizer-staff/` | Staff JWKS authorizer |
| `apps/authorizer-internal/` | Internal API key authorizer |
| `apps/otp/` | OTP service |
| `apps/pdpa/` | PDPA consent management |
| `libs/lambdakafka/` | Kafka for Lambda |
| `serverless-internal.yml` | Lambda function definitions |
| `package.json` | Dependencies |

## Feature Flags
Not detected in NestJS apps (GrowthBook is Go-specific in this monorepo).

## Main Flows
1. **Promotion Lifecycle**: Staff creates promotion via API → promotion app validates and stores → emits lifecycle events → product and content services update
2. **Order-Promotion Apply**: `oms.order.created` event → promotion app calculates applicable promotions → updates order
3. **Notification**: `oms.order.updated.co-created` → notification app dispatches to customer
4. **Auth**: API Gateway invokes authorizer Lambda → validates JWT → returns IAM policy
5. **OTP**: Customer requests OTP → otp app generates → delivers via SMS/email

## Risks
- **Monorepo complexity**: Multiple distinct domains (auth, promotion, notification, OTP, PDPA) in one repo — harder to deploy independently
- **Lambda cold starts**: Event-driven Kafka consumption may have latency
- **No OpenAPI spec**: Contract documentation relies on serverless.yml inspection

## Suggested Improvements
- Consider splitting into separate repos as domains mature
- Add OpenAPI/AsyncAPI specs for each app's contracts
- Document authorizer token format and claims structure
