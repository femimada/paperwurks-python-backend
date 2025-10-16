# Paperwurks Backend — `README.md`

## What We’re Building

**Paperwurks** is a UK proptech platform revolutionizing residential property transactions through AI-powered transparency, compliance, and efficiency.  
Our backend is designed to support multi-actor workflows (agents, solicitors, buyers), regulatory assurance, and scalable AI orchestration.

---

## Architectural Overview

### Modular App Design

Each domain is encapsulated in its own Django app under `apps/`, with clear boundaries and responsibilities.

This repository contains the backend services that power:

- Identity and access management (IAM)
- Property lifecycle and document handling
- Pack assembly and solicitor sign-off
- Regulatory search ingestion
- AI-enhanced document summarization and risk classification
- Feedback capture and compliance tracking

---

### App Overview

| App                  | Purpose                                                      |
| -------------------- | ------------------------------------------------------------ |
| **identity**         | Centralized IAM: authentication, roles, ACLs, Entity scoping |
| **property**         | Property lifecycle, UPRN resolution                          |
| **document**         | Uploads, AI outputs, versioning                              |
| **pack**             | Pack assembly, versioning, solicitor sign-off                |
| **search**           | Regulatory and environmental searches                        |
| **feedback**         | Solicitor overrides, buyer surveys, agent ratings            |
| **compliance**       | Pack-level compliance checkpoints                            |
| **audit**            | Immutable logging of sensitive actions                       |
| **ai_orchestration** | Agentic workflows for parsing, RAG, summarization            |

---

## Core Interaction Model

Apps communicate through a service layer—each app exposes internal services (e.g., `PackService`, `IdentityService`) that encapsulate business logic and enforce permission checks.

- API endpoints are thin wrappers around service calls
- Permissions are enforced via middleware and decorators
- Audit logging is triggered from service methods
- AI orchestration is stateless and triggered via Celery

---

## Design Patterns

### Test-Driven Development (TDD)

- All apps follow a TDD-first workflow
- Unit tests cover model logic and edge cases
- Integration tests simulate real user workflows
- IAM and permission logic must achieve >90% coverage

---

### IAM: RBAC + ACL

- Role-Based Access Control (RBAC) for baseline permissions
- Access Control Lists (ACLs) for fine-grained, resource-level overrides
- All permission changes are logged immutably
- Permission checks are enforced server-side via middleware

---

### Service Layer

- Each app exposes a `services/` module
- Business logic lives in services, not in views or models
- Promotes testability, reuse, and separation of concerns

---

### Async & Task Queues

- Celery is used for async workflows (e.g., AI orchestration, search ingestion)
- Tasks are triggered by events (e.g., document upload)
- Outputs are stored and surfaced via service calls

---

### Audit & Compliance

- All sensitive actions are logged via `AuditService`
- Compliance checkpoints are tracked per pack
- Logs are immutable and scoped to Entity boundaries

---

## Development Workflow

1. Define user stories and test matrix in each app’s `README.md`
2. Write failing tests for each scenario
3. Implement minimal logic to pass tests
4. Validate integration and permission enforcement
5. Ensure audit logging and compliance coverage

---

## Deployment & Environment

- Django + Django Ninja (API layer)
- PostgreSQL (RDS) – primary data store
- S3 – document storage
- BigQuery – AI output storage
- Celery + Redis – task queue
- JWT-based authentication
- CloudWatch + Sentry – monitoring and observability

---

> Paperwurks Backend — Building compliant, intelligent, and human-centric property infrastructure.
