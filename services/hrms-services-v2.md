# hrms-services-v2

## Responsibility
Human Resource Management System (HRMS). Manages staff/employee data. Referenced by multiple other services for staff information lookups.

## Owns
- Staff / employee records
- HR operations

## Does NOT Own
- Customer data (→ cms-services-customer)
- Order management (→ oms-services-order)

## APIs
Confidence: Inferred. Multiple services reference `APP_HRMSURL` or `APP_HRMSDSN` — this is the HTTP API they call.

## Events Published / Consumed
None confirmed. Confidence: Unknown.

## Database Ownership
Not confirmed from available inspection. Confidence: Unknown.

## Dependencies
None confirmed.

## Important Files
Not explored in detail. Directory exists at `~/projects/hrms-services-v2/` (repo: `hrms-services-v2`).

## Services That Depend on HRMS
| Service | Env Var | Usage |
|---------|---------|-------|
| oms-services-order | `APP_HRMSURL` | Staff info lookup |
| oms-services-product | `APP_HRMSDSN` | Staff info |
| oms-services-content | `APP_HRMSDSN` | Staff info |
| oms-service-payment | `APP_HRMSURL` | Staff info |
| cms-services-customer | `HRMS_HOST` | Staff info |

## Risks
- **Underdocumented**: This service is not well-explored — details are Inferred from dependent services
- **High fan-in**: 5+ services depend on HRMS — if it goes down, multiple services are impacted

## Suggested Improvements
- Document HRMS API endpoints and auth requirements
- Add OpenAPI spec
- Consider adding circuit breaker in dependent services
- Explore this service's CLAUDE.md or README for more details
