# Project Atlas Enterprise Transformation CHANGELOG

## [3.0.0] - Universal AI Data Control & Governance Release

### 🚀 Major Platform Architecture Upgrades

#### 1. AI Orchestration Layer (`app/ai/`)
- `providers.py`: Abstract interface and concrete LLM providers (`OpenAIProvider`, `AnthropicProvider`, `OllamaLocalProvider`).
- `router.py`: Created `AIOrchestrator` with automatic provider routing, failover, streaming token handling, and cost optimization.

#### 2. Knowledge Graph Engine (`app/graph/`)
- `engine.py`: Built `KnowledgeGraphEngine` to extract graph entities (`KnowledgeEntity`) and relationships (`KnowledgeRelationship`). Generates graph adjacency structures for Next.js visual traversal canvas.

#### 3. Universal Data Governance & PII Classifier (`app/governance/`)
- `classifier.py`: Created `DataClassifier` for scanning SSN, Phone, Email, API Keys, Passwords, and Financial Data. Automatically assigns security levels (`PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`, `TOP_SECRET`).
- `lineage.py`: Built `DataLineageTracker` enforcing 18-step data lifecycle provenance tracking.

#### 4. Policy Engine & Simulator (`app/policy/`)
- `engine.py`: Built `EnterprisePolicyEngine` supporting dry-run evaluation of dynamic ABAC policies (department rules, IP ranges, time windows, classification locks).

#### 5. Enterprise Next.js UI Expansion (`frontend/src/app/page.tsx`)
- Enhanced workspace with Knowledge Graph Explorer canvas, Data Governance & PII scanner view, Policy Engine Simulator, and AI Orchestrator Studio.

#### 6. DevOps & Infrastructure (`terraform/` & `helm/`)
- Added `terraform/main.tf` EKS cluster definitions and `helm/atlas/Chart.yaml` deployment manifests.

---

## [2.0.0] - Enterprise AI Platform Release

- Real Embedding System with multi-provider abstraction (`OpenAI`, `Voyage`, `Jina`, `Nomic`, `BGE`, `Ollama`).
- Multi-format enterprise document parsers with Tesseract OCR fallback.
- Connector engine for Google Drive, Slack, Jira, GitHub, and Confluence.
- Fine-grained RBAC + ABAC policy evaluator.
- Hybrid Search (BM25 + pgvector Cosine similarity with RRF).
- Full RAG Pipeline with inline citations and SSE streaming responses.
- AES-256-GCM Envelope Encryption and Redis sliding window rate limiter.
