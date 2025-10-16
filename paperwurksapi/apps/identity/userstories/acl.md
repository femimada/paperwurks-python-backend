# ACL Module - User Stories

## Module Overview

The ACL (Access Control List) module provides fine-grained, resource-level permission overrides beyond role-based access control. ACLs enable specific users to access specific resources (properties, packs, documents) even if their role wouldn't normally grant that access.

**Sprint:** Sprint 1B (Week 5-6)  
**Priority:** P0 - Critical  
**Dependencies:** Identity Module, Role Module

## Module Responsibilities

- Grant resource-specific permissions to identities
- Override role-based permissions for specific resources
- Support temporary (expiring) access grants
- Track who granted access and when
- Audit all grant and revoke operations
- Provide efficient permission checking for resources
- Support bulk grant operations
- Enable permission delegation

## ACL Use Cases

1. **Buyer Access**: Grant buyer permission to view specific property pack
2. **Solicitor Assignment**: Grant solicitor access to specific properties
3. **Temporary Sharing**: Grant time-limited access to documents
4. **Cross-Entity Collaboration**: Grant access to resources outside entity boundary
5. **Emergency Access**: Grant temporary elevated permissions

## Core User Stories

### US-018: ACL Model Implementation

**As a** system  
**I want** ACL model for resource-specific permissions  
**So that** I can grant fine-grained access beyond roles

**Priority:** P0  
**Story Points:** 8  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] ACL model created with all required fields
- [ ] ACL links Identity, Resource, and Permission
- [ ] ACL supports resource_type and resource_id (polymorphic)
- [ ] ACL tracks who granted access and when
- [ ] ACL supports expiration timestamps
- [ ] ACL supports revocation with tracking
- [ ] ACL grants can be queried efficiently
- [ ] ACL integrates with permission checking
- [ ] Audit logging for all ACL operations

#### Technical Specifications

**Model Fields:**

```python
ACL:
    - id: UUID (primary key)
    - identity: ForeignKey('Identity')
    - resource_type: CharField(50)  # 'property', 'pack', 'document'
    - resource_id: UUIDField()  # ID of the specific resource
    - permission: ForeignKey('Permission')
    - granted_by: ForeignKey('Identity', related_name='acls_granted')
    - granted_at: DateTimeField(auto_now_add=True)
    - expires_at: DateTimeField(null=True, blank=True)
    - revoked_at: DateTimeField(null=True, blank=True)
    - revoked_by: ForeignKey('Identity', null=True, related_name='acls_revoked')
    - revoke_reason: TextField(null=True, blank=True)
    - metadata: JSONField(default=dict)  # Additional context
    - created_at: DateTimeField(auto_now_add=True)
    - updated_at: DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            ('identity', 'resource_type', 'resource_id', 'permission')
        ]
        indexes = [
            models.Index(fields=['identity', 'resource_type', 'resource_id']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['revoked_at'])
        ]
```

**Helper Methods:**

```python
class ACL(models.Model):
    def is_active(self) -> bool:
        """Check if ACL grant is currently active"""
        if self.revoked_at:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def revoke(self, revoked_by: Identity, reason: str = None):
        """Revoke this ACL grant"""
        self.revoked_at = timezone.now()
        self.revoked_by = revoked_by
        self.revoke_reason = reason
        self.save()

    def extend(self, new_expires_at: datetime):
        """Extend the expiration date"""
        self.expires_at = new_expires_at
        self.save()
```

#### Test Scenarios

**Unit Tests:**

```python
def test_acl_creation_with_required_fields()
def test_acl_unique_constraint()
def test_acl_is_active_when_not_expired()
def test_acl_is_inactive_when_expired()
def test_acl_is_inactive_when_revoked()
def test_acl_revoke_sets_timestamps()
def test_acl_extend_updates_expiration()
def test_acl_query_active_grants()
def test_acl_query_by_resource()
def test_acl_query_by_identity()
```

**Service Tests:**

```python
def test_grant_acl_to_identity()
def test_grant_acl_creates_audit_log()
def test_grant_acl_validates_permission_exists()
def test_revoke_acl()
def test_revoke_acl_creates_audit_log()
def test_check_acl_permission()
def test_list_active_acls_for_identity()
def test_list_acls_for_resource()
def test_bulk_grant_acls()
```

