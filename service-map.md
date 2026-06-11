# Service Map — Freshket Platform

Quick-reference index. For full details see `services/<service-name>.md`.

## Master Table

| Service | Domain | Stack | Port | Databases | Kafka (Pub/Sub) | Key Dependencies |
|---------|--------|-------|------|-----------|-----------------|-----------------|
| **oms-services-order** | Order | Go 1.23, Echo | 1323 | MySQL, MSSQL | Pub: order.*, co.*, po.* | product, promotion, customer, recommendation, orderadapter, lms, oms-api, hrms |
| **oms-services-product** | Product/Catalog | Go 1.23, Echo | 1323 | MySQL, MSSQL, ES, Redis, Algolia | Sub: promotion.* | promotion, recommendation, thai-tokenizer |
| **oms-services-recommendation** | Recommendation | Go 1.22, Echo | 1323 | S3 | — | — |
| **oms-service-payment** | Payment | Go 1.21, Echo | 1323 | MySQL, MSSQL | Sub: billing.*, payment.* | payment gateways (Omise, KBank, KTB, TTB), hrms |
| **cms-services-customer** | Customer | Go 1.22, Fiber+FX | 1323 | MySQL, MSSQL | Sub: crm.user.registered, crm.customer; Pub: cms.customer | order, crm-api, crm-customer-services, MOEngage, Line |
| **crm-customer-services** | CRM/Lead | Go 1.23, Echo+Lambda | 5555 | MySQL, MSSQL | Pub: crm.customer | Salesforce, Braze, Freshchat, crm-api |
| **oms-services-content** | Content | Go 1.22, Echo | 1323 | MongoDB | Sub: promotion.* | product, recommendation |
| **hrms-services-v2** | HRMS | Go | — | — | — | — |
| **oms-services-nestjs** | Promotion, Notification, Auth, OTP, PDPA, OrderAdapter | NestJS 8, Lambda | — | MySQL | Sub: order.*, inv.*; Pub: promotion.* | order, product, notification channels |
| **crm-api** | CRM Backend | NestJS 7 | — | MSSQL, Firebase | Pub: crm.user.registered, crm.customer | Salesforce, Firebase, LINE, Elasticsearch |
| **portal-web** | All frontend domains | React 18, Next.js 14, Nx | — | — | — | All backend services via REST |
| **oms-api** | Legacy OMS | .NET C# | — | Legacy SQL | — | Payment gateways, Firebase |
| **scm-intranet-web** | SCM Intranet | PHP | — | — | — | — |
| **search-analytic** | Analytics tooling | Python | — | — | — | — |
| **fkt-platform-charts** | Infrastructure | Helm + ArgoCD | — | — | — | All services |
| **oms-services-billing** | Billing documents | Go 1.21, Echo | 1323 | MySQL | Sub: oms.co.created, oms.co.updated; Pub: billing.invoice, billing.invoice.updated, billing.credit-note, billing.cash-voucher | oms-services-order, mc-document, AWS S3 |
| **shared-notification-service** | Notifications (in-app, email, WebSocket) | Go 1.26, Echo | 8080 | PostgreSQL, Redis | Sub: notification.trigger; Pub: billing.email.* | SMTP provider, AWS S3 (email templates) |
| **lms-fast-bff-service** | LMS BFF | Go 1.26, Echo | 8081 | Redis | — | delivery service, Firebase, AWS S3 |
| **cms-services-kyc-workflow** | Customer KYC & credit workflow | Go 1.21, Echo, Lambda | — | MySQL, MSSQL | — | cms-services-customer, crm-customer-services, shared-notification-service, oms-services-order, hrms |
| **oms-promotion-workers** | Promotion-product sync workers | Go 1.23, Echo | — | MySQL | Sub: oms.order.created, oms.order.updated, oms.co.created | oms-services-product, promotion system |
| **oms-julian** | OMS marketplace frontend | Next.js 12, React 17 | — | — | — | All backend services via REST |
| **oms-services (mono)** | Multi-purpose OMS services | Go 1.22, Echo | 1323 | MySQL, MSSQL, Redis, ES | Sub: oms.order-delivered-updated, oms.mission_program, oms.gps-order-tracker | oms-api (product-sync), recommendation, AWS SQS |
| **oms-services-promotion** | Promotion management (Go/Lambda) | Go 1.22, Echo, Lambda | — | MySQL | — | — |

## Domain Ownership

