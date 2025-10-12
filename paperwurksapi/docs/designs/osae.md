# OSAE Design Document

## Document Information

- **Version:** 1.0.0
- **Last Updated:** January 2025
- **Status:** Approved for Implementation
- **Target Sprints:** Sprint 3 (Foundation), Sprint 4-5 (Agents), Sprint 6 (Optimization)

## Executive Summary

The Official Search Automation Engine (OSAE) is Paperwurks' intelligent agent system that automates property risk assessment, search orchestration, and legal compliance analysis. This document defines the architecture, agent behaviors, and integration patterns.

## OSAE Architecture Overview

```mermaid
graph TB
    subgraph "Entry Points"
        PROP[Property Added]
        SEARCH[Search Completed]
        DOC[Document Uploaded]
    end

    subgraph "Agent Orchestrator"
        ORCH[Orchestration Layer]
        QUEUE[Task Queue]
        STATE[State Manager]
    end

    subgraph "Specialist Agents"
        RISK[Risk Assessment Agent]
        LEGAL[Legal Analysis Agent]
        SEARCH_COORD[Search Coordinator Agent]
        REPORT[Report Generation Agent]
    end

    subgraph "Knowledge Layer"
        RAG[RAG System]
        KB[Knowledge Bases]
        MEMORY[Conversation Memory]
    end

    subgraph "Output Layer"
        REPORTS[Reports]
        ACTIONS[Action Items]
        NOTIFY[Notifications]
    end

    PROP --> ORCH
    SEARCH --> ORCH
    DOC --> ORCH

    ORCH --> QUEUE
    QUEUE --> STATE
    STATE --> RISK
    STATE --> LEGAL
    STATE --> SEARCH_COORD

    RISK --> RAG
    LEGAL --> RAG
    SEARCH_COORD --> RAG

    RAG --> KB
    RAG --> MEMORY

    RISK --> REPORT
    LEGAL --> REPORT
    REPORT --> REPORTS
    REPORT --> ACTIONS
    REPORT --> NOTIFY
```

## Agent Definitions

### Risk Assessment Agent

#### Purpose

Analyzes property location and characteristics to identify potential risks and recommend necessary searches.

#### Capabilities

| Capability                | Description                    | Data Sources                   | Sprint   |
| ------------------------- | ------------------------------ | ------------------------------ | -------- |
| Location Analysis         | Assess geographic risks        | OS maps, flood data            | Sprint 3 |
| Environmental Screening   | Identify environmental hazards | EA data, contamination records | Sprint 3 |
| Infrastructure Assessment | Check nearby developments      | Planning portal, HS2 routes    | Sprint 3 |
| Historical Analysis       | Review area history            | Historical maps, mining data   | Sprint 3 |
| Search Recommendation     | Recommend relevant searches    | Search matrix, risk factors    | Sprint 3 |
| Cost Estimation           | Estimate total search costs    | Provider pricing, complexity   | Sprint 3 |

#### Input/Output Schema

```mermaid
graph LR
    subgraph "Input"
        I1[Property Address]
        I2[Property Type]
        I3[Transaction Type]
        I4[UPRN/Coordinates]
    end

    subgraph "Processing"
        P1[Location Lookup]
        P2[Risk Analysis]
        P3[Search Matrix]
        P4[Cost Calculation]
    end

    subgraph "Output"
        O1[Risk Assessment Report]
        O2[Risk Score 0-100]
        O3[Search Checklist]
        O4[Cost Breakdown]
        O5[Confidence Scores]
    end

    I1 --> P1
    I2 --> P2
    I3 --> P3
    I4 --> P1

    P1 --> P2
    P2 --> P3
    P3 --> P4

    P2 --> O1
    P2 --> O2
    P3 --> O3
    P4 --> O4
    P1 --> O5
```

#### Risk Categories

