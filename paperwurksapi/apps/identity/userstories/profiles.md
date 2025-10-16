# Profile Module - User Stories

## Module Overview

The Profile module stores domain-specific metadata and preferences for Identities. It provides flexible storage for role-specific information such as solicitor credentials, agent certifications, user preferences, and contact details beyond basic Identity information.

**Sprint:** Sprint 1B (Week 5-6)  
**Priority:** P1  
**Story Points:** 3 (deferred from 1A)  
**Dependencies:** Identity Module

## Module Responsibilities

- Store domain-specific metadata for identities
- Manage user preferences (notifications, theme, language)
- Store professional credentials (solicitor licenses, agent certifications)
- Manage additional contact information
- Support flexible metadata structure (JSON)
- Provide profile validation based on role
- Enable profile completeness checking
- Track profile updates with audit logging

## Profile Types by Role

- **Agent**: Agency details, certifications, territories
- **Solicitor**: SRA number, practice areas, firm details
- **Buyer**: Preferences, budget range, requirements
- **Property Owner**: Property portfolio, preferences

## Core User Stories

### US-013: Profile Model Implementation

**As a** user  
**I want** Profile storage for my domain-specific data  
**So that** my professional information and preferences are maintained

**Priority:** P1  
**Story Points:** 3  
**Sprint:** 1B (deferred from 1A)

#### Acceptance Criteria

- [ ] Profile model created with flexible metadata field
- [ ] One-to-one relationship with Identity
- [ ] Profile created automatically when Identity is created
- [ ] Profile supports JSON metadata storage
- [ ] Profile validation based on Identity role
- [ ] Profile completeness can be calculated
- [ ] Profile updates are audited
- [ ] Profile can store credentials securely
- [ ] Profile supports file attachments (certifications, etc.)

#### Technical Specifications

**Model Fields:**

```python
Profile:
    - id: UUID (primary key)
    - identity: OneToOneField('Identity', related_name='profile')
    - phone: CharField(20, null=True, blank=True)
    - phone_verified: BooleanField(default=False)
    - avatar_url: URLField(null=True, blank=True)
    - bio: TextField(null=True, blank=True)
    - metadata: JSONField(default=dict)
    - preferences: JSONField(default=dict)
    - credentials: JSONField(default=dict)  # Encrypted
    - completeness_score: IntegerField(default=0)
    - last_updated_by: ForeignKey('Identity', null=True)
    - created_at: DateTimeField(auto_now_add=True)
    - updated_at: DateTimeField(auto_now=True)
```

**Metadata Structure by Role:**

```python
# Agent Profile Metadata
{
    "agency": {
        "name": "ABC Estate Agency",
        "role_title": "Senior Agent",
        "territories": ["London", "Surrey"],
        "specializations": ["Residential", "Commercial"]
    },
    "certifications": {
        "naea_member": true,
        "member_number": "12345",
        "expiry_date": "2025-12-31"
    },
    "contact": {
        "office_phone": "+44 20 1234 5678",
        "mobile": "+44 7700 123456",
        "linkedin": "https://linkedin.com/in/agent"
    }
}

# Solicitor Profile Metadata
{
    "legal_practice": {
        "firm_name": "Smith & Associates",
        "sra_number": "SRA123456",
        "position": "Partner",
        "practice_areas": ["Conveyancing", "Property Law"],
        "years_experience": 15
    },
    "qualifications": {
        "law_degree": "LLB",
        "university": "University of London",
        "year": 2008,
        "pqe": 15  # Post-Qualification Experience
    },
    "contact": {
        "office_phone": "+44 20 1234 5678",
        "direct_line": "+44 20 1234 5679",
        "email_secondary": "j.smith@smithlaw.com"
    }
}

# Buyer Profile Metadata
{
    "property_search": {
        "budget_min": 300000,
        "budget_max": 500000,
        "preferred_areas": ["Kensington", "Chelsea"],
        "property_types": ["flat", "house"],
        "bedrooms_min": 2,
        "must_haves": ["parking", "garden"]
    },
    "financing": {
        "mortgage_agreed_in_principle": true,
        "cash_buyer": false,
        "mortgage_provider": "HSBC"
    },
    "timeline": {
        "urgency": "3_months",
        "move_date_target": "2025-06-01"
    }
}
```

**Preferences Structure:**

```python
{
    "notifications": {
        "email": true,
        "sms": false,
        "push": true,
        "digest_frequency": "daily",
        "types": {
            "pack_updates": true,
            "document_uploads": true,
            "compliance_alerts": true,
            "marketing": false
        }
    },
    "ui": {
        "theme": "light",
        "language": "en-GB",
        "timezone": "Europe/London",
        "date_format": "DD/MM/YYYY"
    },
    "privacy": {
        "profile_visibility": "entity",
        "show_phone": false,
        "show_email": true
    }
}
```

