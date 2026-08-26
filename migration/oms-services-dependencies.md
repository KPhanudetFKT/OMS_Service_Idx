# oms-services (mono) — Dependency Inventory

**Stack:** Go 1.23 + uber-go/fx · config via `go-envconfig` (`config/config.go`) + some raw `os.Getenv`.
**Not a single API** — a monorepo of workers/services on Kubernetes (Lambda path deprecated). Entry points in `cmd/`:
- `server-external` / `server-internal` — HTTP APIs
- `kafka-consumer` — Kafka consumer
- `sqs-consumer` — product-sync SQS queue consumer
- `cronjob` — scheduled jobs (e.g. refresh-recommendation weekly)

Sub-services: product-sync-worker, fulfillment-service, log service, refresh-recommendation, mission-program.
**Datastores:** MySQL (product/promotion/order DBs, same host), MSSQL (legacy), Redis (ElastiCache: GPS tracker, postal, OTP). Search via OpenSearch + Algolia.

> 🔐 `.env` carries DB/Kafka/Algolia secrets **and AWS access keys** (`AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`). Prefer IAM roles over static keys post-migration; rotate any committed keys.

## CRITICAL — request-path (server-external / server-internal)

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| **MySQL** | mysql | `MYSQL_HOST/PORT` (+`_DATABASE`, `_DATABASE_PROMOTION`, `_DATABASE_ORDER`) | primary; 3 DBs on one host |
| MSSQL | mssql | `MSSQL_HOST/PORT/...` | legacy DB read by handlers |
| OpenSearch | search | `ELASTICSEARCH_URL` (+user/pass, `SEARCH_INDEX_NAME`) | product search |
| Algolia | search | `ALGOLIA_APP_ID` / `ALGOLIA_API_KEY` / `ALGOLIA_INDEX_NAME` | product search |
| Redis | redis | `REDIS_HOST/PORT` (+ DB indexes) | GPS tracker / postal lookups |
| hrms | http-service | `APP_HRMSDSN` | staff-auth middleware (blocks requests) |
| auth | http-service | `AUTH_ENDPOINT` (+`AUTH_JWT_KEY`, `AUTH_X_API_KEY`) | identity check middleware |
| growthbook | external-api | `APP_GROWTHBOOKURL` (+`APP_GROWTHBOOKKEY`) | flag gating |
| lms | http-service | `LMS_HOST` (+`LMS_API_KEY`) | delivery-core (Locus) data |

## BACKGROUND — workers / consumers / cron

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| Kafka (Confluent) | kafka | `KAFKA_BROKERS` (+SASL, topics) | `kafka-consumer` only |
| product-sync SQS | other (sqs) | `PRODUCT_SYNC_QUEUE_NAME` (+`AWS_REGION`, keys) | `sqs-consumer` + product-sync worker |
| thai-tokenizer | external-api | `THAI_TOKENIZER_URL` | Algolia index sync (worker) |
| promotion-workers | http-service | `PROMOTION_SYNC_URL` (+`PROMOTION_WORKER_API_KEY`) | sync worker |
| recommendation | http-service | `RECOMMENDATION_URL` | cron `/refresh` (weekly) |
| Braze | external-api | `BRAZE_HOST` (+`BRAZE_API_KEY`, campaign ids) | async campaigns |
| Slack webhooks | external-api | `SLACK_CHANNEL_URL`, `SLACK_DLQ_WEBHOOK_URL`, `SLACK_PRICE_SYNC_CHANNEL_WEBHOOK_URL`, `NOTIFICATION_DEFAULT_WEBHOOK_URL` | alerting (non-blocking) |

**Notes:** AWS SQS uses the default SDK session (region/creds from `AWS_*` / IAM); only the queue *name* is configured (`PRODUCT_SYNC_QUEUE_NAME`). `THAI_TOKENIZER_URL` / `LMS_HOST` use `execute-api` API-Gateway hosts in some envs — `endpoints.tsv` uses the canonical ingress as a proxy; confirm per environment. No Mongo, no real S3 bucket. `config.go` is the single source of truth for K8s (serverless.yml deprecated).