| Category      | Risk Factors                       | Weight | Threshold    | Sprint   |
| ------------- | ---------------------------------- | ------ | ------------ | -------- |
| Flooding      | River, surface, groundwater        | 25%    | >1% annual   | Sprint 3 |
| Subsidence    | Clay soil, tree proximity, history | 20%    | Medium+ risk | Sprint 3 |
| Contamination | Industrial history, landfill       | 20%    | Within 250m  | Sprint 3 |
| Mining        | Coal, other minerals, cavities     | 15%    | Any activity | Sprint 3 |
| Planning      | Major developments, HS2, airports  | 10%    | Within 1km   | Sprint 3 |
| Environmental | Radon, conservation, flood defense | 10%    | Various      | Sprint 3 |

### Legal Analysis Agent

#### Purpose

Interprets search results against lender requirements and legal compliance standards.

#### Capabilities

| Capability            | Description                         | Knowledge Base                 | Sprint   |
| --------------------- | ----------------------------------- | ------------------------------ | -------- |
| Search Interpretation | Parse and understand search results | Search templates               | Sprint 5 |
| Lender Compliance     | Check against CML handbook          | CML handbook, lender specifics | Sprint 5 |
| Issue Identification  | Flag potential legal issues         | Case precedents, protocols     | Sprint 5 |
| Risk Scoring          | Assess legal risk level             | Risk matrix, historical data   | Sprint 5 |
| Recommendation Engine | Suggest remedial actions            | Best practices, solutions DB   | Sprint 5 |
| Precedent Matching    | Find similar resolved cases         | Case database                  | Sprint 5 |

#### Analysis Workflow

```mermaid
stateDiagram-v2
    [*] --> ReceiveResults: Search Results Available
    ReceiveResults --> ParseResults: Extract Key Data
    ParseResults --> CheckCompliance: Against Lender Rules
    CheckCompliance --> IdentifyIssues: Flag Problems
    IdentifyIssues --> NoIssues: All Clear
    IdentifyIssues --> MinorIssues: Low Risk
    IdentifyIssues --> MajorIssues: High Risk

    NoIssues --> GenerateReport: Standard Report
    MinorIssues --> FindSolutions: Search Solutions
    MajorIssues --> EscalateSolicitor: Urgent Review

    FindSolutions --> GenerateReport: With Recommendations
    EscalateSolicitor --> GenerateReport: Flagged Report
    GenerateReport --> [*]
```

#### Compliance Rules Engine

| Rule Type        | Description                | Source          | Action              | Sprint   |
| ---------------- | -------------------------- | --------------- | ------------------- | -------- |
| Lender Mandatory | Must-have requirements     | CML Part 1      | Block if missing    | Sprint 5 |
| Lender Specific  | Individual lender rules    | CML Part 2      | Check if applicable | Sprint 5 |
| Legal Required   | Statutory requirements     | Legislation     | Ensure compliance   | Sprint 5 |
| Best Practice    | Recommended practices      | Law Society     | Suggest if missing  | Sprint 5 |
| Local Peculiar   | Area-specific requirements | Local knowledge | Flag if relevant    | Sprint 5 |

### Search Coordinator Agent

#### Purpose

Orchestrates the ordering, tracking, and management of property searches across multiple providers.

#### Capabilities

| Capability         | Description                           | Integration         | Sprint   |
| ------------------ | ------------------------------------- | ------------------- | -------- |
| Provider Selection | Choose optimal provider per search    | Provider matrix     | Sprint 4 |
| Batch Ordering     | Group searches for efficiency         | API orchestration   | Sprint 4 |
| Status Tracking    | Monitor search progress               | Webhook/polling     | Sprint 4 |
| Cost Optimization  | Find best price/speed balance         | Pricing engine      | Sprint 4 |
| Retry Logic        | Handle failures gracefully            | Exponential backoff | Sprint 4 |
| Result Aggregation | Compile results from multiple sources | Data normalizer     | Sprint 4 |

#### Search Priority Matrix

[Mermaid for Search Priority Matrix here]

### Report Generation Agent

#### Purpose

Creates comprehensive, readable reports from agent analyses for different stakeholders.

#### Capabilities

