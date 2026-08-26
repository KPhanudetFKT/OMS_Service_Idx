# oms-services-product — Dependency Inventory

**Stack:** Go 1.23 + Echo · **Entry points:** server, job (Kafka consumer), migrate
**Config sources:** `.env`, `.env.example`, `config/config.yaml`, `config/config.go`, `database/mysql_conf.go`, `database/database_legacy.go`
**Datastores:** MySQL (primary), MSSQL (legacy), Redis (cache) · search via Algolia (primary) / OpenSearch (gated by `SEARCHENGINE`).

> 🔐 The repo `.env` contains live SIT credentials (DB/Algolia/Kafka/OpenSearch). Keep it out of version control and rotate any committed keys.

## CRITICAL — synchronous, request-path

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| **MySQL** | mysql | `MYSQL_HOST/PORT` | primary store, db `oms_product_sit`; nearly every request |
| Algolia | search | `ALGOLIA_APPLICATIONID` / `ALGOLIA_APIKEY` | primary search engine (`SEARCHENGINE=ALGOLIA`), index `sit_skus` |
| OpenSearch | search | `ELASTICSEARCH_HOSTS` | alternate search backend (VPC, gated) |
| thai-tokenizer | external-api | `APP_THAITOKENIZERURL` | synchronous during Thai-keyword search |
| promotion | http-service | `APP_PROMOTIONDNS` | SKU promotion enrichment (note key typo "DNS") |
| recommendation | http-service | `APP_RECOMMENDDSN` | similar-SKU / pre-search |
| product-sync | http-service | `APP_PRODUCTSYNCDSN` | fulfillment product-sync on scope change |
| hrms | http-service | `APP_HRMSDSN` | staff auth on resource/admin endpoints |
| legacy-oms-api | http-service | `APP_LEGACYWEBMVCDSN` | legacy fallbacks |
| growthbook | external-api | `FEATUREFLAGDSN` | flag gating (SDK caches) |
| Redis | redis | `CACHE_ADDRESS` | read-through cache (degrades, not hard-required) |

## BACKGROUND — async / non-request-path

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| Kafka (Confluent) | kafka | `KAFKA_BROKERS` (+SASL) | `cmd/job` consumes promotion.created/updated |
| MSSQL | mssql | `MSSQL_HOST/PORT` | legacy backward-compat reads (e.g. favorite-items) |
| Braze | external-api | `BRAZE_URL` / `BRAZE_API_KEY` | marketing sync on price update (best-effort) |

**Notes:** `.env` uses VPC-endpoint (`*-vpce-*.execute-api...`) hosts for internal services in some envs; `endpoints.tsv` uses the canonical `sit-internal-api` ingress as a proxy — confirm per environment. Duplicate Braze keys exist (`BRAZE_API_KEY` vs `BRAZE_APIKEY`).
