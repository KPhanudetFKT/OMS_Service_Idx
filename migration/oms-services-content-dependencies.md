# oms-services-content — Dependency Inventory

**Stack:** Go + Echo · **Entry points:** server, job (Kafka consumer)
**Config sources:** `.env`, `config/config.yaml`, `config/config.go`, `database/*.go`
**Datastore:** **MongoDB Atlas** (primary, only store) · **No** MySQL / Redis / S3 / DynamoDB in effect.

> 🔐 `.env` carries the Mongo password and Kafka API key/secret in plaintext — keep out of VCS, rotate, move to a secret manager.

## CRITICAL — synchronous, request-path

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| **MongoDB** | mongo | `MONGO_HOSTNAME` / `MONGO_USERNAME` / `MONGO_PASSWORD` / `MONGO_DATABASE` | every read/write; `mongodb+srv://…`, db `oms-content` |
| product | http-service | `APP_PRODUCTDSN` (+`APP_PRODUCTCHUNK`) | SKU/brand enrichment on posts/pages (chunk 40) |
| recommendation | http-service | `APP_RECOMMENDDSN` | recommended-SKU posts |
| hrms | http-service | `APP_HRMSDSN` | staff-auth middleware on every `/admin/*` request |
| growthbook | external-api | `APP_FEATUREFLAGDSN` | feature-flag middleware |

## BACKGROUND — async / non-request-path

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| Kafka (Confluent) | kafka | `KAFKA_BROKERS` (+SASL) | consumer for promotion.{activated,deactivated,fulled,created,updated} → mirrors into Mongo |

**Dead config:** `DYNAMO_*` env vars are leftovers from a DynamoDB→Mongo migration — **not bound** to any config struct, no AWS SDK imported. Ignore for migration. No S3 (image URLs are plain strings hosted upstream).

**Migration note:** MongoDB Atlas is a SaaS host outside any Freshket cloud — its latency from the new cloud depends on the new region's distance to the Atlas cluster (`*.d0i3p.mongodb.net`). It uses SRV records, so a direct TCP probe on the bootstrap name may show `0/N` — point at a resolved shard host to measure.