| Business Capability | Owning Service |
|--------------------|----------------|
| Shopping cart creation | oms-services-order |
| Order placement | oms-services-order |
| Order calculation (price, discount) | oms-services-order |
| Bulk orders | oms-services-order |
| Delivery time slots | oms-services-order |
| SKU / product catalog | oms-services-product |
| Product search | oms-services-product (Algolia primary, ES fallback) |
| Product recommendations | oms-services-recommendation |
| Promotion creation & lifecycle | oms-services-nestjs/promotion |
| Promotion application to orders | oms-services-order (calculation) |
| Payment processing | oms-service-payment |
| Invoice / credit note | oms-service-payment |
| Customer profile & KYC | cms-services-customer |
| Customer credit limit | cms-services-customer |
| Lead & sales management | crm-customer-services + crm-api |
| Salesforce sync | crm-api, crm-customer-services |
| Content (banners, posts, pages) | oms-services-content |
| Push/LINE/email notifications | oms-services-nestjs/notification (legacy), shared-notification-service (new) |
| In-app / real-time / email notifications | shared-notification-service |
| Billing document generation (invoice, credit note) | oms-services-billing |
| KYC verification & credit term workflow | cms-services-kyc-workflow |
| Product-promotion sync | oms-promotion-workers |
| Delivery time slot management (BFF) | oms-services (mono)/fulfillment-service |
| LMS API aggregation | lms-fast-bff-service |
| JWT auth (customer) | oms-services-nestjs/authorizer |
| JWT auth (staff) | oms-services-nestjs/authorizer-staff |
| OTP | oms-services-nestjs/otp |
| PDPA / consent | oms-services-nestjs/pdpa |
| HR & staff | hrms-services-v2 |
| Warehouse operations | wms (separate repo — referenced in fkt-platform-charts) |
| Logistics / delivery tracking | lms (separate repo — referenced in fkt-platform-charts) |
| Merchant / marketplace | mc (portal-web + separate backend) |
| Finance / billing | oms-services-billing (confirmed — now in monorepo workspace) |

## OpenAPI Coverage

| Service | Spec Files |
|---------|-----------|
| oms-services-order | order, shoppingcart, bulkorder, calculation, delivery, health |
| oms-services-product | sku, category, product, brand, label, presearch, setting, health |
| oms-services-content | post, page, banner, brand, health + extras |
| cms-services-customer | customer (info, kyc, credit-limit/check) |
| oms-services-recommendation | recommendation, health |
| oms-service-payment | None (uses internal contracts) |
| crm-customer-services | None (Lambda-native) |
| oms-services-nestjs | None (Lambda event-driven) |
| cms-services-kyc-workflow | customer.open-api.yaml (28 endpoints) |
| oms-promotion-workers | product.openapi.yaml, campaign-openapi.yaml |
| oms-services (mono) | product.openapi.yaml, delivery-openapi.yaml, log.openapi.yaml |
| shared-notification-service | Swagger (generated via swag) |
| lms-fast-bff-service | Swagger (generated via swag) |

## Service URL Environment Variables

| Env Var | Points To | Set In |
|---------|-----------|--------|
| `APP_PRODUCTDSN` | oms-services-product | oms-services-order |
| `APP_PROMOTIONDSN` | oms-services-nestjs/promotion | oms-services-order |
| `APP_RECOMMENDDSN` | oms-services-recommendation | oms-services-order, product, content |
| `APP_CUSTOMERDSN` | cms-services-customer | oms-services-order |
| `APP_FULFILLMENTDSN` | LMS fulfillment (external) | oms-services-order |
| `APP_ORDERADAPTERDSN` | oms-services-nestjs/orderadapter | oms-services-order |
| `APP_LEGACYWEBMVCDSN` | oms-api | oms-services-order |
| `APP_HRMSURL` | hrms-services-v2 | oms-services-order, product, content, payment |
| `APP_BILLINGDSN` | oms-services-billing | oms-services-order |
| `INTERNALCRM_DNS` | crm-api | cms-services-customer |
| `MOENGAGE_HOST` | MOEngage (external) | cms-services-customer |
| `APP_NOTIFICATIONDSN` | shared-notification-service | cms-services-kyc-workflow |
| `APP_CRM_CUSTOMERDSN` | crm-customer-services | cms-services-kyc-workflow |
| `APP_MCDOCUMENT_DSN` | mc-document service | oms-services-billing |
| `THIRDPARTY_DELIVERY_BASE_URI` | Internal delivery service | lms-fast-bff-service |