**API Tests:**

```python
def test_grant_acl_endpoint_returns_201()
def test_grant_acl_requires_permission()
def test_grant_acl_validates_resource_exists()
def test_revoke_acl_endpoint()
def test_list_acls_for_identity()
def test_list_acls_for_resource()
```

**Integration Tests:**

```python
def test_acl_grant_overrides_role_permission()
def test_expired_acl_does_not_grant_permission()
def test_revoked_acl_does_not_grant_permission()
def test_acl_with_property_service()
def test_acl_audit_trail()
```

#### Dependencies

- Identity module for identity linkage
- Role module for permission definitions
- Audit service for grant/revoke logging

#### Definition of Done

- [ ] ACL model created with all fields
- [ ] Model validation implemented
- [ ] Helper methods implemented
- [ ] Database indexes created
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] Admin interface configured
- [ ] Code reviewed and approved

---

### US-019: ACL Grant Management

**As an** admin or resource owner  
**I want to** grant ACL permissions to specific users  
**So that** they can access specific resources

**Priority:** P0  
**Story Points:** 5  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] User can grant permission to another user for specific resource
- [ ] Grant specifies identity, resource, and permission
- [ ] Grant can include expiration date
- [ ] Grant validates that resource exists
- [ ] Grant validates that permission exists
- [ ] Grant creates audit log entry
- [ ] Duplicate grants are prevented
- [ ] Grant can be extended before expiration
- [ ] Only authorized users can grant permissions

#### Technical Specifications

**API Endpoints:**

```
POST /api/acls/grant
Request Body:
{
    "identity_id": "uuid",
    "resource_type": "pack",
    "resource_id": "uuid",
    "permission_codename": "pack.view",
    "expires_at": "2025-12-31T23:59:59Z",  # optional
    "metadata": {
        "reason": "Buyer request",
        "reference": "PROP-12345"
    }
}

Response (201 Created):
{
    "id": "uuid",
    "identity": {
        "id": "uuid",
        "email": "buyer@example.com",
        "name": "John Buyer"
    },
    "resource_type": "pack",
    "resource_id": "uuid",
    "permission": "pack.view",
    "granted_by": {
        "id": "uuid",
        "email": "agent@example.com"
    },
    "granted_at": "2025-01-15T10:00:00Z",
    "expires_at": "2025-12-31T23:59:59Z",
    "is_active": true
}

POST /api/acls/{id}/extend
Request Body:
{
    "new_expires_at": "2026-06-30T23:59:59Z"
}

Response (200 OK):
{...}

GET /api/acls
Query Params:
  ?identity_id=uuid
  &resource_type=pack
  &resource_id=uuid
  &is_active=true

Response (200 OK):
{
    "count": 5,
    "results": [...]
}
```

**Permission Requirements:**

- Granting user must have `acl.grant` permission OR be resource owner
- System admins can always grant ACLs
- Entity admins can grant ACLs within their entity

#### Test Scenarios

**Service Tests:**

```python
def test_grant_acl_success()
def test_grant_acl_to_buyer_for_pack()
def test_grant_acl_with_expiration()
def test_grant_acl_validates_resource_exists()
def test_grant_acl_validates_permission_exists()
def test_grant_acl_validates_identity_exists()
def test_grant_acl_prevents_duplicates()
def test_extend_acl_expiration()
def test_grant_acl_creates_audit_log()
def test_bulk_grant_acls_to_multiple_users()
```

**API Tests:**

```python
def test_grant_acl_endpoint_requires_permission()
def test_grant_acl_endpoint_validates_data()
def test_grant_acl_endpoint_returns_201()
def test_extend_acl_endpoint()
def test_list_acls_filtered_by_identity()
def test_list_acls_filtered_by_resource()
def test_list_acls_only_active()
def test_unauthorized_user_cannot_grant_acl()
```

**Integration Tests:**

```python
def test_grant_acl_flow_end_to_end()
def test_buyer_can_access_pack_after_grant()
def test_buyer_cannot_access_pack_after_expiration()
def test_grant_audit_trail_complete()
```

