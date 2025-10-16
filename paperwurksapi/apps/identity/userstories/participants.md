# Participant Module - User Stories

## Module Overview

The Participant module extends Identity with participant_type classification to influence notification routing, timeline visibility, and engagement flows in property transactions. Participants can be buyers, sellers, dual (both buyer and seller), or proxy representatives.

**Sprint:** Sprint 2+ (Future Enhancement)  
**Priority:** P2  
**Story Points:** TBD  
**Dependencies:** Identity Module, Pack Module, Property Module

## Module Responsibilities

- Classify identities by participant type (buyer, seller, dual, proxy)
- Link participants to specific transactions/properties
- Control notification routing based on participant type
- Filter timeline visibility by participant type
- Track participant engagement with packs and documents
- Support participant role changes during transaction
- Enable participant-specific workflows
- Audit participant type changes

## Participant Types

**Buyer**: Individual or entity purchasing property

- Views packs shared with them
- Receives buyer-specific notifications
- Timeline shows buyer-relevant milestones
- Can submit feedback on packs

**Seller**: Individual or entity selling property

- Views their property packs
- Receives seller-specific notifications
- Timeline shows seller-relevant milestones
- Can track buyer interest

**Dual**: Acting as both buyer and seller (e.g., chain transactions)

- Views both buyer and seller content
- Receives combined notifications
- Timeline shows all milestones
- Can participate in both workflows

**Proxy**: Acting on behalf of buyer or seller

- Views content on behalf of principal
- Receives proxy-specific notifications
- Actions attributed to proxy but linked to principal
- Requires authorization from principal

## Core User Stories (Future Sprint)

### US-PART-001: Participant Type Field

**As a** system  
**I want** participant_type field on Identity  
**So that** I can classify users by transaction role

**Priority:** P2  
**Story Points:** 3  
**Sprint:** TBD

#### Acceptance Criteria

- [ ] Identity model has participant_type field
- [ ] Participant types: buyer, seller, dual, proxy, none
- [ ] Participant type can be updated
- [ ] Multiple participant types supported (via relationship table)
- [ ] Participant type changes are audited
- [ ] Participant type influences permissions
- [ ] Default participant type is 'none'

#### Technical Specifications

**Identity Model Addition:**

```python
Identity:
    # Existing fields...
    default_participant_type: CharField(20, default='none', choices=[
        ('none', 'None'),
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('dual', 'Dual'),
        ('proxy', 'Proxy')
    ])

# New TransactionParticipant linking table
TransactionParticipant:
    - id: UUID (primary key)
    - identity: ForeignKey('Identity')
    - property: ForeignKey('Property')
    - participant_type: CharField(20)
    - represented_by: ForeignKey('Identity', null=True)  # For proxy
    - start_date: DateField()
    - end_date: DateField(null=True)
    - is_active: BooleanField(default=True)
    - metadata: JSONField(default=dict)
    - created_at: DateTimeField(auto_now_add=True)
    - updated_at: DateTimeField(auto_now=True)
```

#### Test Scenarios

```python
def test_identity_has_participant_type()
def test_participant_type_default_is_none()
def test_participant_type_validation()
def test_update_participant_type()
def test_participant_type_change_audited()
def test_transaction_participant_creation()
def test_identity_can_have_multiple_participant_roles()
```

---

### US-PART-002: Participant-Based Notifications

**As a** buyer  
**I want** to receive buyer-specific notifications  
**So that** I only see relevant updates

**Priority:** P2  
**Story Points:** 5  
**Sprint:** TBD

#### Acceptance Criteria

- [ ] Buyer receives pack sharing notifications
- [ ] Buyer receives document update notifications
- [ ] Buyer receives compliance status notifications
- [ ] Seller receives interest notifications
- [ ] Seller receives offer notifications
- [ ] Dual participants receive both notification types
- [ ] Notification preferences respect participant type
- [ ] Notification content customized by participant type

#### Technical Specifications

**Notification Routing:**

