# API Catalog — Freshket Platform

## Authentication Requirements

| Auth Type | Header | Used By |
|-----------|--------|---------|
| Customer JWT | `Authorization: Bearer <token>` | Customer-facing endpoints |
| Staff JWT (JWKS) | `Authorization: Bearer <token>` | Admin/backoffice endpoints |
| Internal HMAC | `X-API-Key` + HMAC signature | Service-to-service |
| API Gateway Lambda | Handled by authorizer Lambda | NestJS Lambda apps |

---

## oms-services-order

Source: `oms-services-order/api/` (6 OpenAPI YAML specs)
Base URL env: `APP_ORDERDSN` (in dependent services)
Port: 1323

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET/POST | `/orders` | Order list / create | Customer JWT |
| GET/PUT/DELETE | `/orders/{id}` | Order CRUD | Customer JWT |
| POST | `/orders/cancellations` | Cancel order | Customer JWT |
| POST | `/orders/pvp-validate` | PVP (pre-verify purchase) validation | Internal |
| GET/POST | `/orders/rebate-programs` | Rebate program management | Staff JWT |
| GET/POST | `/orders/services-fee` | Service fee rules | Staff JWT |
| GET/POST | `/shopping-cart` | Cart CRUD | Customer JWT |
| GET | `/shopping-cart/recommendations` | Cart item recommendations | Customer JWT |
| GET/POST | `/bulk-orders` | Bulk order management | Customer JWT |
| POST | `/calculation` | Order price calculation | Internal |
| GET | `/delivery/time-slots` | Available delivery time slots | Customer JWT |
| GET | `/delivery/dates` | Available delivery dates | Customer JWT |
| GET | `/delivery/base-times` | Delivery base time config | Staff JWT |
| GET/POST | `/admin/orders` | Admin order management | Staff JWT |
| GET | `/resources/orders` | Internal order resource API | Internal |
| GET | `/health` | Health check | None |

---

## oms-services-product

Source: `oms-services-product/api/` (8 OpenAPI YAML specs)
Base URL env: `APP_PRODUCTDSN`
Port: 1323

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/resources/skus` | SKU list (search, filter) | Customer JWT / Internal |
| GET | `/resources/skus/{id}` | SKU detail | Customer JWT / Internal |
| GET | `/resources/skus/area-prices` | Area-based pricing | Internal |
| GET | `/resources/skus/private-prices` | Private pricing | Internal |
| GET/POST/PUT/DELETE | `/admin/skus` | Admin SKU management (40+ endpoints) | Staff JWT |
| GET | `/resources/products` | Product list | Customer JWT |
| GET/POST | `/resources/categories` | Category management | Customer JWT / Staff |
| GET/POST | `/resources/brands` | Brand management | Customer JWT / Staff |
| GET/POST | `/resources/labels` | Label management | Staff JWT |
| GET | `/suggestions` | Search suggestions / autocomplete | Customer JWT |
| GET | `/pre-search-recommendations` | Pre-search product recommendations | Customer JWT |
| GET/PUT | `/admin/settings` | Product settings management | Staff JWT |
| GET | `/health` | Health check | None |

---

## oms-services-content

Source: `oms-services-content/api/` (6 OpenAPI YAML specs)
Port: 1323

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET/POST/PUT/DELETE | `/admin/posts` | Post management | Staff JWT |
| GET/POST/PUT/DELETE | `/admin/banners` | Banner management | Staff JWT |
| GET | `/banners` | Customer-facing banners | Customer JWT |
| GET/POST/PUT/DELETE | `/admin/pages` | Page management | Staff JWT |
| GET | `/pages` | Customer-facing pages | Customer JWT |
| GET/POST/PUT/DELETE | `/admin/brands` | Brand content management | Staff JWT |
| GET | `/images` | Image content | Customer JWT |
| GET | `/term-and-conditions` | T&C content | Customer JWT |
| GET | `/products` | Product content | Customer JWT |
| GET | `/health` | Health check | None |

---

## cms-services-customer (CIMS)

Source: `cms-services-customer/api/customer-openapi.yaml`
Port: 1323 (internal), separate port (external via API Gateway)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/info` | Customer profile information | Customer JWT |
| GET/POST | `/kyc` | KYC verification status/submission | Customer JWT |
| GET | `/credit-limit/check` | Customer credit limit check | Internal |

---

## oms-services-recommendation