#### Definition of Done

- [ ] Grant service method implemented
- [ ] Grant API endpoint created
- [ ] Extend functionality working
- [ ] All unit tests passing (>90% coverage)
- [ ] All integration tests passing
- [ ] Audit logging confirmed working
- [ ] Permission validation working
- [ ] API documentation updated
- [ ] Code reviewed and approved

---

### US-020: ACL Expiration Management

**As a** system  
**I want** ACL grants to expire automatically  
**So that** temporary access is time-limited

**Priority:** P1  
**Story Points:** 3  
**Sprint:** 2 (deferred from 1B)

#### Acceptance Criteria

- [ ] ACL grants can have expiration date
- [ ] Expired ACL grants do not confer permissions
- [ ] System can query expiring grants
- [ ] Notifications sent before expiration
- [ ] Automatic cleanup of old expired grants
- [ ] Grace period for renewal
- [ ] Expiration tracked in audit logs

#### Technical Specifications

**Expiration Check:**

```python
def get_active_acls(identity, resource_type=None, resource_id=None):
    """Get all active ACL grants for identity"""
    queryset = ACL.objects.filter(
        identity=identity,
        revoked_at__isnull=True
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    )

    if resource_type:
        queryset = queryset.filter(resource_type=resource_type)
    if resource_id:
        queryset = queryset.filter(resource_id=resource_id)

    return queryset
```

**Management Command:**

```bash
# python manage.py expire_acls
# Sends notifications for expiring ACLs and cleans up old ones
```

**Notification Schedule:**

```python
EXPIRATION_WARNINGS = {
    '7_days': timedelta(days=7),
    '1_day': timedelta(days=1),
    '1_hour': timedelta(hours=1)
}
```

#### Test Scenarios

**Unit Tests:**

```python
def test_acl_is_active_before_expiration()
def test_acl_is_inactive_after_expiration()
def test_query_expiring_acls()
def test_grace_period_logic()
```

**Service Tests:**

```python
def test_get_expiring_acls_within_days()
def test_send_expiration_notifications()
def test_cleanup_old_expired_acls()
def test_expired_acl_does_not_grant_permission()
```

**Integration Tests:**

```python
def test_expiration_notification_flow()
def test_automatic_cleanup_celery_task()
def test_expired_acl_prevents_resource_access()
```

#### Definition of Done

- [ ] Expiration checking implemented
- [ ] Notification system working
- [ ] Cleanup task created
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Management command documented
- [ ] Code reviewed and approved

---

### US-022: ACL Audit Logging

**As a** compliance officer  
**I want** all ACL grants and revocations logged  
**So that** access changes are tracked for audit

**Priority:** P0  
**Story Points:** 3  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] Audit log created for every ACL grant
- [ ] Audit log created for every ACL revoke
- [ ] Audit log created for every ACL extension
- [ ] Audit logs include grantor and grantee
- [ ] Audit logs include resource details
- [ ] Audit logs include permission details
- [ ] Audit logs include expiration information
- [ ] Audit logs are immutable
- [ ] Audit logs are queryable

#### Technical Specifications

**Audit Event Types:**

```python
class ACLEventType(Enum):
    GRANT = 'acl.grant'
    REVOKE = 'acl.revoke'
    EXTEND = 'acl.extend'
    EXPIRE = 'acl.expire'
```

**Audit Log Structure:**

```python
{
    "event_type": "acl.grant",
    "actor_id": "granter_uuid",
    "target_id": "grantee_uuid",
    "resource_type": "pack",
    "resource_id": "resource_uuid",
    "permission": "pack.view",
    "expires_at": "2025-12-31T23:59:59Z",
    "metadata": {
        "reason": "Buyer request",
        "reference": "PROP-12345"
    },
    "timestamp": "2025-01-15T10:00:00Z"
}
```

#### Test Scenarios

**Service Tests:**

```python
def test_acl_grant_creates_audit_log()
def test_acl_revoke_creates_audit_log()
def test_acl_extend_creates_audit_log()
def test_audit_log_includes_all_details()
def test_audit_log_immutable()
```

**Integration Tests:**

```python
def test_acl_operations_audit_trail()
def test_query_acl_audit_logs()
def test_audit_logs_persist_after_acl_deletion()
```

