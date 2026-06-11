# Event Catalog — Freshket Platform

Kafka broker: `pkc-l9wvm.ap-southeast-1.aws.confluent.cloud:9092` (Confluent Cloud)

## OMS Order Events

| Topic | Producer | Consumers | Payload Location | Confidence |
|-------|----------|-----------|-----------------|-----------|
| `oms.order.created` | oms-services-order | oms-services-nestjs/promotion | `oms-services-order/event/const/event_const.go` | Confirmed |
| `oms.order.updated` | oms-services-order | oms-services-nestjs/promotion | `oms-services-order/event/const/event_const.go` | Confirmed |
| `oms.co.created` | oms-services-order | oms-services-nestjs/orderadapter | `oms-services-order/event/const/event_const.go` | Confirmed |
| `oms.co.updated` | oms-services-order | oms-services-nestjs/orderadapter | `oms-services-order/event/const/event_const.go` | Confirmed |
| `oms.legacy-po.created` | oms-services-order | oms-services-nestjs/orderadapter | `oms-services-order/event/const/event_const.go` | Confirmed |
| `oms.order.updated.co-created` | oms-services-order | oms-services-nestjs/notification | `oms-services-order/.env.example` | Confirmed |
| `oms.order-delivered-updated` | oms-services-order | oms-services (mono)/gps-order-tracker | `oms-services-order/.env.example`, `oms-services/.env` | Confirmed |
| `oms.gps-order-tracker` | oms-services-order / GPS device | oms-services (mono)/gps-order-tracker | `oms-services/.env` (KAFKA_OMS_ORDER_TRACKER_TOPIC) | Confirmed |
| `oms.mission_program` | Unknown | oms-services (mono)/mission-program | `oms-services/.env` (KAFKA_OMS_MISSION_PROGRAM_TOPIC) | Unknown producer |
| `oms.order.updated.co-updated` | oms-services-order | Unknown | `oms-services-order/.env.example` (KAFKA_ORDERUPDATEDCOUPDATEDTOPIC) | Inferred |
| `oms.inv.created` | Unknown (billing?) | oms-services-nestjs/promotion | `oms-services-nestjs/serverless-internal.yml` | Inferred |

## OMS Promotion Events

| Topic | Producer | Consumers | Payload Location | Confidence |
|-------|----------|-----------|-----------------|-----------|
| `oms.promotion.created` | oms-services-nestjs/promotion | oms-services-product, oms-services-content | `oms-services-content/event/`, product `event/config.go` | Confirmed |
| `oms.promotion.updated` | oms-services-nestjs/promotion | oms-services-product, oms-services-content | `oms-services-content/event/`, product `event/config.go` | Confirmed |
| `oms.promotion.activated` | oms-services-nestjs/promotion | oms-services-content | `oms-services-content/event/` | Confirmed |
| `oms.promotion.deactivated` | oms-services-nestjs/promotion | oms-services-content | `oms-services-content/event/` | Confirmed |
| `oms.promotion.fulled` | oms-services-nestjs/promotion | oms-services-content | `oms-services-content/event/` | Confirmed |

Note: Content service topics have env suffix: `oms.promotion.activated.dev` (dev), `oms.promotion.activated.sit` (SIT), etc.

## Payment / Billing Events

| Topic | Producer | Consumers | Payload Location | Confidence |
|-------|----------|-----------|-----------------|-----------|
| `billing.invoice` | **oms-services-billing** (KAFKA_TOPIC_CUSTOMERORDER_DOCUMENTCREATED) | oms-service-payment | `oms-service-payment/config/kafka/`, `oms-services-billing/config/config.go` | **Confirmed** |
| `billing.invoice.updated` | **oms-services-billing** (KAFKA_TOPIC_CUSTOMERORDER_DOCUMENTUPDATED) | oms-service-payment | `oms-service-payment/config/kafka/` | **Confirmed** |
| `billing.credit-note` | **oms-services-billing** (KAFKA_TOPIC_CUSTOMERORDER_DOCUMENTGENERATING) | oms-service-payment | `oms-service-payment/config/kafka/` | Confirmed |
| `billing.cash-voucher` | **oms-services-billing** | oms-service-payment | `oms-service-payment/config/kafka/` | Confirmed |
| `billing.email` | **shared-notification-service** (KAFKA_TOPIC_EMAIL_SENT = `billing.email.<env>`) | billing/finance consumers | `shared-notification-service/config/config.go` | Confirmed |
| `payment.transaction` | Unknown | oms-service-payment, oms-services-nestjs/orderadapter | `oms-service-payment/config/kafka/` | Unknown |
| `payment.coin` | oms-services-order (KAFKA_PAYEMNTCOIN) | oms-service-payment | `oms-services-order/.env.example` | Confirmed |
| `payment.credit-note` | Unknown | Not consumed (tag: consume=false) | `oms-service-payment/config/kafka/` | Unknown |