| Capability          | Description                | Output Format    | Sprint   |
| ------------------- | -------------------------- | ---------------- | -------- |
| Audience Adaptation | Tailor content for role    | Role-specific    | Sprint 5 |
| Risk Summarization  | Executive summary of risks | Traffic light    | Sprint 5 |
| Action Items        | Clear next steps           | Prioritized list | Sprint 5 |
| Timeline Generation | Project completion dates   | Gantt/timeline   | Sprint 6 |
| Cost Breakdown      | Detailed cost analysis     | Itemized table   | Sprint 4 |
| Confidence Scoring  | Reliability indicators     | Percentage/stars | Sprint 5 |

## Agent Communication Patterns

### Inter-Agent Communication

```mermaid
sequenceDiagram
    participant User
    participant Orchestrator
    participant RiskAgent
    participant SearchCoord
    participant LegalAgent
    participant ReportAgent

    User->>Orchestrator: Add Property
    Orchestrator->>RiskAgent: Assess Property
    RiskAgent->>Orchestrator: Risk Report
    Orchestrator->>SearchCoord: Order Searches
    SearchCoord->>Orchestrator: Search Ordered

    Note over SearchCoord: Await Results

    SearchCoord->>Orchestrator: Results Ready
    Orchestrator->>LegalAgent: Analyze Results
    LegalAgent->>Orchestrator: Legal Analysis
    Orchestrator->>ReportAgent: Generate Report
    ReportAgent->>User: Final Report
```

### State Management

```mermaid
graph TB
    subgraph "Agent State"
        IDLE[Idle]
        PROCESSING[Processing]
        WAITING[Waiting for Input]
        COMPLETE[Complete]
        ERROR[Error]
    end

    subgraph "Task State"
        QUEUED[Queued]
        RUNNING[Running]
        BLOCKED[Blocked]
        DONE[Done]
        FAILED[Failed]
    end

    subgraph "Conversation State"
        NEW[New Session]
        ACTIVE[Active Context]
        SUSPENDED[Suspended]
        CLOSED[Closed]
    end

    IDLE --> PROCESSING
    PROCESSING --> WAITING
    PROCESSING --> COMPLETE
    PROCESSING --> ERROR
    WAITING --> PROCESSING
    ERROR --> IDLE
    COMPLETE --> IDLE
```

## Decision Trees

### Risk Assessment Decision Tree

```mermaid
graph TD
    START[Property Details] --> LOC{Location Known?}
    LOC -->|Yes| UPRN[Use UPRN Data]
    LOC -->|No| ADDR[Geocode Address]

    UPRN --> FLOOD{Flood Risk?}
    ADDR --> FLOOD

    FLOOD -->|High| FLOODREQ[Require Flood Report]
    FLOOD -->|Medium| FLOODOPT[Recommend Flood Report]
    FLOOD -->|Low| SUBSIDE{Subsidence Risk?}

    FLOODREQ --> SUBSIDE
    FLOODOPT --> SUBSIDE

    SUBSIDE -->|High| SUBREQ[Require Ground Report]
    SUBSIDE -->|Low| CONTAM{Contamination?}

    SUBREQ --> CONTAM

    CONTAM -->|Yes| ENVREQ[Require Environmental]
    CONTAM -->|No| MINE{Mining Area?}

    ENVREQ --> MINE

    MINE -->|Yes| MINEREQ[Require Mining Search]
    MINE -->|No| COMPLETE[Generate Report]

    MINEREQ --> COMPLETE
```

### Legal Compliance Decision Tree

