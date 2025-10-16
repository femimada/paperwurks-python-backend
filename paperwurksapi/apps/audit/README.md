# Audit Service

## Purpose

Logs all sensitive actions across the platform for compliance, dispute resolution, and transparency.

## Architectural Design

- AuditLog entries are immutable
- Each entry includes actor, target, action, timestamp, and source IP
- Linked to permission changes, sign-offs, and compliance events

## Relationships

- **AuditLog ↔ Identity** (actor)
- **AuditLog ↔ Target entity** (Pack, Document, etc.)
- **AuditLog ↔ ComplianceCheckpoint** (optional)

## Responsibilities

- Record all GRANT/REVOKE actions
- Log sign-offs, overrides, and sensitive updates
- Support audit exports and internal reviews
- Enforce logging hooks across services

## Permission Enforcement

- Audit logs are viewable by Entity admins and compliance officers
- Logs cannot be modified or deleted
- Access scoped to Entity boundaries

## Integration Points

- IdentityService triggers logs on permission changes
- PackService logs sign-offs
- ComplianceService logs checkpoint updates
- FeedbackService logs override submissions

## TDD Guidance

- Test log creation for all sensitive actions
- Validate immutability and access scoping
- Simulate audit export scenarios
- Enforce logging hooks in service workflows
