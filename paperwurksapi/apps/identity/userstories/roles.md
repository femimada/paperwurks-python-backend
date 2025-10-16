# Role Module - User Stories

## Module Overview

The Role module implements Role-Based Access Control (RBAC) for baseline permissions in the Paperwurks platform. Roles define collections of permissions that can be assigned to Identities, providing a foundation for authorization across all services.

**Sprint:** Sprint 1B (Week 5-6)  
**Priority:** P0 - Critical  
**Dependencies:** Identity Module, Entity Module

## Module Responsibilities

- Define system-wide roles (agent, solicitor, buyer, admin)
- Manage permission definitions
- Assign roles to identities
- Check role-based permissions
- Support role inheritance
- Track role changes with audit logging
- Provide role-permission matrix for authorization
- Expose role checking utilities for other services

## Permission Codename Format

All permissions follow the format: `{resource}.{action}`

**Examples:**

- `property.view`
- `property.create`
- `property.update`
- `property.delete`
- `pack.signoff`
- `document.upload`
- `document.annotate`
- `user.manage`

## Core User Stories

### US-015: Role Model Implementation

**As an** admin  
**I want** Role model with permission management  
**So that** I can assign baseline access to users

**Priority:** P0  
**Story Points:** 5  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] Role model created with all required fields
- [ ] Permission model created with codename structure
- [ ] Many-to-many relationship between Role and Permission
- [ ] Many-to-many relationship between Identity and Role
- [ ] Predefined system roles created (agent, solicitor, buyer, admin)
- [ ] Role name is unique
- [ ] Role has description for clarity
- [ ] Permissions organized by resource type
- [ ] Role can be activated or deactivated
- [ ] Audit logging for role creation and modification

#### Technical Specifications

**Model Fields:**

```python
Role:
    - id: UUID (primary key)
    - name: CharField(50, unique)
    - codename: SlugField(50, unique)
    - description: TextField()
    - permissions: ManyToManyField('Permission')
    - is_active: BooleanField(default=True)
    - is_system_role: BooleanField(default=False)
    - created_at: DateTimeField(auto_now_add=True)
    - updated_at: DateTimeField(auto_now=True)

Permission:
    - id: UUID (primary key)
    - name: CharField(100)
    - codename: CharField(100, unique)  # format: resource.action
    - description: TextField()
    - resource_type: CharField(50)  # e.g., 'property', 'pack', 'document'
    - action: CharField(50)  # e.g., 'view', 'create', 'update', 'delete'
    - created_at: DateTimeField(auto_now_add=True)
    - updated_at: DateTimeField(auto_now=True)

IdentityRole (through table):
    - id: UUID (primary key)
    - identity: ForeignKey('Identity')
    - role: ForeignKey('Role')
    - assigned_by: ForeignKey('Identity')
    - assigned_at: DateTimeField(auto_now_add=True)
    - expires_at: DateTimeField(null=True, blank=True)
```

**Predefined Roles:**

```python
SYSTEM_ROLES = {
    'admin': {
        'name': 'System Administrator',
        'description': 'Full system access',
        'permissions': ['*.*']  # All permissions
    },
    'agent': {
        'name': 'Estate Agent',
        'description': 'Manage properties and coordinate transactions',
        'permissions': [
            'property.view', 'property.create', 'property.update',
            'document.view', 'document.upload', 'document.annotate',
            'pack.view', 'pack.create', 'pack.share',
            'user.invite', 'entity.view'
        ]
    },
    'solicitor': {
        'name': 'Solicitor',
        'description': 'Review documents and sign off packs',
        'permissions': [
            'property.view',
            'document.view', 'document.annotate',
            'pack.view', 'pack.signoff', 'pack.review',
            'feedback.submit'
        ]
    },
    'buyer': {
        'name': 'Property Buyer',
        'description': 'View shared packs and documents',
        'permissions': [
            'property.view',
            'document.view',
            'pack.view',
            'feedback.submit'
        ]
    }
}
```

#### Test Scenarios

**Unit Tests:**

```python
def test_role_creation_with_required_fields()
def test_role_name_must_be_unique()
def test_role_codename_must_be_unique()
def test_role_can_have_multiple_permissions()
def test_permission_codename_format_validation()
def test_permission_resource_and_action_extraction()
def test_identity_can_have_multiple_roles()
def test_role_assignment_tracks_assigner()
def test_role_can_expire()
def test_system_role_cannot_be_deleted()
```

