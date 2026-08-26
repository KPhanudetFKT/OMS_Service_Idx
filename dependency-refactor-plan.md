# Refactor Plan — Order · Product · Payment · Content Dependency Hotspots

**Companion to:** `docs/ai/dependency-graph.html` (per-endpoint dependency graph, code-verified June 2026).
**Scope:** synchronous request fan-out across `oms-services-order`, `oms-services-product`, `oms-service-payment`, `oms-services-content` and their 1st/2nd-hop dependencies.
**Goal:** reduce tail latency, blast radius and legacy coupling on the hot request paths — ordered by impact-to-effort.

> This is a planning document, not a committed roadmap. Each item lists the evidence (file refs from the trace), the proposed change, and the risk. Validate file:line refs before starting — a few `order_service.go` line numbers in the source trace were approximate.

---

## Priority tiers at a glance

| # | Hotspot | Problem | Effort | Risk | Impact |
|---|---------|---------|--------|------|--------|
| 1 | `POST /bulk-orders` GENERAL path | Serial HTTP self-calls, N× full create fan-out | M | M | High |
| 2 | `POST /orders` / `/resources/orders` | 6–8 sequential cross-service calls | M | M | High |
| 3 | Content N+1s (`/posts/:guid/brands`, `/pages/:slug`) | One product call per brand / per post | S–M | L | High |
| 4 | Missing resilience (timeouts, retries, breakers) | No circuit breaker on `thirdparty/` clients | M | L | High |
| 5 | Payment charge external-gateway blocking | Gateway round-trip on request thread | M | M | Med |
| 6 | order↔product↔promotion cross-cluster | Shared latency surface, near-cycle | M | M | Med |
| 7 | Legacy MSSQL convergence | 4 services read it directly; decommission risk | L (long) | H | Strategic |
| 8 | Smaller per-item loops | `skus/bulks`, `GET /orders` LMS, rebate v2 | S | L | Med |

---

## 1. `POST /bulk-orders` (Provider=GENERAL) — eliminate the serial HTTP self-call

**Problem.** `CreateGeneralOrders` (`oms-services-order/pkg/bulkorder/service.go:135`) loops `orderApiClient.CreateResourceOrder` — an HTTP `POST resources/orders` back to **this same service** (`APP_ORDERDSN`) — **once per order, serially**. Each self-call re-enters the full `CreateResourceOrder` fan-out (product ×2–3, orderadapter ×3, customer, promotion). Effective cost ≈ `N × (1 self-HTTP round-trip + ~8 downstream calls)`, all sequential, fail-fast. There is an in-code `// TODO: [Refactor] ... calls our own API for each order, which is an antipattern` at `service.go:131`.

**Why it matters.** Worst latency profile in the platform; the HTTP self-hop adds serialization + JSON marshalling + auth overhead on top of the already-heavy create path, multiplied by batch size.

**Proposed approach (incremental):**
1. **Stop crossing the network.** Replace `orderApiClient.CreateResourceOrder` with a direct in-process call to the same service method the HTTP handler invokes. Extract a shared `createResourceOrder(ctx, payload)` used by both the HTTP handler and the bulk loop. Removes marshalling + auth + a network hop per order.
2. **Batch the shared lookups.** The default bulk path already fans out product (chunk 20 / conc 50) and orderadapter buyers (chunk 10) in parallel via `errgroup` — reuse that pattern so SKU/buyer/seller data is fetched **once for the whole batch**, not per order.
3. **Parallelize independent orders** with a bounded `errgroup` (cap concurrency to protect downstreams), and switch fail-fast to **per-order result collection** so one bad order doesn't skip the rest.

**Risk.** Medium — `CreateResourceOrder` has side effects (quota decrement, events, MSSQL writes). Extract carefully; keep the event-emission and quota semantics identical. Add a batch integration test asserting per-order success/failure independence.

---

## 2. `POST /orders` & `POST /resources/orders` — parallelize the create fan-out

