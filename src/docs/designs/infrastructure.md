# Infrastructure Design Document

## Document Information

- **Version:** 1.0.0
- **Last Updated:** January 2025
- **Status:** Approved for Implementation
- **Target Sprints:** Sprint 0-1 (Foundation), Sprint 3-5 (OSAE Components)

## Executive Summary

This document defines two infrastructure architectures for Paperwurks: a managed services approach using AWS Bedrock, and a self-hosted approach with custom ML infrastructure. Both designs support the same business requirements but differ in operational complexity and cost structure.

## Business Requirements

### Functional Requirements

- Support 100 concurrent users initially, scaling to 1000+
- Process 50-100 property documents daily
- Sub-30 second AI analysis response time
- 99.9% uptime SLA for core services
- 7-year document retention compliance

### Non-Functional Requirements

- GDPR compliance with UK data residency
- SOC 2 Type II compliance readiness
- RPO: 1 hour, RTO: 4 hours
- Multi-factor authentication support
- End-to-end encryption for sensitive data

## Architecture Option 1: AWS Bedrock-Powered Infrastructure

### Overview

Leverages AWS managed services with Bedrock for AI capabilities, minimizing operational overhead.

```mermaid
graph TB
    subgraph "Edge Layer"
        CF[CloudFront CDN]
        WAF[AWS WAF]
    end

    subgraph "Application Layer"
        ALB[Application Load Balancer]
        ECS_API[ECS Fargate - API]
        ECS_WORKER[ECS Fargate - Workers]
    end

    subgraph "AI Layer - Managed"
        BEDROCK[AWS Bedrock]
        KB[Knowledge Bases]
        AGENTS[Bedrock Agents]
    end

    subgraph "Data Layer"
        RDS[(RDS PostgreSQL)]
        S3[(S3 Buckets)]
        REDIS[(ElastiCache Redis)]
    end

    subgraph "Integration"
        SQS[SQS Queues]
        EventBridge[EventBridge]
        SecretsMgr[Secrets Manager]
    end

    CF --> WAF
    WAF --> ALB
    ALB --> ECS_API
    ECS_API --> RDS
    ECS_API --> S3
    ECS_API --> REDIS
    ECS_API --> SQS
    SQS --> ECS_WORKER
    ECS_WORKER --> BEDROCK
    BEDROCK --> KB
    BEDROCK --> AGENTS
    ECS_WORKER --> EventBridge
```

### Component Specifications

#### Compute Resources

| Component      | Specification     | Scaling                 | Sprint   |
| -------------- | ----------------- | ----------------------- | -------- |
| API Service    | Fargate 2vCPU/4GB | 2-10 tasks auto-scaling | Sprint 0 |
| Worker Service | Fargate 4vCPU/8GB | 2-5 tasks queue-based   | Sprint 1 |
| Scheduled Jobs | Lambda functions  | On-demand               | Sprint 2 |

#### Managed AI Services

| Service                 | Purpose               | Configuration                 | Sprint   |
| ----------------------- | --------------------- | ----------------------------- | -------- |
| Bedrock Knowledge Bases | RAG document store    | OpenSearch Serverless backend | Sprint 3 |
| Bedrock Agents          | Risk & Legal analysis | Claude 3 Sonnet/Haiku         | Sprint 3 |
| Bedrock Guardrails      | Output filtering      | Custom policies               | Sprint 3 |

#### Data Storage

| Component         | Specification                | Backup Strategy                  | Sprint   |
| ----------------- | ---------------------------- | -------------------------------- | -------- |
| RDS PostgreSQL    | db.t4g.large Multi-AZ        | Daily snapshots, 7-day retention | Sprint 0 |
| S3 Documents      | Standard tier with lifecycle | Cross-region replication         | Sprint 0 |
| ElastiCache Redis | cache.t4g.small              | Daily snapshots                  | Sprint 1 |

### Networking

