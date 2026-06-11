# oms-api Caller Map

Scope: all 86 repos in the `freshket` GitHub organization + local monorepo.
Source: controller inspection of `/Users/freshket/projects/oms-api/FreshKetApi/Controllers/` + GitHub code search.

**Total endpoints: ~175 across 26 controllers**
**Endpoints with active microservice callers: 8**
**Endpoints called only by legacy frontend / scm-intranet-web: 7**
**Endpoints triggered only by external webhooks: 3**
**Endpoints with no caller found: ~149 (~85%)**

---

## Callers by Service

| Caller | GitHub Repo | Endpoints Called |
|--------|-------------|-----------------|
| oms-services-order | freshket/oms-services-order | `POST api/authorize/intranet` |
| oms-promotion-workers | freshket/oms-promotion-workers | `POST api/authorize/intranet` |
| cms-services-kyc-workflow | freshket/cms-services-kyc-workflow | `POST api/authorize/intranet` |
| oms-services-nestjs/orderadapter | freshket/oms-services-nestjs | `POST baseApi/Payments/Paid` |
| scm-intranet-web | freshket/scm-intranet-web | `GET/POST baseApi/Invoice/CreateInvoice`, `POST baseApi/Invoice/CreateInvoices`, `POST baseApi/Payments/CreateReceiveInvoiceFromPayment`, `POST baseApi/Notification/SendNotificationRedeem` |
| portal-web | freshket/portal-web | `GET baseApi/Users/ValidateEmail` |
| oms-julian | freshket/oms-julian | `POST baseApi/Users/RegisterJulian`, `GET baseApi/Users/ValidateEmail`, `POST baseApi/Users/RequestOtp`, `GET baseApi/Users/CustomMessage` |
| oms-monorepo | freshket/oms-monorepo | `GET baseApi/Orders/{userId}/outstanding`, `GET baseApi/Users/CustomMessage` |
| Omise (external gateway) | — | `POST baseApi/OmisePayment/omise/webhook`, `POST baseApi/OmisePayment/PaymentOmise/webhook` |
| 2C2P (external gateway) | — | `POST baseApi/Payment2C2P/payment2c2p/webhook` |
| automate-testing *(test only)* | freshket/automate-testing | `POST api/authorize/intranet`, `POST baseApi/Users/RegisterJulian`, `GET baseApi/Users/ValidateEmail` |
| oms-user-service *(dev .http file only)* | freshket/oms-user-service | `POST baseApi/Auths/Auth`, `POST baseApi/Auths/ResetPassword` |

---

## Endpoint → Caller Detail

### `api/authorize/intranet` — **CRITICAL: 3 active microservice callers**

| Caller | File | Purpose |
|--------|------|---------|
| oms-services-order | `thirdparty/legacywebmvcapi/legacy_webmvc_api.go` | Fetch buyer auth + box pricing; used in order creation and service fee validation (`order_service.go` lines 1327, 2137) |
| oms-promotion-workers | `infrastructure/order/service/order/repository/api/order_api.go` | Buyer auth token for adding SKUs to orders |
| cms-services-kyc-workflow | `infrastructure/legacyWeb/legacyWeb.go` | Buyer auth for KYC credit-term workflow |

---

### `baseApi/Auths/*`

| Endpoint | Caller | Notes |
|----------|--------|-------|
| `POST /baseApi/Auths/Auth` | oms-user-service (`rest.http`) | Dev test file only — not production service code |
| `POST /baseApi/Auths/ResetPassword` | oms-user-service (`rest.http`) | Dev test file only |
| `POST /baseApi/Auths/VerifyToken` | **No caller found** | — |
| `POST /baseApi/Auths/ChangePassword` | **No caller found** | — |

---

### `baseApi/Banner/*`

| Endpoint | Caller | Notes |
|----------|--------|-------|
| `GET /baseApi/Banner/{owner}/{page}/{lang}` | **No caller found** | Replaced by oms-services-content `/banners` |
| `GET /baseApi/Banner/GetBanner` | **No caller found** | Replaced by oms-services-content |

---

### `baseApi/ForSupport/*` — **No callers found (11 endpoints)**

All `[AllowAnonymous]` — likely called directly by CS/ops agents via browser or Postman, not from any service.