#### Test Scenarios

**Unit Tests:**

```python
def test_profile_created_automatically_with_identity()
def test_profile_one_to_one_with_identity()
def test_profile_metadata_default_to_empty_dict()
def test_profile_preferences_default_structure()
def test_profile_completeness_calculation()
def test_profile_phone_validation()
def test_profile_metadata_structure_validation()
```

**Service Tests:**

```python
def test_update_profile_metadata()
def test_update_profile_preferences()
def test_validate_profile_by_role()
def test_calculate_profile_completeness()
def test_profile_update_creates_audit_log()
def test_encrypt_profile_credentials()
def test_get_profile_by_identity()
```

**API Tests:**

```python
def test_get_profile_endpoint()
def test_update_profile_endpoint()
def test_update_preferences_endpoint()
def test_upload_avatar_endpoint()
def test_profile_access_requires_authentication()
def test_user_can_only_update_own_profile()
```

**Integration Tests:**

```python
def test_profile_creation_with_identity_registration()
def test_profile_update_audit_trail()
def test_profile_metadata_persistence()
def test_profile_validation_based_on_role()
```

#### Dependencies

- Identity module for one-to-one relationship
- Audit service for update logging
- File storage for avatar uploads

#### Definition of Done

- [ ] Profile model created with all fields
- [ ] Automatic profile creation on identity creation
- [ ] Metadata validation implemented
- [ ] Completeness calculation working
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] API endpoints functional
- [ ] Code reviewed and approved

---

### US-013A: Profile Management API

**As a** user  
**I want to** manage my profile information  
**So that** my preferences and details are up to date

**Priority:** P1  
**Story Points:** 2  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] User can view their profile
- [ ] User can update their profile metadata
- [ ] User can update their preferences
- [ ] User can upload/update avatar
- [ ] User can verify phone number
- [ ] Profile changes are validated
- [ ] Admins can view any profile
- [ ] Profile updates are audited

#### Technical Specifications

**API Endpoints:**

```
GET /api/profile
Response (200 OK):
{
    "id": "uuid",
    "identity_id": "uuid",
    "phone": "+44 7700 123456",
    "phone_verified": false,
    "avatar_url": "https://...",
    "bio": "Experienced estate agent...",
    "metadata": {...},
    "preferences": {...},
    "completeness_score": 75,
    "updated_at": "2025-01-15T10:00:00Z"
}

PATCH /api/profile
Request Body:
{
    "phone": "+44 7700 123456",
    "bio": "Updated bio...",
    "metadata": {
        "agency": {
            "territories": ["London", "Surrey", "Kent"]
        }
    }
}

Response (200 OK):
{...}

PATCH /api/profile/preferences
Request Body:
{
    "notifications": {
        "email": false,
        "push": true
    }
}

Response (200 OK):
{...}

POST /api/profile/avatar
Request: multipart/form-data
Response (200 OK):
{
    "avatar_url": "https://..."
}

POST /api/profile/verify-phone
Request Body:
{
    "verification_code": "123456"
}

Response (200 OK):
{
    "phone_verified": true
}
```

#### Test Scenarios

**API Tests:**

```python
def test_get_own_profile()
def test_update_profile_metadata()
def test_update_preferences_merge()
def test_upload_avatar()
def test_verify_phone_number()
def test_cannot_access_other_user_profile()
def test_admin_can_view_any_profile()
```

**Integration Tests:**

```python
def test_profile_update_flow()
def test_avatar_upload_and_storage()
def test_phone_verification_flow()
def test_preferences_affect_notifications()
```

#### Definition of Done

- [ ] All API endpoints implemented
- [ ] Profile validation working
- [ ] Avatar upload functional
- [ ] Phone verification working
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] API documentation updated
- [ ] Code reviewed and approved

---

### US-013B: Profile Completeness & Validation

**As a** system  
**I want to** calculate profile completeness  
**So that** users are encouraged to complete their profiles

**Priority:** P2  
**Story Points:** 2  
**Sprint:** 2

#### Acceptance Criteria

- [ ] Profile completeness score calculated (0-100)
- [ ] Required fields defined per role
- [ ] Completeness considers required and optional fields
- [ ] Users notified of incomplete profiles
- [ ] Completeness score displayed in UI
- [ ] Profile validation based on role requirements

#### Technical Specifications

**Completeness Calculation:**

