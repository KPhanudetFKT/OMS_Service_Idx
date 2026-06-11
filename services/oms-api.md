# oms-api

## Responsibility
Legacy monolithic OMS backend built in .NET C#. The original all-in-one API handling orders, payments, products, users, restaurants, notifications, and promotions before the microservices migration began.

## Owns (Legacy)
- Legacy order processing
- Legacy payment integrations (2C2P, Omise, Bank Transfer)
- Legacy product management
- Legacy user / restaurant management
- Legacy promotions engine
- Firebase push notifications
- Invoice generation

## Does NOT Own (Migrated Away)
- New order creation (→ oms-services-order)
- Product catalog (→ oms-services-product)
- Customer profile (→ cms-services-customer)
- New payment processing (→ oms-service-payment)
- Promotion lifecycle (→ oms-services-nestjs/promotion)

## APIs
25+ .NET controllers in `FreshKetApi/Controllers/`:

| Controller | Purpose |
|-----------|---------|
| OrdersController | Order management |
| ProductsController | Product management |
| PaymentsController | Payment handling |
| Payment2C2PController | 2C2P gateway |
| OmisePaymentController | Omise gateway |
| UsersController | User management |
| RestaurantsController | Restaurant/vendor management |
| PromotionsController | Promotion engine |
| NotificationController | Push notifications |
| InvoiceController | Invoice generation |
| AuthsController | Authentication |
| MastersController | Master data |
| GeoController | Geolocation |
| MarketPlaceController | Marketplace |
| GradingController | Grading system |
| FreshketPassController | Freshket Pass program |
| UploadController | File uploads |
| TasksController | Background tasks |
| ForSupportController | CS support tools |
| RemoteConfigController | Remote configuration |
| PosController | POS integration |
| PageController | Content pages |
| LocalController | Localization |

Auth: Inferred — cookie/session or API key (legacy pattern)

## Events Published
None detected (pre-Kafka legacy service).

## Events Consumed
None detected.

## Database Ownership
- Legacy SQL database (specific DB name not confirmed — Inferred from MSSQL pattern)
- Multiple database schemas across FreshKetApi.Models (~397 model files)
- FreshKetApi.PG.Models — PostgreSQL models (Inferred: dual DB legacy system)

## Dependencies
- Firebase Admin SDK — push notifications (FirebaseMessagingService)
- 2C2P payment gateway
- Omise payment gateway
- Bank transfer processing
- Email service (EmailService)
- Encryption service (EncryptionService)

## Important Files
| File | Purpose |
|------|---------|
| `FreshKetApi/Controllers/` | 25+ API controllers |
| `FreshKetApi.Services/` | ~67 service files |
| `FreshKetApi.Models/` | ~397 data model files |
| `FreshKetApi.RestModels/` | ~94 REST DTO files |
| `FreshKetApi.Interfaces/` | Service interfaces |
| `FreshKetApi.Utils/` | Utility functions |
| `FreshKetApi.Tests/` | Test suite |
| `FreshKetApi.sln` | Solution file |

## Feature Flags
None detected (pre-GrowthBook).

## Main Flows
Legacy flows — now partially or fully migrated to Go microservices:
1. Legacy order placement and management
2. Legacy payment processing (2C2P, Omise)
3. Legacy push notifications via Firebase
4. Legacy product catalog management

## Caller Summary

Full detail: see `oms-api-caller-map.md` in this directory.

**~175 total endpoints. ~85% have no known callers.**

### Active microservice callers
| Caller | Endpoint | File |
|--------|----------|------|
| oms-services-order | `POST api/authorize/intranet` | `thirdparty/legacywebmvcapi/legacy_webmvc_api.go` |
| oms-promotion-workers | `POST api/authorize/intranet` | `infrastructure/order/service/order/repository/api/order_api.go` |
| cms-services-kyc-workflow | `POST api/authorize/intranet` | `infrastructure/legacyWeb/legacyWeb.go` |
| oms-services-nestjs/orderadapter | `POST baseApi/Payments/Paid` | `apps/orderadapter/src/modules/payment/payment.service.ts` |

### Legacy / frontend callers
| Caller | Endpoints |
|--------|-----------|
| scm-intranet-web | `baseApi/Invoice/CreateInvoice(s)`, `baseApi/Payments/CreateReceiveInvoiceFromPayment`, `baseApi/Notification/SendNotificationRedeem` |
| portal-web | `baseApi/Users/ValidateEmail` |
| oms-julian | `baseApi/Users/RegisterJulian`, `baseApi/Users/ValidateEmail`, `baseApi/Users/RequestOtp`, `baseApi/Users/CustomMessage` |
| oms-monorepo | `baseApi/Orders/{userId}/outstanding`, `baseApi/Users/CustomMessage` |

### External webhook callers (payment gateways)
- Omise → `baseApi/OmisePayment/omise/webhook`, `baseApi/OmisePayment/PaymentOmise/webhook`
- 2C2P → `baseApi/Payment2C2P/payment2c2p/webhook`

## Risks
- **.NET legacy**: .NET 4.6.1 — very old framework, security and maintenance risk
- **High coupling**: 397 model files suggest high internal coupling — hard to extract further
- **Actively called**: `api/authorize/intranet` called by 3 Go microservices — must be migrated before decommission
- **No OpenAPI spec**: No machine-readable contract for 25+ controllers
- **~85% dead endpoints**: Most endpoints have no known callers — significant dead code surface
- **Unknown DB schema**: Exact database name/schema not confirmed from available files

## Suggested Improvements
- **Priority**: Eliminate `api/authorize/intranet` dependency — build buyer-auth endpoint in oms-services-order or cms-services-customer
- Migrate `baseApi/Payments/Paid` call to oms-service-payment (oms-services-nestjs/orderadapter)
- Migrate `baseApi/Users/*` calls from oms-julian to oms-services-nestjs/otp and auth
- Migrate scm-intranet-web invoice/payment calls to billing service
- Decommission clearly superseded controllers: MarketPlace (→ oms-services-product), Products, Promotions, Banner, Page
- Add OpenAPI spec for the 15 actively-called endpoints before migration
