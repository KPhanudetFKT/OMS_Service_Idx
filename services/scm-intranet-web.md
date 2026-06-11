# scm-intranet-web

## Responsibility
Internal intranet portal for Supply Chain Management operations. Legacy PHP-based system used by SCM team for day-to-day supply chain operations.

## Owns
- SCM internal operations UI
- ~190 SCM action modules
- ~75 scheduled cron jobs

## Does NOT Own
- Customer-facing features (→ portal-web)
- Product catalog (→ oms-services-product)
- Order management (→ oms-services-order)

## APIs
No REST API detected. Server-side rendered PHP (traditional web app, not a microservice).

## Events Published / Consumed
None detected.

## Database Ownership
Database configuration in `config.php`. Specific DB/schema not confirmed from available inspection. Inferred: MySQL or MSSQL (legacy pattern). Confidence: Inferred.

## Dependencies
None detected (self-contained legacy app).

## External Integrations
None confirmed.

## Important Files
| File | Purpose |
|------|---------|
| `index.php` | Main entry point |
| `login.php` | Authentication page |
| `config.php` | Configuration |
| `lib/function.php` | Core PHP functions |
| `action/` | ~190 feature modules |
| `cronjob/` | ~75 scheduled tasks |
| `templates/` | HTML templates |
| `assets/` | JS, CSS, images |

## Feature Flags
None.

## Main Flows
1. SCM staff log in via `login.php`
2. Navigate to feature modules in `action/`
3. Cron jobs in `cronjob/` run scheduled SCM operations

## Risks
- **Legacy PHP**: No modern framework — custom implementation, high maintenance risk
- **No API contracts**: Cannot be called by other services in a structured way
- **No documentation**: Purpose of 190 action modules is undocumented
- **Separate technology stack**: PHP vs Go/NestJS — separate operational concern

## Suggested Improvements
- Document the purpose of each major action module
- Consider migration path to portal-web (React/Next.js) for consistency
- Identify which cron jobs could be moved to a managed scheduler