#### Definition of Done

- [ ] Audit logging integrated for all ACL operations
- [ ] All unit tests passing (>90% coverage)
- [ ] Integration with AuditService confirmed
- [ ] Audit logs are immutable
- [ ] Query functionality working
- [ ] Documentation updated

---

## Integration Stories

### INT-009: ACL + Permission Checking

**As a** system  
**I want** ACL grants checked during permission validation  
**So that** resource-specific access is enforced

**Priority:** P0  
**Story Points:** 3  
**Sprint:** 1B

#### Acceptance Criteria

- [ ] Permission checking includes ACL grants
- [ ] ACL grants can override role restrictions
- [ ] ACL grants are checked after role permissions
- [ ] Expired/revoked ACL grants are ignored
- [ ] Permission checking is performant (cached)
- [ ] Permission denial includes reason

#### Technical Specifications

**Permission Checking Flow:**

```python
def has_permission(identity, permission_codename, resource_type=None, resource_id=None):
    """
    Check if identity has permission
    1. Check role-based permissions (baseline)
    2. If resource specified, check ACL grants (override)
    3. Return True if either grants permission
    """
    # Check role permissions
    if identity.has_role_permission(permission_codename):
        return True

    # Check ACL if resource specified
    if resource_type and resource_id:
        acl_grants = ACL.objects.filter(
            identity=identity,
            resource_type=resource_type,
            resource_id=resource_id,
            permission__codename=permission_codename,
            revoked_at__isnull=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        ).exists()

        if acl_grants:
            return True

    return False
```

#### Test Scenarios

```python
def test_acl_grant_allows_access_without_role()
def test_role_permission_alone_allows_access()
def test_acl_grant_overrides_role_restriction()
def test_expired_acl_does_not_grant_access()
def test_revoked_acl_does_not_grant_access()
def test_permission_checking_performance()
def test_permission_denial_includes_reason()
```

---

### INT-010: ACL + Resource Services Integration

**As a** resource service (Property, Pack, Document)  
**I want** to check ACL permissions  
**So that** resource access is controlled

**Priority:** P1  
**Story Points:** 3  
**Sprint:** 2

#### Acceptance Criteria

- [ ] Property service checks ACL for property access
- [ ] Pack service checks ACL for pack access
- [ ] Document service checks ACL for document access
- [ ] ACL checking integrated in service layer
- [ ] ACL checking integrated in API endpoints
- [ ] 403 errors returned for denied access

#### Test Scenarios

```python
def test_property_view_with_acl_grant()
def test_property_view_without_acl_grant()
def test_pack_view_buyer_with_acl()
def test_document_download_with_acl()
def test_resource_access_denied_without_acl()
```

---

## Advanced User Stories (Sprint 2+)

### US-021-FUTURE: Bulk ACL Operations

**As an** admin  
**I want** to grant ACLs to multiple users at once  
**So that** I can efficiently manage pack sharing

**Priority:** P2  
**Story Points:** 5  
**Sprint:** 2

#### Acceptance Criteria

- [ ] Grant same permission to multiple identities
- [ ] Grant multiple permissions to same identity
- [ ] Bulk revoke operations
- [ ] Bulk operation validation
- [ ] Bulk operation atomic (all or nothing)
- [ ] Bulk operations logged as single audit event

---

### US-022-FUTURE: ACL Delegation

**As a** resource owner  
**I want** to delegate ACL granting authority  
**So that** others can share my resources

**Priority:** P2  
**Story Points:** 5  
**Sprint:** 3

#### Acceptance Criteria

- [ ] Resource owner can delegate grant authority
- [ ] Delegated user can grant permissions
- [ ] Delegation has limits (what can be granted)
- [ ] Delegation can be revoked
- [ ] Delegation is audited

---

## TDD Guidance

### Development Workflow

1. **Start with Model**: Create ACL model
2. **Permission Checking**: Implement permission checking logic
3. **Grant/Revoke**: Implement grant and revoke operations
4. **Expiration**: Implement expiration logic
5. **Audit**: Integrate with audit service
6. **Integration**: Test with resource services

### Test Coverage Requirements