```mermaid
graph LR
    subgraph "VPC 10.0.0.0/16"
        subgraph "Public Subnets"
            ALB[Load Balancer]
            NAT[NAT Gateway]
        end
        subgraph "Private Subnets"
            ECS[ECS Tasks]
            LAMBDA[Lambda Functions]
        end
        subgraph "Database Subnets"
            RDS[RDS Instances]
            REDIS[Redis Cluster]
        end
    end

    Internet --> ALB
    ECS --> NAT
    NAT --> Internet
    ECS --> RDS
    ECS --> REDIS
```

### Cost Structure (Monthly)

| Component     | Cost Range   | Notes                             |
| ------------- | ------------ | --------------------------------- |
| Compute (ECS) | £200-300     | Includes Fargate Spot for workers |
| Bedrock AI    | £100-200     | Pay per invocation                |
| Database      | £150-200     | Multi-AZ deployment               |
| Storage       | £50-100      | Including CDN                     |
| Networking    | £100-150     | NAT Gateway, data transfer        |
| **Total**     | **£600-950** | Scales linearly with usage        |

### Deployment Pipeline

```mermaid
graph LR
    GH[GitHub] --> CB[CodeBuild]
    CB --> TEST[Run Tests]
    TEST --> BUILD[Build Container]
    BUILD --> ECR[Push to ECR]
    ECR --> STAGING[Deploy Staging]
    STAGING --> PROD[Deploy Production]

    CB --> NOTIFY[Slack Notification]
```

## Architecture Option 2: Self-Hosted ML Infrastructure

### Overview

Custom-built ML pipeline with self-managed vector database and model serving.

```mermaid
graph TB
    subgraph "Edge Layer"
        CF[CloudFront CDN]
        WAF[AWS WAF]
    end

    subgraph "Application Layer"
        ALB[Application Load Balancer]
        EKS[EKS Cluster]
        API_PODS[API Pods]
        WORKER_PODS[Worker Pods]
    end

    subgraph "AI Layer - Self-Hosted"
        ML_NODES[GPU Nodes - g5.xlarge]
        QDRANT[Qdrant Vector DB]
        MODELS[Model Servers]
    end

    subgraph "Data Layer"
        RDS[(RDS PostgreSQL)]
        S3[(S3 Buckets)]
        REDIS[(ElastiCache Redis)]
        OPENSEARCH[(OpenSearch)]
    end

    subgraph "Integration"
        SQS[SQS Queues]
        AIRFLOW[Apache Airflow]
        SecretsMgr[Secrets Manager]
    end

    CF --> WAF
    WAF --> ALB
    ALB --> API_PODS
    API_PODS --> RDS
    API_PODS --> S3
    API_PODS --> REDIS
    API_PODS --> SQS
    SQS --> WORKER_PODS
    WORKER_PODS --> ML_NODES
    ML_NODES --> MODELS
    WORKER_PODS --> QDRANT
    WORKER_PODS --> OPENSEARCH
    AIRFLOW --> WORKER_PODS
```

### Component Specifications

#### Kubernetes Cluster

| Component         | Specification   | Node Count       | Sprint   |
| ----------------- | --------------- | ---------------- | -------- |
| Control Plane     | EKS managed     | 3 (HA)           | Sprint 0 |
| API Node Group    | t3.large        | 2-6 auto-scaling | Sprint 0 |
| Worker Node Group | t3.xlarge       | 2-4 auto-scaling | Sprint 1 |
| ML Node Group     | g5.xlarge (GPU) | 1-2 on-demand    | Sprint 3 |

#### Self-Hosted AI Stack

| Service         | Technology            | Infrastructure     | Sprint   |
| --------------- | --------------------- | ------------------ | -------- |
| Vector Database | Qdrant                | 2x m5.xlarge pods  | Sprint 3 |
| Search Engine   | OpenSearch            | 3-node cluster     | Sprint 3 |
| Model Serving   | TorchServe/vLLM       | GPU nodes          | Sprint 4 |
| Embeddings      | Sentence Transformers | CPU intensive pods | Sprint 3 |

### Data Pipeline

