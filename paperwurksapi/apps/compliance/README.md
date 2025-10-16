# Compliance Service

## Purpose

Tracks regulatory milestones and pack-level compliance status. Supports audit readiness, internal QA, and partner assurance.

## Architectural Design

- ComplianceCheckpoints are linked to Packs
- Each checkpoint represents a regulatory milestone (e.g., search complete, solicitor sign-off)
- Status can be pending, passed, or flagged
- Fully auditable and queryable

## Relationships

- **ComplianceCheckpoint ↔ Pack** (many-to-one)
- **ComplianceCheckpoint ↔ Identity** (actor)
- **ComplianceCheckpoint ↔ AuditLog** (linked via action)

## Responsibilities

- Track pack-level compliance status
- Surface checkpoint status to agents and solicitors
- Support dashboards and reporting
- Enforce checkpoint updates via role and workflow triggers

## Permission Enforcement

- `pack.view` required to see compliance status
- Only solicitors or system agents can update checkpoints
- Audit logs must be created for all updates

## Integration Points

- PackService triggers checkpoint updates
- AuditService logs all compliance actions
- SearchService and DocumentService feed checkpoint status

## TDD Guidance

- Test checkpoint creation and status transitions
- Validate role-based update permissions
- Simulate flagged compliance scenarios
- Ensure audit logging and dashboard visibility
