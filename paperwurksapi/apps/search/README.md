# Search Service

## Purpose

Handles regulatory, environmental, and planning searches triggered by property metadata. Supports automated due diligence and pack completeness.

## Architectural Design

- SearchResults are linked to Properties and Entities
- Triggered via UPRN or manual request
- Includes vendor attribution, liability metadata, and timestamps
- Search completeness feeds into ComplianceCheckpoint

## Relationships

- **SearchResult ↔ Property** (many-to-one)
- **SearchResult ↔ Pack** (many-to-many)
- **SearchResult ↔ Entity** (via Property)

## Responsibilities

- Trigger searches via vendor APIs
- Store structured results and metadata
- Enforce access via Entity and ACL
- Surface search status to PackService and ComplianceService

## Permission Enforcement

- `searchresult.view` gated by role or ACL
- Solicitors can view results for assigned properties
- Agents can view status but not raw data unless permitted

## Integration Points

- PackService includes search results in pack assembly
- ComplianceService verifies search completeness
- AuditService logs search triggers and result ingestion

## TDD Guidance

- Test search trigger logic and vendor integration
- Validate result storage and metadata parsing
- Enforce access rules for viewing results
- Simulate incomplete search scenarios for compliance tracking
