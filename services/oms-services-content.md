# oms-services-content

## Responsibility
Content management service. Manages editorial content for the platform: posts, pages, banners, brand content, and promotion display. Migrated from DynamoDB to MongoDB.

## Owns
- Posts (articles, editorial content)
- Pages (static pages)
- Banners (marketing banners)
- Brand content / premium brands
- Promotion display content (mirrors promotion data from events)
- Term and conditions content

## Does NOT Own
- Promotion rules (→ oms-services-nestjs/promotion)
- Product catalog (→ oms-services-product)
- Recommendations (→ oms-services-recommendation)
- Customer-facing CMS for orders (→ oms-api, legacy)

## APIs
Source: `api/*.yaml` (6 specs)

| Spec | Base Path | Key Endpoints |
|------|-----------|---------------|
| post-openapi.yaml | /admin/posts | Post CRUD |
| page-openapi.yaml | /admin/pages | Page CRUD |
| banner-openapi.yaml | /admin/banners | Banner management |
| brand-openapi.yaml | /admin/brands | Premium brand content |
| health-openapi.yaml | /health | Health check |
| (additional) | /images, /term-and-conditions, /products | Misc content endpoints |

Auth: Bearer JWT (customer), Staff JWT (admin routes)

## Events Published
None detected.

## Events Consumed
| Topic | Trigger | Confidence |
|-------|---------|-----------|
| `oms.promotion.created` (env: `KAFKA_PROMOTION_CREATED_TOPIC`) | New promotion → create content | Confirmed |
| `oms.promotion.updated` (env: `KAFKA_PROMOTION_UPDATED_TOPIC`) | Promotion update → sync content | Confirmed |
| `oms.promotion.activated` (env: `KAFKA_PROMOTION_ACTIVATED_TOPIC`) | Promotion active → show banner/page | Confirmed |
| `oms.promotion.deactivated` (env: `KAFKA_PROMOTION_DEACTIVATED_TOPIC`) | Promotion inactive → hide content | Confirmed |
| `oms.promotion.fulled` (env: `KAFKA_PROMOTION_FULLED_TOPIC`) | Promotion quota full → update content | Confirmed |

Consumer entry: `cmd/job/main.go`
Kafka library: Shopify/sarama

Note: Topic names include environment suffix in dev: e.g., `oms.promotion.activated.dev`

## Database Ownership
- **MongoDB** (`freshket-lynx-dev0.d0i3p.mongodb.net/oms-content`) — primary (migrated from DynamoDB)
  - Collections: posts, pages, banners, premium_brands, promotions
  - Schema-less — no migration files

## Dependencies

### Internal Services (HTTP)
| Env Var | Target Service | Usage |
|---------|---------------|-------|
| `APP_PRODUCTDSN` | oms-services-product | Product data for content |
| `APP_RECOMMENDDSN` | oms-services-recommendation | Recommendation data |
| `APP_HRMSDSN` | hrms-services-v2 | Staff info |

HTTP clients in: `thirdparty/productapi/`, `thirdparty/recommendapi/`

## External Integrations
- GrowthBook feature flags (`APP_FEATUREFLAGDSN`)

## Important Files
| File | Purpose |
|------|---------|
| `cmd/server/main.go` | HTTP server entry point |
| `cmd/job/main.go` | Kafka consumer entry point |
| `cmd/migrate/main.go` | MongoDB initialization |
| `event/` | Kafka consumer handlers |
| `pkg/post/` | Post domain logic |
| `pkg/page/` | Page domain logic |
| `pkg/banner/` | Banner domain logic |
| `pkg/promotion/` | Promotion content sync |
| `database/` | MongoDB connection |
| `http/middleware/feature_flag.go` | GrowthBook middleware |

## Feature Flags
- GrowthBook: `APP_FEATUREFLAGDSN`
- Feature flag middleware in `http/middleware/feature_flag.go`

## Main Flows
1. **Promotion Content Sync**: Consumes 5 promotion lifecycle events → creates/updates/hides content in MongoDB
2. **Banner Management**: Staff manage banners via `/admin/banners` → displayed to customers
3. **Post Management**: Editorial team creates posts via `/admin/posts` → customer-facing articles
4. **Product Content**: Fetches product data from oms-services-product to enrich content

## Architecture Notes
- Previously used DynamoDB; migrated to MongoDB (see `last-dynamodb` git branch)
- MongoDB is schema-less — all content stored as documents

## Risks
- **Promotion content lag**: Content updates depend on Kafka event delivery — possible delay between promotion activation and content display
- **No schema enforcement**: MongoDB schema-less design can lead to data inconsistency

## Suggested Improvements
- Add JSON Schema validation for MongoDB documents
- Add event replay mechanism for content sync recovery
- Document topic suffix strategy (`.dev`, `.sit`) clearly
