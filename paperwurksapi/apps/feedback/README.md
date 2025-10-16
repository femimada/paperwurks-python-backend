# Feedback Service

## Purpose

Captures solicitor overrides, agent ratings, buyer surveys, and post-pack feedback. Feeds into AI tuning and trust metrics.

## Architectural Design

- Feedback is linked to Packs and Identities
- Includes override rationale, survey responses, and NPS scores
- Used to monitor AI performance and user satisfaction

## Relationships

- **Feedback ↔ Pack** (many-to-one)
- **Feedback ↔ Identity** (submitted_by)
- **Feedback ↔ Document** (optional, for clause-level overrides)

## Responsibilities

- Store structured feedback and override data
- Surface feedback to AIOrchestrationService
- Support analytics and trust scoring
- Enforce submission rights via role and ACL

## Permission Enforcement

- `feedback.submit` gated by role and Entity
- Solicitors can override AI outputs
- Agents and buyers can submit surveys post-pack

## Integration Points

- AIOrchestrationService uses feedback for model tuning
- PackService displays feedback summary
- ComplianceService monitors override frequency

## TDD Guidance

- Test feedback submission and override logic
- Validate feedback visibility by role
- Simulate feedback-driven AI tuning scenarios
- Enforce feedback access and audit logging