| Endpoint |
|----------|
| `POST /baseApi/ForSupport/Void` |
| `POST /baseApi/ForSupport/UnVoid` |
| `POST /baseApi/ForSupport/UnVoidCn` |
| `POST /baseApi/ForSupport/ClearUserSuspenDate` |
| `POST /baseApi/ForSupport/EditRemark` |
| `POST /baseApi/ForSupport/CheckPromocode` |
| `POST /baseApi/ForSupport/EditRefund` |
| `POST /baseApi/ForSupport/EditBox` |
| `POST /baseApi/ForSupport/regen-item` |
| `POST /baseApi/ForSupport/ReadFile` |
| `POST /baseApi/ForSupport/sync-bulk-item` |

---

### `baseApi/FreshketPass/*` — **No callers found (7 endpoints)**

| Endpoint |
|----------|
| `GET /baseApi/FreshketPass/Categories` |
| `GET /baseApi/FreshketPass/PeriodValues` |
| `GET /baseApi/FreshketPass/Items` |
| `POST /baseApi/FreshketPass/Save` |
| `GET /baseApi/FreshketPass/SendMailEndOfMonth` |
| `GET /baseApi/FreshketPass/SendMailBeforeEndOfMonth` |
| `GET /baseApi/FreshketPass/SendMailDaily` |

---

### `baseApi/Geo/*` — **No callers found**

| Endpoint |
|----------|
| `POST /baseApi/Geo/GetAreaByLocation` |

---

### `baseApi/Grading/*` — **No callers found**

| Endpoint | Notes |
|----------|-------|
| `POST /baseApi/Grading/GetTransactions` | — |
| `POST /baseApi/Grading/GetMasterRedeemPoints` | — |
| `POST /baseApi/Grading/ConverPointToPromo` | scm-intranet-web calls Notification/SendNotificationRedeem after grading but does NOT call Grading controller directly |

---

### `baseApi/Invoice/*`

| Endpoint | Caller | File |
|----------|--------|------|
| `GET /baseApi/Invoice/CreateInvoice` | scm-intranet-web | `action/operation_custom_fkpo/ajax.php` |
| `POST /baseApi/Invoice/CreateInvoices` | scm-intranet-web | `cronjob/confirm_all_po.php`, `action/WMS_printing/ajax.php`, `action/post_billing/ajax.php` |
| `GET /baseApi/Invoice/GetInvById` | **No caller found** | — |
| `GET /baseApi/Invoice/GetInvUrl` | **No caller found** | — |

---

### `baseApi/local/*` — **No callers found (4 endpoints)**

Likely used by internal cron or manual admin invocation.

| Endpoint |
|----------|
| `GET /baseApi/local/SyncMarket` |
| `GET /baseApi/local/SyncCategory` |
| `GET /baseApi/local/SyncLastOrder` |
| `GET /baseApi/local/SyncLastOrders` |

---

### `baseApi/MarketPlace/*` — **No callers found (11 endpoints)**

All replaced by `oms-services-product` (Algolia/Elasticsearch search). Confidence: deprecated.

| Endpoint |
|----------|
| `POST /baseApi/MarketPlace/Search` |
| `POST /baseApi/MarketPlace/SearchCampaignProduct` |
| `POST /baseApi/MarketPlace/SearchNewProduct` |
| `POST /baseApi/MarketPlace/SearchFreshketDealItems` |
| `POST /baseApi/MarketPlace/SearchMyFreshketDealItems` |
| `GET /baseApi/MarketPlace/AutoComplete` |
| `POST /baseApi/MarketPlace/NewAutoComplete` |
| `GET /baseApi/MarketPlace/GetAllCampaign` |
| `GET /baseApi/MarketPlace/GetAllLifeStyle` |
| `GET /baseApi/MarketPlace/GetAllBanner` |
| `GET /baseApi/MarketPlace/GetAllRecipe` |

---

### `baseApi/Masters/*` — **No callers found (9 endpoints)**

May be called from mobile app (`freshket/oms-mobile-app` — not deeply indexed).

| Endpoint |
|----------|
| `GET /baseApi/Masters/GetAllCategories` |
| `GET /baseApi/Masters/GetTypesOfBusiness` |
| `GET /baseApi/Masters/GetAllAreas` |
| `GET /baseApi/Masters/GetAvailableCountries` |
| `POST /baseApi/Masters/GetAvailableProvinces` |
| `POST /baseApi/Masters/GetAvailableDistricts` |
| `POST /baseApi/Masters/GetAvailableSubDistricts` |
| `GET /baseApi/Masters/GetNoOfBranch` |
| `GET /baseApi/Masters/GetAverageBasketSize` |

---

### `baseApi/Notification/*`

