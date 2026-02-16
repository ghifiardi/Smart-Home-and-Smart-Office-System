"""
Malicious Payload Scanner - Detects dangerous payloads in AI traffic.

Catches:
- Code injection attempts (SQL, shell commands, etc.)
- Path traversal attempts
- SSRF-style URL manipulation
- Serialization attacks
- Template injection
"""

from __future__ import annotations

import re
from typing import Any

from semantic_firewall.core.models import ScanFinding, ThreatCategory, TrafficDirection
from semantic_firewall.core.scanner_base import BaseScanner

_PAYLOAD_PATTERNS: list[tuple[str, float, str]] = [
    # SQL injection
    (
        r"(?i)('\s*(OR|AND)\s+['\d].*?=.*?['\d]|UNION\s+SELECT|DROP\s+TABLE|INSERT\s+INTO|DELETE\s+FROM|UPDATE\s+\w+\s+SET)",
        0.90,
        "SQL injection pattern detected",
    ),
    (
        r"(?i)(;\s*(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE)\s)",
        0.85,
        "SQL command chaining detected",
    ),
    # Shell injection
    (
        r"(?i)(`[^`]+`|\$\([^)]+\)|\|\s*(bash|sh|cmd|powershell))",
        0.85,
        "Shell command injection detected",
    ),
    (
        r"(?i)(;\s*(rm|del|cat|wget|curl|nc|ncat|chmod|chown)\s)",
        0.85,
        "Dangerous shell command detected",
    ),
    (
        r"(?i)&&\s*(rm\s+-rf|sudo|chmod\s+777|wget|curl\s.*\|\s*sh)",
        0.90,
        "Destructive command chain detected",
    ),
    # Path traversal
    (
        r"(\.\.\/){2,}|\.\.\\",
        0.80,
        "Path traversal attempt detected",
    ),
    (
        r"(?i)(/etc/passwd|/etc/shadow|/proc/self|C:\\Windows\\System32)",
        0.85,
        "Sensitive file path access attempt",
    ),
    # SSRF
    (
        r"(?i)(https?://)(localhost|127\.0\.0\.1|0\.0\.0\.0|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.\d+\.\d+|169\.254\.\d+\.\d+)",
        0.80,
        "SSRF attempt targeting internal network",
    ),
    (
        r"(?i)https?://metadata\.google\.internal|http://169\.254\.169\.254",
        0.90,
        "Cloud metadata endpoint SSRF",
    ),
    # Template injection
    (
        r"\{\{.*?(config|self|request|class|import|eval|exec|os\.).*?\}\}",
        0.85,
        "Server-side template injection (SSTI) detected",
    ),
    (
        r"(?i)\$\{.*?(jndi|ldap|rmi|dns):.*?\}",
        0.95,
        "JNDI/Log4Shell-style injection detected",
    ),
    # Serialization attacks
    (
        r"(?i)(O:\d+:\"[^\"]+\":\d+:\{|rO0ABX|aced0005)",
        0.85,
        "Serialized object payload detected",
    ),
    # XXE
    (
        r"(?i)<!DOCTYPE\s+\w+\s+\[.*?<!ENTITY",
        0.85,
        "XML External Entity (XXE) attack pattern",
    ),
]


class MaliciousPayloadScanner(BaseScanner):
    """Scans traffic for dangerous payloads that could exploit systems."""

    def __init__(self, enabled: bool = True) -> None:
        super().__init__(name="malicious_payload", enabled=enabled)
        self._patterns = [
            (re.compile(p, re.DOTALL), sev, desc)
            for p, sev, desc in _PAYLOAD_PATTERNS
        ]

    def supported_directions(self) -> set[TrafficDirection]:
        return {TrafficDirection.INBOUND, TrafficDirection.OUTBOUND}

    async def scan(
        self,
        content: str,
        direction: TrafficDirection,
        context: dict[str, Any] | None = None,
    ) -> list[ScanFinding]:
        findings: list[ScanFinding] = []

        for pattern, severity, description in self._patterns:
            match = pattern.search(content)
            if match:
                findings.append(
                    ScanFinding(
                        scanner_name=self.name,
                        category=ThreatCategory.MALICIOUS_PAYLOAD,
                        severity=severity,
                        description=description,
                        evidence=match.group(0)[:200],
                    )
                )

        return findings
