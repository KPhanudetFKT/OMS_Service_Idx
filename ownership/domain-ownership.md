# Domain Ownership — Freshket Platform

## Ownership Matrix

| Business Capability | Primary Owner | Secondary / Reads From | NOT Owned By |
|--------------------|--------------|----------------------|-------------|
| **Shopping cart** | oms-services-order | — | portal-web (UI only) |
| **Order placement** | oms-services-order | product, promotion, customer | oms-api (legacy only) |
| **Order calculation** | oms-services-order | product (pricing), nestjs/promotion (discounts) | oms-services-product |
| **Order status lifecycle** | oms-services-order | — | — |
| **Bulk orders** | oms-services-order | — | — |
| **Delivery time slots** | oms-services-order | LMS (fulfillment) | lms (external) |
| **Delivery fulfillment** | LMS service (external repo) | — | oms-services-order |
| **SKU / product catalog** | oms-services-product | — | oms-services-order (reads only) |
| **Product pricing** | oms-services-product | — | oms-services-order |
| **Area / private pricing** | oms-services-product | — | — |
| **Product search** | oms-services-product (Algolia + ES) | — | — |
| **Product recommendations** | oms-services-recommendation | oms-services-product (catalog data) | oms-services-product |
| **Promotion rules** | oms-services-nestjs/promotion | — | oms-services-order |
| **Promotion application** | oms-services-order (applies) + nestjs/promotion (defines) | — | — |
| **Promotion content display** | oms-services-content | nestjs/promotion (events) | oms-services-nestjs |
| **Payment charges** | oms-service-payment | — | oms-services-order |
| **Invoices** | oms-service-payment | billing service (events) | — |
| **Credit notes / refunds** | oms-service-payment | billing service (events) | — |
| **Cash vouchers** | oms-service-payment | — | — |
| **Loyalty coins** | oms-service-payment | — | — |
| **Customer profile** | cms-services-customer | crm-api, crm-customer-services | oms-services-order |
| **KYC verification (data)** | cms-services-customer | — | — |
| **KYC verification workflow (approval)** | cms-services-kyc-workflow | cms-services-customer, oms-services-order, hrms | cms-services-customer |
| **Credit term requests** | cms-services-kyc-workflow | — | — |
| **Credit limit requests** | cms-services-kyc-workflow | — | — |
| **Customer credit limit (data)** | cms-services-customer | — | — |
| **Lead management** | crm-customer-services + crm-api | — | cms-services-customer |
| **Salesforce sync** | crm-api + crm-customer-services | — | cms-services-customer |
| **CRM backoffice** | crm-api | — | crm-customer-services |
| **Content (banners, posts)** | oms-services-content | — | — |
| **Push / email notifications (legacy)** | oms-services-nestjs/notification | — | — |
| **In-app / real-time notifications** | shared-notification-service | — | oms-services-nestjs/notification |
| **Email notifications (new)** | shared-notification-service | — | oms-services-nestjs/notification |
| **LINE notifications** | cms-services-customer, crm-api | — | — |
| **Billing document generation** | oms-services-billing | oms-services-order (consumes CO events) | oms-service-payment |
| **Product-promotion price sync** | oms-promotion-workers | oms-services-product, promotion system | — |
| **GPS order tracking** | oms-services (mono)/gps-order-tracker | oms-services-order (emits events) | — |
| **Mission programs** | oms-services (mono)/mission-program | — | — |
| **Delivery BFF (LMS)** | lms-fast-bff-service | delivery service (internal) | — |
| **JWT issuance (customer)** | oms-services-nestjs/authorizer | — | — |
| **JWT issuance (staff)** | oms-services-nestjs/authorizer-staff | — | — |
| **OTP** | oms-services-nestjs/otp | — | — |
| **PDPA / consent** | oms-services-nestjs/pdpa | — | — |
| **Staff / employee data** | hrms-services-v2 | — | — |
| **Warehouse operations** | WMS service (external repo) | — | — |
| **Logistics / routing** | LMS service (external repo) | — | — |
| **Merchant portal** | mc-web + mc-bff (portal-web) | — | — |
| **Billing invoices (display)** | billing-web (portal-web) | oms-service-payment | — |
| **SCM intranet** | scm-intranet-web | — | — |

---

## Shared / Contested Boundaries (Risks)

| Capability | Issue | Services Involved |
|-----------|-------|-----------------|
| **LINE notifications** | Both cms-services-customer and crm-api send LINE messages | cms-services-customer, crm-api |
| **CRM customer data** | crm-customer-services and crm-api both publish customer events with overlapping data | crm-api, crm-customer-services, cms-services-customer |
| **Promotion application** | Split: nestjs/promotion defines rules, oms-services-order applies them — tight coupling | oms-services-nestjs/promotion, oms-services-order |
| **Legacy order ops** | oms-services-order still calls oms-api for some operations — migration incomplete | oms-services-order, oms-api |
| **Customer lookup** | cms-services-customer has 4 CRM-related env vars — unclear authority | cms-services-customer, crm-api, crm-customer-services |
| ~~**Billing event producers**~~ | **RESOLVED**: oms-services-billing produces billing.* topics consumed by oms-service-payment | oms-service-payment, oms-services-billing |

---

## External Repos Referenced (Not in This Monorepo)

| Domain | Referenced As | Evidence |
|--------|--------------|---------|
| LMS (Logistics) | `APP_FULFILLMENTDSN`, `lms.delivery-task` topic, fkt-platform-charts/lms/ | oms-services-order, K8s charts |
| WMS (Warehouse) | fkt-platform-charts/wms/ | K8s charts |
| SCN (Supply Chain Network) | fkt-platform-charts/scn/ | K8s charts |
| ~~Billing / Finance~~ | **RESOLVED**: oms-services-billing confirmed in workspace — see `services/oms-services-billing.md` | oms-services-order, oms-service-payment |
| PIM (Product Info Mgmt) | fkt-platform-charts/pim/ | K8s charts |
| AIS (Adapter Integration) | fkt-platform-charts/ais/ | K8s charts |
| MC (Merchant backend) | fkt-platform-charts/mc/ | K8s charts |

---

## Recommended Service for New Features

| Feature Type | Recommended Service |
|-------------|-------------------|
| New order field or status | oms-services-order |
| New product attribute or pricing model | oms-services-product |
| New promotion type or discount rule | oms-services-nestjs/promotion |
| New payment method | oms-service-payment |
| New customer data field | cms-services-customer |
| New CRM lead field | crm-customer-services or crm-api |
| New editorial content type | oms-services-content |
| New notification channel | shared-notification-service (new) or oms-services-nestjs/notification (legacy) |
| New KYC / credit term approval flow | cms-services-kyc-workflow |
| New billing document type | oms-services-billing |
| New customer auth mechanism | oms-services-nestjs/authorizer |
| New frontend page (customer) | portal-web/oms-web |
| New admin backoffice page | portal-web (appropriate app) |
| New HR feature | hrms-services-v2 |