**Problem.** Order placement makes ~6–8 **sequential** cross-service calls: product pricing → orderadapter buyer/seller/items (×3) → customer credit-limit → promotion validate → product quota decrement, plus legacy MSSQL + `fk-web-host` buyer-authorize on the resource path. Most are independent reads run one-after-another (`oms-services-order/pkg/order/order_service.go`, create pipeline).

**Proposed approach:**
1. **Group independent reads into one `errgroup`** — product SKU/price, orderadapter buyer+seller+items, and customer credit-limit have no ordering dependency and can run concurrently. This alone collapses ~5 serial round-trips into 1 wall-clock slot.
2. Keep **ordering only where a real data dependency exists** (e.g. promotion validate needs priced cart; quota decrement after validation).
3. Apply per-call **context timeouts** so the slowest dependency bounds latency instead of the sum.

**Risk.** Medium — verify none of the "reads" mutate state or depend on each other's output. Promotion and quota steps stay sequential.

---

## 3. Content N+1s — bound the per-item product fan-out

**Problem A — `GET /posts/:guid/brands`** (`oms-services-content/pkg/brand/db/brand_repository_v2.go:19,60`): spawns **one goroutine + one product API call per brand**, unbounded by brand count.
**Problem B — `GET /pages/:slug`** (`pkg/page/db/page_repository_v2.go:212-234`): **sequential** `FindOneByGUID` per layout post.

**Proposed approach:**
- **Brands:** collect all seller-SKU IDs across brands first, issue a **single batched** product call (the `thirdparty/productapi` client already chunks at 40 and runs chunks concurrently), then fan the results back to each brand in memory. Turns N calls into ⌈total/40⌉.
- **Pages:** batch the post reads (`FindManyByGUIDs`) instead of looping `FindOneByGUID`; enrich in one pass.
- Add a **concurrency cap** (`errgroup.SetLimit`) on any remaining per-item goroutines so a content page can't open unbounded connections to product.

**Risk.** Low — read-only enrichment; errors here are already logged-and-swallowed (degrade, not 5xx). Keep that degradation behavior.

---

## 4. Resilience: timeouts, retries, circuit breakers on `thirdparty/` clients

**Problem.** The service docs flag "no circuit breaker / retry for thirdparty HTTP calls." With order placement depending on 8+ services synchronously, a single slow dependency stalls the whole request thread; a hard-down dependency cascades.

**Proposed approach:**
1. Standardize a **shared HTTP client wrapper** across all `thirdparty/*` clients (order, product, payment, content) with: per-call context timeout, bounded retries with backoff on idempotent GETs only, and a **circuit breaker** (e.g. sony/gobreaker) per downstream.
2. Classify each dependency as **hard** (fail the request: product pricing, customer credit) vs **soft** (degrade: LMS tracking on `GET /orders`, content enrichment). Soft deps should fail-open, not block.
3. Emit breaker-open metrics to the existing Slack/alerting path.

**Risk.** Low–medium — retries on non-idempotent POSTs are dangerous (double charge / double order). Restrict retries to GETs; make POST paths idempotent (idempotency key) before retrying them.

---

## 5. Payment charge — decouple from the external gateway round-trip

**Problem.** `POST /payments/charges` and `/public/payments/webhook/:provider` block on a **synchronous external gateway** call (Omise / TTB / KTB / KBank) on the request thread (`oms-service-payment/internal/charge/service.go`). Request latency tracks the slowest provider; provider outage = endpoint outage.

**Proposed approach:**
- Enforce strict **per-provider timeouts** and a circuit breaker per gateway (item 4).
- For async-capable providers, lean on the **webhook confirmation path** rather than long-polling inquiry-back inline; the event (`payment.transaction`) already publishes fire-and-forget via `errgroup`.
- Surface provider health so the frontend can fail fast / offer alternates.