| Endpoint | Caller | File |
|----------|--------|------|
| `POST /baseApi/Notification/NewRegister` | **No caller found** | — |
| `POST /baseApi/Notification/Register` | **No caller found** | — |
| `POST /baseApi/Notification/UnRegister` | **No caller found** | — |
| `POST /baseApi/Notification/Send` | **No caller found** | — |
| `POST /baseApi/Notification/SendForgotPassword` | **No caller found** | — |
| `POST /baseApi/Notification/SendNotificationAll` | **No caller found** | — |
| `POST /baseApi/Notification/SendNotification` | **No caller found** | — |
| `POST /baseApi/Notification/SendNotificationGrading` | **No caller found** | — |
| `POST /baseApi/Notification/SendNotificationRedeem` | scm-intranet-web | `action/grading_request_gift/ajax.php` |
| `GET /baseApi/Notification/SendLineNotify` | **No caller found** | — |
| `POST /baseApi/Notification/SendNotificationTest` | **No caller found** | — |
| `GET /baseApi/Notification/SendNotificationCannotRegister` | **No caller found** | — |
| `GET /baseApi/Notification/SendNotificationDeliverySuccess` | **No caller found** | — |

Note: `oms-services-nestjs/notification` now handles platform notifications — most of these are superseded.

---

### `baseApi/OmisePayment/*`

| Endpoint | Caller | Notes |
|----------|--------|-------|
| `POST /baseApi/OmisePayment/PayWithClientToken` | **No caller found** | Likely mobile app (unindexed) |
| `POST /baseApi/OmisePayment/PayWithToken` | **No caller found** | Likely mobile app |
| `POST /baseApi/OmisePayment/CreateCharge` | **No caller found** | Superseded by oms-service-payment |
| `POST /baseApi/OmisePayment/GeneratePaymentToken` | **No caller found** | — |
| `POST /baseApi/OmisePayment/omise/webhook` | Omise (external) | Payment gateway callback |
| `POST /baseApi/OmisePayment/TestPayToken` | **No caller found** | Test only |
| `GET /baseApi/OmisePayment/CreateTransactionId` | **No caller found** | — |
| `POST /baseApi/OmisePayment/PaymentOmise/webhook` | Omise (external) | Duplicate webhook path |

---

### `baseApi/Orders/*`

| Endpoint | Caller | File |
|----------|--------|------|
| `POST /baseApi/Orders/GetOrders` | **No caller found** | — |
| `POST /baseApi/Orders/GetInvoices` | **No caller found** | — |
| `POST /baseApi/Orders/GetLastOrders` | **No caller found** | — |
| `POST /baseApi/Orders/SearchFavItems` | **No caller found** | — |
| `POST /baseApi/Orders/GetTimeSlots` | **No caller found** | — |
| `POST /baseApi/Orders/GetItemsSupplierValid` | **No caller found** | — |
| `GET /baseApi/Orders/{userId}/outstanding` | oms-monorepo | `libs/shared/data-access/account-information/src/outstanding-order/outstanding-order-repository.ts` |

Note: `/outstanding` route is not in the analyzed controller — may be an undocumented route or legacy path variant.

---

### `baseApi/Page/*`

| Endpoint | Caller | Notes |
|----------|--------|-------|
| `GET /baseApi/Page/Section` | **No caller found** | Superseded by oms-services-content |

---

### `baseApi/Payment2C2P/*`

| Endpoint | Caller | Notes |
|----------|--------|-------|
| `POST /baseApi/Payment2C2P/Pay` | **No caller found** | Superseded by oms-service-payment |
| `GET /baseApi/Payment2C2P/CreateTransactionId` | **No caller found** | — |
| `POST /baseApi/Payment2C2P/payment2c2p/webhook` | 2C2P (external) | Payment gateway callback |

---

### `baseApi/Payments/*`

| Endpoint | Caller | File |
|----------|--------|------|
| `GET /baseApi/Payments/GetPayments` | **No caller found** | — |
| `POST /baseApi/Payments/UploadFileSlip` | **No caller found** | — |
| `POST /baseApi/Payments/CreatePayPlus` | **No caller found** | — |
| `POST /baseApi/Payments/CreateThaiQrCodePayment` | **No caller found** | — |
| `GET /baseApi/Payments/ApproveBankTransfer` | **No caller found** | — |
| `GET /baseApi/Payments/RejectBankTransfer` | **No caller found** | — |
| `GET /baseApi/Payments/TestSendEmail` | **No caller found** | Test only |
| `POST /baseApi/Payments/PayPlusRest` | **No caller found** | — |
| `POST /baseApi/Payments/PayPlusNotification` | **No caller found** | — |
| `POST /baseApi/Payments/CreateReceiveInvoiceFromPayment` | scm-intranet-web | `action/post_billing/ajax.php` |
| `GET /baseApi/Payments/Point` | **No caller found** | — |
| `POST /baseApi/Payments/Paid` | oms-services-nestjs/orderadapter | `apps/orderadapter/src/modules/payment/payment.service.ts` |

