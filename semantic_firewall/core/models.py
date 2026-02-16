"""Core data models for the Semantic Firewall."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TrafficDirection(str, Enum):
    """Direction of traffic through the firewall."""

    INBOUND = "inbound"  # Data flowing INTO the AI system
    OUTBOUND = "outbound"  # Data flowing OUT of the AI system


class ScanVerdict(str, Enum):
    """Result verdict from a scanner."""

    PASS = "pass"
    WARN = "warn"
    BLOCK = "block"


class ThreatCategory(str, Enum):
    """Categories of threats detected by scanners."""

    PROMPT_INJECTION = "prompt_injection"
    JAILBREAK_ATTEMPT = "jailbreak_attempt"
    PII_LEAKAGE = "pii_leakage"
    DATA_EXFILTRATION = "data_exfiltration"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    MALICIOUS_PAYLOAD = "malicious_payload"
    POLICY_VIOLATION = "policy_violation"
    CONTENT_SAFETY = "content_safety"
    SCHEMA_VIOLATION = "schema_violation"
    RATE_ANOMALY = "rate_anomaly"
    TOKEN_ABUSE = "token_abuse"


class ScanFinding(BaseModel):
    """A single finding from a scanner."""

    scanner_name: str
    category: ThreatCategory
    severity: float = Field(ge=0.0, le=1.0, description="Severity score 0-1")
    description: str
    evidence: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScanResult(BaseModel):
    """Result of running the full scanner pipeline on a piece of traffic."""

    scan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    direction: TrafficDirection
    verdict: ScanVerdict
    findings: list[ScanFinding] = Field(default_factory=list)
    aggregate_risk_score: float = Field(
        ge=0.0, le=1.0, description="Combined risk score 0-1"
    )
    content_hash: str | None = None
    latency_ms: float = 0.0
    policy_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def blocked(self) -> bool:
        return self.verdict == ScanVerdict.BLOCK

    @property
    def has_warnings(self) -> bool:
        return self.verdict == ScanVerdict.WARN or any(
            f.severity >= 0.5 for f in self.findings
        )


class PolicyAction(str, Enum):
    """Action to take when a policy rule matches."""

    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"
    REDACT = "redact"
    LOG = "log"


class PolicyRule(BaseModel):
    """A single rule within a firewall policy."""

    rule_id: str
    name: str
    description: str = ""
    enabled: bool = True
    direction: TrafficDirection | None = None  # None = both directions
    categories: list[ThreatCategory] = Field(default_factory=list)
    severity_threshold: float = Field(
        ge=0.0, le=1.0, default=0.7,
        description="Minimum severity to trigger this rule",
    )
    action: PolicyAction = PolicyAction.BLOCK
    priority: int = Field(default=100, description="Lower number = higher priority")


class FirewallPolicy(BaseModel):
    """A complete firewall policy with ordered rules."""

    policy_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    version: str = "1.0.0"
    enabled: bool = True
    rules: list[PolicyRule] = Field(default_factory=list)
    default_action: PolicyAction = PolicyAction.WARN
    block_threshold: float = Field(
        ge=0.0, le=1.0, default=0.8,
        description="Risk score threshold for automatic blocking",
    )
    warn_threshold: float = Field(
        ge=0.0, le=1.0, default=0.4,
        description="Risk score threshold for warnings",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class AuditLogEntry(BaseModel):
    """An entry in the firewall audit log."""

    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    scan_result: ScanResult
    source_ip: str | None = None
    destination: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    endpoint: str | None = None
    action_taken: PolicyAction
    content_preview: str | None = None
    request_size_bytes: int = 0
