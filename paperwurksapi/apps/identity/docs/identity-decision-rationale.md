# Identity App - Design Decisions & Rationale

**Document Type:** Architecture Decision Record  
**Date:** October 16, 2025  
**Status:** Approved  
**Decision Maker:** CTO + Backend Lead  
**Stakeholders:** Backend Team, Product Team

---

## Executive Summary

This document captures the key architectural decisions made for the Paperwurks Identity app, including the rationale for building a custom IAM system rather than using Django's built-in authentication, and why multi-tenancy is critical for our business model.

**Key Decisions:**

1. ✅ Build custom Identity app (not Django's built-in User/Groups)
2. ✅ Implement Entity model for multi-tenancy
3. ✅ Build custom ACL system for resource-level permissions
4. ✅ Split EPIC-002 into two sprints (4 weeks total)
5. ✅ Defer MFA to Sprint 2

**Investment:** 4 weeks development time  
**Justification:** SaaS platform serving multiple independent organizations requires sophisticated multi-tenancy and access control

---

## Table of Contents

1. [The Core Question](#the-core-question)
2. [Django vs Custom Authentication](#django-vs-custom-authentication)
3. [Understanding Multi-Tenancy](#understanding-multi-tenancy)
4. [Business Model Analysis](#business-model-analysis)
5. [Final Design Decision](#final-design-decision)
6. [Missing Features Analysis](#missing-features-analysis)
7. [Implementation Trade-offs](#implementation-trade-offs)
8. [Lessons Learned](#lessons-learned)

---

## The Core Question

### Initial Challenge

**Question:** Why build a custom Identity system when Django provides User, Groups, and Permissions out of the box?

**Concern:** Are we over-engineering a solution that could be solved with standard Django patterns?

**Stakes:** 4 weeks of development time vs 3 days using Django defaults

---

## Django vs Custom Authentication

### What Django Provides

Django's built-in authentication system includes:

```python
from django.contrib.auth.models import User, Group, Permission

# Users
user = User.objects.create_user('john@example.com', password='...')

# Groups (similar to Roles)
agents = Group.objects.create(name='Estate Agents')
agents.permissions.add(permission)

# Assign user to group
user.groups.add(agents)

# Check permissions
if user.has_perm('property.add_property'):
    # Allow action
```

**Strengths:**

- ✅ Battle-tested across millions of deployments
- ✅ Extensive documentation and community support
- ✅ Works seamlessly with Django Admin
- ✅ Compatible with third-party packages (django-allauth, django-guardian)
- ✅ Every Django developer understands it
- ✅ Can be implemented in 2-3 days
- ✅ Less custom code to maintain

**Limitations for Paperwurks:**

- ❌ No built-in multi-tenancy (can't scope by organization)
- ❌ Permissions are model-level only (can't grant access to specific property)
- ❌ No flexible metadata storage for role-specific data
- ❌ No support for transaction-specific roles
- ❌ No built-in comprehensive audit trail
- ❌ Not designed for JWT-first API architecture

### Our Custom Identity Design

**Components:**

- Identity (core principal)
- Entity (multi-tenancy scoping)
- Role (RBAC like Django Groups)
- Permission (like Django Permissions)
- ACL (resource-level permissions)
- Profile (flexible metadata)
- Participant (transaction roles - future)

**Strengths:**

- ✅ Multi-tenancy built into data model (Entity scopes everything)
- ✅ Resource-level permissions (grant buyer access to specific pack)
- ✅ Flexible metadata per role (SRA numbers, certifications)
- ✅ Transaction-specific roles (buyer on property A, seller on property B)
- ✅ Comprehensive audit trail by design
- ✅ JWT-first architecture for API
- ✅ Optimized for SaaS use case

**Weaknesses:**

- ❌ 6 custom models to maintain
- ❌ 4 weeks to build vs 3 days
- ❌ Custom code increases bug surface area
- ❌ Team learning curve
- ❌ Can't leverage Django Admin easily
- ❌ Reinventing some wheels

### Hybrid Approach Considered

**Concept:** Extend Django's User instead of replacing it

```python
from django.contrib.auth.models import AbstractUser, Group as Role

class Identity(AbstractUser):
    """Extend Django's User, don't replace it"""
    entity = ForeignKey('Entity')  # Add multi-tenancy
    participant_type = CharField(...)  # Add transaction role

# Use Django's Group as Role
Role = Group

# Add only what Django lacks
class Entity(Model):  # Multi-tenancy
    name = CharField(...)

class ACL(Model):  # Resource-level permissions
    identity = ForeignKey(Identity)
    resource_type = CharField(...)
    resource_id = UUIDField()
    permission = ForeignKey(Permission)

class Profile(Model):  # Flexible metadata
    user = OneToOneField(Identity)
    metadata = JSONField()
```

**Analysis:**

- Would save ~40% of development time
- Leverages Django's battle-tested auth
- Still requires Entity + ACL (the complex parts)
- Profile could be a simple extension
- **At 60% custom code anyway**, full custom gives more control

**Decision:** Rejected - if we're building 60% custom already, go 100% for full control and optimization

---

## Understanding Multi-Tenancy

### What is Multi-Tenancy?

**Simple Definition:** Multiple independent organizations use the same application and database, but their data must be completely isolated.

**Not Multi-Tenancy:**

- One company with multiple departments
- One organization with multiple teams
- Internal tool for a single business

**Is Multi-Tenancy:**

- Salesforce serving thousands of companies
- Slack serving thousands of workspaces
- Paperwurks serving hundreds of estate agencies

### The Paperwurks Scenario

**Multiple Independent Organizations Share the Platform:**

**ABC Estate Agency (London)**

- 15 agents
- 200 properties listed
- Works with 5 solicitor firms
- **MUST NOT see XYZ's data**

**XYZ Estate Agency (Manchester)**

- 10 agents
- 150 properties listed
- Works with 3 solicitor firms
- **MUST NOT see ABC's data**

**Smith & Associates Law (London Solicitors)**

- 8 solicitors
- Reviews packs for BOTH ABC and XYZ
- Has own client properties
- **Needs cross-organization access**

### Without Multi-Tenancy (Disaster Scenario)

```python
# User logs in
agent_john = User.objects.get(email='john@abcestates.com')

# Query returns EVERYTHING across ALL companies
properties = Property.objects.all()
# Returns: ABC's + XYZ's + Everyone else's properties

# Every query must manually filter
properties = Property.objects.filter(agency=user.agency)
# Forget once? Data leak. GDPR breach. Competitive disaster.
```

**Problems:**

- ❌ 500+ queries across codebase = 500 opportunities for mistakes
- ❌ One forgotten filter = security breach
- ❌ Competitive information leakage
- ❌ GDPR violations
- ❌ Legal liability

### With Multi-Tenancy (Entity Design)

```python
# User logs in
agent_john = User.objects.get(email='john@abcestates.com')
# agent_john.entity = Entity(name="ABC Estate Agency")

# Every model linked to Entity
class Property(Model):
    entity = ForeignKey(Entity)  # Data isolation boundary
    address = CharField(...)

# Queries automatically scoped
properties = Property.objects.filter(entity=agent_john.entity)
# Returns: ONLY ABC's properties - NEVER XYZ's

# Security enforced at model level, not query level
```

**Benefits:**

- ✅ Data isolation enforced structurally
- ✅ Cannot accidentally leak data between organizations
- ✅ GDPR compliance by design
- ✅ Competitive information protected
- ✅ Clear security boundaries

### Cross-Organization Collaboration (Why ACL is Needed)

**Scenario:** Solicitor works with multiple agencies

```python
# Jane's base entity
jane.entity = Entity(name="Smith & Associates")

# ACL grants for specific properties (crossing entity boundaries)
ACL.create(
    identity=jane,
    resource_type='property',
    resource_id='abc-property-123',
    permission='property.view'
)

ACL.create(
    identity=jane,
    resource_type='property',
    resource_id='xyz-property-456',
    permission='property.view'
)

# Jane sees:
# - Her firm's data (via Entity)
# - ABC Property 123 (via ACL grant)
# - XYZ Property 456 (via ACL grant)
# - Nothing else
```

**This requires both Entity (baseline isolation) and ACL (controlled exceptions).**

---

## Business Model Analysis

### Critical Evidence from Project Documents

#### 1. MVP Launch Targets (EPIC-010)

From sprint plan:

- **"5 estate agents onboarded"**
- **"5 solicitors active"**
- **"First property transaction completed"**

**Interpretation:** Not 5 employees - these are 5 different **customer organizations**.

#### 2. Platform Vision

From "About Paperwurks":

> "Marketplace Vision: Long-term, Paperwurks becomes a full-featured listing and transaction platform—**rivaling Rightmove and Zoopla**"

**Rightmove/Zoopla serve thousands of independent estate agencies.** Paperwurks has the same ambition.

#### 3. Go-to-Market Strategy

From investor Q&A:

> "We're **targeting forward-thinking estate agents and solicitors** who already feel the pain... Once they see Paperwurks reduce time-to-exchange... **they become our evangelists**"

**Interpretation:** Acquiring **multiple independent professional firms** as customers.

#### 4. Customer Success Function

From sprint plan:

> "US-050: As a **customer success manager**, I need onboarding process for **new agents**"

**You don't need customer success for internal employees - only for external SaaS customers.**

#### 5. Cross-Organization Workflow

From "Key Actors":

- **Estate Agent** (independent business) manages properties
- **Solicitor** (different independent firm) reviews packs
- **Buyer** (consumer) views packs
- Multiple independent firms collaborating on shared transactions

### Business Model Conclusion

**Paperwurks is a B2B SaaS platform** serving:

- Multiple independent estate agencies
- Multiple independent law firms
- Consumers (buyers/sellers)
- Enabling cross-organization collaboration on property transactions

**This is NOT:**

- Internal tool for one company
- Custom deployment per customer
- Single-tenant application

**This IS:**

- Multi-tenant SaaS (like Salesforce, Slack, Stripe)
- One platform URL: app.paperwurks.com
- Hundreds of future customers
- Data isolation required by law (GDPR) and competition

---

## Final Design Decision

### Decision: Build Custom Identity App with Full Multi-Tenancy

**Rationale:**

#### 1. Multi-Tenancy is Non-Negotiable

- SaaS business model confirmed
- Multiple independent organizations will use platform
- GDPR requires data isolation
- Competitive information must be protected
- Entity model is **critical infrastructure**

#### 2. Resource-Level Permissions Required

- Solicitors work with multiple agencies
- Buyers need access to specific packs
- Cross-organization collaboration is core workflow
- ACL system is **essential for business logic**

#### 3. Complex Role Requirements

- Same person can be buyer and seller
- Transaction-specific roles needed
- Role-specific metadata (SRA numbers, certifications)
- Participant model needed (future sprint)

#### 4. Audit Trail Mandatory

- Legal compliance requirement
- Dispute resolution dependency
- GDPR right-to-access requirement
- Must log all permission changes

#### 5. Hybrid Approach Insufficient

At 60% custom code (Entity + ACL + Profile), the benefits of Django's auth are diluted:

- Still need to maintain complex custom models
- Still need custom permission logic
- Still need to work around Django's assumptions
- **Might as well own 100% for full optimization**

### Components Built

**Sprint 1A (Core):**

- Identity model (authentication principal)
- Entity model (multi-tenancy boundary)
- JWT authentication
- Password management
- Email verification
- Audit logging integration

**Sprint 1B (Authorization):**

- Role model (RBAC baseline)
- Permission model (action definitions)
- ACL model (resource-level overrides)
- Profile model (flexible metadata)
- Permission middleware
- Integration with other services

**Sprint 2+ (Enhancement):**

- MFA implementation
- Participant model (transaction roles)
- Permission caching
- Advanced ACL features

### Investment Justified

**Time Investment:** 4 weeks (Sprint 1A + 1B)  
**Alternative Time:** 3 days (Django built-in + basic extensions)  
**Extra Investment:** ~3.5 weeks

**Return on Investment:**

- ✅ Proper multi-tenancy from day one
- ✅ Scalable to thousands of customers
- ✅ No refactoring needed when scaling
- ✅ GDPR-compliant architecture
- ✅ Optimized for SaaS use case
- ✅ Full control over data model
- ✅ Foundation for marketplace features

**Cost of Wrong Decision:**

- ❌ Refactoring after 6 months: 8-12 weeks
- ❌ Data migration: 2-4 weeks
- ❌ Customer downtime during migration
- ❌ Potential data leakage incidents
- ❌ Technical debt accumulation

**Verdict:** 3.5 extra weeks now prevents 10-16 weeks of refactoring later.

---

## Missing Features Analysis

### MFA (Multi-Factor Authentication)

**Status:** Deferred to Sprint 2  
**Story Points:** 8  
**Priority:** P1 (should have, not must have)

#### Why Deferred?

1. **Sprint Capacity:** Sprint 1A/1B already at 29 points each (at capacity)
2. **Foundation First:** Core authentication must work before adding MFA
3. **Complexity:** TOTP implementation + QR codes + authenticator app testing
4. **Not MVP Blocker:** Users can still register and login securely without MFA

#### Current Workaround

**What works without MFA:**

- Strong password requirements (8+ chars, mixed case, numbers, special chars)
- Password reset flow via email
- Rate limiting on login attempts
- JWT token expiration (1 hour)
- Email verification required

**What's missing:**

- Second factor authentication
- TOTP/authenticator app support
- SMS verification codes
- Backup codes

#### Sprint 2 MFA Implementation Plan

**Simplified approach (5 points):**

```python
# Add to Identity model
mfa_enabled = BooleanField(default=False)
mfa_secret = CharField(null=True)  # TOTP secret

# API endpoints
POST /api/auth/mfa/enable
POST /api/auth/mfa/verify
POST /api/auth/mfa/disable

# Login flow with MFA
1. User enters email/password
2. If mfa_enabled: Request TOTP code
3. Verify TOTP code
4. Issue JWT tokens
```

**Dependencies:**

- `pyotp` library for TOTP
- `qrcode` library for QR generation
- Profile module for user preferences

**Decision:** Can launch MVP without MFA, add as security enhancement in Sprint 2.

### Other Deferred Features

**From Sprint 1B to Sprint 2:**

- **ACL Expiration (US-020):** 3 points - Nice to have for temporary access
- **Permission Middleware (US-021):** 8 points - Can start with decorator-based checks
- **IdentityService API (US-023):** 5 points - Basic integration sufficient initially

**Rationale:** These are enhancements, not blockers. Basic permission checking works without them.

---

## Implementation Trade-offs

### Trade-off Analysis

#### What We Gain

**Functionality:**

- ✅ Proper multi-tenancy (Entity)
- ✅ Resource-level permissions (ACL)
- ✅ Transaction-specific roles (Participant)
- ✅ Flexible metadata (Profile)
- ✅ Comprehensive audit trail
- ✅ JWT-first architecture
- ✅ Optimized for SaaS

**Architecture:**

- ✅ Full control over data model
- ✅ No Django legacy constraints
- ✅ Clean separation of concerns
- ✅ Optimized database queries
- ✅ Custom caching strategies
- ✅ Tailored to business needs

**Business:**

- ✅ Scalable to thousands of customers
- ✅ GDPR-compliant by design
- ✅ Foundation for marketplace
- ✅ Competitive advantage
- ✅ No refactoring later

#### What We Sacrifice

**Development:**

- ❌ 4 weeks vs 3 days (3.5 extra weeks)
- ❌ 6 custom models to maintain
- ❌ Custom code = potential bugs
- ❌ Team learning curve
- ❌ More test coverage needed

**Maintenance:**

- ❌ Custom migrations
- ❌ Security updates our responsibility
- ❌ Can't leverage Django Admin easily
- ❌ Can't use some third-party packages
- ❌ Documentation burden

**Risk:**

- ❌ Higher complexity
- ❌ More testing required
- ❌ Longer debugging cycles
- ❌ Steeper onboarding for new developers

### Risk Mitigation

**Development Risks:**
| Risk | Mitigation |
|------|------------|
| Timeline slip | Strict story point limits, defer non-critical features |
| Bug surface area | >90% test coverage requirement, TDD approach |
| Team learning curve | Comprehensive documentation, pair programming |
| Over-engineering | Regular review against business requirements |

**Operational Risks:**
| Risk | Mitigation |
|------|------------|
| Security vulnerabilities | Security review at each sprint, penetration testing |
| Performance issues | Load testing, query optimization, caching strategy |
| Data leakage | Comprehensive integration tests, audit logging |
| Maintenance burden | Clear documentation, code reviews, standard patterns |

### Success Metrics

**Sprint 1A Success:**

- [ ] Users can register and login
- [ ] JWT tokens working
- [ ] Entity-scoped queries working
- [ ] > 90% test coverage
- [ ] All security checks passed

**Sprint 1B Success:**

- [ ] Role assignment working
- [ ] ACL grants working
- [ ] Permission checking functional
- [ ] Integration tests passing
- [ ] Security review passed

**Overall Success (by Sprint 2):**

- [ ] Platform supports 5+ customer organizations
- [ ] Zero data leakage incidents
- [ ] Permission checks < 50ms
- [ ] All integration points working
- [ ] Production deployment successful

---

## Lessons Learned

### Key Insights from Design Process

#### 1. Question Everything

**Initial Assumption:** "We need a custom Identity system"  
**Challenge:** "Why not use Django's built-in auth?"  
**Outcome:** Forced rigorous justification, confirmed decision was correct

**Lesson:** Always challenge architectural decisions. If you can't defend it, reconsider.

#### 2. Business Model Drives Architecture

**Discovery:** Once we confirmed SaaS business model, multi-tenancy became non-negotiable.  
**Insight:** Architecture must serve business model, not the other way around.

**Lesson:** Understand the business model before choosing technical architecture.

#### 3. Hybrid Approaches Have Hidden Costs

**Consideration:** "Let's extend Django's User to save time"  
**Reality:** At 60% custom code, hybrid loses its benefits  
**Decision:** Go 100% custom for full control

**Lesson:** Hybrid approaches often end up with worst of both worlds. Choose one path.

#### 4. Multi-Tenancy is Not Optional

**Question:** "What does multi-tenancy really mean?"  
**Answer:** Data isolation between independent organizations using same platform  
**Impact:** Entity model became most critical component

**Lesson:** Multi-tenancy is a foundational architectural decision, not a feature.

#### 5. Defer Non-Blockers Ruthlessly

**Example:** MFA deferred from Sprint 1 to Sprint 2  
**Rationale:** Core auth must work first, MFA is enhancement  
**Benefit:** Kept sprints at capacity, delivered MVP faster

**Lesson:** Distinguish between must-have and nice-to-have. Ship the former first.

#### 6. Documentation Prevents Regret

**Problem:** Architectural decisions get forgotten or questioned later  
**Solution:** This document captures the "why" behind decisions  
**Value:** Future team members understand rationale, not just implementation

**Lesson:** Document architectural decisions and their rationale in detail.

### What We'd Do Differently

**If starting over:**

1. ✅ Would still build custom Identity (decision validated)
2. ✅ Would still implement Entity for multi-tenancy (critical)
3. ✅ Would still build ACL system (business requirement)
4. ⚠️ Might consider django-guardian for ACL (battle-tested alternative)
5. ⚠️ Might keep Django's Permission model instead of custom
6. ⚠️ Might implement simpler Profile initially (JSON field sufficient)

**What we got right:**

- Challenging the assumptions early
- Understanding business model first
- Documenting the decision process
- Planning for 4 weeks instead of rushing 3 days
- Test-driven development approach
- Audit logging from day one

**What we'd improve:**

- Could have explored django-guardian more deeply
- Could have prototyped hybrid approach
- Could have benchmarked performance earlier
- Could have considered microservices (Identity as separate service)

---

## Conclusion

### Decision Summary

**Build custom Identity app with:**

- Identity model (authentication principal)
- Entity model (multi-tenancy scoping)
- Role model (RBAC baseline)
- ACL model (resource-level permissions)
- Profile model (flexible metadata)
- Comprehensive audit logging

**Investment:** 4 weeks development  
**Justification:** SaaS business model requires proper multi-tenancy and resource-level permissions  
**Alternative considered:** Django built-in auth (rejected - insufficient for requirements)  
**Status:** Approved and implementation beginning Sprint 1A

### Next Steps

1. **Immediate (This Week):**

   - ✅ Design decision documented and approved
   - [ ] Sprint 1A kickoff scheduled
   - [ ] Development environment setup
   - [ ] User stories assigned to developers

2. **Sprint 1A (Weeks 3-4):**

   - [ ] Identity and Entity models implemented
   - [ ] Authentication flows working
   - [ ] JWT tokens operational
   - [ ] > 90% test coverage achieved

3. **Sprint 1B (Weeks 5-6):**

   - [ ] Role and ACL models implemented
   - [ ] Permission system operational
   - [ ] Integration tests passing
   - [ ] Production deployment ready

4. **Sprint 2 (Weeks 7-8):**
   - [ ] MFA implementation
   - [ ] Permission middleware
   - [ ] Advanced ACL features
   - [ ] Performance optimization

### References

- Identity App Implementation Plan: `identity_implementation_plan.md`
- User Stories: `paperwurksapi/apps/identity/USERSTORIES/`
- Updated Sprint Plan: `paperwurksapi/docs/designs/sprint.md`
- Architecture Documentation: `paperwurksapi/apps/identity/README.md`

---

**Document Owner:** CTO  
**Reviewed By:** Backend Lead, Product Manager  
**Last Updated:** October 16, 2025  
**Next Review:** End of Sprint 1A  
**Status:** Approved for Implementation

---

## Appendix: Alternative Approaches Considered

### A. Django Built-in User/Groups

**Pros:** Fast, standard, well-documented  
**Cons:** No multi-tenancy, no resource-level permissions  
**Decision:** Rejected - insufficient for requirements

### B. Hybrid (Django User + Custom Extensions)

**Pros:** Leverages Django foundation  
**Cons:** 60% custom code anyway, loses hybrid benefits  
**Decision:** Rejected - at 60% custom, go 100%

### C. Django + django-guardian (for ACL)

**Pros:** Battle-tested ACL library  
**Cons:** Still need Entity, Profile, Participant  
**Decision:** Considered for Sprint 2 optimization

### D. Separate Identity Microservice

**Pros:** Complete isolation, independent scaling  
**Cons:** Network latency, deployment complexity, overkill for MVP  
**Decision:** Rejected for MVP, reconsider at scale

### E. Third-party Auth (Auth0, Okta)

**Pros:** Fully managed, no maintenance  
**Cons:** Expensive, no multi-tenancy, no ACL, vendor lock-in  
**Decision:** Rejected - need full control for SaaS

---

**End of Document**
