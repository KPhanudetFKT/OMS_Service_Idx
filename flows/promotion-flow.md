# Promotion Flow

## Overview
Lifecycle of a promotion from staff creation through customer order application and content display.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant STAFF as Staff (backoffice)
    participant PROMO as nestjs/promotion
    participant KAFKA as Kafka
    participant PRODUCT as oms-services-product
    participant CONTENT as oms-services-content
    participant ORDER as oms-services-order
    participant C as Customer

    STAFF->>PROMO: Create promotion (API call)
    PROMO->>PROMO: Validate and store promotion
    PROMO->>KAFKA: Publish oms.promotion.created
    KAFKA-->>PRODUCT: oms.promotion.created → index promotion on products
    KAFKA-->>CONTENT: oms.promotion.created → create promotion content (banner/page)

    STAFF->>PROMO: Activate promotion
    PROMO->>KAFKA: Publish oms.promotion.activated
    KAFKA-->>CONTENT: oms.promotion.activated → show promotion content
    Note over CONTENT: Banner/page goes live

    C->>ORDER: Place order
    ORDER->>PROMO: Validate applicable promotions for order
    PROMO-->>ORDER: Applicable promotions + discount amounts
    ORDER->>ORDER: Apply discounts to order calculation
    ORDER->>KAFKA: Publish oms.order.created
    KAFKA-->>PROMO: oms.order.created → track promotion usage

    Note over PROMO: Promotion reaches quota
    PROMO->>KAFKA: Publish oms.promotion.fulled
    KAFKA-->>CONTENT: oms.promotion.fulled → update content (show "sold out")
    KAFKA-->>PRODUCT: oms.promotion.updated → remove from product listing

    STAFF->>PROMO: Deactivate promotion
    PROMO->>KAFKA: Publish oms.promotion.deactivated
    KAFKA-->>CONTENT: oms.promotion.deactivated → hide content
    KAFKA-->>PRODUCT: oms.promotion.updated → remove from product search
```

## Key Services

| Service | Role |
|---------|------|
| oms-services-nestjs/promotion | Owns promotion rules, lifecycle, quota management |
| oms-services-product | Indexes promotions on products for search/display |
| oms-services-content | Shows promotion banners/pages to customers |
| oms-services-order | Applies promotion discounts during order calculation |

## Promotion Event Flow

```
oms.promotion.created   → product (index) + content (create)
oms.promotion.updated   → product (re-index) + content (update)
oms.promotion.activated → content (show)
oms.promotion.deactivated → content (hide)
oms.promotion.fulled    → content (sold-out display)
```

## Files to Modify for Promotion Feature Changes

| Change | Primary File(s) |
|--------|----------------|
| New promotion type / rule | `oms-services-nestjs/apps/promotion/` |
| Promotion content display | `oms-services-content/pkg/promotion/`, `event/` |
| Promotion on product search | `oms-services-product/event/` |
| Promotion application in order | `oms-services-order/thirdparty/promotionapi/`, `pkg/calculation/` |
| Promotion banner UI | `portal-web/apps/oms-web/` |

## Topic Note

Content service topics include environment suffix:
- Dev: `oms.promotion.activated.dev`
- SIT: `oms.promotion.activated.sit`
- UAT/PROD: Confirm via env config