**Service Tests:**

```python
def test_create_role_with_permissions()
def test_assign_role_to_identity()
def test_remove_role_from_identity()
def test_get_identity_permissions_from_roles()
def test_role_assignment_creates_audit_log()
def test_create_system_roles()
def test_update_role_permissions()
```

**API Tests:**

```python
def test_create_role_endpoint_returns_201()
def test_list_roles_with_permissions()
def test_get_role_by_id_includes_permissions()
def test_update_role_permissions()
def test_assign_role_to_identity_endpoint()
```

**Integration Tests:**

```python
def test_role_based_permission_checking()
def test_multiple_roles_combine_permissions()
def test_expired_role_not_granting_permissions()
def test_role_assignment_audit_logging()
```

#### Dependencies

- Identity module for role assignment
- Audit service for change logging

#### Definition of Done

- [ ] Role and Permission models created
- [ ] Many-to-many relationships implemented
- [ ] System roles created via migration
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] Admin interface configured
- [ ] Code reviewed and approved

---

### US-016: Permission System Implementation

**As a** system  
**I want** comprehensive permission definitions  
**So that** I can control resource access granularly

**Priority:** P0  
**Story Points:** 5  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] All resource types have permission definitions
- [ ] Standard CRUD permissions defined for each resource
- [ ] Special permissions defined (e.g., pack.signoff)
- [ ] Permission descriptions are clear and accurate
- [ ] Permissions can be queried by resource type
- [ ] Permission matrix documented
- [ ] Wildcard permission support (_._) for admins
- [ ] Permission validation in place

#### Technical Specifications

**Permission Definitions:**

```python
PERMISSION_DEFINITIONS = {
    'property': {
        'view': 'View property details',
        'create': 'Create new property',
        'update': 'Update property information',
        'delete': 'Delete property',
        'assign': 'Assign property to users'
    },
    'document': {
        'view': 'View documents',
        'upload': 'Upload new documents',
        'download': 'Download documents',
        'delete': 'Delete documents',
        'annotate': 'Add annotations to documents',
        'version': 'Manage document versions'
    },
    'pack': {
        'view': 'View packs',
        'create': 'Create new packs',
        'update': 'Update pack contents',
        'delete': 'Delete packs',
        'signoff': 'Sign off packs (solicitor)',
        'share': 'Share packs with others',
        'review': 'Review pack completeness'
    },
    'search': {
        'view': 'View search results',
        'order': 'Order new searches',
        'download': 'Download search reports'
    },
    'feedback': {
        'view': 'View feedback',
        'submit': 'Submit feedback',
        'respond': 'Respond to feedback'
    },
    'user': {
        'view': 'View user profiles',
        'create': 'Create new users',
        'update': 'Update user information',
        'delete': 'Delete users',
        'invite': 'Invite new users',
        'manage': 'Full user management'
    },
    'entity': {
        'view': 'View entity details',
        'create': 'Create new entities',
        'update': 'Update entity settings',
        'delete': 'Delete entities',
        'manage': 'Full entity management'
    },
    'role': {
        'view': 'View roles',
        'create': 'Create new roles',
        'update': 'Update role permissions',
        'delete': 'Delete roles',
        'assign': 'Assign roles to users'
    },
    'acl': {
        'view': 'View ACL grants',
        'grant': 'Grant ACL permissions',
        'revoke': 'Revoke ACL permissions',
        'manage': 'Full ACL management'
    }
}
```

**Management Command:**

```python
# python manage.py create_permissions
# Creates all permission definitions
```

#### Test Scenarios

**Unit Tests:**

```python
def test_permission_codename_unique()
def test_permission_parse_resource_and_action()
def test_permission_string_representation()
def test_permission_validation()
def test_wildcard_permission()
```

**Service Tests:**

```python
def test_create_all_permissions()
def test_get_permissions_by_resource()
def test_get_permissions_by_action()
def test_permission_matrix_generation()
```

**Integration Tests:**

```python
def test_permissions_created_via_migration()
def test_permissions_available_for_role_assignment()
```

#### Definition of Done

- [ ] All permissions defined
- [ ] Management command created
- [ ] Permissions created via migration
- [ ] All unit tests passing
- [ ] Permission matrix documented
- [ ] Code reviewed and approved