**Risk.** Medium — payment correctness is critical. No change to the money path semantics; only timeout/breaker/observability hardening. Coordinate with the payments team before touching charge state transitions.

---

## 6. order ↔ product ↔ promotion cross-cluster

**Problem.** product enriches SKUs by calling promotion (`FindManyBySellerSkuIDs`, batched/50, gated by `ENABLED_PROMOTION_API`); promotion validation calls back into product `/skus` (`oms-services-nestjs/apps/promotion/.../product.api.ts:24`). Not an infinite cycle (different operations), but order→product and order→promotion on the same request both touch this pair → shared, amplified latency surface.

**Proposed approach:**
- Confirm promotion-during-validation actually needs a **live** product call vs. data already in the priced cart passed from order — if order already has SKU/price context, pass it through to avoid the product re-fetch.
- Cache promotion-label / promotion-applicability lookups with a short TTL where correctness allows.
- Keep the `ENABLED_PROMOTION_API` gate; treat promotion enrichment as **soft** (degrade to no-promo display rather than failing the SKU list).

**Risk.** Medium — promotion correctness (pricing) is user-visible. Validate cache TTLs against promo start/end edges.

---

## 7. Legacy MSSQL convergence — strategic decommission

**Problem.** order, payment, orderadapter **and** customer all read the legacy MSSQL DB **directly** (in-process GORM / ACL layers, not via a service boundary). It's the single most depended-on resource in this slice and the stated decommission target. Direct multi-service DB coupling means schema changes have an invisible, cross-service blast radius.

**Proposed approach (long-horizon, track separately):**
- Inventory every direct MSSQL read per service (the trace lists: order restaurant/PVP/invoices; payment invoices/receipts/CN; orderadapter buyer/seller/items; customer `inv`/`po` for credit).
- Move each behind the **owning modern service's API** (e.g. restaurant/buyer data → orderadapter or customer; invoices → billing) so only one service owns each table.
- Use the existing `freshket-oms-migration` / `freshket-legacy-migration` playbooks; sequence by read-only-first, lowest-coupling-first.

**Risk.** High and broad — this is a program, not a PR. Listed here for visibility; do not bundle with items 1–6.

---

## 8. Smaller per-item loops (quick wins)

| Endpoint | Loop | Fix |
|---|---|---|
| `PATCH /resources/orders/:guid/skus/bulks` | `FindOneResourceByGUID` per SKU | batch into one `FindManyResources` call |
| `GET /orders` | LMS `GetDeliveryTrackingInfo` per order (soft-fail) | batch the tracking lookup, or load lazily on detail only |
| `GET /orders/rebate-programs/v2` | legacy invoice lookup per program | batch the MSSQL invoice query |
| `POST /resources/skus/labels` (product) | `AddLabel` write per SKU | bulk insert |
| `POST /admin/rebate/rewards` (order) | payment `GrantCoins` per buyer | confirm if a batch grant API exists; else cap concurrency |

**Risk.** Low — mechanical batching of reads/writes. Verify ordering isn't relied upon.

---

## Sequencing recommendation

1. **Quick wins first** (item 8 + item 3) — low risk, immediate latency relief, build batching patterns.
2. **Resilience layer** (item 4) — unlocks safe parallelization and protects everything else.
3. **Hot-path parallelization** (items 1, 2) — the biggest latency wins, now safe behind timeouts/breakers.
4. **Payment + promotion hardening** (items 5, 6) — higher coordination cost.
5. **MSSQL decommission** (item 7) — separate program, ongoing.

## Cross-cutting notes
- Follow the platform rule: every I/O function takes `context.Context` first; use `context.WithoutCancel` for fire-and-forget goroutines to preserve trace IDs.
- Gate risky changes behind GrowthBook flags (already used for rebate/promo rollouts).
- **Out-of-workspace boundaries:** billing/finance and LMS/fulfillment repos were not available for this trace — confirm their fan-out before relying on items 4/5/8 assumptions about them.
