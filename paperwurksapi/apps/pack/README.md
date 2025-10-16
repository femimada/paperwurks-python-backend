# Pack Service

## Purpose

Assembles pre-sale packs from documents and search results. Tracks versioning and solicitor sign-off.

## Architectural Design

- Packs are linked to Properties and Entities
- Include documents, search results, AI summaries, and feedback
- Versioned and signed off by solicitors

## Relationships

- **Pack ↔ Property** (many-to-one)
- **Pack ↔ Document** (many-to-many)
- **Pack ↔ SearchResult** (many-to-many)
- **Pack ↔ Identity** (signed_off_by)

## Responsibilities

- Assemble packs from validated inputs
- Track version history and sign-off status
- Enforce access via ACL and role
- Surface pack status to agents and buyers

## Permission Enforcement

- `pack.view`, `pack.signoff` gated by role or ACL
- Solicitors must belong to same Entity
- Buyers can view signed-off packs via ACL

## Integration Points

- ComplianceService tracks pack completeness
- FeedbackService captures post-pack insights
- AuditService logs sign-off actions

## TDD Guidance

- Test pack creation and versioning
- Validate sign-off flow and solicitor access
- Enforce pack visibility rules
- Simulate pack lifecycle transitions
