# portal-web

## Responsibility
Frontend monorepo containing all customer-facing and internal web applications for the Freshket platform. Built with React, Next.js, and managed by Nx. Each app targets a distinct business domain.

## Owns
- All web frontend applications
- BFF (Backend-for-Frontend) layers for select domains
- Shared frontend libraries and design system

## Does NOT Own
- Business logic (→ respective backend services)
- Data persistence (→ backend services)

## Apps

| App | Purpose | Audience |
|-----|---------|---------|
| **oms-web** | Order Management — customer orders, cart, catalog browse | Customers (B2B buyers) |
| **lms-web** | Logistics Management — delivery tracking, routing | Logistics staff |
| **wms-web** | Warehouse Management — inventory, stock picking | Warehouse staff |
| **mc-web** | Merchant / Marketplace portal | Merchants/suppliers |
| **cs-web** | Customer Service portal — support tickets, customer lookup | CS agents |
| **billing-web** | Billing and invoice portal | Finance/customers |
| **scn-web** | Supply Chain Network portal | SCM team |
| **mc-bff** | BFF for mc-web | Internal |
| **billing-bff** | BFF for billing-web | Internal |
| **cs-bff** | BFF for cs-web | Internal |
| **core-web** | Core platform shared UI components | Internal |

## Stack
- React 18.2 — UI framework
- Next.js 14.2 — SSR/SSG framework
- TypeScript — language
- Nx 22.2.3 — monorepo build orchestration
- pnpm 8.8.0+ — package manager
- tRPC — type-safe BFF ↔ web communication
- TanStack React Query — server state management
- MUI (Material UI) — component library
- Zod / Yup — validation
- Axios — HTTP client
- React Hook Form — form management
- Zustand — global state (via Julian oms-web)
- NextAuth — authentication
- AWS SDK (S3) — file uploads

## Backend API Connections
| Env Var | Target Service |
|---------|---------------|
| `NEXT_PUBLIC_OMS_SERVICE_HOST` | oms-services-order |
| `NEXT_PUBLIC_AUTH_SERVICE_HOST` | oms-services-nestjs/authorizer |
| `NEXT_PUBLIC_CRM_API_HOST` | crm-api |
| `NEXT_PUBLIC_PUBLIC_API_HOST` | Public API gateway |
| `LEGACY_API_HOST` | oms-api (legacy .NET) |

## Shared Libraries (npm packages)
| Package | Purpose |
|---------|---------|
| `@freshket/oms-shared-config` | Shared configuration constants |
| `@freshket/oms-shared-data-access-auth` | Auth data access layer |
| `@freshket/oms-shared-util` | Shared utilities |
| `@freshket/oms-web-next-auth-config` | NextAuth configuration |
| `@freshket/react-feature-flags` | GrowthBook React integration |
| `@freshket/ts-utilities` | TypeScript utilities |

## Observability
- DataDog RUM — real-user monitoring
- Pino — structured logging
- OpenTelemetry — distributed tracing

## Important Files
| File | Purpose |
|------|---------|
| `package.json` | Root dependencies |
| `pnpm-workspace.yaml` | pnpm workspace config |
| `nx.json` | Nx configuration |
| `apps/oms-web/` | Main customer-facing OMS portal |
| `apps/mc-bff/` | Merchant BFF |
| `apps/billing-bff/` | Billing BFF |
| `apps/cs-bff/` | Customer Service BFF |
| `.github/workflows/pr.yml` | PR CI (lint, test, type-check via Nx Cloud) |

## CI/CD
- PR checks: Nx Cloud — format, lint, test, type-check
- Node: v20.19.0
- pnpm: v9.12.0

## Commands
```bash
pnpm install
pnpm run oms          # start oms-web dev server
pnpm run build        # build all apps
pnpm test             # run all tests
pnpm run lint
pnpm run format
```

## Main Flows
1. **Order Flow**: Customer browses catalog (oms-web) → adds to cart → checkout → payment
2. **Merchant Flow**: Supplier manages products/inventory (mc-web) → via mc-bff
3. **CS Flow**: Agent looks up customer → views orders → resolves tickets (cs-web → cs-bff)
4. **Billing Flow**: Finance views invoices → downloads PDFs (billing-web → billing-bff)
5. **Auth Flow**: NextAuth → oms-services-nestjs/authorizer → JWT stored in session

## Risks
- **BFF inconsistency**: Only mc-web, billing-web, cs-web have BFFs — other apps call backends directly
- **Multiple HTTP patterns**: tRPC (BFF), Axios (direct), React Query — inconsistent across apps
- **Large monorepo**: 11 apps in Nx — build times can grow without proper caching

## Suggested Improvements
- Standardize HTTP pattern across all apps (prefer tRPC BFF or centralize direct calls)
- Add BFFs for remaining apps (oms-web, lms-web, wms-web) for consistent API contract
- Document which backend APIs each frontend app calls