```python
def calculate_completeness(profile: Profile) -> int:
    """Calculate profile completeness score 0-100"""
    identity = profile.identity
    role = identity.roles.first()  # Primary role

    required_fields = ROLE_REQUIRED_FIELDS.get(role.codename, [])
    optional_fields = ROLE_OPTIONAL_FIELDS.get(role.codename, [])

    required_weight = 0.7  # 70% of score
    optional_weight = 0.3  # 30% of score

    # Check required fields
    required_complete = sum(
        1 for field in required_fields
        if check_field_complete(profile, field)
    )
    required_score = (required_complete / len(required_fields)) * 100 * required_weight

    # Check optional fields
    optional_complete = sum(
        1 for field in optional_fields
        if check_field_complete(profile, field)
    )
    optional_score = (optional_complete / len(optional_fields)) * 100 * optional_weight

    return int(required_score + optional_score)

ROLE_REQUIRED_FIELDS = {
    'agent': ['phone', 'metadata.agency.name', 'metadata.agency.territories'],
    'solicitor': ['phone', 'metadata.legal_practice.sra_number', 'metadata.legal_practice.firm_name'],
    'buyer': ['phone', 'metadata.property_search.budget_min'],
}
```

#### Test Scenarios

```python
def test_completeness_calculation_agent()
def test_completeness_calculation_solicitor()
def test_completeness_with_required_fields_missing()
def test_completeness_with_all_fields_complete()
def test_completeness_updates_on_profile_change()
```

---

## Integration Stories

### INT-011: Profile + Identity Integration

**As a** system  
**I want** Profile automatically created with Identity  
**So that** profile data is always available

**Priority:** P0  
**Story Points:** 1  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] Profile created when Identity is created
- [ ] Profile deleted when Identity is deleted
- [ ] Profile accessible via identity.profile
- [ ] Profile signals handled correctly

#### Test Scenarios

```python
def test_profile_created_on_identity_creation()
def test_profile_accessible_via_identity()
def test_profile_deleted_with_identity()
def test_profile_signal_handlers()
```

---

### INT-012: Profile + Audit Integration

**As a** system  
**I want** Profile changes audited  
**So that** data changes are tracked

**Priority:** P1  
**Story Points:** 1  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] Profile updates create audit logs
- [ ] Metadata changes tracked in detail
- [ ] Preference changes logged
- [ ] Credential updates logged
- [ ] Avatar changes logged

#### Test Scenarios

```python
def test_profile_update_creates_audit_log()
def test_metadata_change_audited()
def test_preference_change_audited()
```

---

## TDD Guidance

### Development Workflow

1. **Start with Model**: Create Profile model with JSONField
2. **Auto-creation**: Implement signal for automatic profile creation
3. **Validation**: Implement role-based validation
4. **Completeness**: Implement completeness calculation
5. **API**: Create management endpoints
6. **Integration**: Test with Identity service

### Test Coverage Requirements

- **Unit Tests**: >90% coverage for Profile model
- **Service Tests**: >90% coverage for ProfileService
- **API Tests**: 100% coverage for all endpoints
- **Integration Tests**: Profile lifecycle tests

---

## Definition of Done - Module Level

- [ ] Profile model implemented
- [ ] Auto-creation working
- [ ] Validation implemented
- [ ] Completeness calculation working
- [ ] All API endpoints implemented
- [ ] > 90% test coverage achieved
- [ ] All integration tests passing
- [ ] Audit logging working
- [ ] Avatar upload functional
- [ ] API documentation complete
- [ ] Code review completed

---

## Technical Debt & Future Enhancements

- Profile templates by role
- Profile import/export
- Profile sharing controls
- Profile history/versioning
- Advanced validation rules
- Profile badges/achievements
- Social profile links
- Professional network integration

---

## Dependencies on Other Modules

- **Identity Module**: Profile belongs to Identity
- **Audit Module**: Profile changes must be audited
- **File Storage**: Profile needs avatar storage
- **Notification Module**: Profile preferences control notifications

---

## Notes for Developers

1. **Use JSONField carefully**: Validate structure before saving
2. **Encrypt credentials**: Use field-level encryption for sensitive data
3. **Default preferences**: Ensure sane defaults for all preferences
4. **Completeness caching**: Cache completeness score, recalculate on change
5. **Role-specific validation**: Different validation rules per role
6. **Migration strategy**: Plan for metadata structure changes
7. **Phone verification**: Use SMS service for verification codes
8. **Avatar storage**: Use S3 for avatar images
9. **Privacy controls**: Respect profile visibility settings
10. **Performance**: Index metadata JSONB fields for common queries (PostgreSQL)
