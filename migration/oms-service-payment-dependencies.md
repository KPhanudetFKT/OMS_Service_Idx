# oms-service-payment — Dependency Inventory

**Stack:** Go 1.23 + Echo · **Entry points:** server, kafka-consumer, scheduler
**Config sources:** `.env`, `config/config.yaml`, `config/config.go`, `mysql_config.go`, `mssql_config.go`, `kafka/config.go`
**Datastores:** MySQL (primary, `oms_payment_*`), MSSQL (legacy) · **No** Redis / S3 / Mongo (stubs only).

> 🔐 `.env`/`config.yaml` contain live DB passwords, Kafka SASL secrets, payment-gateway keys and **TTB RSA private keys**. Treat as high-sensitivity secrets — rotate, move to SOPS/secret manager, never share.

## CRITICAL — synchronous, request-path

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| **MySQL** | mysql | `MYSQL_HOST/PORT/...` | primary store for every charge/payment op |
| Omise | payment-gateway | `THIRDPARTY_APPOMISE_BASEURL` (+keys) | card charges — blocks request thread |
| KBank | payment-gateway | `THIRDPARTY_APPKBANKCONFIG_BASEURL` (+merchant params) | PayPlus |
| KTB | payment-gateway | `THIRDPARTY_APPKTBCONFIG_*` | (creds only; no base URL in config) |
| TTB / 2C2P PACO | payment-gateway | `THIRDPARTY_TTB_BASEURL` (+API/RSA keys) | redirect/charge |
| order (public) | http-service | `THIRDPARTY_ORDERAPI_ORDERDSN` | void/cancel callbacks into order |
| order (internal) | http-service | `THIRDPARTY_ORDERAPI_INTERNALORDERDSN` | internal order ops |
| crm-customer | http-service | `THIRDPARTY_CRMCUSTOMERAPI_CRMCUSTOMERDSN` | group-billing customer ids |
| customer (CIMS) | http-service | `THIRDPARTY_CUSTOMERAPI_CUSTOMERDSN` | customer info (often blank) |
| billing-finance | http-service | `THIRDPARTY_BILLINGCONFIG_FINANCEDSN` (+`_KEY`) | invoice/billing reconcile |
| billing | http-service | `THIRDPARTY_BILLINGDSN` | billing service |
| legacy-payment-api | external-api | `THIRDPARTY_LEGACYPAYMENTAPI_HOST` (+`_KEY`) | legacy .NET `/baseApi/Payments` (receipts) |
| julian-hybrid | http-service | `APP_JULIANBASEURL` / `APP_JULIANREDIRECTURL` | payment redirect web |
| growthbook | external-api | `THIREDPARTY_FEATUREFLAGDSN` | flag gating (note key typo "THIRED") |
| MSSQL | mssql | `MSSQL_HOST/PORT/...` | legacy invoice/receipt reads/writes |

Active gateways are gated by `THIRDPARTY_ACTIVEPAYMENTPROVIDERS="omise,kbank,ktb,ttb,offline"`.

## BACKGROUND — async / non-request-path

| Dependency | Kind | Env var | Notes |
|---|---|---|---|
| Kafka (Confluent) | kafka | `KAFKA_BROKERS` (+topics) | `cmd/kafka-consumer` + scheduler (billing/payment/coin events) |
| notification | http-service | `THIRDPARTY_NOTIFICATIONAPI_NOTIFICATIONDSN` | fire-and-forget (often blank / unused) |
| intranet | http-service | `APP_INTRANETDOMAIN` (+`_SECRETKEY`) | legacy PDF proxy |
| Slack DLQ | external-api | `KAFKA_SLACKDLQ_webhookURL` | consumer failure alerts |

**Notes:** `2C2P` (`THIRDPARTY_APP2C2P_BASEURL`) and Mandrill email are referenced but largely unused on the HTTP path (2C2P often blank; email lives in legacy oms-api). `.env` overrides `config.yaml` via Viper `AutomaticEnv()` — they carry different values for the same keys; trust the deployed `.env`. **No Redis/S3** config (empty package stubs).