```python
class NotificationRouter:
    NOTIFICATION_TYPES_BY_PARTICIPANT = {
        'buyer': [
            'pack.shared',
            'pack.updated',
            'document.added',
            'compliance.complete',
            'search.available'
        ],
        'seller': [
            'pack.viewed',
            'buyer.interest',
            'offer.received',
            'pack.signed'
        ],
        'dual': [
            # All notifications from both buyer and seller
        ],
        'proxy': [
            # Same as principal's type
        ]
    }
```

#### Test Scenarios

```python
def test_buyer_receives_pack_shared_notification()
def test_seller_receives_interest_notification()
def test_dual_receives_both_notification_types()
def test_notification_preferences_by_participant_type()
def test_proxy_receives_principal_notifications()
```

---

### US-PART-003: Participant Timeline Visibility

**As a** buyer  
**I want** to see buyer-relevant timeline events  
**So that** my dashboard shows appropriate milestones

**Priority:** P2  
**Story Points:** 5  
**Sprint:** TBD

#### Acceptance Criteria

- [ ] Buyer timeline shows pack sharing events
- [ ] Buyer timeline shows document updates
- [ ] Buyer timeline shows search results
- [ ] Seller timeline shows buyer interest
- [ ] Seller timeline shows offer events
- [ ] Dual participants see complete timeline
- [ ] Timeline events filtered by participant type
- [ ] Timeline visibility respects ACL grants

#### Technical Specifications

**Timeline Event Visibility:**

```python
TIMELINE_EVENTS_BY_PARTICIPANT = {
    'buyer': [
        'pack.shared',
        'pack.updated',
        'document.added',
        'document.updated',
        'search.complete',
        'compliance.updated'
    ],
    'seller': [
        'pack.created',
        'pack.viewed',
        'interest.registered',
        'offer.received',
        'offer.accepted',
        'sale.agreed'
    ],
    'dual': [
        # All events
    ]
}

def get_timeline_events(identity: Identity, property_id: UUID) -> QuerySet:
    """Get timeline events visible to identity based on participant type"""
    participant = TransactionParticipant.objects.get(
        identity=identity,
        property_id=property_id,
        is_active=True
    )

    visible_event_types = TIMELINE_EVENTS_BY_PARTICIPANT.get(
        participant.participant_type,
        []
    )

    return TimelineEvent.objects.filter(
        property_id=property_id,
        event_type__in=visible_event_types
    )
```

#### Test Scenarios

```python
def test_buyer_timeline_shows_pack_events()
def test_seller_timeline_shows_interest_events()
def test_dual_timeline_shows_all_events()
def test_timeline_filtered_by_participant_type()
def test_timeline_respects_acl_grants()
```

---

### US-PART-004: Participant Pack Access

**As a** system  
**I want** participant type to influence pack visibility  
**So that** users see appropriate packs

**Priority:** P2  
**Story Points:** 5  
**Sprint:** TBD

#### Acceptance Criteria

- [ ] Buyers can view packs shared with them
- [ ] Sellers can view their property packs
- [ ] Agents can view all packs in their entity
- [ ] Dual participants can view both buyer and seller packs
- [ ] Pack access respects ACL grants
- [ ] Participant type checked before pack access
- [ ] Access denial includes reason

#### Technical Specifications

**Pack Access Control:**

```python
def can_access_pack(identity: Identity, pack: Pack) -> bool:
    """Check if identity can access pack based on participant type"""

    # Check role-based access first
    if identity.has_permission('pack.view'):
        return True

    # Check ACL grants
    if has_acl_grant(identity, 'pack', pack.id, 'pack.view'):
        return True

    # Check participant-based access
    participant = TransactionParticipant.objects.filter(
        identity=identity,
        property=pack.property,
        is_active=True
    ).first()

    if not participant:
        return False

    # Buyers can view shared packs
    if participant.participant_type == 'buyer':
        return pack.shared_with_buyers

    # Sellers can view their property packs
    if participant.participant_type == 'seller':
        return pack.property.owner == identity

    # Dual can view all
    if participant.participant_type == 'dual':
        return True

    return False
```

#### Test Scenarios

