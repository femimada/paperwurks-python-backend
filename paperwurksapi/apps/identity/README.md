# Identity Service

## Purpose

Centralized IAM (Identity and Access Management) system for authentication, role assignment, and permission enforcement. Replaces legacy user logic with a scalable, auditable framework.

## Architectural Design

- **Identity** is the core principal (person or service account)
- **Entity** scopes tenancy and access boundaries, notifications, and engagement flows
- **Roles** define baseline access (RBAC)
- **ACLs** enable fine-grained, resource-level overrides
- **Profiles** store domain-specific metadata (e.g., solicitor credentials)

- **Participants** Identity is extended with a participant_type field
- **ParticipantType** Types include: buyer, seller, dual, proxy

## Relationships

- **Identity ↔ Entity** (many-to-one)
- **Identity ↔ Profile** (one-to-one)
- **Identity ↔ Role** (many-to-many)
- **Identity ↔ ACL** (many-to-many via resource grants)
- **Identity ↔ TransactionParticipant** (optional, for role-specific logic)

## Responsibilities

- Authenticate users
- Enforce role and ACL-based access
- Manage identity lifecycle (activation, MFA, verification)
- Expose internal IAM API for other services
- Participant type influences notification and timeline visibility
- Test participant classification logic
- Simulate buyer/seller interactions with packs and documents
- Ensure ACL overrides respect participant type

## Permission Enforcement

- All resource access gated by RBAC or ACL
- Middleware checks for `action.resource` codename
- ACL grants can expire and are fully auditable

## Integration Points

- Used by all services for access control
- Identity metadata exposed to PackService, DocumentService, etc.
- AuditService logs all GRANT/REVOKE actions

## TDD Guidance

- Start with Identity creation, Entity linkage, and role assignment
- Test login, MFA, and permission enforcement
- Validate ACL overrides and expiration logic
- Ensure audit logs are triggered correctly
