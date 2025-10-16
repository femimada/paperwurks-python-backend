# Identity Module - User Stories

## Module Overview

The Identity module represents the core principal (person or service account) in the Paperwurks IAM system. It manages user authentication, lifecycle, and serves as the primary entity for all permission checks.

**Sprint:** Sprint 1A (Week 3-4)  
**Priority:** P0 - Critical  
**Dependencies:** None (foundational module)

## Module Responsibilities

- User registration and account creation
- Authentication (login/logout)
- JWT token generation and validation
- Password management (hashing, reset, change)
- Email verification
- Multi-factor authentication (MFA) setup
- Account lifecycle management (activation, deactivation)
- Audit logging for authentication events

## Core User Stories

### US-006: User Registration

**As a** new user  
**I want to** register an account  
**So that** I can access the Paperwurks platform

**Priority:** P0  
**Story Points:** 5  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] User can register with email, password, first name, last name
- [ ] Email must be unique across the system
- [ ] Password must meet security requirements (min 8 chars, uppercase, lowercase, number, special char)
- [ ] Password is hashed using bcrypt before storage
- [ ] User account is created in inactive state pending email verification
- [ ] Verification email is sent to user's email address
- [ ] User receives confirmation of successful registration
- [ ] Audit log entry created for registration event
- [ ] Registration fails gracefully with clear error messages

#### Technical Specifications

**Model Fields:**

```python
Identity:
    - id: UUID (primary key)
    - email: EmailField (unique, indexed)
    - password_hash: CharField(128)
    - first_name: CharField(50)
    - last_name: CharField(50)
    - entity_id: ForeignKey(Entity, null=True)
    - is_active: BooleanField(default=False)
    - is_verified: BooleanField(default=False)
    - mfa_enabled: BooleanField(default=False)
    - verification_token: CharField(64, null=True)
    - verification_token_expires: DateTimeField(null=True)
    - last_login: DateTimeField(null=True)
    - created_at: DateTimeField(auto_now_add=True)
    - updated_at: DateTimeField(auto_now=True)
```

**API Endpoint:**

```
POST /api/auth/register
Request Body:
{
    "email": "user@example.com",
    "password": "SecureP@ss123",
    "first_name": "John",
    "last_name": "Doe"
}

Response (201 Created):
{
    "id": "uuid",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": false,
    "message": "Registration successful. Please check your email for verification."
}
```

**Password Requirements:**

- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character
- Not in common password list

#### Test Scenarios

**Unit Tests:**

```python
def test_identity_creation_with_valid_data()
def test_identity_email_must_be_unique()
def test_password_is_hashed_before_save()
def test_password_hash_uses_bcrypt()
def test_identity_defaults_to_inactive()
def test_identity_defaults_to_unverified()
def test_verification_token_generated_on_creation()
def test_verification_token_expires_after_24_hours()
```

**Service Tests:**

```python
def test_register_user_creates_identity()
def test_register_user_sends_verification_email()
def test_register_user_creates_audit_log()
def test_register_user_fails_with_duplicate_email()
def test_register_user_fails_with_weak_password()
def test_register_user_validates_email_format()
```

**API Tests:**

```python
def test_register_endpoint_returns_201()
def test_register_endpoint_validates_required_fields()
def test_register_endpoint_returns_400_for_invalid_data()
def test_register_endpoint_returns_409_for_duplicate_email()
def test_register_endpoint_does_not_expose_password()
```

**Integration Tests:**

```python
def test_registration_triggers_email_service()
def test_registration_creates_audit_log_entry()
def test_registration_with_entity_assignment()
```

#### Dependencies

- Email service for verification email
- Audit service for event logging
- Password hashing utility (bcrypt)

#### Definition of Done

- [ ] Identity model created with all fields
- [ ] Password hashing implemented with bcrypt
- [ ] Registration service method implemented
- [ ] API endpoint created and documented
- [ ] Verification email sent successfully
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] API documentation updated
- [ ] Code reviewed and approved

---

### US-007: User Login (Authentication)

**As a** registered user  
**I want to** login securely  
**So that** my data is protected and I can access my account

**Priority:** P0  
**Story Points:** 5  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] User can login with email and password
- [ ] Password is validated against stored hash
- [ ] Login fails for unverified email addresses
- [ ] Login fails for inactive accounts
- [ ] JWT access token and refresh token generated on successful login
- [ ] Tokens include user identity and permissions
- [ ] Last login timestamp updated on successful login
- [ ] Audit log entry created for login event
- [ ] Failed login attempts are logged
- [ ] Rate limiting prevents brute force attacks
- [ ] Login fails gracefully with appropriate error messages