```python
def test_buyer_can_access_shared_pack()
def test_buyer_cannot_access_unshared_pack()
def test_seller_can_access_own_property_pack()
def test_dual_can_access_all_packs()
def test_pack_access_respects_acl()
def test_pack_access_denial_message()
```

---

### US-PART-005: Proxy Participant Support

**As a** proxy  
**I want** to act on behalf of a principal  
**So that** I can manage transactions for them

**Priority:** P2  
**Story Points:** 8  
**Sprint:** TBD

#### Acceptance Criteria

- [ ] Proxy can be assigned to principal
- [ ] Proxy authorization must be granted by principal
- [ ] Proxy actions attributed to proxy but linked to principal
- [ ] Proxy has same access as principal
- [ ] Proxy authorization can be revoked
- [ ] Proxy relationships are audited
- [ ] Multiple proxies can represent same principal
- [ ] Proxy cannot delegate to another proxy

#### Technical Specifications

**Proxy Authorization:**

```python
ProxyAuthorization:
    - id: UUID (primary key)
    - principal: ForeignKey('Identity')  # Person being represented
    - proxy: ForeignKey('Identity', related_name='proxies')
    - scope: CharField(50)  # 'property', 'transaction', 'all'
    - resource_id: UUIDField(null=True)  # Specific resource if scoped
    - authorized_actions: JSONField(default=list)  # Specific permissions
    - granted_at: DateTimeField(auto_now_add=True)
    - granted_by: ForeignKey('Identity')
    - expires_at: DateTimeField(null=True)
    - revoked_at: DateTimeField(null=True)
    - revoked_by: ForeignKey('Identity', null=True)
    - is_active: BooleanField(default=True)

def check_proxy_permission(proxy: Identity, principal: Identity,
                          action: str, resource: Any) -> bool:
    """Check if proxy is authorized to act on behalf of principal"""
    authorization = ProxyAuthorization.objects.filter(
        proxy=proxy,
        principal=principal,
        is_active=True,
        revoked_at__isnull=True
    ).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    ).first()

    if not authorization:
        return False

    # Check scope
    if authorization.scope != 'all':
        if resource and authorization.resource_id != resource.id:
            return False

    # Check authorized actions
    if authorization.authorized_actions:
        if action not in authorization.authorized_actions:
            return False

    return True
```

#### Test Scenarios

```python
def test_proxy_authorization_creation()
def test_proxy_can_act_on_behalf_of_principal()
def test_proxy_has_principal_access()
def test_proxy_actions_attributed_correctly()
def test_proxy_authorization_can_be_revoked()
def test_proxy_cannot_delegate()
def test_expired_proxy_authorization_invalid()
def test_scoped_proxy_authorization()
```

---

## Integration Stories

### INT-PART-001: Participant + Notification Integration

**As a** system  
**I want** notifications routed by participant type  
**So that** users receive relevant updates

**Priority:** P2  
**Story Points:** 3  
**Sprint:** TBD

#### Test Scenarios

```python
def test_notification_routing_by_participant_type()
def test_buyer_notification_content()
def test_seller_notification_content()
def test_dual_receives_all_notifications()
```

---

### INT-PART-002: Participant + Timeline Integration

**As a** system  
**I want** timeline events filtered by participant type  
**So that** dashboards show relevant information

**Priority:** P2  
**Story Points:** 3  
**Sprint:** TBD

#### Test Scenarios

```python
def test_timeline_filtering_by_participant_type()
def test_buyer_timeline_content()
def test_seller_timeline_content()
def test_dual_timeline_shows_all()
```

---

### INT-PART-003: Participant + Pack Integration

**As a** system  
**I want** pack access controlled by participant type  
**So that** access is properly scoped

**Priority:** P2  
**Story Points:** 3  
**Sprint:** TBD

#### Test Scenarios

```python
def test_pack_access_by_participant_type()
def test_buyer_pack_visibility()
def test_seller_pack_visibility()
def test_participant_type_checked_before_pack_access()
```

---

## Advanced User Stories (Future)

### US-PART-006: Participant Analytics

**As an** agent  
**I want** to see participant engagement analytics  
**So that** I can track transaction progress

