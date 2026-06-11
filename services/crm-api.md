# crm-api

## Responsibility
CRM backend API service. Manages CRM backoffice operations: accounts, leads, restaurants, messaging (LINE), Salesforce integration, Elasticsearch-backed search, and background job queues.

## Owns
- Account management (B2B customer accounts)
- Lead management (backoffice)
- Restaurant/vendor data management
- LINE messaging integration
- Salesforce data bidirectional sync
- CRM search (Elasticsearch)
- File management
- CRM settings

## Does NOT Own
- Customer-facing profile (→ cms-services-customer)
- Customer acquisition lead flow (→ crm-customer-services)
- Order data (→ oms-services-order)

## APIs
No OpenAPI spec found. NestJS REST modules.

Modules in `src/modules/`:
- `account/` — Account CRUD
- `auth/` — Authentication (JWT strategy)
- `cs/` — Customer support
- `database/` — DB connection management
- `elasticsearch/` — Search integration
- `event/` — Event management
- `files/` — File handling
- `lead/` — Lead management
- `line/` — LINE messaging
- `message/` — Messaging service
- `queues/` — Bull job queues
- `restaurant/` — Restaurant/vendor data
- `salesforce/` — Salesforce sync
- `setting/` — CRM configuration

Auth: JWT Bearer token (NestJS JWT strategy)

## Events Published
| Topic | Trigger | Confidence |
|-------|---------|-----------|
| `crm.user.registered` | New user registered | Confirmed |
| `crm.customer` | Customer data updated | Likely |

## Events Consumed
Not detected.

## Database Ownership
- **MSSQL** (`freshket-dev-mssql.*`) — legacy CRM data
- **Firebase** (Realtime Database) — messaging state

## Dependencies

### Internal Services
None explicitly detected (acts as a standalone CRM backend).

## External Integrations
- **Salesforce** (`SALESFORCE_HOST`) — jsforce SDK for bidirectional CRM sync
- **Firebase Admin** — FCM push notifications, Firebase Realtime Database
- **LINE Bot SDK** — LINE messaging
- **Elasticsearch** — CRM search backend
- **Bull** — Job queue (Redis-backed)
- **ELK Stack** — Log aggregation (`ELK_NODE`, `ELK_USERNAME`, `ELK_PASSWORD`)
- **Sentry** — Error tracking (`SENTRY_DSN`)

## Important Files
| File | Purpose |
|------|---------|
| `src/modules/account/` | Account domain |
| `src/modules/lead/` | Lead management |
| `src/modules/salesforce/` | Salesforce integration |
| `src/modules/line/` | LINE messaging |
| `src/modules/queues/` | Bull job queues |
| `src/modules/elasticsearch/` | Search integration |
| `src/modules/auth/jwt.strategy.ts` | JWT auth strategy |
| `.env.example` | Environment variable reference |
| `package.json` | Dependencies (NestJS 7) |

## Feature Flags
Not detected.

## Main Flows
1. **User Registration**: New user → publish `crm.user.registered` → cms-services-customer picks up
2. **Lead Management**: Sales staff manage leads via backoffice UI → optional Salesforce sync
3. **Salesforce Sync**: Bidirectional: pull Salesforce data → store in CRM; push CRM updates → Salesforce
4. **LINE Messaging**: Customer service sends LINE messages via LINE Bot SDK
5. **Background Jobs**: Bull queues for async operations (email, sync, notifications)
6. **CRM Search**: Elasticsearch powers account/lead search in backoffice

## Risks
- **Old NestJS version**: NestJS 7 (vs 8 in oms-services-nestjs) — potential security/compatibility drift
- **MSSQL primary**: Legacy SQL Server as primary DB — not aligned with MySQL-primary Go services
- **No OpenAPI spec**: No machine-readable contract
- **ELK + Sentry**: Separate observability stack from other services (which use Zap/Winston)

## Suggested Improvements
- Upgrade NestJS to v8+ for consistency with oms-services-nestjs
- Add OpenAPI spec
- Migrate from MSSQL to MySQL for consistency
- Align observability tooling with rest of platform