#### Technical Specifications

**API Endpoint:**

```
POST /api/auth/login
Request Body:
{
    "email": "user@example.com",
    "password": "SecureP@ss123"
}

Response (200 OK):
{
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
        "id": "uuid",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "entity_id": "uuid"
    }
}

Response (401 Unauthorized):
{
    "error": "Invalid credentials"
}

Response (403 Forbidden):
{
    "error": "Account not verified. Please check your email."
}
```

**JWT Token Payload:**

```json
{
  "sub": "user_id (UUID)",
  "email": "user@example.com",
  "entity_id": "entity_uuid",
  "iat": 1234567890,
  "exp": 1234571490,
  "token_type": "access"
}
```

**Token Lifetimes:**

- Access Token: 1 hour (3600 seconds)
- Refresh Token: 7 days (604800 seconds)

#### Test Scenarios

**Unit Tests:**

```python
def test_verify_password_returns_true_for_correct_password()
def test_verify_password_returns_false_for_incorrect_password()
def test_identity_can_check_if_verified()
def test_identity_can_check_if_active()
def test_last_login_updated_on_successful_auth()
```

**Service Tests:**

```python
def test_authenticate_with_valid_credentials()
def test_authenticate_fails_with_invalid_password()
def test_authenticate_fails_for_unverified_user()
def test_authenticate_fails_for_inactive_user()
def test_authenticate_updates_last_login()
def test_authenticate_creates_audit_log()
def test_generate_jwt_tokens()
def test_jwt_token_contains_correct_claims()
def test_jwt_token_expiration()
```

**API Tests:**

```python
def test_login_endpoint_returns_200_with_valid_credentials()
def test_login_endpoint_returns_401_with_invalid_credentials()
def test_login_endpoint_returns_403_for_unverified_user()
def test_login_endpoint_returns_tokens()
def test_login_endpoint_does_not_expose_sensitive_data()
def test_login_endpoint_rate_limiting()
```

**Integration Tests:**

```python
def test_login_flow_end_to_end()
def test_token_can_be_used_for_authenticated_requests()
def test_audit_log_created_on_login()
def test_audit_log_created_on_failed_login()
```

#### Dependencies

- JWT library (PyJWT)
- Redis for rate limiting
- Audit service for event logging

#### Definition of Done

- [ ] Password verification implemented
- [ ] JWT token generation implemented
- [ ] Login service method implemented
- [ ] API endpoint created and documented
- [ ] Rate limiting configured
- [ ] Last login timestamp updated
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] Security review completed

---

### US-008: JWT Token Management

**As a** system  
**I want to** manage JWT tokens securely  
**So that** sessions are secure, stateless, and scalable

**Priority:** P0  
**Story Points:** 5  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] Access tokens generated with 1-hour expiration
- [ ] Refresh tokens generated with 7-day expiration
- [ ] Tokens are signed using HS256 algorithm
- [ ] Token secret stored securely in environment variables
- [ ] Tokens include user ID, entity ID, and permissions
- [ ] Token validation checks signature and expiration
- [ ] Expired tokens are rejected with 401 status
- [ ] Refresh endpoint allows token renewal
- [ ] Refresh tokens can be revoked
- [ ] Token blacklist implemented for logout
- [ ] Tokens are not stored in database (stateless)

#### Technical Specifications

**Token Generation:**

```python
def generate_access_token(identity: Identity) -> str:
    payload = {
        'sub': str(identity.id),
        'email': identity.email,
        'entity_id': str(identity.entity_id),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(hours=1),
        'token_type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def generate_refresh_token(identity: Identity) -> str:
    payload = {
        'sub': str(identity.id),
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7),
        'token_type': 'refresh'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
```

**API Endpoints:**

```
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

Response (200 OK):
{
    "access_token": "eyJhbGc...",
    "token_type": "Bearer",
    "expires_in": 3600
}

POST /api/auth/logout
Authorization: Bearer <access_token>

Response (204 No Content)
```

**Token Blacklist:**

- Store revoked tokens in Redis with TTL equal to token expiration
- Check blacklist on every authenticated request
- Key format: `blacklist:token:<jti>`

#### Test Scenarios

**Unit Tests:**

