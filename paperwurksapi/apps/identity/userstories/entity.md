# Entity Module - User Stories

## Module Overview

The Entity module represents organizational boundaries and multi-tenancy scoping in the Paperwurks platform. Entities define access boundaries for notifications, engagement flows, and data isolation between organizations (estate agencies, law firms, etc.).

**Sprint:** Sprint 1A (Week 3-4)  
**Priority:** P0 - Critical  
**Dependencies:** None (foundational module alongside Identity)

## Module Responsibilities

- Multi-tenant organization management
- Access boundary definition
- Data isolation between organizations
- Entity-level configuration and settings
- Entity lifecycle management (creation, activation, deactivation)
- Entity type classification (estate agency, law firm, property company)
- Entity relationship with Identities

## Core User Stories

### US-011: Entity Model Implementation

**As a** system  
**I want** Entity model for multi-tenancy  
**So that** I can scope access boundaries and isolate data between organizations

**Priority:** P0  
**Story Points:** 5  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] Entity model created with all required fields
- [ ] Entity types supported: estate_agency, law_firm, property_company
- [ ] Entity can have multiple Identities
- [ ] Entity can be activated or deactivated
- [ ] Entity settings stored as JSON field for flexibility
- [ ] Entity has unique identifier (UUID)
- [ ] Entity timestamps tracked (created_at, updated_at)
- [ ] Entity can be queried efficiently
- [ ] Soft delete capability for Entity
- [ ] Audit logging for Entity creation

#### Technical Specifications

**Model Fields:**

```python
Entity:
    - id: UUID (primary key)
    - name: CharField(255, unique)
    - entity_type: CharField(50, choices=[
        'estate_agency',
        'law_firm',
        'property_company',
        'individual'
    ])
    - registration_number: CharField(50, null=True, blank=True)
    - address: TextField(null=True, blank=True)
    - postcode: CharField(10, null=True, blank=True)
    - phone: CharField(20, null=True, blank=True)
    - email: EmailField(null=True, blank=True)
    - website: URLField(null=True, blank=True)
    - settings: JSONField(default=dict)
    - subscription_tier: CharField(50, default='free')
    - is_active: BooleanField(default=True)
    - deleted_at: DateTimeField(null=True, blank=True)
    - created_at: DateTimeField(auto_now_add=True)
    - updated_at: DateTimeField(auto_now=True)
```

**Default Settings Structure:**

```json
{
  "notifications": {
    "email_enabled": true,
    "sms_enabled": false,
    "push_enabled": true
  },
  "compliance": {
    "require_solicitor_signoff": true,
    "require_search_results": true
  },
  "branding": {
    "logo_url": null,
    "primary_color": "#007bff",
    "secondary_color": "#6c757d"
  },
  "features": {
    "ai_analysis_enabled": true,
    "pack_sharing_enabled": true,
    "document_versioning": true
  }
}
```

**Relationships:**

```python
# One-to-Many: Entity -> Identity
identities = models.ForeignKey('Identity', related_name='entity')

# One-to-Many: Entity -> Property (future)
properties = models.ForeignKey('Property', related_name='entity')
```

#### Test Scenarios

**Unit Tests:**

```python
def test_entity_creation_with_required_fields()
def test_entity_name_must_be_unique()
def test_entity_type_must_be_valid_choice()
def test_entity_defaults_to_active()
def test_entity_settings_default_to_empty_dict()
def test_entity_soft_delete()
def test_entity_restore_from_soft_delete()
def test_entity_string_representation()
def test_entity_get_active_entities()
def test_entity_filter_by_type()
```

**Service Tests:**

```python
def test_create_entity_with_valid_data()
def test_create_entity_creates_audit_log()
def test_create_entity_with_default_settings()
def test_update_entity_settings()
def test_deactivate_entity()
def test_activate_entity()
def test_delete_entity_soft_deletes()
```

**API Tests:**

```python
def test_create_entity_endpoint_returns_201()
def test_create_entity_validates_required_fields()
def test_get_entity_by_id()
def test_list_entities_with_pagination()
def test_update_entity_endpoint()
def test_delete_entity_endpoint()
```

**Integration Tests:**

```python
def test_entity_creation_triggers_audit_log()
def test_entity_with_multiple_identities()
def test_entity_settings_persistence()
def test_entity_deactivation_affects_identities()
```

#### Dependencies

- Audit service for event logging

#### Definition of Done

- [ ] Entity model created with all fields
- [ ] Model validation implemented
- [ ] Soft delete functionality working
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] Database migration created
- [ ] Model registered in admin interface
- [ ] Code reviewed and approved

---

### US-012: Entity Management API

**As an** admin  
**I want to** manage Entities through API  
**So that** I can control organizational access and configuration

**Priority:** P1  
**Story Points:** 3  
**Sprint:** 1B (deferred from 1A)

#### Acceptance Criteria

- [ ] Admin can create new Entity
- [ ] Admin can view Entity details
- [ ] Admin can list all Entities with filtering
- [ ] Admin can update Entity information
- [ ] Admin can update Entity settings
- [ ] Admin can activate/deactivate Entity
- [ ] Admin can soft delete Entity
- [ ] Only system admins can manage Entities
- [ ] Entity changes are audit logged
- [ ] API responses include related Identity count