Source: `oms-services-recommendation/api/recommendation-openapi.yaml`
Base URL env: `APP_RECOMMENDDSN`
Port: 1323

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/recommendations` (inferred) | Product recommendations | Customer JWT / Internal |
| GET | `/health` | Health check | None |

Note: Exact endpoints inferred — read the YAML for details.

---

## oms-service-payment

No OpenAPI spec. HTTP handlers in `http/handlers/` by domain.

| Domain | Inferred Endpoints | Auth |
|--------|-------------------|------|
| Charge | `/charge/*` | Internal / Staff JWT |
| Payment | `/payment/*` | Internal / Customer JWT |
| Invoice | `/invoice/*` | Internal / Staff JWT |
| Credit Note | `/credit-note/*` | Internal / Staff JWT |
| Cash Voucher | `/cash-voucher/*` | Internal / Customer JWT |
| Coin | `/coin/*` | Internal / Customer JWT |

---

## oms-api (Legacy .NET)

No OpenAPI spec. 25+ controllers — partial list of inferred endpoints:

| Controller | Base Path | Auth |
|-----------|-----------|------|
| OrdersController | `/api/orders` | Legacy auth |
| ProductsController | `/api/products` | Legacy auth |
| PaymentsController | `/api/payments` | Legacy auth |
| UsersController | `/api/users` | Legacy auth |
| RestaurantsController | `/api/restaurants` | Legacy auth |
| PromotionsController | `/api/promotions` | Legacy auth |
| NotificationController | `/api/notifications` | Legacy auth |
| InvoiceController | `/api/invoices` | Legacy auth |
| AuthsController | `/api/auths` | N/A |

---

## cms-services-kyc-workflow

Source: `api/customer.open-api.yaml` (28 endpoints)
Base path: `cms/kyc-workflow` (Lambda via API Gateway)

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/customers/request-verifications` | Submit customer verification | Customer JWT |
| GET | `/customers` | Get verification info | Customer JWT |
| GET | `/resources/customers` | Search customers | Staff JWT |
| GET/POST | `/resources/customers/verifications` | List / create verifications | Staff JWT |
| GET | `/resources/customers/verifications/{guid}` | Verification detail | Staff JWT |
| POST | `/resources/customers/verifications/{guid}/approve` | Approve verification | Staff JWT |
| POST | `/resources/customers/verifications/{guid}/reject` | Reject verification | Staff JWT |
| POST | `/resources/customers/request-credit-term` | Submit credit term request | Customer JWT |
| PUT | `/resources/customers/request-credit-term/{guid}` | Edit credit term | Staff JWT |
| POST | `/resources/customers/request-credit-limit` | Submit credit limit request | Customer JWT |
| PUT | `/resources/customers/request-credit-limit/{guid}` | Edit credit limit | Staff JWT |
| GET | `/resources/customers/request-credit-terms` | List credit term requests | Staff JWT |
| GET/DELETE | `/resources/customers/request-credit-terms/{guid}` | Detail / delete credit term | Staff JWT |
| POST | `/resources/customers/request-credit-terms/{guid}/approve` | Approve credit term | Staff JWT |
| POST | `/resources/customers/request-credit-terms/{guid}/reject` | Reject credit term | Staff JWT |
| GET | `/resources/my/customers/request-credit-terms` | Own credit term requests | Customer JWT |
| GET | `/customers/invoice-upload-permissions` | Invoice upload permission check | Customer JWT |

---

## oms-promotion-workers

Source: `api/product.openapi.yaml`, `api/campaign-openapi.yaml`

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/admin/bulk_save_skus_to_promotion` | Bulk sync SKUs to promotion | Staff/Internal |
| POST | `/admin/sync_one_sku_price_off_to_product` | Sync single SKU price-off | Staff/Internal |
| GET | `/admin/sync_priceoff_to_product` | Bulk sync all price-offs | Staff/Internal |
| POST | `/tray` | Insert tray SKU for campaign | Internal |

---

## oms-services (mono)

Source: `api/product.openapi.yaml`, `api/delivery-openapi.yaml`, `api/log.openapi.yaml`

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | `/product-sync` | Sync product from legacy | Internal |
| GET | `/delivery/delivery-dates` | Available delivery dates | Customer JWT |
| GET | `/delivery/delivery-time-slots` | Time slots for a date | Customer JWT |
| POST | `/delivery/refresh-data` | Force refresh delivery data | Internal |
| GET | `/delivery/base-time-slots` | Base delivery time slot config | Staff JWT |
| POST | `/public/logs/requests` | Save frontend request log | Public |

---

## shared-notification-service

Source: Swagger (auto-generated via `make swag-api`)
Port: 8080 (`API_PORT`)

Endpoint domains (two boundary modes: `external` = Auth0 JWT, `internal` = X-Api-Key):
- Notification list, mark read, unread count
- WebSocket connection for real-time push
- Email send endpoint

Full spec available at `http://localhost:8080/swagger/index.html` when running locally.

---

## lms-fast-bff-service

Source: Swagger (auto-generated via `make swag-api`)
Port: 8081 (`API_PORT`)

Endpoint domains (Firebase JWT auth for rider-facing routes):
- Delivery time slots and dates
- Rider attendance
- Document uploads (S3)
- Health check

Full spec available at `http://localhost:8081/swagger/index.html` when running locally.

---

## Coverage Gaps

| Service | Gap |
|---------|-----|
| oms-service-payment | No OpenAPI spec |
| crm-customer-services | No OpenAPI spec (Lambda-native) |
| oms-services-nestjs | No OpenAPI spec (event-driven Lambda) |
| crm-api | No OpenAPI spec |
| oms-api | No OpenAPI spec (legacy) |
| hrms-services-v2 | Not explored |
| oms-services-billing | No OpenAPI spec found |
| oms-services-promotion | No OpenAPI spec found |

Services with full OpenAPI coverage: oms-services-order (6), oms-services-product (8), oms-services-content (6), cms-services-customer (1), oms-services-recommendation (2), cms-services-kyc-workflow (1).
