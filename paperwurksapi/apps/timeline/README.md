# Timeline Service

## Purpose

Provides a visual and queryable timeline of transaction milestones for agents, buyers, and sellers.

## Architectural Design

- TransactionTimeline stores milestone events per property or pack
- Includes event type, timestamp, actor, and status
- Used to power dashboards and progress trackers

## Relationships

- **TransactionTimeline ↔ Property or Pack**
- **TransactionTimeline ↔ Identity** (actor)
- **TransactionTimeline ↔ ComplianceCheckpoint** (optional linkage)

## Responsibilities

- Record key workflow events (e.g., search complete, pack signed)
- Surface progress to agents and owners
- Support filtering and milestone analytics

## Permission Enforcement

- Timeline visibility scoped to Entity and ACL
- Buyers and sellers see only their own transactions
- Admins and solicitors see full history

## TDD Guidance

- Test milestone creation and status transitions
- Validate timeline visibility per role
- Simulate dashboard rendering from timeline data
- Ensure audit logging on milestone updates
