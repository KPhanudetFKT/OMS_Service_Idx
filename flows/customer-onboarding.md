# Customer Onboarding Flow

## Overview
Flow from new customer lead creation through registration, KYC verification, and credit limit assignment — enabling the customer to place their first order.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant SALES as Sales / CRM Agent
    participant CRM_CS as crm-customer-services
    participant CRM_API as crm-api
    participant KAFKA as Kafka
    participant CIMS as cms-services-customer
    participant AUTH as nestjs/authorizer
    participant MOENGAGE as MOEngage (external)
    participant C as Customer

    SALES->>CRM_CS: Create lead (K8s API / Lambda)
    CRM_CS->>CRM_CS: Store lead in crm_customer DB
    CRM_CS->>KAFKA: Publish crm.customer

    KAFKA-->>CIMS: crm.customer → create customer record
    CIMS->>CIMS: Store customer in oms_customer DB

    Note over C: Customer registers / activates account
    C->>CRM_API: Register (creates user account)
    CRM_API->>KAFKA: Publish crm.user.registered

    KAFKA-->>CIMS: crm.user.registered → link user to customer record

    CIMS->>KAFKA: Publish cms.customer (profile ready)
    CIMS->>MOENGAGE: Sync customer profile to MOEngage

    Note over C: KYC verification
    C->>CIMS: Submit KYC documents (POST /kyc)
    CIMS->>CIMS: Process KYC verification
    CIMS->>CIMS: Update KYC status
    CIMS-->>C: KYC status response

    Note over SALES: Credit limit assignment
    SALES->>CIMS: Assign credit limit (internal API)
    CIMS->>CIMS: Store credit limit

    Note over C: First order
    C->>AUTH: Authenticate → get JWT token
    AUTH-->>C: JWT token
    C->>ORDER: Place order (with JWT)
    ORDER->>CIMS: Check credit limit (GET /credit-limit/check)
    CIMS-->>ORDER: Credit limit approved
    ORDER-->>C: Order confirmed
```

## Key Services

| Service | Role |
|---------|------|
| crm-customer-services | Lead creation, Salesforce sync |
| crm-api | User registration, CRM backoffice |
| cms-services-customer | Customer of record: profile, KYC, credit limit |
| oms-services-nestjs/authorizer | JWT issuance for authenticated access |
| MOEngage | Marketing engagement after onboarding |

## Files to Modify for Onboarding Changes

| Change | Primary File(s) |
|--------|----------------|
| New lead field | `crm-customer-services/internal/domains/` |
| Customer profile field | `cms-services-customer/service/customer/`, migration |
| KYC flow | `cms-services-customer/service/customer/`, `api/customer-openapi.yaml` |
| Credit limit logic | `cms-services-customer/service/customer/` |
| Post-registration notification | `cms-services-customer/service/customer-notification/` |

## Integration Gaps

- 4 CRM-related env vars in cms-services-customer — determine which is authoritative for each use case
- `cms.customer` topic consumers are undocumented — who downstream receives the customer-ready signal?