---

### `baseApi/Pos/*` — **No callers found (6 endpoints)**

| Endpoint |
|----------|
| `POST /baseApi/Pos/GetPoes` |
| `GET /baseApi/Pos/GetPoDetail/{po_id}` |
| `GET /baseApi/Pos/GetPo` |
| `GET /baseApi/Pos/GetPoById` |
| `GET /baseApi/Pos/VoidPo` |
| `GET /baseApi/Pos/VoidCurrentPayment` |

---

### `baseApi/Products/*` — **No callers found**

All superseded by `oms-services-product`.

| Endpoint |
|----------|
| `GET /baseApi/Products/ProductDetail` |
| `POST /baseApi/Products/ProductDetail` |
| `POST /baseApi/Products/ReCheckPrices` |
| `POST /baseApi/Products/ReloadItems` |

---

### `baseApi/Promotions/*` — **No callers found**

All superseded by `oms-services-nestjs/promotion`.

| Endpoint |
|----------|
| `POST /baseApi/Promotions/VerifyPromoCode` |
| `POST /baseApi/Promotions/GetPromoCodes` |
| `POST /baseApi/Promotions/GetPromoCodeTrans` |
| `POST /baseApi/Promotions/GetPromoBaskets` |

---

### `baseApi/Remote/*` — **No callers found**

| Endpoint |
|----------|
| `GET /baseApi/Remote/Config` |
| `GET /baseApi/Remote/ResetOTP` |
| `GET /baseApi/Remote/AddPreFixPhone` |

---

### `baseApi/Restaurants/*` — **No callers found**

| Endpoint |
|----------|
| `POST /baseApi/Restaurants/UpdateRestaurant` |
| `POST /baseApi/Restaurants/AddAccount` |

---

### `baseApi/Tasks/*` — **No callers found (13 endpoints)**

Likely invoked by scheduler/cron (AWS EventBridge or internal timer), not by any microservice client.

| Endpoint |
|----------|
| `GET /baseApi/Tasks/NotificationOrder` |
| `GET /baseApi/Tasks/NotificationPrepaid` |
| `GET /baseApi/Tasks/NotificationPayment` |
| `GET /baseApi/Tasks/KbankEnquiry` |
| `GET /baseApi/Tasks/KbankEnquiry/{transaction_id}` |
| `GET /baseApi/Tasks/JobDowngrades` |
| `POST /baseApi/Tasks/TestJobDowngrade` |
| `GET /baseApi/Tasks/JobAlertBeforeDowngrades` |
| `GET /baseApi/Tasks/JobAlertPromoExpired` |
| `GET /baseApi/Tasks/JobAlertPromoReferral` |
| `GET /baseApi/Tasks/JobResetGradingEndYear` |
| `GET /baseApi/Tasks/NotificationRegister` |
| `GET /baseApi/Tasks/NotificationCartOrder` |

---

### `baseApi/Upload/*` — **No callers found**

| Endpoint |
|----------|
| `POST /baseApi/Upload/UploadSlip` |

---

### `baseApi/Users/*`

