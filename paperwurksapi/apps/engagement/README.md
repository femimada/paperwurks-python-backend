# Engagement Service

## Purpose

Tracks buyer and seller engagement with packs, documents, and feedback flows. Supports analytics and transparency.

## Architectural Design

- EngagementLog records views, interactions, and feedback submissions
- Includes timestamps, actor, resource type, and optional notes
- Used to measure transparency and user activity

## Relationships

- **EngagementLog ↔ Identity** (actor)
- **EngagementLog ↔ Pack or Document**
- **EngagementLog ↔ Feedback** (optional linkage)

## Responsibilities

- Track when users view packs and documents
- Log feedback and override interactions
- Support analytics and transparency metrics

## Permission Enforcement

- Logs only created for permitted views
- Admins and compliance officers can query logs
- Buyers and sellers can view their own history

## TDD Guidance

- Test log creation on view and feedback events
- Validate access scoping and visibility
- Simulate engagement analytics queries
- Ensure logs are immutable and timestamped
