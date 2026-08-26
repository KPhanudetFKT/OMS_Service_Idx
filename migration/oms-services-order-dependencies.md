# oms-services-order — Dependency Inventory

**Stack:** Go 1.23 + Echo · **Entry points:** server, job (Kafka consumer), scheduler, migrate
**Config sources:** `.env.example`, `config/config.yaml`, `config/config.go`, `database.go`, `mq_config.go`
**Datastores:** MySQL (primary), MSSQL (legacy) · **No** Mongo / Redis / S3 in config.

> ⚠️ Order config ships **placeholders** (`product-service-host`, etc.) — the host targets in `endpoints.tsv` are inferred from sibling services. Confirm real per-environment hosts before measuring.

## CRITICAL — synchronous, request-path

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| product | http-service | `APP_PRODUCTDSN` | SKU/pricing/search on order, cart, calculation |
| orderadapter | http-service | `APP_ORDERADAPTERDSN` (+`_APIKEY`) | buyer/seller/customer-item lookups |
| promotion | http-service | `APP_PROMOTIONDSN` | promo validation on cart/order |
| fulfillment | http-service | `APP_FULFILLMENTDSN` | delivery dates / time-slots |
| order-self | http-service | `APP_ORDERDSN` | ⚠ bulk-orders GENERAL self-call (see refactor plan) |
| recommendation | http-service | `APP_RECOMMENDDSN` | cart recommendations |
| customer | http-service | `APP_CUSTOMERDSN` | credit-limit check |
| fk-web-legacy | http-service | `APP_LEGACYWEBMVCDSN` | legacy buyer-authorize (host = `fk-web-host`, **not** oms-api) |
| billing | http-service | `APP_BILLINGDSN` | invoice reference (often blank in config) |
| hrms | http-service | `APP_HRMSURL` | staff info lookup |
| lms | http-service | `LMS_HOST` (+`LMS_X_API_KEY`) | delivery-task / tracking |
| google-maps | external-api | `APP_GOOGLEMAPSBASEURL` (+`APP_GOOGLEMAPSAPIKEY`) | geocode/distance proxy |
| growthbook | external-api | `APP_GROWTHBOOKURL` (+`APP_GROWTHBOOKKEY`) | feature flags (SDK caches) |
| **MySQL** | mysql | `MYSQL_HOST/PORT/...` | primary order DB — every request |
| **MSSQL** | mssql | `MSSQL_HOST/PORT/...` | legacy reads/writes (restaurants, invoices, PVP) |

## BACKGROUND — async / non-request-path

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| Kafka (Confluent) | kafka | `KAFKA_BROKERS` (+SASL, topic vars) | producers + `cmd/job` consumer |
| Line Notify | external-api | `APP_LINEAPITOKEN` | fire-and-forget order notifications |
| Slack DLQ | external-api | `KAFKA_SLACKDLQWEBHOOK` | DLQ failure alerts |

**Auth secrets (not endpoints):** `APP_HMACSECRET`, `APP_ORDERADAPTER_APIKEY`, `LMS_X_API_KEY`, `APP_XAPIKEY`, `APP_OMSTOKEN`.

**Config note:** `.env.example` is incomplete vs `config.yaml` (missing MSSQL, HRMS, billing, LMS, GrowthBook, several Kafka topics). `config.yaml` is the fuller reference. Payment-coin key is misspelled `KAFKA_PAYEMNTCOIN` in `.env.example`.
