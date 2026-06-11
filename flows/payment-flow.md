# Payment Flow

## Overview
Payment processing from checkout through gateway confirmation and invoice generation.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant C as Customer (oms-web)
    participant ORDER as oms-services-order
    participant PAYMENT as oms-service-payment
    participant GW as Payment Gateway (Omise/KBank/KTB/TTB)
    participant BILLING as Billing Service (external)
    participant KAFKA as Kafka

    C->>ORDER: Checkout order
    ORDER-->>C: Payment methods + redirect URL

    C->>PAYMENT: Initiate payment (POST /payment)
    PAYMENT->>GW: Create charge (gateway-specific API)
    GW-->>PAYMENT: Charge token / redirect URL
    PAYMENT-->>C: Redirect to gateway

    C->>GW: Complete payment (card details / bank auth)
    GW-->>PAYMENT: Payment webhook (success/failure)

    PAYMENT->>PAYMENT: Record transaction
    PAYMENT->>KAFKA: Publish payment.transaction (Inferred)
    ORDER->>KAFKA: Publish oms.order.updated (payment confirmed)

    BILLING->>KAFKA: Publish billing.invoice (from billing service)
    KAFKA-->>PAYMENT: billing.invoice → store invoice record

    BILLING->>KAFKA: Publish billing.invoice.updated
    KAFKA-->>PAYMENT: billing.invoice.updated → update invoice

    Note over PAYMENT: Scheduled reconciliation
    PAYMENT->>GW: Reconcile transaction status
    GW-->>PAYMENT: Confirmed status
```

## Payment Gateways

| Gateway | Code Location | Usage |
|---------|--------------|-------|
| Omise | `third_party/omise/` | Primary Thai payment gateway |
| KBank | `third_party/kbank/` | Thai bank gateway |
| KTB | `third_party/ktb/` | Krungthai bank gateway |
| TTB | `third_party/ttb/` | TMBThanachart bank gateway |
| Offline | `third_party/offline` | Manual/bank transfer payments |

Gateway selection: `APP_PAYMENTGATEWAY` env var → `omise` / `kbank` / `ktb` / `ttb` / `offline`

## Payment Methods

| Method | Kafka Topic | Confidence |
|--------|-------------|-----------|
| Standard charge | `payment.transaction` | Confirmed (consumed) |
| Invoice payment | `billing.invoice` | Confirmed (consumed) |
| Credit note / refund | `billing.credit-note` | Confirmed (consumed) |
| Cash voucher | `billing.cash-voucher` | Confirmed (consumed) |
| Coin (loyalty points) | `payment.coin` | Confirmed (consumed) |

## Files to Modify for Payment Feature Changes

| Change | Primary File(s) |
|--------|----------------|
| New payment gateway | `oms-service-payment/third_party/<gateway>/`, `config/thirdparty/` |
| New payment method | `oms-service-payment/internal/services/`, Kafka consumer config |
| Invoice processing | `oms-service-payment/internal/services/invoice/` |
| Scheduled reconciliation | `oms-service-payment/cmd/scheduler/` |
| Feature flag for gateway | `oms-service-payment/` GrowthBook integration |

## Gaps

- Producer of `billing.*` topics is unknown (billing service is in a separate repo not indexed here)
- Payment redirect URL (`APP_JULIANBASEURL`) points to oms-web customer portal
- No OpenAPI spec for oms-service-payment REST endpoints
