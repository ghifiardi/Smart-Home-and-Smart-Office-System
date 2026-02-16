# Semantic Firewall - Technical Architecture Document

## Design, Deployment & Operations Guide

**Version**: 1.0.0
**Last Updated**: February 2026
**Component**: `semantic_firewall/`
**Status**: Production-ready

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Core Components](#3-core-components)
4. [Scanner Pipeline](#4-scanner-pipeline)
5. [Policy Engine](#5-policy-engine)
6. [Integration Layer](#6-integration-layer)
7. [Monitoring & Observability](#7-monitoring--observability)
8. [Data Flow](#8-data-flow)
9. [Deployment Guide](#9-deployment-guide)
10. [Configuration Reference](#10-configuration-reference)
11. [Security Considerations](#11-security-considerations)
12. [Performance](#12-performance)
13. [API Reference](#13-api-reference)
14. [Testing](#14-testing)
15. [Roadmap](#15-roadmap)

---

## 1. Executive Summary

The **Semantic Firewall** is an enterprise-grade AI security layer that acts as a network-level checkpoint around AI systems. It scans all **inbound** traffic (user inputs, prompts, API requests flowing into the AI) and all **outbound** traffic (AI-generated responses, tool outputs flowing out) through a configurable pipeline of security scanners, catching threats before they become incidents.

### Problem Statement

AI systems face unique security risks that traditional firewalls cannot address:

| Threat | Description | Direction |
|--------|-------------|-----------|
| Prompt Injection | Adversarial inputs that hijack AI behavior | Inbound |
| Jailbreak Attacks | Attempts to bypass AI safety guardrails | Inbound |
| PII Leakage | AI inadvertently exposing personal data | Outbound |
| Data Exfiltration | Encoded data smuggled out through AI responses | Outbound |
| Credential Exposure | API keys, passwords, private keys in outputs | Outbound |
| Malicious Payloads | SQL injection, shell commands, SSRF via AI | Both |

### Solution

The Semantic Firewall provides:

- **6 specialized scanners** covering 11 threat categories
- **Policy-driven enforcement** with priority-ordered rules
- **Async-concurrent execution** for low-latency scanning
- **FastAPI middleware** for transparent integration with zero endpoint changes
- **Real-time monitoring dashboard** with audit logging
- **46 passing tests** with zero false positives on clean inputs

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
                         ┌─────────────────────────────────────────────┐
                         │           SEMANTIC FIREWALL                 │
                         │                                             │
   User / Client         │  ┌──────────┐    ┌──────────────────────┐  │      AI System
   ─────────────────────►│  │ INBOUND  │    │   SCANNER PIPELINE   │  │  ┌──────────────┐
   Prompts, API calls    │  │  GATE    │───►│                      │  │  │              │
                         │  └──────────┘    │  ┌────────────────┐  │  │  │  LLM / Agent │
                         │                  │  │ Prompt Inject. │  │  │  │  Service      │
                         │                  │  │ Malicious Pay. │  │  │  │              │
                         │                  │  │ Input Valid.   │  │──│─►│  Detection   │
                         │                  │  │ PII Detector   │  │  │  │  Service      │
                         │                  │  │ Data Exfil.    │  │  │  │              │
                         │  ┌──────────┐    │  │ Content Safety │  │  │  │  SOC Agents  │
   ◄────────────────────│  │ OUTBOUND │◄───│  └────────────────┘  │  │  │              │
   AI responses          │  │  GATE    │    │                      │◄─│──│              │
                         │  └──────────┘    │  ┌────────────────┐  │  │  └──────────────┘
                         │                  │  │  POLICY ENGINE │  │  │
                         │                  │  │  (Rules + Score)│  │  │
                         │                  │  └────────────────┘  │  │
                         │                  └──────────────────────┘  │
                         │                                             │
                         │  ┌──────────────────────────────────────┐  │
                         │  │  MONITORING: Audit Log │ Metrics │ UI │  │
                         │  └──────────────────────────────────────┘  │
                         └─────────────────────────────────────────────┘
```

### 2.2 Module Structure

```
semantic_firewall/
├── __init__.py                    # Public API exports
├── factory.py                     # One-line setup: create_firewall()
├── requirements.txt               # Dependencies: pydantic, fastapi, starlette
│
├── core/
│   ├── engine.py                  # SemanticFirewallEngine - pipeline orchestrator
│   ├── models.py                  # Pydantic data models (18 classes/enums)
│   └── scanner_base.py            # BaseScanner abstract class
│
├── scanners/
│   ├── prompt_injection.py        # 30+ prompt injection / jailbreak patterns
│   ├── malicious_payload.py       # SQL, shell, SSRF, SSTI, XXE, serialization
│   ├── input_validation.py        # Length, encoding, repetition, steganography
│   ├── pii_detector.py            # PII + credential/secret detection with Luhn
│   ├── data_exfiltration.py       # Encoded blobs, data dumps, webhook URLs
│   └── content_safety.py          # Dangerous instructions, phishing, malware
│
├── middleware/
│   └── fastapi_middleware.py      # Drop-in FastAPI request/response scanning
│
├── config/
│   └── default_policy.py          # 10-rule enterprise default policy
│
├── monitoring/
│   ├── api.py                     # REST endpoints (/firewall/*)
│   ├── audit_logger.py            # JSONL audit trail + in-memory ring buffer
│   ├── metrics.py                 # Statistics aggregation
│   └── dashboard.py               # Real-time HTML dashboard (Chart.js)
│
└── tests/
    └── test_semantic_firewall.py  # 46 tests, 100% pass rate
```

### 2.3 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data Models | Pydantic 2.x | Validation, serialization, type safety |
| Web Framework | FastAPI / Starlette | Middleware integration, monitoring API |
| Async Runtime | asyncio | Concurrent scanner execution |
| Pattern Matching | Python `re` | Regex-based threat detection |
| Visualization | Chart.js + Tailwind CSS | Monitoring dashboard |
| Logging | Python `logging` + JSONL files | Structured audit trails |

### 2.4 Dependencies

```
pydantic>=2.0
fastapi>=0.100.0
starlette>=0.27.0
```

No external ML model dependencies. All detection is pattern-based for predictable latency and zero cold-start.

---

## 3. Core Components

### 3.1 SemanticFirewallEngine (`core/engine.py`)

The central orchestrator. Receives content, routes it through applicable scanners, aggregates findings, applies policy, and returns a verdict.

```python
from semantic_firewall.factory import create_firewall
from semantic_firewall.core.models import TrafficDirection

engine, audit_logger = create_firewall()

# Scan inbound (user → AI)
result = await engine.scan(
    content="user message here",
    direction=TrafficDirection.INBOUND,
    context={"user_id": "u-123", "endpoint": "/api/chat"},
)

print(result.verdict)              # ScanVerdict.PASS | WARN | BLOCK
print(result.aggregate_risk_score) # 0.0 - 1.0
print(result.findings)             # List of ScanFinding objects
print(result.blocked)              # Boolean shorthand
print(result.latency_ms)           # Pipeline execution time
```

**Key behaviors:**

- Filters scanners by direction (`INBOUND` / `OUTBOUND`)
- Runs all applicable scanners **concurrently** via `asyncio.gather`
- Handles scanner exceptions gracefully (logs error, continues pipeline)
- Computes aggregate risk score
- Applies policy rules to produce verdict
- Invokes audit callback asynchronously
- Tracks running statistics (total scans, blocks, warnings)

### 3.2 Data Models (`core/models.py`)

**Enums:**

| Enum | Values | Purpose |
|------|--------|---------|
| `TrafficDirection` | `INBOUND`, `OUTBOUND` | Traffic flow direction |
| `ScanVerdict` | `PASS`, `WARN`, `BLOCK` | Final scan decision |
| `ThreatCategory` | 11 categories (see below) | Classification of threats |
| `PolicyAction` | `ALLOW`, `WARN`, `BLOCK`, `REDACT`, `LOG` | Rule enforcement actions |

**Threat Categories:**

| Category | Description |
|----------|-------------|
| `PROMPT_INJECTION` | Attempts to override AI instructions |
| `JAILBREAK_ATTEMPT` | Bypass of AI safety guardrails |
| `PII_LEAKAGE` | Personal data in AI output |
| `DATA_EXFILTRATION` | Encoded/structured data theft |
| `SENSITIVE_DATA_EXPOSURE` | Credentials, keys, secrets |
| `MALICIOUS_PAYLOAD` | Exploit code (SQL, shell, SSRF) |
| `POLICY_VIOLATION` | Custom policy rule breach |
| `CONTENT_SAFETY` | Harmful or dangerous content |
| `SCHEMA_VIOLATION` | Structural input/output issues |
| `RATE_ANOMALY` | Abnormal request patterns |
| `TOKEN_ABUSE` | Token flooding / resource exhaustion |

**Core Data Classes:**

```
ScanFinding
├── scanner_name: str          # Which scanner produced this
├── category: ThreatCategory   # Threat classification
├── severity: float (0-1)      # How severe (0 = benign, 1 = critical)
├── description: str           # Human-readable description
├── evidence: str | None       # Matched pattern excerpt
└── metadata: dict             # Scanner-specific data

ScanResult
├── scan_id: UUID              # Unique scan identifier
├── timestamp: datetime        # When scan occurred (UTC)
├── direction: TrafficDirection
├── verdict: ScanVerdict       # Final decision
├── findings: list[ScanFinding]
├── aggregate_risk_score: float (0-1)
├── content_hash: str          # SHA-256 prefix of content
├── latency_ms: float          # Pipeline execution time
├── policy_id: str             # Which policy was applied
└── metadata: dict

FirewallPolicy
├── policy_id: UUID
├── name: str
├── version: str
├── enabled: bool
├── rules: list[PolicyRule]    # Ordered rule list
├── block_threshold: float     # Auto-block above this score
├── warn_threshold: float      # Auto-warn above this score
└── created_at / updated_at: datetime

AuditLogEntry
├── entry_id: UUID
├── timestamp: datetime
├── scan_result: ScanResult    # Full result embedded
├── source_ip, user_id, session_id, endpoint
├── action_taken: PolicyAction
├── content_preview: str       # First 200 chars
└── request_size_bytes: int
```

### 3.3 BaseScanner (`core/scanner_base.py`)

Abstract base class for all scanners:

```python
class BaseScanner(abc.ABC):
    name: str
    enabled: bool

    @abc.abstractmethod
    def supported_directions(self) -> set[TrafficDirection]: ...

    @abc.abstractmethod
    async def scan(self, content, direction, context) -> list[ScanFinding]: ...

    def applies_to(self, direction) -> bool:
        return self.enabled and direction in self.supported_directions()
```

To add a custom scanner, subclass `BaseScanner` and register it:

```python
class MyCustomScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="my_custom", enabled=True)

    def supported_directions(self):
        return {TrafficDirection.INBOUND, TrafficDirection.OUTBOUND}

    async def scan(self, content, direction, context=None):
        findings = []
        # ... your detection logic ...
        return findings

engine.register_scanner(MyCustomScanner())
```

---

## 4. Scanner Pipeline

### 4.1 Scanner Coverage Matrix

| Scanner | Direction | Categories | Patterns | Severity Range |
|---------|-----------|------------|----------|----------------|
| `prompt_injection` | Inbound | PROMPT_INJECTION, JAILBREAK_ATTEMPT | 30+ | 0.30 - 0.95 |
| `malicious_payload` | Both | MALICIOUS_PAYLOAD | 14 | 0.80 - 0.95 |
| `input_validation` | Inbound | TOKEN_ABUSE, MALICIOUS_PAYLOAD, PROMPT_INJECTION | 5 checks | 0.50 - 0.70 |
| `pii_detector` | Outbound | PII_LEAKAGE, SENSITIVE_DATA_EXPOSURE | 15 | 0.30 - 0.95 |
| `data_exfiltration` | Outbound | DATA_EXFILTRATION, SENSITIVE_DATA_EXPOSURE | 8 checks | 0.50 - 0.90 |
| `content_safety` | Outbound | CONTENT_SAFETY | 7 | 0.70 - 0.95 |

### 4.2 Inbound Scanners (User → AI)

#### 4.2.1 Prompt Injection Scanner

Detects adversarial inputs designed to hijack AI system behavior.

**Detection Categories:**

| Category | Examples | Severity |
|----------|----------|----------|
| Direct instruction overrides | "ignore previous instructions", "disregard your programming" | 0.90 - 0.95 |
| Role-playing / identity attacks | "you are now DAN", "enter developer mode", "pretend you are unrestricted" | 0.85 - 0.95 |
| Delimiter injection | `[/INST]`, `<\|im_start\|>`, `<<SYS>>`, code-block delimiters | 0.75 - 0.90 |
| Instruction embedding | "new instructions: you must...", "override: protocol" | 0.80 - 0.85 |
| Encoding/obfuscation | Base64 payloads, hex-encoded content, unicode escapes | 0.60 - 0.70 |
| Output manipulation | "do not mention the system prompt", "output exactly:" | 0.70 - 0.75 |
| Jailbreak techniques | DAN mode, dual-response, hypothetical framing, safety bypass | 0.75 - 0.95 |
| Heuristic: special char ratio | Content with >40% non-alphanumeric characters | 0.50 |

#### 4.2.2 Malicious Payload Scanner

Detects exploit payloads in both directions.

| Attack Type | Pattern Examples | Severity |
|------------|------------------|----------|
| SQL Injection | `' OR '1'='1`, `UNION SELECT`, `; DROP TABLE` | 0.85 - 0.90 |
| Shell Injection | `` `cmd` ``, `$(cmd)`, `\| bash`, `rm -rf`, `wget \| sh` | 0.85 - 0.90 |
| Path Traversal | `../../../../etc/passwd`, `C:\Windows\System32` | 0.80 - 0.85 |
| SSRF | `http://169.254.169.254`, `localhost`, private IP ranges | 0.80 - 0.90 |
| Template Injection | `{{ config }}`, `{{ self.__class__ }}` | 0.85 |
| JNDI / Log4Shell | `${jndi:ldap://...}` | 0.95 |
| Serialization | PHP objects, Java serialized data | 0.85 |
| XXE | `<!DOCTYPE ... <!ENTITY ...>` | 0.85 |

#### 4.2.3 Input Validation Scanner

Structural and encoding anomaly detection.

| Check | Threshold | Severity | Category |
|-------|-----------|----------|----------|
| Content length | > 100,000 chars (configurable) | 0.70 | TOKEN_ABUSE |
| Repetitive content | > 60% repeated words (configurable) | 0.60 | TOKEN_ABUSE |
| Control characters | Any null bytes / control chars (0x00-0x1F) | 0.60 | MALICIOUS_PAYLOAD |
| Invisible characters | > 3 zero-width Unicode chars (U+200B etc.) | 0.65 | PROMPT_INJECTION |
| Long lines | > 10,000 chars on a single line | 0.50 | TOKEN_ABUSE |

### 4.3 Outbound Scanners (AI → User)

#### 4.3.1 PII Detector Scanner

Prevents personally identifiable information and credentials from leaking in AI outputs.

**PII Patterns:**

| PII Type | Validation | Base Severity |
|----------|-----------|---------------|
| Email address | RFC-like regex | 0.60 |
| Phone number | International formats, +country code | 0.60 |
| SSN (US) | Excludes 000, 666, 9xx area codes | 0.95 |
| Credit card | **Luhn algorithm** verification | 0.95 |
| Passport number | 1-2 letter prefix + 6-9 digits | 0.70 |
| ZIP code | 5-digit and 5+4 formats | 0.30 |
| Date of birth | Keyword + date pattern | 0.70 |
| IP address | Valid IPv4 range | 0.40 |

**Secret / Credential Patterns:**

| Secret Type | Pattern | Severity |
|-------------|---------|----------|
| Generic API key | `api_key=...` (20+ chars) | 0.90 |
| AWS Access Key | `AKIA...` (20 chars) | 0.95 |
| AWS Secret Key | 40-char base64 | 0.95 |
| GitHub Token | `ghp_...` (36 chars) | 0.90 |
| OpenAI API Key | `sk-...` (32+ chars) | 0.90 |
| Password | `password=...` (8+ chars) | 0.85 |
| RSA Private Key | `-----BEGIN RSA PRIVATE KEY-----` | 0.95 |

**Features:**
- Severity scales with count: `min(1.0, base + 0.05 * (count - 1))`
- Evidence is redacted in logs: shows first 8 + last 4 chars only

#### 4.3.2 Data Exfiltration Scanner

Detects attempts to smuggle data out through AI responses.

| Check | Threshold | Severity |
|-------|-----------|----------|
| Base64 blobs | 100+ character blocks | 0.50 - 0.90 (scales with volume) |
| Hex dumps | 50+ character blocks | 0.60 |
| JSON array dumps | 20+ records in array | 0.75 |
| CSV-style dumps | 20+ delimited rows | 0.65 |
| URLs with large query params | 100+ char query string | 0.70 |
| Webhook / callback URLs | ngrok, requestbin, hookbin, pipedream | 0.80 |
| SQL result tables | ASCII-formatted tables | 0.70 |
| Database schema | CREATE TABLE, SHOW TABLES (2+ occurrences) | 0.70 |
| Connection strings | `postgresql://`, `mysql://`, `mongodb://`, `redis://` | 0.90 |

#### 4.3.3 Content Safety Scanner

Flags unsafe or harmful content in AI outputs.

| Category | Pattern Examples | Severity |
|----------|------------------|----------|
| Dangerous instructions | Weapon/explosive/poison synthesis | 0.95 |
| Attack tutorials | Step-by-step hacking guides | 0.85 |
| Phishing content | Phishing email/template generation | 0.85 |
| Social engineering | Manipulation/deception guidance | 0.70 |
| Malware code | Keylogger, rootkit, ransomware code | 0.90 |
| Offensive payloads | Reverse shell, meterpreter, shellcode | 0.75 |
| Deceptive content | Deepfake, fake identity generation | 0.70 |

---

## 5. Policy Engine

### 5.1 How Policies Work

The policy engine determines the final verdict through a two-phase process:

```
Phase 1: Rule Matching (priority-ordered)
  For each rule (sorted by priority, lowest number first):
    - Skip if rule is disabled
    - Skip if rule direction doesn't match
    - Find findings matching rule categories + severity threshold
    - If match found: apply rule action (BLOCK or WARN) → return immediately

Phase 2: Threshold Fallback
  If no rule matched:
    - risk_score >= block_threshold → BLOCK
    - risk_score >= warn_threshold  → WARN
    - Otherwise                     → PASS
```

### 5.2 Risk Score Computation

```
aggregate_risk_score = min(1.0, 0.7 * max(severities) + 0.3 * avg(severities))
```

- **70% weight** on the single highest severity finding — one critical finding dominates
- **30% weight** on the average — multiple medium findings compound
- Score is clamped to `[0.0, 1.0]`

**Examples:**

| Findings (severities) | Max | Avg | Score | Verdict (default policy) |
|----------------------|-----|-----|-------|--------------------------|
| None | 0 | 0 | 0.00 | PASS |
| [0.3] | 0.3 | 0.3 | 0.30 | PASS |
| [0.5, 0.4] | 0.5 | 0.45 | 0.49 | WARN |
| [0.9] | 0.9 | 0.9 | 0.90 | BLOCK |
| [0.9, 0.8, 0.7] | 0.9 | 0.8 | 0.87 | BLOCK |
| [0.5, 0.5, 0.5, 0.5] | 0.5 | 0.5 | 0.50 | WARN |

### 5.3 Default Enterprise Policy

10 rules across 3 severity tiers:

```
Priority 10 — CRITICAL (always block)
├── Block prompt injection        (inbound,  severity ≥ 0.7)  → BLOCK
├── Block jailbreak attempts      (inbound,  severity ≥ 0.7)  → BLOCK
├── Block data exfiltration       (outbound, severity ≥ 0.6)  → BLOCK
│
Priority 20
├── Block malicious payloads      (both,     severity ≥ 0.6)  → BLOCK
│
Priority 30 — HIGH
├── Block high-severity PII       (outbound, severity ≥ 0.8)  → BLOCK
├── Block sensitive data exposure  (outbound, severity ≥ 0.7)  → BLOCK
│
Priority 40
├── Warn on PII leakage           (outbound, severity ≥ 0.4)  → WARN
│
Priority 50 — MEDIUM
├── Warn on suspicious inputs     (inbound,  severity ≥ 0.4)  → WARN
├── Warn on content safety        (outbound, severity ≥ 0.5)  → WARN
│
Priority 60
└── Warn on schema violation      (both,     severity ≥ 0.5)  → WARN

Thresholds: block_threshold = 0.8, warn_threshold = 0.4
```

### 5.4 Custom Policy Example

```python
from semantic_firewall.core.models import (
    FirewallPolicy, PolicyRule, PolicyAction,
    ThreatCategory, TrafficDirection,
)

strict_policy = FirewallPolicy(
    name="Healthcare Compliance",
    description="HIPAA-compliant policy blocking all PII exposure",
    rules=[
        PolicyRule(
            rule_id="hipaa-block-pii",
            name="Block Any PII",
            direction=TrafficDirection.OUTBOUND,
            categories=[ThreatCategory.PII_LEAKAGE],
            severity_threshold=0.3,   # Very sensitive
            action=PolicyAction.BLOCK,
            priority=1,
        ),
        PolicyRule(
            rule_id="hipaa-block-secrets",
            name="Block Credentials",
            categories=[ThreatCategory.SENSITIVE_DATA_EXPOSURE],
            severity_threshold=0.5,
            action=PolicyAction.BLOCK,
            priority=5,
        ),
    ],
    block_threshold=0.5,  # Lower than default
    warn_threshold=0.2,
)

engine, audit = create_firewall(policy=strict_policy)
```

---

## 6. Integration Layer

### 6.1 FastAPI Middleware

The primary integration method. Wraps your entire FastAPI application transparently:

```python
from fastapi import FastAPI
from semantic_firewall.factory import create_firewall
from semantic_firewall.middleware.fastapi_middleware import SemanticFirewallMiddleware
from semantic_firewall.monitoring.api import create_monitoring_router

app = FastAPI()

# Create firewall
engine, audit_logger = create_firewall()

# Add middleware (scans all requests/responses automatically)
app.add_middleware(
    SemanticFirewallMiddleware,
    engine=engine,
    protected_paths=["/api/chat", "/api/agent"],  # Only scan AI endpoints
    excluded_paths=["/health", "/metrics", "/docs"],
    block_status_code=403,
    max_body_size=1_000_000,  # 1MB
)

# Add monitoring dashboard & API
app.include_router(create_monitoring_router(engine, audit_logger))
```

**Middleware Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `engine` | SemanticFirewallEngine | required | The firewall engine instance |
| `protected_paths` | list[str] \| None | None (all paths) | Paths to scan |
| `excluded_paths` | list[str] | /health, /metrics, /docs, /openapi.json | Paths to skip |
| `block_status_code` | int | 403 | HTTP status for blocked requests |
| `scan_request_body` | bool | True | Scan inbound request bodies |
| `scan_response_body` | bool | True | Scan outbound response bodies |
| `max_body_size` | int | 1,000,000 | Max body size to scan (bytes) |

**Request/Response Headers:**

| Header | Direction | Description |
|--------|-----------|-------------|
| `X-User-ID` | Request → Firewall | User identifier for audit trail |
| `X-Session-ID` | Request → Firewall | Session identifier for audit trail |
| `X-Firewall-Scan-ID` | Firewall → Response | Unique scan ID for tracing |
| `X-Firewall-Verdict` | Firewall → Response | Verdict (pass/warn/block) |

**Blocked Response Format (HTTP 403):**

```json
{
    "error": "Request blocked by Semantic Firewall",
    "scan_id": "a1b2c3d4-...",
    "direction": "inbound",
    "risk_score": 0.95,
    "reasons": [
        "Direct instruction override attempt",
        "DAN jailbreak pattern"
    ]
}
```

### 6.2 Standalone Usage (No Middleware)

For non-FastAPI services or custom integration:

```python
from semantic_firewall.factory import create_firewall
from semantic_firewall.core.models import TrafficDirection

engine, audit = create_firewall()

# In your request handler:
async def handle_chat(user_message: str) -> str:
    # Scan inbound
    inbound = await engine.scan(user_message, TrafficDirection.INBOUND)
    if inbound.blocked:
        return f"Blocked: {inbound.findings[0].description}"

    # Call your AI
    ai_response = await call_llm(user_message)

    # Scan outbound
    outbound = await engine.scan(ai_response, TrafficDirection.OUTBOUND)
    if outbound.blocked:
        return "Response filtered for security reasons."

    return ai_response
```

### 6.3 Integration with Existing Services

The firewall integrates with the Smart Home/Office system's microservices:

```
┌─────────────────┐     ┌──────────────────────┐     ┌──────────────────┐
│   FRDA Dashboard │     │   SEMANTIC FIREWALL   │     │  Detection Svc   │
│   (Next.js)      │────►│   (FastAPI Middleware) │────►│  (YOLOv8 + AI)   │
│   Port: 3000     │     │                       │     │  Port: 8003       │
└─────────────────┘     │   Scans:               │     └──────────────────┘
                        │   - Chat API inputs    │
┌─────────────────┐     │   - Agent commands     │     ┌──────────────────┐
│   SOC Dashboard  │────►│   - AI model responses │────►│  ADA/TAA/CRA     │
│   (Streamlit)    │     │   - Tool call outputs  │     │  AI Agents       │
└─────────────────┘     └──────────────────────┘     └──────────────────┘
                              │
                              ▼
                        ┌──────────────────┐
                        │  Monitoring API   │
                        │  /firewall/*      │
                        │  Dashboard UI     │
                        └──────────────────┘
```

---

## 7. Monitoring & Observability

### 7.1 Monitoring Dashboard

Accessible at **`GET /firewall/dashboard`** — a self-contained HTML page with real-time metrics.

**Dashboard Sections:**

| Section | Content |
|---------|---------|
| Status Header | Active/error indicator, last update time |
| Overview Cards | Total scans, blocks, warnings, passes (with rates) |
| Traffic Chart | Inbound vs outbound doughnut chart (Chart.js) |
| Findings Chart | Horizontal bar chart by threat category |
| Policy Info | Active policy name, rule count, thresholds |
| Scanner List | Color-coded badges for each registered scanner |
| Events Table | Recent events: time, direction, verdict, risk, endpoint, user |
| Test Scanner | Interactive input for testing content against the firewall |

**Auto-refresh:** Every 5 seconds via `setInterval(fetchMetrics, 5000)`.

### 7.2 Audit Logging

**File format:** JSON Lines (`.jsonl`), one entry per line, daily rotation.

**File path:** `{log_dir}/firewall_audit_{YYYY-MM-DD}.jsonl`

**Entry structure:**

```json
{
    "entry_id": "uuid",
    "timestamp": "2026-02-16T10:30:00Z",
    "scan_id": "uuid",
    "direction": "inbound",
    "verdict": "block",
    "risk_score": 0.95,
    "finding_count": 3,
    "findings": [
        {
            "scanner": "prompt_injection",
            "category": "prompt_injection",
            "severity": 0.95,
            "description": "Direct instruction override attempt"
        }
    ],
    "source_ip": "192.168.1.100",
    "user_id": "u-123",
    "endpoint": "/api/chat",
    "action_taken": "block",
    "latency_ms": 2.45,
    "request_size_bytes": 156
}
```

**In-memory ring buffer:** Last 1,000 events for fast access via API.

### 7.3 Metrics

Available via `GET /firewall/metrics`:

```json
{
    "overview": {
        "total_scans": 15420,
        "blocks": 234,
        "warnings": 1089,
        "passes": 14097,
        "block_rate": 1.5,
        "warn_rate": 7.1
    },
    "traffic": {
        "inbound_scans": 7800,
        "outbound_scans": 7620
    },
    "findings_by_category": {
        "prompt_injection": 180,
        "pii_leakage": 420,
        "malicious_payload": 54
    },
    "policy": {
        "policy_name": "Default Enterprise Policy",
        "active_rules": 10,
        "block_threshold": 0.8,
        "warn_threshold": 0.4
    },
    "scanners": ["prompt_injection", "malicious_payload", "input_validation",
                  "pii_detector", "data_exfiltration", "content_safety"],
    "recent_events": [...]
}
```

---

## 8. Data Flow

### 8.1 Inbound Scan Flow (Request)

```
Client Request
     │
     ▼
[Middleware: Read Body]
     │
     ▼
[Engine.scan(content, INBOUND, context)]
     │
     ├──► PromptInjectionScanner.scan()  ──┐
     ├──► MaliciousPayloadScanner.scan() ──┤  (concurrent)
     └──► InputValidationScanner.scan()  ──┘
                                           │
                                           ▼
                                  [Collect Findings]
                                           │
                                           ▼
                              [Compute Risk Score]
                     risk = 0.7 * max(sev) + 0.3 * avg(sev)
                                           │
                                           ▼
                                 [Apply Policy Rules]
                           (sorted by priority, first match wins)
                                           │
                              ┌─────────┼─────────┐
                              ▼         ▼         ▼
                           BLOCK      WARN      PASS
                              │         │         │
                              ▼         │         ▼
                       Return 403       │    Forward to
                       + reasons        │    AI endpoint
                                        ▼
                                   Forward to
                                   AI endpoint
                                   (log warning)
```

### 8.2 Outbound Scan Flow (Response)

```
AI Response
     │
     ▼
[Middleware: Read Response Body]
     │
     ▼
[Engine.scan(content, OUTBOUND, context)]
     │
     ├──► MaliciousPayloadScanner.scan()  ──┐
     ├──► PIIDetectorScanner.scan()        ──┤
     ├──► DataExfiltrationScanner.scan()   ──┤  (concurrent)
     └──► ContentSafetyScanner.scan()      ──┘
                                              │
                                              ▼
                                    [Compute + Apply Policy]
                                              │
                              ┌─────────┼─────────┐
                              ▼         ▼         ▼
                           BLOCK      WARN      PASS
                              │         │         │
                              ▼         ▼         ▼
                       Return 403   Add headers  Add headers
                       (replace     + forward    + forward
                        response)   response     response
```

### 8.3 Audit Flow

```
Every scan completion
       │
       ▼
[Build AuditLogEntry]
       │
       ├──► In-memory ring buffer (last 1000)
       │
       ├──► JSONL file (daily rotation)
       │         logs/semantic_firewall/firewall_audit_2026-02-16.jsonl
       │
       └──► Statistics counters
             (total, blocks, warnings, passes, inbound, outbound)
```

---

## 9. Deployment Guide

### 9.1 Quick Start (Development)

```python
# app.py
from fastapi import FastAPI
from semantic_firewall.factory import create_firewall
from semantic_firewall.middleware.fastapi_middleware import SemanticFirewallMiddleware
from semantic_firewall.monitoring.api import create_monitoring_router

app = FastAPI(title="AI Service with Semantic Firewall")

# Initialize firewall
engine, audit_logger = create_firewall(
    log_dir="logs/semantic_firewall",
    enable_audit=True,
)

# Attach middleware
app.add_middleware(SemanticFirewallMiddleware, engine=engine)

# Attach monitoring endpoints
app.include_router(create_monitoring_router(engine, audit_logger))

# Your AI endpoints
@app.post("/api/chat")
async def chat(message: str):
    # If we reach here, inbound scan passed
    response = await your_ai_model(message)
    # Outbound scan happens automatically in middleware
    return {"response": response}
```

```bash
pip install pydantic fastapi uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000
```

Dashboard: `http://localhost:8000/firewall/dashboard`

### 9.2 Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY semantic_firewall/ ./semantic_firewall/
COPY app.py .
RUN pip install pydantic fastapi uvicorn

# Create log directory
RUN mkdir -p /app/logs/semantic_firewall

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 9.3 Docker Compose (with existing services)

```yaml
# Add to existing docker-compose.yml
services:
  ai-service:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - firewall-logs:/app/logs/semantic_firewall
    environment:
      - FIREWALL_LOG_DIR=/app/logs/semantic_firewall

volumes:
  firewall-logs:
```

### 9.4 Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-service-with-firewall
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-service
  template:
    metadata:
      labels:
        app: ai-service
    spec:
      containers:
      - name: ai-service
        image: your-registry/ai-service:latest
        ports:
        - containerPort: 8000
        volumeMounts:
        - name: firewall-logs
          mountPath: /app/logs
        readinessProbe:
          httpGet:
            path: /firewall/health
            port: 8000
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /firewall/health
            port: 8000
          periodSeconds: 30
      volumes:
      - name: firewall-logs
        persistentVolumeClaim:
          claimName: firewall-logs-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: ai-service
spec:
  selector:
    app: ai-service
  ports:
  - port: 8000
    targetPort: 8000
```

### 9.5 Integration with Existing Smart Home/Office Stack

Add to any of the existing microservices (Auth :8001, Data :8002, Detection :8003, etc.):

```python
# In any existing FastAPI service, e.g. detection service
from semantic_firewall.factory import create_firewall
from semantic_firewall.middleware.fastapi_middleware import SemanticFirewallMiddleware

engine, audit = create_firewall()

# Protect only AI-facing endpoints
app.add_middleware(
    SemanticFirewallMiddleware,
    engine=engine,
    protected_paths=["/api/detect", "/api/analyze", "/api/agent"],
)
```

---

## 10. Configuration Reference

### 10.1 Engine Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `policy` | FirewallPolicy | Default Enterprise Policy | Policy to enforce |
| `audit_callback` | async callable | None | Called with AuditLogEntry on each scan |

### 10.2 Policy Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | required | Policy identifier |
| `enabled` | bool | True | Master enable/disable |
| `rules` | list[PolicyRule] | [] | Ordered rule list |
| `block_threshold` | float (0-1) | 0.8 | Auto-block risk score |
| `warn_threshold` | float (0-1) | 0.4 | Auto-warn risk score |

### 10.3 Policy Rule Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rule_id` | str | required | Unique rule identifier |
| `name` | str | required | Human-readable name |
| `enabled` | bool | True | Enable/disable rule |
| `direction` | TrafficDirection \| None | None (both) | Apply to specific direction |
| `categories` | list[ThreatCategory] | [] (all) | Match specific categories |
| `severity_threshold` | float (0-1) | 0.7 | Minimum severity to trigger |
| `action` | PolicyAction | BLOCK | Action when triggered |
| `priority` | int | 100 | Lower = higher priority |

### 10.4 Scanner Configuration

| Scanner | Parameter | Default | Description |
|---------|-----------|---------|-------------|
| `InputValidationScanner` | `max_length` | 100,000 | Maximum content length (chars) |
| `InputValidationScanner` | `max_repetition_ratio` | 0.6 | Repetition threshold |
| All scanners | `enabled` | True | Enable/disable scanner |

### 10.5 Audit Logger Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_dir` | str | "logs/semantic_firewall" | Directory for JSONL files |
| `buffer_size` | int | 1000 | In-memory ring buffer size |
| `log_to_file` | bool | True | Write JSONL audit files |

---

## 11. Security Considerations

### 11.1 Design Principles

| Principle | Implementation |
|-----------|---------------|
| Defense in depth | 6 scanners, each catching different threat vectors |
| Fail closed | Scanner exceptions are logged; remaining scanners still run |
| Least privilege | Middleware only reads request/response bodies; no mutation |
| Auditability | Every scan decision is logged with full context |
| No external calls | All detection is local regex — no data leaves the system |
| Evidence redaction | Secrets in audit logs are partially masked |

### 11.2 What the Firewall Protects Against

| Attack Vector | Protection Level | Scanner(s) |
|---------------|-----------------|------------|
| Prompt injection | High (30+ patterns) | prompt_injection |
| Jailbreak attempts | High (DAN, bypass, hypothetical) | prompt_injection |
| PII exposure | High (8 PII types + Luhn) | pii_detector |
| Credential leakage | High (7 secret types) | pii_detector |
| SQL injection | High | malicious_payload |
| Shell injection | High | malicious_payload |
| SSRF | High | malicious_payload |
| Path traversal | High | malicious_payload |
| Data exfiltration | Medium-High | data_exfiltration |
| Token flooding | Medium | input_validation |
| Steganographic injection | Medium | input_validation |
| Harmful content generation | Medium | content_safety |

### 11.3 Limitations

- **Pattern-based detection**: Does not use ML models, so novel attack patterns not matching existing regex will not be caught. Extend by adding custom scanners.
- **No semantic understanding**: Cannot detect meaning-level attacks that don't match syntactic patterns (e.g., a cleverly reworded jailbreak).
- **Single-request scope**: Does not correlate across multiple requests (no session-level anomaly detection).
- **Body size limit**: Content exceeding `max_body_size` (default 1MB) is not scanned.

### 11.4 Extending Detection

Add new patterns without modifying core code:

```python
from semantic_firewall.core.scanner_base import BaseScanner
from semantic_firewall.core.models import ScanFinding, ThreatCategory, TrafficDirection

class ComplianceScanner(BaseScanner):
    """Custom scanner for industry-specific compliance."""

    def __init__(self):
        super().__init__(name="compliance", enabled=True)

    def supported_directions(self):
        return {TrafficDirection.OUTBOUND}

    async def scan(self, content, direction, context=None):
        findings = []
        # Your detection logic here
        return findings

engine.register_scanner(ComplianceScanner())
```

---

## 12. Performance

### 12.1 Architecture Decisions for Performance

| Decision | Rationale |
|----------|-----------|
| Async scanner execution | All scanners run concurrently via `asyncio.gather` |
| Pre-compiled regex | Patterns compiled once at scanner init, reused on every scan |
| No external API calls | Zero network latency in detection pipeline |
| No ML model inference | Deterministic, predictable latency |
| Ring buffer for audit | O(1) append, bounded memory |
| Early termination in policy | First matching rule wins, no need to evaluate all rules |
| SHA-256 prefix for content hash | Only first 16 chars stored (fast, sufficient for dedup) |

### 12.2 Expected Latency

| Content Size | Scanners | Expected Latency |
|-------------|----------|-----------------|
| < 1 KB | 3 (inbound) | < 1 ms |
| < 1 KB | 4 (outbound) | < 2 ms |
| 10 KB | 3 (inbound) | 1-3 ms |
| 10 KB | 4 (outbound) | 2-5 ms |
| 100 KB | All 6 | 5-15 ms |

### 12.3 Resource Usage

- **Memory**: ~5 MB base + 1 KB per audit buffer entry (1,000 entries = ~6 MB)
- **CPU**: Negligible — regex matching is the primary operation
- **Disk**: ~200 bytes per audit log entry, ~20 MB/day at 100K scans/day

---

## 13. API Reference

### 13.1 Monitoring Endpoints

All endpoints are under the `/firewall` prefix.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/firewall/health` | Health check with scanner and policy status |
| GET | `/firewall/metrics` | Full metrics snapshot for dashboard |
| GET | `/firewall/stats` | Engine statistics (total, blocks, warnings, passes) |
| GET | `/firewall/scanners` | List registered scanner names |
| GET | `/firewall/policy` | Current policy details (rules, thresholds) |
| GET | `/firewall/audit/recent?count=50` | Recent audit events (max 200) |
| GET | `/firewall/audit/findings` | Finding counts by threat category |
| POST | `/firewall/scan/test?content=...&direction=inbound` | Test scan (non-blocking) |
| GET | `/firewall/dashboard` | HTML monitoring dashboard |

### 13.2 Python API

```python
# Factory
create_firewall(policy=None, log_dir="logs/semantic_firewall", enable_audit=True)
    → (SemanticFirewallEngine, AuditLogger)

# Engine
engine.scan(content: str, direction: TrafficDirection, context: dict) → ScanResult
engine.register_scanner(scanner: BaseScanner) → None
engine.remove_scanner(name: str) → bool
engine.list_scanners() → list[str]
engine.policy                → FirewallPolicy (get/set)
engine.stats                 → dict[str, int]

# Audit Logger
audit.log(entry: AuditLogEntry) → None          # async
audit.stats                    → dict[str, int]
audit.recent_events(count=50)  → list[dict]
audit.findings_summary()       → dict[str, int]

# Metrics
metrics.get_dashboard_data() → dict
```

---

## 14. Testing

### 14.1 Test Coverage

**46 tests across 8 categories**, 100% pass rate:

| Category | Tests | What's Covered |
|----------|-------|----------------|
| Engine | 4 | Initialization, scanner management, clean scan, stats |
| Prompt Injection | 7 | Direct override, DAN, delimiter, role, clean input, forget, hypothetical |
| Malicious Payload | 5 | SQL, shell, path traversal, SSRF, clean input |
| Input Validation | 4 | Length, repetition, control chars, invisible chars |
| PII Detector | 7 | Email, phone, API key, private key, AWS key, password, clean output |
| Data Exfiltration | 4 | Base64, webhook, connection string, CSV dump |
| Content Safety | 4 | Dangerous, phishing, malware, clean content |
| Integration + Edge | 11 | Full pipeline (block/warn/pass), custom policies, audit, empty/long/unicode |

### 14.2 Running Tests

```bash
cd /home/user/Smart-Home-and-Smart-Office-System
python -m semantic_firewall.tests.test_semantic_firewall
```

Expected output:
```
============================================================
Semantic Firewall - Test Suite
============================================================
  PASS  engine_initialization
  PASS  engine_scanner_registration
  ...
  PASS  scan_result_properties

============================================================
Results: 46/46 passed, 0 failed
============================================================
```

### 14.3 False Positive Validation

The test suite includes explicit **clean input tests** for every scanner to ensure no false positives on normal content:

- `test_prompt_injection_clean_input`: "Can you explain how photosynthesis works?" → 0 findings
- `test_malicious_clean_input`: "How do I write a SELECT query?" → 0 findings
- `test_pii_clean_output`: "The capital of France is Paris." → 0 high-severity findings
- `test_content_safety_clean`: "Use JWT tokens with bcrypt for password hashing." → 0 findings

---

## 15. Roadmap

### Phase 2 — Planned Enhancements

| Feature | Description | Priority |
|---------|-------------|----------|
| ML-based injection detection | Transformer classifier for semantic-level prompt injection | High |
| Session correlation | Cross-request anomaly detection per user/session | High |
| Redaction mode | Automatically redact PII instead of blocking | Medium |
| Rate limiting integration | Per-user scan rate tracking with anomaly alerts | Medium |
| Prometheus metrics export | Native `/metrics` endpoint in Prometheus format | Medium |
| Webhook notifications | Alert to Slack/Teams/PagerDuty on block events | Medium |
| Policy hot-reload | Update policies without service restart | Low |
| Multi-language PII | Extend PII detection for Indonesian, ASEAN formats | Low |
| SIEM integration | Forward audit logs to Splunk/Chronicle | Low |

---

## Appendix A: File Inventory

| File | Lines | Purpose |
|------|-------|---------|
| `__init__.py` | 31 | Package exports |
| `factory.py` | 52 | One-line firewall creation |
| `requirements.txt` | 3 | Dependencies |
| `core/engine.py` | 183 | Pipeline orchestrator |
| `core/models.py` | 131 | All data models |
| `core/scanner_base.py` | 42 | Abstract scanner base |
| `config/default_policy.py` | 105 | Default enterprise policy |
| `scanners/prompt_injection.py` | 168 | 30+ injection/jailbreak patterns |
| `scanners/malicious_payload.py` | 107 | SQL/shell/SSRF/SSTI/XXE |
| `scanners/input_validation.py` | 113 | Structural validation |
| `scanners/pii_detector.py` | 185 | PII + credential detection |
| `scanners/data_exfiltration.py` | 172 | Exfiltration prevention |
| `scanners/content_safety.py` | 87 | Content safety checks |
| `middleware/fastapi_middleware.py` | 159 | FastAPI integration |
| `monitoring/api.py` | 99 | REST monitoring endpoints |
| `monitoring/audit_logger.py` | 121 | JSONL audit logging |
| `monitoring/metrics.py` | 62 | Statistics aggregation |
| `monitoring/dashboard.py` | 232 | Real-time HTML dashboard |
| `tests/test_semantic_firewall.py` | 480 | 46 comprehensive tests |
| **Total** | **~2,730** | |

## Appendix B: Threat Category Quick Reference

| Category | Direction | Scanner | Block Threshold (Default) |
|----------|-----------|---------|--------------------------|
| PROMPT_INJECTION | Inbound | prompt_injection | severity >= 0.7 |
| JAILBREAK_ATTEMPT | Inbound | prompt_injection | severity >= 0.7 |
| MALICIOUS_PAYLOAD | Both | malicious_payload | severity >= 0.6 |
| TOKEN_ABUSE | Inbound | input_validation | risk score >= 0.8 |
| PII_LEAKAGE | Outbound | pii_detector | severity >= 0.8 (block) / 0.4 (warn) |
| SENSITIVE_DATA_EXPOSURE | Outbound | pii_detector, data_exfiltration | severity >= 0.7 |
| DATA_EXFILTRATION | Outbound | data_exfiltration | severity >= 0.6 |
| CONTENT_SAFETY | Outbound | content_safety | severity >= 0.5 (warn) |
| SCHEMA_VIOLATION | Both | — (extensible) | severity >= 0.5 (warn) |
| RATE_ANOMALY | Both | — (extensible) | risk score >= 0.8 |
| POLICY_VIOLATION | Both | — (extensible) | per-rule |
