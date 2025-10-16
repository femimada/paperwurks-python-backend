# Event-Driven Architecture for Paperwurks

## Overview

Paperwurks uses an event-driven architecture to enable modular, reactive workflows across backend services. Events represent meaningful changes in system state—such as a document upload, pack sign-off, or permission grant—and are used to trigger downstream actions like AI orchestration, compliance updates, notifications, and audit logging.

This document defines the core events, their purpose, and the schema used for inter-service communication.

## Event Model

### What Is an Event?

An event is a structured message that signals a change in system state. It contains metadata about:

- What happened (event type)
- Who triggered it (actor)
- What it affected (target resource)
- When it occurred (timestamp)
- Why it matters (context)

Events are emitted by services and consumed by others to maintain loose coupling and reactive behavior.

## Event Schema

All events follow a consistent schema to ensure interoperability across services.

## Core Events

### `document.uploaded`

Triggered when a document is successfully uploaded.

- **Emitted by**: DocumentService
- **Consumed by**: AIOrchestrationService, AuditService
- **Purpose**: Start AI parsing, log upload

### `document.reviewed`

Triggered when a solicitor reviews or overrides AI output.

- **Emitted by**: FeedbackService
- **Consumed by**: AuditService, ComplianceService
- **Purpose**: Log override, update compliance status

### `pack.signed_off`

Triggered when a solicitor signs off a pack.

- **Emitted by**: PackService
- **Consumed by**: ComplianceService, TimelineService, NotificationService, AuditService
- **Purpose**: Mark pack as complete, notify stakeholders, log action

### `search.result_received`

Triggered when a search result is ingested.

- **Emitted by**: SearchService
- **Consumed by**: ComplianceService, NotificationService
- **Purpose**: Update compliance checkpoint, alert solicitor

### `acl.granted`

Triggered when a resource-level permission is granted.

- **Emitted by**: IdentityService
- **Consumed by**: AuditService, NotificationService
- **Purpose**: Log permission change, notify recipient

### `pack.viewed`

Triggered when a buyer or agent views a pack.

- **Emitted by**: PackService
- **Consumed by**: EngagementService, TimelineService
- **Purpose**: Track engagement, update timeline

### `feedback.submitted`

Triggered when feedback is submitted by any actor.

- **Emitted by**: FeedbackService
- **Consumed by**: AIOrchestrationService, AuditService
- **Purpose**: Improve AI models, log feedback

### `entity.created`

Triggered when a new Entity (tenant) is onboarded.

- **Emitted by**: IdentityService
- **Consumed by**: AuditService, NotificationService
- **Purpose**: Log onboarding, notify admins

### `compliance.flagged`

Triggered when a compliance checkpoint is flagged.

- **Emitted by**: ComplianceService
- **Consumed by**: NotificationService, AuditService
- **Purpose**: Alert stakeholders, log issue

## Event Routing Strategy

- Events are emitted from service-layer logic only
- Consumers subscribe based on event type and target resource
- Events are stored or forwarded based on business rules (e.g. audit, notification, orchestration)

## TDD Guidance

Each event should be:

- Emitted during relevant service actions
- Consumed by downstream services with clear business logic
- Tested for emission and consumption behavior
- Audited for traceability and compliance