#### Technical Specifications

**API Endpoints:**

```
POST /api/entities
Request Body:
{
    "name": "ABC Estate Agency",
    "entity_type": "estate_agency",
    "registration_number": "12345678",
    "email": "contact@abcestates.com",
    "settings": {...}
}

Response (201 Created):
{
    "id": "uuid",
    "name": "ABC Estate Agency",
    "entity_type": "estate_agency",
    "is_active": true,
    "identity_count": 0,
    "created_at": "2025-01-15T10:00:00Z"
}

GET /api/entities
Query Params: ?entity_type=estate_agency&is_active=true&page=1&limit=20

Response (200 OK):
{
    "count": 50,
    "next": "/api/entities?page=2",
    "previous": null,
    "results": [...]
}

GET /api/entities/{id}
Response (200 OK):
{
    "id": "uuid",
    "name": "ABC Estate Agency",
    "entity_type": "estate_agency",
    "registration_number": "12345678",
    "settings": {...},
    "identity_count": 15,
    "property_count": 42,
    "is_active": true,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-20T14:30:00Z"
}

PATCH /api/entities/{id}
Request Body:
{
    "name": "ABC Estate Agency Ltd",
    "settings": {
        "notifications": {
            "email_enabled": false
        }
    }
}

Response (200 OK):
{...}

DELETE /api/entities/{id}
Response (204 No Content)
```

**Permissions:**

- Only users with `entity.manage` permission can access these endpoints
- System administrators have full access
- Entity-scoped admins can only view their own Entity

#### Test Scenarios

**Service Tests:**

```python
def test_entity_service_create()
def test_entity_service_update()
def test_entity_service_update_settings_merge()
def test_entity_service_deactivate()
def test_entity_service_get_by_id()
def test_entity_service_list_with_filters()
def test_entity_service_get_identity_count()
```

**API Tests:**

```python
def test_create_entity_requires_admin_permission()
def test_create_entity_validates_entity_type()
def test_list_entities_with_filters()
def test_get_entity_includes_related_counts()
def test_update_entity_partial_update()
def test_update_entity_settings_merge()
def test_delete_entity_soft_deletes()
def test_unauthorized_user_cannot_manage_entities()
```

**Integration Tests:**

```python
def test_entity_management_end_to_end()
def test_entity_deactivation_affects_operations()
def test_entity_settings_affect_features()
```

#### Dependencies

- Role module for permission checks
- Audit service for change logging

#### Definition of Done

- [ ] All CRUD endpoints implemented
- [ ] Permission checks enforced
- [ ] Entity settings merge logic working
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] API documentation updated
- [ ] Postman collection created
- [ ] Code reviewed and approved

---

## Integration Stories

### INT-003: Entity + Identity Integration

**As a** system  
**I want** Identities to be scoped to Entities  
**So that** multi-tenancy is enforced

**Priority:** P0  
**Story Points:** 2  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] Identity has foreign key to Entity
- [ ] Identity can belong to one Entity
- [ ] Entity can have many Identities
- [ ] Queries can filter Identities by Entity
- [ ] Entity deactivation restricts Identity access
- [ ] Cascade rules defined for Entity deletion
- [ ] Entity-scoped permissions work correctly

#### Test Scenarios

```python
def test_identity_belongs_to_entity()
def test_entity_has_many_identities()
def test_query_identities_by_entity()
def test_deactivated_entity_restricts_identity_access()
def test_entity_deletion_handles_identities()
def test_entity_scoped_queries()
```

---

### INT-004: Entity + Property Integration

**As a** system  
**I want** Properties to be scoped to Entities  
**So that** property data is isolated by organization

**Priority:** P1  
**Story Points:** 2  
**Sprint:** 2

#### Acceptance Criteria

- [ ] Property model has foreign key to Entity
- [ ] Property queries filtered by Entity
- [ ] Entity admins can only see their Entity's properties
- [ ] Cross-entity property access prevented
- [ ] Entity-level property analytics available

#### Test Scenarios

```python
def test_property_belongs_to_entity()
def test_query_properties_by_entity()
def test_cross_entity_property_access_denied()
def test_entity_property_count()
def test_entity_property_analytics()
```

---

### INT-005: Entity + Audit Integration

**As a** system  
**I want** Entity changes logged to AuditService  
**So that** organizational changes are tracked

**Priority:** P0  
**Story Points:** 1  
**Sprint:** 1A

#### Acceptance Criteria

- [ ] Entity creation logged
- [ ] Entity updates logged with changes
- [ ] Entity deactivation logged
- [ ] Entity deletion logged
- [ ] Settings changes tracked in detail
- [ ] Audit logs include actor Identity

#### Test Scenarios

```python
def test_entity_creation_creates_audit_log()
def test_entity_update_creates_audit_log()
def test_entity_settings_change_audited()
def test_entity_deactivation_audited()
def test_audit_log_includes_actor()
```

