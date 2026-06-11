# oms-julian

## Responsibility
Customer-facing marketplace frontend for Freshket OMS. Next.js 12 application (Pages Router) with TypeScript. Provides the primary B2B food ordering experience: product browsing, cart, order placement, and order tracking.

## Owns
- Customer-facing marketplace UI (product search, cart, checkout)
- Order history and status views
- Customer profile and KYC UI
- Feature-flag-driven A/B tested experiences

## Does NOT Own
- Any backend business logic (pure frontend)
- Auth token issuance (→ oms-services-nestjs/authorizer)

## Tech Stack
- Framework: Next.js 12.1.6 (Pages Router), React 17, TypeScript
- UI: Material-UI v4 + JSS (CSS-in-JS)
- State: Zustand (global UI) + React Context (feature state) + React Query (server state)
- Auth: NextAuth 4
- Forms: React Hook Form + Yup/Zod
- i18n: next-i18next (Thai `th` + English `en`)
- Search: Algolia
- Feature flags: @freshket/react-feature-flags + GrowthBook

## Backend Services Called
| Env Var | Target Service |
|---------|---------------|
| `NEXT_PUBLIC_OMS_SERVICE_HOST` | Main OMS API (oms-services-order, product) |
| `NEXT_PUBLIC_AUTH_SERVICE_HOST` | oms-services-nestjs/authorizer |
| `NEXT_PUBLIC_CRM_API_HOST` | crm-api |
| `NEXT_PUBLIC_PUBLIC_API_HOST` | Public endpoints |
| `LEGACY_API_HOST` | oms-api (legacy) |

## Commands
```bash
yarn dev              # Start dev server (.env.development.local)
yarn dev:uat          # Start dev server (.env.uat.local)
yarn build            # Production build
yarn test             # Jest tests (no watch)
yarn check-type       # TypeScript check
yarn lint             # ESLint
```

## Directory Structure
```
pages/          # Next.js routes (thin wrappers)
src/
  features/     # Feature-based modules (primary code)
  components/   # Shared UI components
  hooks/        # Shared custom hooks
  zustand/      # Global Zustand stores
  contexts/     # Shared React Contexts
  utils/        # Utility functions
  libs/         # Third-party integrations (GTM, Algolia, Omise)
  types/        # Shared TypeScript types
  theme/        # MUI themes (LIGHT, ONE_DARK, UNICORN)
```

## Feature Module Pattern
Each `src/features/<name>/` contains: `api/`, `components/`, `store/`, `context/`, `hooks/`, `types/`, `utils/`

## Environments
`.env.development.local`, `.env.uat.local`, `.env.production.local`, `.env.staging.local`

## External Integrations
- Google Tag Manager (`GTM_ID`)
- Algolia search (`NEXT_PUBLIC_ALGOLIA_*`)
- GrowthBook feature flags (`NEXT_PUBLIC_GROWTHBOOK_*`)
- AWS AppConfig (`APP_CONFIG_APP_IDENTIFIER=oms`)
- Cloudflare Turnstile CAPTCHA (`TURNSTILE_*`)
- Omise (payment UI via `src/libs/`)

## Notes
- Version 2.9.0 — actively maintained marketplace frontend
- API mocking via MSW (`API_MOCKING=enabled`) for local dev without backend
- `LEGACY_API_HOST` still referenced — some flows call oms-api directly from frontend