```python
def test_generate_access_token()
def test_generate_refresh_token()
def test_access_token_expires_in_1_hour()
def test_refresh_token_expires_in_7_days()
def test_token_includes_required_claims()
def test_decode_valid_token()
def test_decode_expired_token_raises_exception()
def test_decode_invalid_signature_raises_exception()
```

**Service Tests:**

```python
def test_validate_token_success()
def test_validate_token_fails_for_expired()
def test_validate_token_fails_for_invalid_signature()
def test_refresh_token_generates_new_access_token()
def test_refresh_token_fails_with_access_token()
def test_revoke_token_adds_to_blacklist()
def test_blacklisted_token_is_rejected()
```

**API Tests:**

```python
def test_refresh_endpoint_returns_new_token()
def test_refresh_endpoint_requires_refresh_token()
def test_logout_endpoint_revokes_token()
def test_authenticated_request_requires_valid_token()
def test_authenticated_request_rejects_expired_token()
def test_authenticated_request_rejects_blacklisted_token()
```

**Integration Tests:**

```python
def test_token_lifecycle_end_to_end()
def test_token_refresh_flow()
def test_logout_and_token_revocation()
def test_concurrent_requests_with_same_token()
```

#### Dependencies

- PyJWT library
- Redis for token blacklist
- Environment variables for token secret

#### Definition of Done

- [ ] Token generation utility implemented
- [ ] Token validation utility implemented
- [ ] Refresh endpoint created
- [ ] Logout endpoint created
- [ ] Token blacklist implemented in Redis
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Security review completed
- [ ] Documentation updated

---

### US-009: Password Reset Flow

**As a** user who forgot their password  
**I want to** reset my password securely  
**So that** I can regain access to my account

**Priority:** P0  
**Story Points:** 3  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] User can request password reset via email
- [ ] Reset token generated and sent to user's email
- [ ] Reset token expires after 1 hour
- [ ] User can reset password using valid token
- [ ] Old password is invalidated after reset
- [ ] Password must meet security requirements
- [ ] Reset token can only be used once
- [ ] Audit log entry created for password reset
- [ ] User receives confirmation email after successful reset
- [ ] Rate limiting prevents abuse

#### Technical Specifications

**Model Fields (added to Identity):**

```python
password_reset_token: CharField(64, null=True)
password_reset_token_expires: DateTimeField(null=True)
```

**API Endpoints:**

```
POST /api/auth/forgot-password
Request Body:
{
    "email": "user@example.com"
}

Response (200 OK):
{
    "message": "If the email exists, a password reset link has been sent."
}

POST /api/auth/reset-password
Request Body:
{
    "token": "reset_token_here",
    "new_password": "NewSecureP@ss123"
}

Response (200 OK):
{
    "message": "Password has been reset successfully."
}
```

**Reset Token Format:**

- Cryptographically secure random string (64 characters)
- Stored hashed in database
- Expires after 1 hour
- Single-use only

#### Test Scenarios

**Unit Tests:**

```python
def test_generate_password_reset_token()
def test_reset_token_expires_after_1_hour()
def test_verify_reset_token()
def test_reset_password_with_valid_token()
def test_reset_token_invalidated_after_use()
def test_expired_token_cannot_reset_password()
```

**Service Tests:**

```python
def test_request_password_reset_sends_email()
def test_request_password_reset_generates_token()
def test_request_password_reset_creates_audit_log()
def test_reset_password_updates_password_hash()
def test_reset_password_invalidates_token()
def test_reset_password_sends_confirmation_email()
def test_reset_password_fails_with_weak_password()
```

**API Tests:**

```python
def test_forgot_password_endpoint_returns_200()
def test_forgot_password_does_not_reveal_if_email_exists()
def test_reset_password_endpoint_validates_token()
def test_reset_password_endpoint_validates_password_strength()
def test_reset_password_rate_limiting()
```

**Integration Tests:**

```python
def test_password_reset_flow_end_to_end()
def test_cannot_login_with_old_password_after_reset()
def test_can_login_with_new_password_after_reset()
```

#### Dependencies

- Email service for reset link
- Audit service for event logging
- Secure random token generation

#### Definition of Done

- [ ] Reset token generation implemented
- [ ] Forgot password endpoint created
- [ ] Reset password endpoint created
- [ ] Reset email sent successfully
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] Security review completed
- [ ] Rate limiting configured

---

### US-010A: Email Verification

**As a** newly registered user  
**I want to** verify my email address  
**So that** my account is authenticated and I can access the platform