---

## Advanced User Stories (Future Sprints)

### US-013-FUTURE: Entity Hierarchy

**As a** large organization  
**I want** hierarchical Entity structure  
**So that** I can manage sub-organizations

**Priority:** P2  
**Story Points:** 8  
**Sprint:** TBD

#### Acceptance Criteria

- [ ] Entity can have parent Entity
- [ ] Entity can have multiple child Entities
- [ ] Permissions cascade down hierarchy
- [ ] Settings can inherit from parent
- [ ] Cross-entity operations within hierarchy

---

### US-014-FUTURE: Entity Subscription Management

**As an** Entity admin  
**I want** to manage subscription tier  
**So that** I can control feature access

**Priority:** P2  
**Story Points:** 5  
**Sprint:** TBD

#### Acceptance Criteria

- [ ] Entity has subscription tier (free, basic, premium, enterprise)
- [ ] Features gated by subscription tier
- [ ] Usage tracking per Entity
- [ ] Billing integration
- [ ] Upgrade/downgrade workflows

---

## TDD Guidance

### Development Workflow

1. **Start with Model**: Create Entity model
2. **Test Relationships**: Test Entity-Identity relationship
3. **Test Settings**: Test JSON field settings management
4. **Test Lifecycle**: Test activation, deactivation, soft delete
5. **Test Scoping**: Test multi-tenancy queries
6. **Integration**: Test with Identity and Audit services

### Test Coverage Requirements

- **Unit Tests**: >90% coverage for Entity model
- **Service Tests**: >90% coverage for EntityService
- **API Tests**: 100% coverage for all endpoints
- **Integration Tests**: All relationship tests

### Key Test Patterns

```python
# Model Tests
@pytest.mark.django_db
class TestEntityModel:
    def test_entity_creation(self):
        entity = Entity.objects.create(
            name="Test Agency",
            entity_type="estate_agency"
        )
        assert entity.id is not None
        assert entity.is_active is True

    def test_entity_settings_default(self):
        entity = Entity.objects.create(name="Test")
        assert isinstance(entity.settings, dict)

# Multi-tenancy Tests
class TestEntityScoping:
    def test_queries_respect_entity_boundaries(self):
        entity1 = create_entity(name="Entity 1")
        entity2 = create_entity(name="Entity 2")
        identity1 = create_identity(entity=entity1)
        identity2 = create_identity(entity=entity2)

        identities = Identity.objects.filter(entity=entity1)
        assert identity1 in identities
        assert identity2 not in identities
```

---

## Definition of Done - Module Level

- [ ] Entity model implemented with all fields
- [ ] Entity service layer implemented
- [ ] Entity API endpoints implemented
- [ ] Multi-tenancy scoping working
- [ ] Settings management working
- [ ] > 90% test coverage achieved
- [ ] All integration tests passing
- [ ] Audit logging working
- [ ] Admin interface configured
- [ ] API documentation complete
- [ ] Database migrations created
- [ ] Code review completed
- [ ] Deployed to development environment

---

## Technical Debt & Future Enhancements

- Entity hierarchy (parent-child relationships)
- Entity templates for quick setup
- Entity cloning functionality
- Cross-entity reporting for admins
- Entity usage analytics
- Subscription tier management
- Billing integration
- Entity invitation system

---

## Dependencies on Other Modules

- **Identity Module**: Entity needs Identity for ownership
- **Audit Module**: Entity needs AuditService for logging
- **Property Module**: Entity scopes Property data (Sprint 2)
- **Pack Module**: Entity scopes Pack data (Sprint 2)

---

## Notes for Developers

1. Always filter queries by Entity for multi-tenancy
2. Test both active and inactive Entity scenarios
3. Use JSONField carefully - validate settings structure
4. Consider Entity deactivation impact on all operations
5. Implement soft delete to preserve audit trail
6. Use select_related() for Entity queries with Identities
7. Cache Entity settings for performance
8. Document all settings structure changes
9. Test Entity settings merge behavior thoroughly
10. Consider Entity-level feature flags

---

## Entity Settings Schema

### Notification Settings

```json
{
  "notifications": {
    "email_enabled": true,
    "sms_enabled": false,
    "push_enabled": true,
    "digest_frequency": "daily",
    "notification_types": {
      "pack_updates": true,
      "compliance_alerts": true,
      "document_uploads": true,
      "search_results": true
    }
  }
}
```

### Compliance Settings

```json
{
  "compliance": {
    "require_solicitor_signoff": true,
    "require_search_results": true,
    "require_ai_analysis": false,
    "retention_days": 2555,
    "encryption_enabled": true
  }
}
```

### Feature Flags

```json
{
  "features": {
    "ai_analysis_enabled": true,
    "pack_sharing_enabled": true,
    "document_versioning": true,
    "timeline_enabled": true,
    "feedback_collection": true,
    "case_management": false
  }
}
```

### Branding Settings

```json
{
  "branding": {
    "logo_url": "https://...",
    "primary_color": "#007bff",
    "secondary_color": "#6c757d",
    "custom_domain": null
  }
}
```
