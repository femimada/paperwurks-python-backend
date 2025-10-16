# Case Management Service

## Purpose

Supports solicitor caseload tracking, task assignment, and prioritization across multiple properties and packs.

## Architectural Design

- CaseAssignment links solicitors to properties or packs
- Includes status, priority, timestamps, and optional notes
- Enables dashboard views and workload analytics

## Relationships

- **CaseAssignment ↔ Identity** (solicitor)
- **CaseAssignment ↔ Property or Pack**
- **CaseAssignment ↔ Entity** (via solicitor)

## Responsibilities

- Track solicitor workload and assignments
- Surface active cases and deadlines
- Support prioritization and filtering

## Permission Enforcement

- Only solicitors and Entity admins can view assignments
- Assignments scoped to Entity boundaries
- Audit logs created for assignment changes

## TDD Guidance

- Test assignment creation and status transitions
- Validate solicitor visibility and access
- Simulate dashboard filtering by priority
- Ensure audit logging on assignment updates