**Priority:** P3  
**Story Points:** 5  
**Sprint:** TBD

#### Acceptance Criteria

- [ ] Track buyer engagement with packs
- [ ] Track seller engagement with updates
- [ ] Dashboard shows participant activity
- [ ] Analytics show time spent on documents
- [ ] Engagement score calculated per participant
- [ ] Alerts for low engagement

---

### US-PART-007: Participant Communication Preferences

**As a** buyer  
**I want** to set communication preferences  
**So that** I control how I'm contacted

**Priority:** P3  
**Story Points:** 3  
**Sprint:** TBD

#### Acceptance Criteria

- [ ] Participant can set preferred contact method
- [ ] Participant can set contact hours
- [ ] Participant can opt out of certain notification types
- [ ] Preferences respect participant type
- [ ] Preferences stored in profile metadata

---

## TDD Guidance

### Development Workflow

1. **Start with Field**: Add participant_type to Identity
2. **Transaction Linking**: Create TransactionParticipant model
3. **Notification Routing**: Implement participant-based routing
4. **Timeline Filtering**: Filter events by participant type
5. **Pack Access**: Implement participant-based access control
6. **Proxy Support**: Add proxy authorization system

### Test Coverage Requirements

- **Unit Tests**: >90% coverage for participant logic
- **Service Tests**: >90% coverage for participant services
- **Integration Tests**: All participant flows tested
- **Access Control Tests**: Comprehensive permission testing

---

## Definition of Done - Module Level

- [ ] Participant type field added to Identity
- [ ] TransactionParticipant model created
- [ ] Notification routing by participant type working
- [ ] Timeline filtering by participant type working
- [ ] Pack access control by participant type working
- [ ] Proxy authorization system implemented
- [ ] > 90% test coverage achieved
- [ ] All integration tests passing
- [ ] Audit logging working
- [ ] API documentation complete
- [ ] Code review completed

---

## Technical Debt & Future Enhancements

- Participant role transitions (buyer becomes seller)
- Participant groups (multiple buyers)
- Participant verification workflows
- Participant onboarding flows
- Participant communication history
- Participant satisfaction tracking
- Automated participant classification
- Machine learning for participant behavior prediction

---

## Dependencies on Other Modules

- **Identity Module**: Participant extends Identity
- **Property Module**: Participants linked to Properties
- **Pack Module**: Participant type controls pack access
- **Notification Module**: Routing depends on participant type
- **Timeline Module**: Event visibility filtered by participant type
- **Engagement Module**: Tracks participant interactions

---

## Notes for Developers

1. **Participant type vs Role**: Participant type is transaction-specific, Role is system-wide
2. **Multiple transactions**: Identity can have different participant types per transaction
3. **Proxy chain prevention**: Proxy cannot authorize another proxy
4. **Privacy**: Respect participant privacy preferences
5. **Audit trail**: Log all participant type changes
6. **Performance**: Index participant queries
7. **Caching**: Cache participant access checks
8. **Validation**: Validate participant type transitions
9. **Notifications**: Batch notifications by participant type
10. **Testing**: Test all participant type combinations

---

## Participant Type State Machine

```
none --> buyer
none --> seller
none --> dual
none --> proxy

buyer --> dual (when also selling)
seller --> dual (when also buying)
dual --> buyer (when sale completes)
dual --> seller (when purchase completes)

proxy --> none (when authorization revoked)

* All transitions should be audited
* Transitions should trigger notification routing updates
```

---

## API Endpoints (Future Sprint)

```
GET /api/participants/me
# Get current user's participant roles

GET /api/properties/{id}/participants
# List all participants for a property

POST /api/properties/{id}/participants
# Add participant to property transaction

PATCH /api/participants/{id}
# Update participant type

DELETE /api/participants/{id}
# Remove participant from transaction

POST /api/participants/{id}/authorize-proxy
# Authorize proxy to act on behalf

DELETE /api/participants/{id}/revoke-proxy
# Revoke proxy authorization

GET /api/participants/{id}/timeline
# Get participant-specific timeline

GET /api/participants/{id}/notifications
# Get participant-specific notifications
```
