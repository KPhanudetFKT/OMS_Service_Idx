# oms-services-recommendation

## Responsibility
Recommendation engine service. Provides product recommendations to customers and the shopping cart experience.

## Owns
- Product recommendation data (stored in AWS S3)
- Recommendation API endpoints

## Does NOT Own
- Product catalog data (→ oms-services-product)
- Order data (→ oms-services-order)
- User behavior tracking source (→ inferred: external analytics)

## APIs
Source: `api/*.yaml` (2 specs)

| Spec | Purpose |
|------|---------|
| recommendation-openapi.yaml | Recommendation endpoints |
| health-openapi.yaml | Health check |

Auth: Inferred — Bearer JWT or X-API-Key (consistent with other services)

## Events Published
None detected.

## Events Consumed
None detected.

## Database Ownership
- **AWS S3** — recommendation data store (read-only at runtime)
- No traditional SQL database detected

## Dependencies
None detected. Read-only service consuming S3 data.

## External Integrations
- AWS S3 (AWS SDK v2, S3 Manager v1.9.0)

## Important Files
| File | Purpose |
|------|---------|
| `cmd/server/main.go` | HTTP server entry point |
| `cmd/migrate/main.go` | Likely S3 data initialization |
| `storage/` | AWS S3 integration |
| `api/recommendation-openapi.yaml` | API spec |

## Feature Flags
None detected.

## Main Flows
1. **Cart Recommendations**: oms-services-order calls recommendation API when displaying cart
2. **Product Recommendations**: oms-services-product and oms-services-content call for related products
3. **Data Refresh**: S3-backed — recommendation data likely refreshed by batch/ML pipeline (external)

## Risks
- **Opaque data pipeline**: No Kafka events or DB migrations suggest recommendations are pre-computed externally — pipeline not visible in this repo
- **S3 dependency**: Cold data reads may introduce latency
- **Low footprint**: Minimal codebase — purpose and data freshness strategy are unclear

## Suggested Improvements
- Document how recommendation data is populated in S3 (ML pipeline, batch job)
- Add confidence level to API responses
- Consider adding Kafka consumer if real-time updates are needed
