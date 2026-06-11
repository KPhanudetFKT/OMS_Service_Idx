# Order Lifecycle Flow

## Overview
End-to-end flow from a B2B customer adding products to cart through delivery completion.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant C as Customer (oms-web)
    participant ORDER as oms-services-order
    participant PRODUCT as oms-services-product
    participant PROMO as nestjs/promotion
    participant CUSTOMER as cms-services-customer
    participant RECOMMEND as oms-services-recommendation
    participant ADAPTER as nestjs/orderadapter
    participant LMS as LMS Service (external)
    participant NOTIFY as nestjs/notification
    participant KAFKA as Kafka

    C->>ORDER: Add item to cart (POST /shopping-cart)
    ORDER->>PRODUCT: Fetch SKU pricing (GET /resources/skus)
    PRODUCT-->>ORDER: Pricing + product data
    ORDER->>RECOMMEND: Get cart recommendations
    RECOMMEND-->>ORDER: Related products
    ORDER-->>C: Cart with totals + recommendations

    C->>ORDER: Place order (POST /orders)
    ORDER->>CUSTOMER: Check credit limit (GET /credit-limit/check)
    CUSTOMER-->>ORDER: Credit limit status
    ORDER->>PRODUCT: Validate SKU availability
    PRODUCT-->>ORDER: Availability confirmed
    ORDER->>PROMO: Validate applicable promotions
    PROMO-->>ORDER: Applicable discounts
    ORDER->>ORDER: Calculate final price (tax, service fee, rebate)
    ORDER->>KAFKA: Publish oms.order.created
    ORDER-->>C: Order confirmed (order ID)

    KAFKA-->>PROMO: oms.order.created → apply promotions
    PROMO->>ORDER: Update order with promotion result (Likely)

    ORDER->>KAFKA: Publish oms.co.created
    KAFKA-->>ADAPTER: oms.co.created → sync to downstream systems

    ORDER->>LMS: Schedule delivery (POST fulfillment)
    LMS-->>ORDER: Delivery task ID
    ORDER->>KAFKA: Publish oms.order.updated (delivery scheduled)

    KAFKA-->>NOTIFY: oms.order.updated.co-created → notify customer
    NOTIFY-->>C: Push / LINE notification

    LMS->>KAFKA: lms.delivery-task (delivery status update)
    KAFKA-->>ORDER: Update delivery status

    ORDER->>KAFKA: Publish oms.order.updated (delivered)
    ORDER->>KAFKA: Publish oms.order-delivered-updated
```

## Key Services

| Service | Role in Flow |
|---------|-------------|
| oms-services-order | Orchestrator — owns cart, order, delivery scheduling |
| oms-services-product | SKU pricing and availability validation |
| oms-services-nestjs/promotion | Promotion calculation and application |
| cms-services-customer | Credit limit gating |
| oms-services-recommendation | Cart recommendations |
| oms-services-nestjs/orderadapter | Syncs CO data to downstream |
| LMS (external) | Physical delivery execution |
| oms-services-nestjs/notification | Customer notifications |

## Files to Modify for Order Feature Changes

| Change | Primary File(s) |
|--------|----------------|
| New order field | `oms-services-order/pkg/order/`, `api/order-openapi.yaml`, migration |
| New calculation logic | `oms-services-order/pkg/calculation/` |
| Delivery slot changes | `oms-services-order/pkg/delivery/`, `api/delivery-openapi.yaml` |
| New promotion type | `oms-services-nestjs/apps/promotion/` |
| Cart recommendation changes | `oms-services-recommendation/` |

## Error Scenarios

| Scenario | Handling |
|----------|---------|
| Credit limit exceeded | ORDER rejects with 4xx, customer notified |
| SKU unavailable | ORDER returns validation error |
| Promotion invalid | ORDER proceeds without discount |
| Delivery scheduling fails | ORDER saves without delivery task (async retry) |
| Kafka publish fails | DLQ → Slack alert |