| Endpoint | Caller | File |
|----------|--------|------|
| `POST /baseApi/Users/Register` | **No caller found** | — |
| `POST /baseApi/Users/RegisterJulian` | oms-julian, automate-testing | Frontend registration flow |
| `GET /baseApi/Users/ValidateEmail` | portal-web, oms-julian, automate-testing | `apps/oms-web/.../verify-email.ts` |
| `POST /baseApi/Users/ValidateIdentitiesNumber` | **No caller found** | — |
| `GET /baseApi/Users/ValidatePhone` | **No caller found** | — |
| `GET /baseApi/Users/ForgotPassword` | **No caller found** | — |
| `POST /baseApi/Users/UpdateNotiToken` | **No caller found** | — |
| `GET /baseApi/Users/UserAuth` | **No caller found** | — |
| `POST /baseApi/Users/UpdateSetting` | **No caller found** | — |
| `POST /baseApi/Users/UserChangePassword` | **No caller found** | — |
| `POST /baseApi/Users/RequestOtp` | oms-julian, fkt-iac-config (Kong route) | `useSendOtp.ts` |
| `POST /baseApi/Users/CheckOtp` | **No caller found** | — |
| `POST /baseApi/Users/UpdateSubDistrict` | **No caller found** | — |
| `GET /baseApi/Users/ForgotEmail` | **No caller found** | — |
| `GET /baseApi/Users/UpdateUseBasket` | **No caller found** | — |
| `POST /baseApi/Users/QAGetOTP` | **No caller found** | QA/test only |
| `POST /baseApi/Users/QAClearOTP` | **No caller found** | QA/test only |
| `POST /baseApi/Users/SavePrivacyPolicy` | **No caller found** | — |
| `POST /baseApi/Users/SaveRestoreId` | **No caller found** | — |
| `POST /baseApi/Users/SaveDeliveryAddress` | **No caller found** | — |
| `POST /baseApi/Users/SaveBillingAddress` | **No caller found** | — |
| `GET /baseApi/Users/GetListDeliveryAddress` | **No caller found** | — |
| `GET /baseApi/Users/GetDeliveryAddressById` | **No caller found** | — |
| `POST /baseApi/Users/AddDeliveryAddress` | **No caller found** | — |
| `POST /baseApi/Users/SaveNotifyStatus` | **No caller found** | — |
| `POST /baseApi/Users/UpdateDeliveryAddress` | **No caller found** | — |
| `POST /baseApi/Users/DeleteDeliveryAddress` | **No caller found** | — |
| `POST /baseApi/Users/SetDefaultDeliveryAddress` | **No caller found** | — |
| `POST /baseApi/Users/SaveTaxInvoice` | **No caller found** | — |
| `POST /baseApi/Users/SavePolicy` | **No caller found** | — |
| `GET /baseApi/Users/CustomMessage` | oms-julian, oms-monorepo | Mock handlers + shared lib |

---

## Migration Readiness Assessment

### Safe to decommission (no callers, superseded by new services)
| Controller / Endpoints | Superseded By |
|-----------------------|--------------|
| `baseApi/Banner/*` (2) | oms-services-content |
| `baseApi/MarketPlace/*` (11) | oms-services-product |
| `baseApi/Products/*` (4) | oms-services-product |
| `baseApi/Promotions/*` (4) | oms-services-nestjs/promotion |
| `baseApi/Page/*` (1) | oms-services-content |
| `baseApi/OmisePayment/*` (non-webhook, 6) | oms-service-payment |
| `baseApi/Payment2C2P/Pay`, `CreateTransactionId` (2) | oms-service-payment |

### Requires migration before decommission
| Endpoint | Current Caller | Migration Target |
|----------|---------------|-----------------|
| `POST api/authorize/intranet` | oms-services-order, oms-promotion-workers, cms-services-kyc-workflow | Build buyer-auth API in oms-services-order or cms-services-customer |
| `POST baseApi/Payments/Paid` | oms-services-nestjs/orderadapter | Migrate to oms-service-payment API |
| `baseApi/Invoice/CreateInvoice(s)` | scm-intranet-web | Migrate scm-intranet-web to billing service |
| `baseApi/Payments/CreateReceiveInvoiceFromPayment` | scm-intranet-web | Migrate scm-intranet-web to billing service |
| `baseApi/Notification/SendNotificationRedeem` | scm-intranet-web | Migrate to oms-services-nestjs/notification |
| `baseApi/Users/ValidateEmail` | portal-web | Migrate to oms-services-nestjs/auth or new user service |
| `baseApi/Users/RegisterJulian` | oms-julian | Migrate to oms-services-nestjs/auth or new user service |
| `baseApi/Users/RequestOtp` | oms-julian | Migrate to oms-services-nestjs/otp |
| `baseApi/Users/CustomMessage` | oms-julian, oms-monorepo | Migrate to appropriate service |

### Unknown — may have callers in unindexed systems
| Endpoint | Reason |
|----------|--------|
| `baseApi/OmisePayment/PayWith*`, `CreateCharge` | Mobile app (`oms-mobile-app`) not deeply indexed |
| `baseApi/Masters/*` | Mobile app may call these |
| `baseApi/Tasks/*` | Likely cron-triggered — scheduler config not found |
| `baseApi/ForSupport/*` | May be called via direct browser/Postman by ops team |
