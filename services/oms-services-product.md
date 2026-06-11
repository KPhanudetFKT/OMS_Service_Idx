# oms-services-product

## Responsibility
Product and catalog domain service. Manages SKUs, categories, brands, labels, pricing (including area-based and private pricing), and product search. Primary data source for all product information consumed by the order service and frontends.

## Owns
- SKU definitions and metadata
- Product categories and brands
- Product labels and tags
- Area-based pricing and private pricing
- Product search index (Algolia primary, Elasticsearch fallback)
- Pre-search recommendations
- Product settings / configuration

## Does NOT Own
- Promotion rules (→ oms-services-nestjs/promotion)
- Order-specific pricing calculation (→ oms-services-order)
- Customer-specific pricing outside of private price (→ oms-services-order)
- Product recommendations (→ oms-services-recommendation)

## APIs
Source: `api/*.yaml` (8 specs)

| Spec | Base Path | Key Endpoints |
|------|-----------|---------------|
| sku-openapi.yaml | /resources/skus, /admin/skus | SKU CRUD, 40+ endpoints, area-prices, private-prices |
| product-openapi.yaml | /resources/products | Product management |
| category-openapi.yaml | /resources/categories | Category management |
| brand-openapi.yaml | /resources/brands | Brand management |
| label-openapi.yaml | /resources/labels | Label management |
| presearch-openapi.yaml | /pre-search-recommendations, /suggestions | Pre-search |
| setting-openapi.yaml | /admin/settings | Product settings |
| health-openapi.yaml | /health | Health check |

Auth: Bearer JWT (customer), Staff JWT, X-API-Key (internal)

## Events Published
None directly. Promotion updates are reflected via consumed events.

## Events Consumed
| Topic | Handler | Confidence |
|-------|---------|-----------|
| `oms.promotion.created` | Update product promotion data | Confirmed |
| `oms.promotion.updated` | Update product promotion data | Confirmed |

Consumer entry: `cmd/job/main.go`, event config: `event/config.go`

## Database Ownership
- **MySQL** (`nonprod-db-oms.freshket.co:3306/oms_product_sit`) — primary
  - 54 migration files in `database/migration/`
- **MSSQL** (`freshket-dev-mssql.cth9muhntj72.ap-southeast-1.rds.amazonaws.com:1433/freshketdev`) — legacy SKU data
- **Elasticsearch** (`vpc-opensearch-dev-*.ap-southeast-1.es.amazonaws.com`, index: `product_search_sit`) — search
- **Redis** (localhost:6379) — caching layer (5-minute TTL)
- **Algolia** — primary search SaaS

## Dependencies

### Internal Services (HTTP)
| Env Var | Target Service | Usage |
|---------|---------------|-------|
| `APP_RECOMMENDDSN` | oms-services-recommendation | Recommendation data |
| `APP_PROMOTIONDNS` | oms-services-nestjs/promotion | Promotion info |
| `APP_HRMSDSN` | hrms-services-v2 | Staff lookup |
| `APP_THAITOKENIZERURL` | shared/thai-tokenizer (K8s) | Thai search tokenization |

HTTP clients in: `thirdparty/promotionapi/`, `thirdparty/recommendapi/`

## External Integrations
- Algolia (primary search — `ALGOLIA_APP_ID`, `ALGOLIA_INDEX`)
- Elasticsearch / AWS OpenSearch (fallback search)
- Braze marketing API (`BRAZE_URL`, `BRAZE_API_KEY`)
- GrowthBook feature flags (`FEATUREFLAGDSN`)

## Important Files
| File | Purpose |
|------|---------|
| `cmd/server/main.go` | HTTP server entry point |
| `cmd/job/main.go` | Kafka consumer entry point |
| `cmd/migrate/main.go` | DB migration runner |
| `event/start.go` | Kafka consumer startup |
| `event/config.go` | Topic configuration |
| `config/config.yaml` | Full service configuration |
| `.env.example` | Environment variable reference |
| `api/sku-openapi.yaml` | Primary API spec (most complex) |

## Feature Flags
- GrowthBook: `FEATUREFLAGDSN=https://growthbook-api.freshket.co/...`
- Middleware integration in `http/middleware/feature_flag.go`
- Cache TTL: 5 minutes

## Main Flows
1. **Product Lookup**: Order service calls `/resources/skus` to fetch pricing for cart items
2. **Search**: Frontend calls `/resources/skus` with search query → Algolia (primary) or ES (fallback)
3. **Promotion Sync**: Consumes promotion events from Kafka to keep product promotion data current
4. **Admin Management**: Staff use `/admin/skus` for catalog management via backoffice

## Risks
- **Dual search systems**: Algolia + Elasticsearch creates operational complexity and potential inconsistency
- **Large API surface**: 40+ SKU endpoints — high maintenance burden
- **Test coverage**: README badge shows 21.5% — low for a critical service
- **Legacy MSSQL dependency**: Legacy SKU data read from MSSQL

## Suggested Improvements
- Increase test coverage (currently 21.5%)
- Document Algolia vs Elasticsearch failover logic
- Add AsyncAPI spec for promotion consumption