---

### US-017: Role Assignment to Identities

**As an** admin  
**I want to** assign Roles to Identities  
**So that** users have appropriate access levels

**Priority:** P0  
**Story Points:** 3  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] Admin can assign role to identity
- [ ] Admin can remove role from identity
- [ ] Identity can have multiple roles
- [ ] Role assignment tracks who assigned and when
- [ ] Role assignment can have expiration date
- [ ] Expired role assignments are automatically excluded
- [ ] Audit log created for role assignments
- [ ] Audit log created for role removals
- [ ] API endpoints for role assignment

#### Technical Specifications

**API Endpoints:**

```
POST /api/identities/{id}/roles
Request Body:
{
    "role_id": "uuid",
    "expires_at": "2025-12-31T23:59:59Z"  # optional
}

Response (201 Created):
{
    "identity_id": "uuid",
    "role": {
        "id": "uuid",
        "name": "Estate Agent",
        "codename": "agent"
    },
    "assigned_by": "uuid",
    "assigned_at": "2025-01-15T10:00:00Z",
    "expires_at": "2025-12-31T23:59:59Z"
}

DELETE /api/identities/{id}/roles/{role_id}
Response (204 No Content)

GET /api/identities/{id}/roles
Response (200 OK):
{
    "roles": [
        {
            "id": "uuid",
            "name": "Estate Agent",
            "codename": "agent",
            "assigned_at": "2025-01-15T10:00:00Z",
            "expires_at": null
        }
    ]
}
```

#### Test Scenarios

**Service Tests:**

```python
def test_assign_role_to_identity()
def test_remove_role_from_identity()
def test_identity_has_role()
def test_get_identity_roles()
def test_get_identity_all_permissions()
def test_role_assignment_with_expiration()
def test_expired_role_not_included()
def test_role_assignment_creates_audit_log()
```

**API Tests:**

```python
def test_assign_role_endpoint_requires_permission()
def test_assign_role_validates_role_exists()
def test_assign_role_validates_identity_exists()
def test_remove_role_endpoint()
def test_get_identity_roles_endpoint()
def test_cannot_assign_role_without_permission()
```

**Integration Tests:**

```python
def test_role_assignment_flow_end_to_end()
def test_multiple_role_permission_combination()
def test_role_expiration_removes_permissions()
def test_audit_trail_for_role_changes()
```

#### Definition of Done

- [ ] Role assignment service methods implemented
- [ ] API endpoints created
- [ ] Expiration logic working
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] API documentation updated
- [ ] Code reviewed and approved

---

## Integration Stories

### INT-006: Role + Identity Integration

**As a** system  
**I want** Identities to have Roles  
**So that** permission checking works via RBAC

**Priority:** P0  
**Story Points:** 2  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] Identity model has many-to-many with Role
- [ ] Identity can have multiple roles
- [ ] Identity method to check if has permission
- [ ] Identity method to get all permissions
- [ ] Identity method to check if has role
- [ ] Role changes reflect immediately in permission checks

#### Test Scenarios

```python
def test_identity_has_roles()
def test_identity_get_all_permissions()
def test_identity_has_permission()
def test_identity_check_permission_with_multiple_roles()
def test_identity_permission_cache_invalidation()
```

---

### INT-007: Role + Audit Integration

**As a** system  
**I want** Role and permission changes logged  
**So that** authorization changes are tracked

**Priority:** P0  
**Story Points:** 1  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] Role creation logged
- [ ] Role updates logged
- [ ] Role assignment logged
- [ ] Role removal logged
- [ ] Permission changes logged
- [ ] Audit logs include actor and target

#### Test Scenarios

```python
def test_role_creation_creates_audit_log()
def test_role_assignment_creates_audit_log()
def test_role_removal_creates_audit_log()
def test_permission_change_creates_audit_log()
```

---

### INT-008: Role + Property Service Integration

**As a** Property service  
**I want** to check role-based permissions  
**So that** I can enforce access control

**Priority:** P1  
**Story Points:** 2  
**Sprint:** 2 (deferred)

#### Acceptance Criteria

- [ ] Property service can check if identity has permission
- [ ] Property endpoints enforce role permissions
- [ ] Property creation requires 'property.create' permission
- [ ] Property update requires 'property.update' permission
- [ ] Property deletion requires 'property.delete' permission
- [ ] Unauthorized access returns 403 status