```mermaid
graph LR
    DOC[Document Upload] --> S3[S3 Storage]
    S3 --> EXTRACT[Text Extraction]
    EXTRACT --> CHUNK[Document Chunking]
    CHUNK --> EMBED[Generate Embeddings]
    EMBED --> QDRANT[Store in Qdrant]

    QUERY[User Query] --> QEMBED[Query Embedding]
    QEMBED --> SEARCH[Vector Search]
    SEARCH --> RERANK[Re-ranking]
    RERANK --> LLM[LLM Processing]
    LLM --> RESPONSE[Response]
```

### Cost Structure (Monthly)

| Component       | Cost Range       | Notes                 |
| --------------- | ---------------- | --------------------- |
| EKS Cluster     | £300-400         | Include node costs    |
| GPU Instances   | £500-800         | g5.xlarge for ML      |
| Vector DB Nodes | £200-300         | High memory instances |
| OpenSearch      | £250-350         | 3-node cluster        |
| Database        | £150-200         | Same as Option 1      |
| Storage         | £50-100          | Same as Option 1      |
| **Total**       | **£1,450-2,150** | Higher fixed costs    |

## Infrastructure Comparison Matrix

| Aspect                 | Bedrock Architecture | Self-Hosted Architecture | Recommendation |
| ---------------------- | -------------------- | ------------------------ | -------------- |
| Initial Setup Time     | 1-2 weeks            | 4-6 weeks                | Bedrock ✓      |
| Operational Complexity | Low                  | High                     | Bedrock ✓      |
| Monthly Cost (MVP)     | £600-950             | £1,450-2,150             | Bedrock ✓      |
| Scalability            | Automatic            | Manual configuration     | Bedrock ✓      |
| Customization          | Limited              | Full control             | Self-Hosted ✓  |
| Vendor Lock-in         | High                 | Low                      | Self-Hosted ✓  |
| ML Model Options       | AWS models only      | Any model                | Self-Hosted ✓  |
| Maintenance Effort     | Minimal              | Significant              | Bedrock ✓      |

## Security Architecture

### Network Security

```mermaid
graph TB
    subgraph "Internet"
        USER[Users]
        ATTACKER[Threats]
    end

    subgraph "AWS Security"
        SHIELD[AWS Shield]
        WAF[WAF Rules]
        NACL[Network ACLs]
        SG[Security Groups]
    end

    subgraph "Application Security"
        AUTH[Authentication]
        AUTHZ[Authorization]
        ENCRYPT[Encryption]
    end

    USER --> SHIELD
    ATTACKER --> SHIELD
    SHIELD --> WAF
    WAF --> NACL
    NACL --> SG
    SG --> AUTH
    AUTH --> AUTHZ
    AUTHZ --> ENCRYPT
```

### Production Network Topology

```mermaid
graph TB
    subgraph "EU-WEST-2 (London)"
        subgraph "VPC 10.0.0.0/16"
            subgraph "AZ-1 (eu-west-2a)"
                PS1[Public Subnet<br/>10.0.1.0/24]
                PRS1[Private Subnet<br/>10.0.10.0/24]
                DBS1[DB Subnet<br/>10.0.20.0/24]
            end
            subgraph "AZ-2 (eu-west-2b)"
                PS2[Public Subnet<br/>10.0.2.0/24]
                PRS2[Private Subnet<br/>10.0.11.0/24]
                DBS2[DB Subnet<br/>10.0.21.0/24]
            end
        end
    end

    IGW[Internet Gateway] --> PS1
    IGW --> PS2
    PS1 --> NAT1[NAT Gateway]
    PS2 --> NAT2[NAT Gateway]
    NAT1 --> PRS1
    NAT2 --> PRS2
```

### Security Controls