**Gap resolved**: `oms-services-billing` is the producer of `billing.invoice`, `billing.invoice.updated`, `billing.credit-note`, `billing.cash-voucher` topics. It consumes `oms.co.created` and `oms.co.updated` to generate billing documents.

## CRM Events

| Topic | Producer | Consumers | Payload Location | Confidence |
|-------|----------|-----------|-----------------|-----------|
| `crm.user.registered` (env suffix: `.sit`) | crm-api | cms-services-customer | `cms-services-customer/.env.example` (KAFKA_TOPIC_CRM_USER_REGISTERED) | Confirmed |
| `crm.customer` | crm-customer-services | cms-services-customer | `cms-services-customer/.env.example` (KAFKA_TOPIC_CRM_CUSTOMER) | Confirmed |

## CMS Events

| Topic | Producer | Consumers | Payload Location | Confidence |
|-------|----------|-----------|-----------------|-----------|
| `cms.customer` | cms-services-customer | Unknown | `cms-services-customer/.env.example` (KAFKA_TOPIC_CMS_CUSTOMER) | Unknown |

**Gap**: Consumers of `cms.customer` topic are not identified in this codebase.

## Notification Events

| Topic | Producer | Consumers | Payload Location | Confidence |
|-------|----------|-----------|-----------------|-----------|
| `notification.trigger` | Any service that needs to trigger a notification | shared-notification-service | `shared-notification-service/constants/constants.go` | Confirmed |
| `notification.email.send` | shared-notification-service (internal) | shared-notification-service | `shared-notification-service/constants/constants.go` | Confirmed |
| `notification.email.sent` | shared-notification-service | Unknown | `shared-notification-service/constants/constants.go` | Confirmed |

Note: `KAFKA_TOPIC_EMAIL_SENT` in shared-notification-service maps to `billing.email.<env>` (e.g. `billing.email.sit`, `billing.email.prd`) for backwards compatibility with finance consumers. Same event, different topic name per environment.

## LMS Events

| Topic | Producer | Consumers | Payload Location | Confidence |
|-------|----------|-----------|-----------------|-----------|
| `lms.delivery-task` | LMS service (external repo) | oms-services-order, oms-services-nestjs/promotion | `oms-services-order/.env.example` | Inferred |

## Topic Naming Convention

```
{domain}.{entity}.{action}[.{env-suffix}]
```

- Domain prefixes: `oms`, `crm`, `cms`, `lms`, `billing`, `payment`
- Environment suffixes (in some services): `.sit`, `.uat`, `.prod`, `.dev`
- Not all topics use env suffixes — check `.env.example` for the actual topic name per environment

## Kafka Library by Service

| Service | Library |
|---------|---------|
| oms-services-order | Shopify/sarama |
| oms-services-product | Shopify/sarama |
| oms-services-content | Shopify/sarama |
| oms-service-payment | segmentio/kafka-go |
| cms-services-customer | segmentio/kafka-go |
| crm-customer-services | segmentio/kafka-go |
| oms-services-nestjs | kafkajs |
| crm-api | kafkajs |
| oms-services-billing | Shopify/sarama |
| oms-promotion-workers | Shopify/sarama |
| oms-services (mono) | segmentio/kafka-go |
| shared-notification-service | IBM/sarama |

## Architecture Gaps in Event Catalog

1. ~~**billing.\* producers unknown**~~ **RESOLVED** — `oms-services-billing` produces billing.invoice, billing.invoice.updated, billing.credit-note, billing.cash-voucher
2. **cms.customer consumers unknown** — downstream consumer not identified
3. **oms.inv.created producer unknown** — likely billing or legacy OMS
4. **oms.mission_program producer unknown** — consumed by oms-services (mono)
5. **payment.transaction producer unknown** — consumed by oms-service-payment and orderadapter
6. **lms.delivery-task producer** — LMS service is a separate repo, not indexed here
7. **No AsyncAPI spec** — no formal event schema documentation exists for any topic