---

## TDD Guidance

### Development Workflow

1. **Start with Models**: Create Role and Permission models
2. **Create System Roles**: Migration to create predefined roles
3. **Assignment Logic**: Implement role assignment to identities
4. **Permission Checking**: Build permission checking utilities
5. **Integration**: Test with Identity service

### Test Coverage Requirements

- **Unit Tests**: >90% coverage for models and utilities
- **Service Tests**: >90% coverage for RoleService
- **API Tests**: 100% coverage for all endpoints
- **Integration Tests**: All permission checking flows

### Key Test Patterns

```python
# Permission Checking Tests
class TestPermissionChecking:
    def test_identity_has_permission_from_role(self):
        role = create_role(permissions=['property.view'])
        identity = create_identity(roles=[role])
        assert identity.has_permission('property.view') is True
        assert identity.has_permission('property.delete') is False

    def test_multiple_roles_combine_permissions(self):
        role1 = create_role(permissions=['property.view'])
        role2 = create_role(permissions=['property.update'])
        identity = create_identity(roles=[role1, role2])
        assert identity.has_permission('property.view') is True
        assert identity.has_permission('property.update') is True

# Role Assignment Tests
class TestRoleAssignment:
    def test_assign_role_creates_audit_log(self, audit_service_mock):
        assign_role_to_identity(identity, role, assigned_by=admin)
        audit_service_mock.log.assert_called_once()
```

---

## Definition of Done - Module Level

- [ ] Role and Permission models implemented
- [ ] System roles created via migration
- [ ] Role assignment logic implemented
- [ ] Permission checking utilities created
- [ ] All API endpoints implemented
- [ ] > 90% test coverage achieved
- [ ] All integration tests passing
- [ ] Audit logging working
- [ ] Admin interface configured
- [ ] API documentation complete
- [ ] Permission matrix documented
- [ ] Code review completed
- [ ] Deployed to development environment

---

## Technical Debt & Future Enhancements

- Role hierarchy (role inheritance)
- Dynamic permission creation
- Permission groups/categories
- Role templates
- Bulk role assignment
- Role-based analytics
- Permission usage tracking
- Role expiration notifications

---

## Dependencies on Other Modules

- **Identity Module**: Roles are assigned to Identities
- **Entity Module**: Some roles may be Entity-scoped
- **Audit Module**: Role changes must be audited
- **ACL Module**: Roles provide baseline, ACL provides overrides

---

## Notes for Developers

1. **Cache permissions**: Cache Identity permissions for performance
2. **Use database indexing**: Index codename fields
3. **Validate codenames**: Ensure format is resource.action
4. **System roles immutable**: Prevent modification of system roles
5. **Test permission combinations**: Test multiple roles per identity
6. **Document new permissions**: Add to permission matrix
7. **Consider performance**: Use select_related for role queries
8. **Expiration checks**: Query should exclude expired assignments
9. **Wildcard support**: Admin role has _._ permission
10. **Permission inheritance**: Consider future role hierarchy

---

## Permission Matrix

| Resource          | Agent | Solicitor | Buyer | Admin |
| ----------------- | ----- | --------- | ----- | ----- |
| property.view     | ✅    | ✅        | ✅    | ✅    |
| property.create   | ✅    | ❌        | ❌    | ✅    |
| property.update   | ✅    | ❌        | ❌    | ✅    |
| property.delete   | ❌    | ❌        | ❌    | ✅    |
| document.view     | ✅    | ✅        | ✅    | ✅    |
| document.upload   | ✅    | ❌        | ❌    | ✅    |
| document.annotate | ✅    | ✅        | ❌    | ✅    |
| pack.view         | ✅    | ✅        | ✅    | ✅    |
| pack.create       | ✅    | ❌        | ❌    | ✅    |
| pack.signoff      | ❌    | ✅        | ❌    | ✅    |
| pack.share        | ✅    | ❌        | ❌    | ✅    |
| user.invite       | ✅    | ❌        | ❌    | ✅    |
| user.manage       | ❌    | ❌        | ❌    | ✅    |
| entity.view       | ✅    | ✅        | ❌    | ✅    |
| entity.manage     | ❌    | ❌        | ❌    | ✅    |