```mermaid
graph TD
    RESULTS[Search Results] --> PARSE{Parse Success?}
    PARSE -->|No| MANUAL[Flag for Manual Review]
    PARSE -->|Yes| LENDER{Lender Known?}

    LENDER -->|Yes| SPECIFIC[Check Specific Requirements]
    LENDER -->|No| GENERAL[Check General Requirements]

    SPECIFIC --> COMPLY{Compliant?}
    GENERAL --> COMPLY

    COMPLY -->|Yes| MINOR{Minor Issues?}
    COMPLY -->|No| MAJOR[Major Issues Found]

    MINOR -->|Yes| SOLUTION[Find Solutions]
    MINOR -->|No| APPROVE[Approve Pack]

    SOLUTION --> INDEMNITY{Indemnity Possible?}
    INDEMNITY -->|Yes| RECOMMEND[Recommend Indemnity]
    INDEMNITY -->|No| REMEDIAL[Require Remedial Action]

    MAJOR --> SOLICITOR[Escalate to Solicitor]
    MANUAL --> SOLICITOR
    REMEDIAL --> REPORT[Generate Report]
    RECOMMEND --> REPORT
    APPROVE --> REPORT
    SOLICITOR --> REPORT
```

## Performance Specifications

### Response Time Requirements

| Agent Operation   | Target | Maximum | Retry After | Sprint   |
| ----------------- | ------ | ------- | ----------- | -------- |
| Risk Assessment   | 15s    | 30s     | 60s         | Sprint 3 |
| Search Ordering   | 5s     | 10s     | 30s         | Sprint 4 |
| Legal Analysis    | 30s    | 60s     | 120s        | Sprint 5 |
| Report Generation | 10s    | 20s     | 60s         | Sprint 5 |
| Status Check      | 1s     | 3s      | 10s         | Sprint 4 |

### Throughput Requirements

| Metric              | Target | Peak | Degraded Mode | Sprint   |
| ------------------- | ------ | ---- | ------------- | -------- |
| Properties/hour     | 100    | 500  | 50            | Sprint 3 |
| Searches/hour       | 200    | 1000 | 100           | Sprint 4 |
| Reports/hour        | 50     | 200  | 25            | Sprint 5 |
| Concurrent sessions | 20     | 100  | 10            | Sprint 3 |

## Error Handling

### Error Categories

```mermaid
graph LR
    subgraph "Recoverable Errors"
        RE1[API Timeout]
        RE2[Rate Limit]
        RE3[Temporary Failure]
    end

    subgraph "Partial Failures"
        PF1[Missing Data]
        PF2[Incomplete Results]
        PF3[Low Confidence]
    end

    subgraph "Critical Failures"
        CF1[Auth Failure]
        CF2[Data Corruption]
        CF3[System Error]
    end

    RE1 --> RETRY[Retry Logic]
    RE2 --> BACKOFF[Exponential Backoff]
    RE3 --> QUEUE[Requeue Task]

    PF1 --> DEGRADE[Degraded Service]
    PF2 --> PARTIAL[Partial Report]
    PF3 --> MANUAL[Manual Review]

    CF1 --> ALERT[Alert Ops]
    CF2 --> HALT[Halt Processing]
    CF3 --> FAILOVER[Failover]
```

### Fallback Strategies

| Scenario                | Primary          | Fallback 1         | Fallback 2   | Manual         | Sprint   |
| ----------------------- | ---------------- | ------------------ | ------------ | -------------- | -------- |
| RAG Unavailable         | Bedrock KB       | Cached results     | Basic rules  | Human review   | Sprint 3 |
| Search API Down         | Primary provider | Secondary provider | Manual order | Phone order    | Sprint 4 |
| AI Model Error          | Primary model    | Simpler model      | Rule engine  | Human analysis | Sprint 3 |
| Report Generation Fails | Full report      | Summary only       | Raw data     | Email data     | Sprint 5 |

## Monitoring & Observability

### Key Metrics

| Metric            | Description            | Alert Threshold | Dashboard  | Sprint   |
| ----------------- | ---------------------- | --------------- | ---------- | -------- |
| Agent Latency     | Time per operation     | >2x target      | Operations | Sprint 3 |
| Success Rate      | Successful completions | <95%            | Business   | Sprint 3 |
| Confidence Score  | Average confidence     | <70%            | Quality    | Sprint 3 |
| Queue Depth       | Pending tasks          | >100            | Operations | Sprint 3 |
| Error Rate        | Failures per hour      | >5%             | Operations | Sprint 3 |
| Cost per Analysis | AI service costs       | >£5             | Finance    | Sprint 3 |