**Priority:** P0  
**Story Points:** 3  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] Verification email sent immediately after registration
- [ ] Email contains unique verification link with token
- [ ] Token expires after 24 hours
- [ ] User can verify email by clicking link
- [ ] Account is_verified flag set to true after verification
- [ ] Account is_active flag set to true after verification
- [ ] User can request new verification email if token expired
- [ ] Audit log entry created for email verification
- [ ] User redirected to login after successful verification
- [ ] Clear error messages for invalid/expired tokens

#### Technical Specifications

**Verification Link Format:**

```
https://app.paperwurks.com/verify-email?token=<verification_token>
```

**API Endpoints:**

```
POST /api/auth/verify-email
Request Body:
{
    "token": "verification_token_here"
}

Response (200 OK):
{
    "message": "Email verified successfully. You can now log in."
}

POST /api/auth/resend-verification
Request Body:
{
    "email": "user@example.com"
}

Response (200 OK):
{
    "message": "Verification email has been resent."
}
```

#### Test Scenarios

**Unit Tests:**

```python
def test_verification_token_generated_on_creation()
def test_verification_token_is_unique()
def test_verification_token_expires_after_24_hours()
def test_verify_email_with_valid_token()
def test_verify_email_sets_is_verified_true()
def test_verify_email_sets_is_active_true()
def test_expired_token_cannot_verify()
```

**Service Tests:**

```python
def test_send_verification_email()
def test_verify_email_creates_audit_log()
def test_resend_verification_generates_new_token()
def test_resend_verification_invalidates_old_token()
def test_already_verified_user_cannot_reverify()
```

**API Tests:**

```python
def test_verify_email_endpoint_returns_200()
def test_verify_email_endpoint_validates_token()
def test_verify_email_endpoint_returns_400_for_expired_token()
def test_resend_verification_endpoint_sends_email()
def test_resend_verification_rate_limiting()
```

**Integration Tests:**

```python
def test_email_verification_flow_end_to_end()
def test_cannot_login_before_verification()
def test_can_login_after_verification()
def test_resend_and_verify_with_new_token()
```

#### Dependencies

- Email service
- Audit service
- Token generation utility

#### Definition of Done

- [ ] Verification token generation implemented
- [ ] Verify email endpoint created
- [ ] Resend verification endpoint created
- [ ] Verification email sent successfully
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] User cannot login before verification

---

### US-014: Authentication Audit Logging

**As a** compliance officer  
**I want** audit logs for all authentication events  
**So that** I can track user access and security events

**Priority:** P0  
**Story Points:** 3  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] Audit log created for successful registration
- [ ] Audit log created for successful login
- [ ] Audit log created for failed login attempts
- [ ] Audit log created for password reset request
- [ ] Audit log created for password reset completion
- [ ] Audit log created for email verification
- [ ] Audit log created for logout
- [ ] Audit logs include timestamp, IP address, user agent
- [ ] Audit logs are immutable
- [ ] Audit logs are queryable by admin
- [ ] Integration with AuditService app

#### Technical Specifications

**Audit Event Types:**

```python
class AuthEventType(Enum):
    REGISTRATION = 'auth.registration'
    LOGIN_SUCCESS = 'auth.login.success'
    LOGIN_FAILED = 'auth.login.failed'
    LOGOUT = 'auth.logout'
    PASSWORD_RESET_REQUEST = 'auth.password_reset.request'
    PASSWORD_RESET_COMPLETE = 'auth.password_reset.complete'
    EMAIL_VERIFICATION = 'auth.email.verification'
    TOKEN_REFRESH = 'auth.token.refresh'
```

**Audit Log Structure:**

```python
{
    "event_type": "auth.login.success",
    "actor_id": "uuid",
    "actor_email": "user@example.com",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "timestamp": "2025-01-15T10:30:00Z",
    "metadata": {
        "entity_id": "uuid",
        "location": "London, UK"
    }
}
```

#### Test Scenarios

**Unit Tests:**

```python
def test_audit_log_created_with_required_fields()
def test_audit_log_immutability()
```

**Service Tests:**

```python
def test_registration_creates_audit_log()
def test_login_success_creates_audit_log()
def test_login_failure_creates_audit_log()
def test_password_reset_creates_audit_logs()
def test_email_verification_creates_audit_log()
def test_audit_log_includes_ip_and_user_agent()
```

**Integration Tests:**

