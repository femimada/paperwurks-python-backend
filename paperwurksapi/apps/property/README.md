## Purpose

Manages property lifecycle, metadata, and UPRN resolution. Anchors all transaction-related data.

## Architectural Design

- Properties are scoped to an Entity
- Linked to Documents, Packs, and SearchResults
- Status field drives lifecycle (draft → signed off → exchanged)

## Relationships

- **Property ↔ Entity** (many-to-one)
- **Property ↔ Document** (one-to-many)
- **Property ↔ Pack** (one-to-many)
- **Property ↔ SearchResult** (one-to-many)

## Responsibilities

- Create and manage property records
- Resolve UPRN and trigger searches
- Enforce Entity-based access
- Surface property status to agents and solicitors

## Permission Enforcement

- `property.view` and `property.edit` gated by role or ACL
- Solicitors can view assigned properties
- Buyers can view specific properties via ACL

## Integration Points

- SearchService triggers based on UPRN
- PackService assembles packs per property
- ComplianceService tracks search completeness

## TDD Guidance

- Test property creation and Entity scoping
- Validate UPRN resolution and search triggers
- Enforce permission checks for view/edit
- Simulate lifecycle transitions
