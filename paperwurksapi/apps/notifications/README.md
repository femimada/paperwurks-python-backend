# Notifications Service

## Purpose

Delivers proactive alerts and updates to agents, buyers, and solicitors based on workflow events and compliance flags.

## Architectural Design

- Notification model stores event type, recipient, message, and read status
- Triggered by pack updates, compliance flags, search delays, etc.
- Scoped to Identity and Entity

## Relationships

- **Notification ↔ Identity** (recipient)
- **Notification ↔ Pack or Property** (optional context)
- **Notification ↔ ComplianceCheckpoint** (optional trigger)

## Responsibilities

- Deliver timely alerts to relevant users
- Support unread tracking and dashboard display
- Enable filtering by role and event type

## Permission Enforcement

- Notifications scoped to recipient's Entity
- Buyers and agents only see relevant updates
- Admins can view all notifications within Entity

## TDD Guidance

- Test notification creation on key events
- Validate delivery and read tracking
- Simulate role-based filtering and dashboard views
- Ensure compliance flags trigger alerts