```python
def test_audit_service_receives_auth_events()
def test_audit_logs_queryable_by_admin()
def test_audit_logs_cannot_be_modified()
```

#### Dependencies

- AuditService app
- Request context for IP and user agent

#### Definition of Done

- [ ] Audit logging integrated for all auth events
- [ ] All unit tests passing (>90% coverage)
- [ ] Integration with AuditService confirmed
- [ ] Audit logs are immutable
- [ ] Admin can query audit logs
- [ ] Documentation updated

---

## Integration Stories

### INT-001: Identity + Entity Integration

**As a** system  
**I want** Identity to be linked to Entity  
**So that** multi-tenancy scoping works correctly

**Priority:** P0  
**Story Points:** 2  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] Identity model has foreign key to Entity
- [ ] User can be assigned to Entity during registration
- [ ] User can be assigned to Entity after registration
- [ ] Identity inherits Entity-level permissions
- [ ] All Identity queries respect Entity boundaries
- [ ] Entity deletion handles related Identities appropriately

#### Test Scenarios

```python
def test_identity_linked_to_entity()
def test_identity_can_be_created_without_entity()
def test_identity_entity_assignment()
def test_identity_inherits_entity_permissions()
def test_query_identities_by_entity()
```

---

### INT-002: Identity + Audit Integration

**As a** system  
**I want** Identity authentication events logged to AuditService  
**So that** all security events are tracked

**Priority:** P0  
**Story Points:** 2  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] All authentication events trigger audit logs
- [ ] Audit logs include Identity ID and email
- [ ] Failed attempts are logged with reason
- [ ] Audit service can query by Identity ID
- [ ] Audit logs persist across Identity lifecycle

#### Test Scenarios

```python
def test_auth_events_create_audit_logs()
def test_audit_log_includes_identity_info()
def test_failed_login_audited_with_reason()
def test_query_audit_logs_by_identity()
```

---

## TDD Guidance

### Development Workflow

1. **Start with Models**: Create Identity model with all fields
2. **Write Failing Tests**: Create test cases before implementation
3. **Implement Minimal Logic**: Make tests pass
4. **Refactor**: Clean up code while keeping tests green
5. **Integration**: Test with Entity and Audit services

### Test Coverage Requirements

- **Unit Tests**: >90% coverage for models and utilities
- **Service Tests**: >90% coverage for business logic
- **API Tests**: 100% coverage for all endpoints
- **Integration Tests**: All critical flows tested

### Key Test Patterns

```python
# Model Tests
@pytest.mark.django_db
class TestIdentityModel:
    def test_identity_creation(self):
        identity = Identity.objects.create(...)
        assert identity.id is not None

# Service Tests
class TestAuthService:
    @patch('identity.services.send_email')
    def test_registration_sends_email(self, mock_send):
        service = AuthService()
        service.register(...)
        mock_send.assert_called_once()

# API Tests
class TestAuthAPI:
    def test_login_returns_tokens(self, client):
        response = client.post('/api/auth/login', {...})
        assert response.status_code == 200
        assert 'access_token' in response.json()
```

---

## Definition of Done - Module Level

- [ ] All user stories completed with acceptance criteria met
- [ ] Identity model implemented with all fields
- [ ] All service methods implemented and tested
- [ ] All API endpoints implemented and documented
- [ ] > 90% test coverage achieved
- [ ] All integration tests passing
- [ ] Audit logging working for all events
- [ ] Security review completed
- [ ] Code review completed
- [ ] API documentation updated
- [ ] Deployed to development environment
- [ ] Smoke tests passing in dev

---

## Technical Debt & Future Enhancements

- MFA implementation (Sprint 2)
- Social authentication (OAuth) (Sprint 3)
- Passwordless authentication (Sprint 4)
- Biometric authentication (Future)
- Session management UI (Sprint 2)
- Suspicious activity detection (Sprint 3)

---

## Dependencies on Other Modules

- **Entity Module**: Identity needs Entity model for tenancy
- **Audit Module**: Identity needs AuditService for logging
- **Email Service**: Identity needs email service for verification
- **Redis**: Identity needs Redis for token blacklist

---

## Notes for Developers

1. Always hash passwords with bcrypt (work factor 12)
2. Never log passwords or tokens
3. Always use environment variables for secrets
4. Test both happy path and error cases
5. Consider rate limiting for all auth endpoints
6. Use transaction.atomic() for critical operations
7. Validate all user input rigorously
8. Follow OWASP authentication best practices