- **Unit Tests**: >90% coverage for ACL model and utilities
- **Service Tests**: >90% coverage for ACLService
- **API Tests**: 100% coverage for all endpoints
- **Integration Tests**: All permission flows tested

### Key Test Patterns

```python
# ACL Permission Tests
class TestACLPermissions:
    def test_acl_grants_permission_without_role(self):
        identity = create_identity()  # No role permissions
        pack = create_pack()
        grant_acl(identity, 'pack', pack.id, 'pack.view')
        assert identity.has_permission('pack.view', 'pack', pack.id) is True

    def test_expired_acl_does_not_grant_permission(self):
        identity = create_identity()
        pack = create_pack()
        acl = grant_acl(
            identity, 'pack', pack.id, 'pack.view',
            expires_at=timezone.now() - timedelta(days=1)
        )
        assert identity.has_permission('pack.view', 'pack', pack.id) is False

# ACL Audit Tests
class TestACLAudit:
    def test_grant_creates_audit_log(self, audit_service_mock):
        grant_acl(identity, 'pack', pack.id, 'pack.view')
        audit_service_mock.log.assert_called_once_with(
            event_type='acl.grant',
            ...
        )
```

---

## Definition of Done - Module Level

- [ ] ACL model implemented with all fields
- [ ] Grant and revoke logic implemented
- [ ] Expiration handling working
- [ ] Permission checking integrated with ACL
- [ ] All API endpoints implemented
- [ ] > 90% test coverage achieved
- [ ] All integration tests passing
- [ ] Audit logging working for all operations
- [ ] Performance optimized (queries, indexes)
- [ ] Admin interface configured
- [ ] API documentation complete
- [ ] Code review completed
- [ ] Deployed to development environment

---

## Performance Considerations

### Indexing Strategy

```python
# Critical indexes for ACL queries
indexes = [
    ('identity', 'resource_type', 'resource_id'),  # Permission checking
    ('resource_type', 'resource_id'),              # Resource ACL listing
    ('expires_at',),                               # Expiration queries
    ('revoked_at',),                               # Active ACL filtering
]
```

### Caching Strategy

```python
# Cache ACL permissions for identities
cache_key = f"acl:permissions:{identity.id}:{resource_type}:{resource_id}"
cache_timeout = 300  # 5 minutes

# Invalidate cache on ACL grant/revoke
def invalidate_acl_cache(identity_id, resource_type, resource_id):
    cache_key = f"acl:permissions:{identity_id}:{resource_type}:{resource_id}"
    cache.delete(cache_key)
```

### Query Optimization

```python
# Use select_related to reduce queries
acls = ACL.objects.filter(...).select_related(
    'identity',
    'permission',
    'granted_by'
)

# Prefetch ACLs when loading resources
packs = Pack.objects.prefetch_related(
    Prefetch('acls', queryset=ACL.objects.filter(revoked_at__isnull=True))
)
```

---

## Technical Debt & Future Enhancements

- ACL templates for common grant patterns
- ACL groups (grant to group of users)
- ACL inheritance (child resources inherit parent ACLs)
- ACL approval workflow (require approval before grant)
- ACL analytics and reporting
- ACL notifications for grantees
- ACL auto-renewal options
- Conditional ACLs (based on attributes)

---

## Dependencies on Other Modules

- **Identity Module**: ACLs are granted to Identities
- **Role Module**: ACLs use Permission definitions
- **Audit Module**: ACL operations must be audited
- **Property Module**: ACLs control property access
- **Pack Module**: ACLs control pack access
- **Document Module**: ACLs control document access

---

## Notes for Developers

1. **Always check expiration**: Query should filter expired ACLs
2. **Always check revocation**: Query should filter revoked ACLs
3. **Use transactions**: Grant/revoke should be atomic
4. **Cache wisely**: Cache permission checks but invalidate on changes
5. **Index properly**: Critical for permission checking performance
6. **Audit everything**: Every ACL operation must be logged
7. **Validate resources**: Ensure resource exists before granting ACL
8. **Handle conflicts**: Prevent duplicate grants gracefully
9. **Test edge cases**: Expired, revoked, non-existent resources
10. **Security first**: Validate granter has permission to grant
