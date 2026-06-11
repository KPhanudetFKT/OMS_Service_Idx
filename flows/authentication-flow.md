# Authentication Flow

## Overview
Three distinct authentication patterns used across the platform: customer JWT, staff JWT (JWKS), and internal service-to-service HMAC authentication.

## Authentication Types

### 1. Customer Authentication (JWT)

```mermaid
sequenceDiagram
    participant C as Customer (oms-web)
    participant NEXTAUTH as NextAuth (portal-web)
    participant AUTH as nestjs/authorizer (Lambda)
    participant API as Go Service (e.g., oms-services-order)

    C->>NEXTAUTH: Login (credentials)
    NEXTAUTH->>AUTH: Validate credentials → issue JWT
    AUTH-->>NEXTAUTH: JWT token
    NEXTAUTH-->>C: Session with JWT

    C->>API: Request (Authorization: Bearer <jwt>)
    API->>API: Validate JWT in authorized.go middleware
    API-->>C: Response
```

**Implementation:**
- Middleware: `oms-services-order/http/middleware/authorized.go`
- Token format: Bearer JWT
- Validator: Lambda custom authorizer (`oms-services-nestjs/apps/authorizer/`)
- Frontend: NextAuth (`@freshket/oms-web-next-auth-config`)

---

### 2. Staff Authentication (JWKS)

```mermaid
sequenceDiagram
    participant STAFF as Staff (backoffice portal)
    participant STAFF_AUTH as nestjs/authorizer-staff (Lambda)
    participant API as Go Service (admin endpoints)

    STAFF->>STAFF_AUTH: Login → JWT with staff claims
    STAFF_AUTH-->>STAFF: JWT (JWKS-signed)

    STAFF->>API: Request (Authorization: Bearer <staff-jwt>)
    API->>API: Validate via JWKS in authorized_staff.go
    API-->>STAFF: Response (admin routes only)
```

**Implementation:**
- Middleware: `oms-services-order/http/middleware/authorized_staff.go`
- JWKS endpoint: configured in staff authorizer Lambda
- Lambda: `oms-services-nestjs/apps/authorizer-staff/`

---

### 3. Internal Service-to-Service Authentication

```mermaid
sequenceDiagram
    participant SVC_A as Calling Service (e.g., oms-services-order)
    participant SVC_B as Target Service (e.g., cms-services-customer)

    SVC_A->>SVC_A: Sign request with HMAC (APP_HMACSECRET)
    SVC_A->>SVC_B: Request (X-API-Key + HMAC signature)
    SVC_B->>SVC_B: Validate in authorized_internal.go
    SVC_B-->>SVC_A: Response
```

**Implementation:**
- Middleware: `oms-services-order/http/middleware/authorized_internal.go`
- Header: `X-API-Key`
- Signing: HMAC with shared secret (`APP_HMACSECRET`)
- Used for: service-to-service calls on internal endpoints

---

### 4. Lambda API Gateway Authorization

```mermaid
sequenceDiagram
    participant C as Client
    participant APIGW as API Gateway
    participant LAMBDA_AUTH as Authorizer Lambda
    participant LAMBDA_SVC as Service Lambda (e.g., promotion)

    C->>APIGW: Request with token
    APIGW->>LAMBDA_AUTH: Authorize request
    LAMBDA_AUTH->>LAMBDA_AUTH: Validate token
    LAMBDA_AUTH-->>APIGW: IAM Allow/Deny policy
    APIGW->>LAMBDA_SVC: Forward if allowed
    LAMBDA_SVC-->>C: Response
```

**Implementation:**
- Customer authorizer: `oms-services-nestjs/apps/authorizer/`
- Staff authorizer: `oms-services-nestjs/apps/authorizer-staff/`
- Internal authorizer: `oms-services-nestjs/apps/authorizer-internal/`
- Configured in: `serverless-internal.yml`, `serverless-external.yml`

---

## Auth Configuration Summary

| Pattern | Header | Middleware File | Config |
|---------|--------|----------------|--------|
| Customer JWT | `Authorization: Bearer <token>` | `http/middleware/authorized.go` | JWT secret in env |
| Staff JWT (JWKS) | `Authorization: Bearer <token>` | `http/middleware/authorized_staff.go` | JWKS endpoint in env |
| Internal HMAC | `X-API-Key` | `http/middleware/authorized_internal.go` | `APP_HMACSECRET` |
| Lambda auth | API Gateway event | `apps/authorizer*/` (NestJS Lambda) | Serverless config |

## Files to Modify for Auth Changes

| Change | Primary File(s) |
|--------|----------------|
| Customer JWT validation logic | `oms-services-order/http/middleware/authorized.go` (pattern repeated per service) |
| Staff JWT / JWKS changes | `oms-services-nestjs/apps/authorizer-staff/` |
| Internal auth secret rotation | All services' `APP_HMACSECRET` env var |
| New authorizer Lambda | `oms-services-nestjs/apps/` + `serverless-*.yml` |
| Frontend auth config | `portal-web` `@freshket/oms-web-next-auth-config` |
| Feature flag per auth method | GrowthBook SDK in each service |

## Risks

- **Repeated middleware**: Each Go service has its own copy of auth middleware — changes must be applied to all services consistently
- **HMAC secret management**: Shared secret across all service-to-service calls — rotation requires coordinated deployment
