# AI Orchestration Service

## Purpose

Manages agentic workflows for document parsing, RAG retrieval, risk classification, and summarization. Powers AI-enhanced transparency.

## Architectural Design

- Stateless agents triggered via Celery
- Each agent performs a discrete task (e.g., chunking, summarization)
- Outputs stored with clause references and confidence scores
- Feedback loop integrated via FeedbackService

## Relationships

- **AI outputs ↔ Document** (via metadata)
- **AI outputs ↔ Pack** (via summary inclusion)
- **AI feedback ↔ Feedback** (override rationale)

## Responsibilities

- Trigger AI pipelines on document upload
- Store structured outputs for downstream use
- Ingest feedback for model tuning
- Surface clause-level insights to solicitors

## Permission Enforcement

- AI outputs scoped to document access permissions
- Feedback ingestion gated by override rights
- No direct access to orchestration endpoints by users

## Integration Points

- DocumentService triggers orchestration
- FeedbackService provides override data
- PackService displays AI summaries
- ComplianceService monitors override frequency

## TDD Guidance

- Test agent triggering and output storage
- Validate clause-level metadata and confidence scores
- Simulate feedback ingestion and tuning logic
- Enforce access scoping for AI outputs
