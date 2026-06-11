# oms-services-promotion

## Responsibility
Go-based promotion management service (separate from oms-services-nestjs/promotion). Deployed as AWS Lambda. Manages promotion rules, product promotions, and discount configurations. Uses uber-go/fx for dependency injection. May be a newer Go rewrite of the NestJS promotion Lambda.

## Owns
- Promotion rule storage and management
- Product promotion configurations
- Discount rule definitions

## Does NOT Own
- Promotion application to orders (→ oms-services-order)
- Product catalog (→ oms-services-product)
- Notification on promotion events (→ oms-services-nestjs/promotion still publishes events)

## APIs
No OpenAPI spec found in root. Uses Echo v4 HTTP handlers.
Base path: `oms/promotion/v3` (`APP_BASEURL`)
Deployed as Lambda via AWS Lambda Go proxy.

## Events
No Kafka events identified in available source files.

## Database Ownership
- **MySQL** (`oms_product_sit` database — note: shares product DB namespace)
  - `SQL_HOST`: freshket-dev-oms.cth9muhntj72.ap-southeast-1.rds.amazonaws.com
- NoSQL configuration present but appears to use same MySQL host

## Stack
- Go 1.22.3, Echo v4, GORM, uber-go/fx (dependency injection)
- AWS Lambda Go proxy, JWT auth

## Entry Points (`cmd/`)
| Entry Point | Purpose |
|-------------|---------|
| `cmd/server/` (inferred) | HTTP server / Lambda handler |

## Dependencies
- `APP_BASEURL=oms/promotion/v3` — registered path prefix
- No external service DSNs found in `.env.example`

## Notes
- Uses `oms_product_sit` as database — may share schema with oms-services-product or have a separate promotion-specific schema in the same DB instance
- uber-go/fx DI pattern (shared with cms-services-customer)
- Relationship to `oms-services-nestjs/promotion` unclear — may be a migration target or parallel implementation

## Risks
- Relationship to NestJS promotion Lambda unclear — two promotion services may coexist
- No `.env.example` Kafka config — if events are needed, must check runtime config
