# Glossary — Freshket Platform

## Business Terms

| Term | Definition |
|------|-----------|
| **CO** | Customer Order — an order placed by a customer (buyer). Used in Kafka topic names: `oms.co.created` |
| **PO** | Purchase Order — an order to a supplier. Legacy term. Kafka: `oms.legacy-po.created` |
| **SKU** | Stock Keeping Unit — a specific product variant with price and inventory |
| **Rebate** | Post-purchase discount refunded to customers, often volume-based |
| **Bulk Order** | Large-quantity order, managed via bulk-order domain in oms-services-order |
| **Credit Limit** | Maximum outstanding credit a customer can have; managed by cms-services-customer |
| **KYC** | Know Your Customer — identity verification process for new customers |
| **PDPA** | Personal Data Protection Act — Thai data privacy law; consent managed by oms-services-nestjs/pdpa |
| **Promotion** | Discount rule applied to orders; lifecycle managed by oms-services-nestjs/promotion |
| **Invoice** | Billing document for completed orders; owned by oms-service-payment domain |
| **Credit Note** | Refund document issued against an invoice |
| **Cash Voucher** | Pre-paid voucher used as payment method |
| **Coin** | Freshket loyalty points used as partial payment |
| **Julian** | Internal name for the customer-facing OMS web portal (oms-web) |

## System / Service Abbreviations

| Abbreviation | Full Name | Directory |
|-------------|-----------|-----------|
| **OMS** | Order Management System | oms-services-order, oms-services-nestjs, oms-api |
| **CIMS** | Customer Information Management System | cms-services-customer |
| **CRM** | Customer Relationship Management | crm-api, crm-customer-services |
| **WMS** | Warehouse Management System | wms (external repo) |
| **LMS** | Logistics Management System | lms (external repo) |
| **SCN** | Supply Chain Network | scn (external repo) |
| **SCM** | Supply Chain Management | scm-intranet-web |
| **PIM** | Product Information Management | pim (external — fkt-platform-charts/pim/) |
| **MC** | Merchant / Marketplace | mc-web, mc-bff |
| **CS** | Customer Service | cs-web, cs-bff |
| **BFF** | Backend-for-Frontend | mc-bff, billing-bff, cs-bff in portal-web |
| **HRMS** | Human Resource Management System | hrms-services-v2 |

## Technical Abbreviations

| Term | Definition |
|------|-----------|
| **DSN** | Data Source Name — used in Freshket as a URL/address for a service or database (e.g., `APP_PRODUCTDSN`) |
| **DLQ** | Dead Letter Queue — Kafka messages that fail processing, trigger Slack alert |
| **oapi-codegen** | OpenAPI-to-Go code generator; generates `*.gen.go` from YAML specs |
| **Mockery** | Go mock generator; produces `*_mock.go` from interfaces |
| **Sarama** | Shopify's Go Kafka client library |
| **FX** | uber-go/fx — dependency injection framework used by cms-services-customer |
| **GORM** | Go ORM library used for MySQL access |
| **SOPS** | Secret encryption tool used for `th-resource/` Helm chart values (AWS KMS) |
| **GrowthBook** | Feature flag SaaS platform used across all services |
| **Algolia** | Managed search SaaS (primary product search) |
| **MOEngage** | Customer engagement / marketing automation platform |
| **Braze** | Marketing platform used by oms-services-product and crm-customer-services |
| **Freshchat** | Customer support chat platform integrated in crm-customer-services |
| **Omise** | Thai payment gateway (primary) |
| **KBank / KTB / TTB** | Thai bank payment gateway integrations in oms-service-payment |
| **SIT** | System Integration Testing environment (first non-local env) |
| **UAT** | User Acceptance Testing environment |
| **ArgoCD** | GitOps CD tool; syncs Helm charts to Kubernetes clusters |
| **Nx** | Monorepo build tool used by portal-web |
| **pnpm** | Package manager used by portal-web |
| **Confluent** | Managed Kafka cloud service (Confluent Cloud) |

## Kafka Topic Naming Convention

```
{domain}.{entity}.{action}[.{environment}]
```

Examples:
- `oms.order.created` — Order domain, order entity, created action
- `oms.co.created` — OMS domain, Customer Order entity, created action
- `crm.user.registered.sit` — CRM domain, user entity, registered action, SIT environment suffix
- `oms.promotion.activated.dev` — OMS domain, promotion entity, activated action, dev suffix

Note: Some topics include environment suffix (`.sit`, `.dev`, `.uat`); others are environment-agnostic and use config to select the correct Kafka cluster.