| Layer       | Control               | Implementation          | Sprint   |
| ----------- | --------------------- | ----------------------- | -------- |
| Network     | DDoS Protection       | AWS Shield Standard     | Sprint 0 |
| Network     | WAF                   | OWASP Top 10 rules      | Sprint 0 |
| Application | Authentication        | JWT with refresh tokens | Sprint 1 |
| Application | Authorization         | RBAC with Django        | Sprint 1 |
| Data        | Encryption at Rest    | AES-256                 | Sprint 0 |
| Data        | Encryption in Transit | TLS 1.3                 | Sprint 0 |
| Audit       | Logging               | CloudWatch + CloudTrail | Sprint 0 |

## Monitoring & Observability

### Metrics Collection

```mermaid
graph LR
    subgraph "Application Metrics"
        APP[Django App] --> CW[CloudWatch]
        CELERY[Celery] --> CW
    end

    subgraph "Infrastructure Metrics"
        ECS[ECS/EKS] --> CW
        RDS[RDS] --> CW
        S3[S3] --> CW
    end

    subgraph "Business Metrics"
        CUSTOM[Custom Metrics] --> CW
    end

    CW --> ALARM[Alarms]
    CW --> DASH[Dashboards]
    ALARM --> SNS[SNS]
    SNS --> SLACK[Slack]
    SNS --> PAGER[PagerDuty]
```

### Key Performance Indicators

| Metric                  | Target | Alert Threshold | Dashboard      |
| ----------------------- | ------ | --------------- | -------------- |
| API Latency P95         | <500ms | >1000ms         | Operations     |
| Error Rate              | <0.1%  | >1%             | Operations     |
| AI Processing Time      | <30s   | >60s            | OSAE           |
| Document Upload Success | >99%   | <95%            | Business       |
| Database CPU            | <60%   | >80%            | Infrastructure |
| Cost per Property       | <£5    | >£10            | Finance        |

## Disaster Recovery

### Backup Strategy

| Component          | RPO      | RTO        | Method                 | Frequency  |
| ------------------ | -------- | ---------- | ---------------------- | ---------- |
| Database           | 1 hour   | 2 hours    | Automated snapshots    | Continuous |
| Documents          | 0        | 1 hour     | S3 cross-region        | Real-time  |
| Application Config | 24 hours | 30 minutes | Infrastructure as Code | Daily      |
| Knowledge Bases    | 24 hours | 4 hours    | S3 backup              | Daily      |

### Recovery Procedures

```mermaid
graph TB
    INCIDENT[Incident Detected] --> ASSESS[Assess Impact]
    ASSESS --> MINOR[Minor Issue]
    ASSESS --> MAJOR[Major Outage]

    MINOR --> FIX[Apply Fix]
    FIX --> VERIFY[Verify Resolution]

    MAJOR --> FAILOVER[Initiate Failover]
    FAILOVER --> RESTORE[Restore from Backup]
    RESTORE --> VALIDATE[Validate Services]
    VALIDATE --> VERIFY

    VERIFY --> REPORT[Post-Mortem Report]
```

## Implementation Phases

### Phase 1: Foundation (Sprint 0-1)

- VPC and networking setup
- Basic compute infrastructure
- Database provisioning
- CI/CD pipeline
- Monitoring foundation

### Phase 2: Application Platform (Sprint 1-2)

- ECS/EKS cluster setup
- Load balancer configuration
- Auto-scaling policies
- Cache layer implementation
- Message queue setup

### Phase 3: AI Infrastructure (Sprint 3-4)

- Bedrock setup OR Qdrant deployment
- Knowledge base creation
- Model serving infrastructure
- RAG pipeline implementation

### Phase 4: Production Hardening (Sprint 5-6)

- Security audit implementation
- Disaster recovery testing
- Performance optimization
- Cost optimization
- Documentation completion

## Appendix: Compliance Checklist

### GDPR Compliance

- [ ] Data residency in UK/EU
- [ ] Encryption at rest and in transit
- [ ] Right to be forgotten implementation
- [ ] Data portability features
- [ ] Consent management
- [ ] Audit trail for data access

### Security Compliance

- [ ] SOC 2 Type II controls
- [ ] Penetration testing scheduled
- [ ] Vulnerability scanning automated
- [ ] Security incident response plan
- [ ] Business continuity plan
- [ ] Regular security training
