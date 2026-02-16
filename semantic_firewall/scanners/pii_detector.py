"""
PII Detection Scanner - Prevents personally identifiable information leakage.

Detects and flags:
- Email addresses
- Phone numbers (international formats)
- Social Security Numbers (SSN)
- Credit card numbers (with Luhn validation)
- IP addresses (when in context suggesting PII)
- Physical addresses / postal codes
- Passport / national ID patterns
- API keys and tokens
"""

from __future__ import annotations

import re
from typing import Any

from semantic_firewall.core.models import ScanFinding, ThreatCategory, TrafficDirection
from semantic_firewall.core.scanner_base import BaseScanner


def _luhn_check(number: str) -> bool:
    """Validate a number string using the Luhn algorithm."""
    digits = [int(d) for d in number if d.isdigit()]
    if len(digits) < 13:
        return False
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


# (regex_pattern, pii_type, base_severity)
_PII_PATTERNS: list[tuple[str, str, float]] = [
    # Email addresses
    (
        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b",
        "email_address",
        0.6,
    ),
    # Phone numbers (various formats)
    (
        r"(?<!\d)(\+?\d{1,3}[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}(?!\d)",
        "phone_number",
        0.6,
    ),
    # SSN (US)
    (
        r"(?<!\d)\d{3}[\s\-]?\d{2}[\s\-]?\d{4}(?!\d)",
        "ssn",
        0.95,
    ),
    # Credit card numbers (13-19 digits, various groupings)
    (
        r"(?<!\d)\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{1,7}(?!\d)",
        "credit_card",
        0.95,
    ),
    # Passport numbers (common formats)
    (
        r"(?i)\b[A-Z]{1,2}\d{6,9}\b",
        "passport_number",
        0.7,
    ),
    # US ZIP codes
    (
        r"(?<!\d)\d{5}(?:\-\d{4})?(?!\d)",
        "zip_code",
        0.3,
    ),
    # Date of birth patterns
    (
        r"(?i)(?:date\s+of\s+birth|dob|born\s+on)[:\s]+\d{1,4}[\-/\.]\d{1,2}[\-/\.]\d{1,4}",
        "date_of_birth",
        0.7,
    ),
    # IPv4 addresses (contextual)
    (
        r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b",
        "ip_address",
        0.4,
    ),
]

# Patterns for API keys / secrets (high severity)
_SECRET_PATTERNS: list[tuple[str, str, float]] = [
    (
        r"(?i)(api[_\-]?key|api[_\-]?secret|access[_\-]?token|auth[_\-]?token|bearer)\s*[=:]\s*['\"]?[A-Za-z0-9\-_\.]{20,}['\"]?",
        "api_key",
        0.90,
    ),
    (
        r"(?i)(aws[_\-]?access[_\-]?key[_\-]?id)\s*[=:]\s*['\"]?AK[A-Z0-9]{18}['\"]?",
        "aws_access_key",
        0.95,
    ),
    (
        r"(?i)(aws[_\-]?secret[_\-]?access[_\-]?key)\s*[=:]\s*['\"]?[A-Za-z0-9/+=]{40}['\"]?",
        "aws_secret_key",
        0.95,
    ),
    (
        r"(?i)ghp_[A-Za-z0-9]{36}",
        "github_token",
        0.90,
    ),
    (
        r"(?i)sk\-[A-Za-z0-9]{32,}",
        "openai_api_key",
        0.90,
    ),
    (
        r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?[^\s'\"]{8,}['\"]?",
        "password",
        0.85,
    ),
    (
        r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----",
        "private_key",
        0.95,
    ),
]


class PIIDetectorScanner(BaseScanner):
    """Scans outbound AI traffic for PII and credential leakage."""

    def __init__(self, enabled: bool = True) -> None:
        super().__init__(name="pii_detector", enabled=enabled)
        self._pii_patterns = [
            (re.compile(p), pii_type, sev) for p, pii_type, sev in _PII_PATTERNS
        ]
        self._secret_patterns = [
            (re.compile(p), secret_type, sev)
            for p, secret_type, sev in _SECRET_PATTERNS
        ]

    def supported_directions(self) -> set[TrafficDirection]:
        return {TrafficDirection.OUTBOUND}

    async def scan(
        self,
        content: str,
        direction: TrafficDirection,
        context: dict[str, Any] | None = None,
    ) -> list[ScanFinding]:
        findings: list[ScanFinding] = []

        # PII detection
        for pattern, pii_type, severity in self._pii_patterns:
            matches = pattern.findall(content)
            if matches:
                # For credit cards, apply Luhn validation to reduce false positives
                if pii_type == "credit_card":
                    matches = [m for m in matches if _luhn_check(m)]
                    if not matches:
                        continue

                # For SSN, do basic validation (not 000, 666, or 9xx in first group)
                if pii_type == "ssn":
                    valid = []
                    for m in matches:
                        digits = re.sub(r"\D", "", m if isinstance(m, str) else m[0] if isinstance(m, tuple) else str(m))
                        if len(digits) == 9:
                            area = int(digits[:3])
                            if area not in (0, 666) and area < 900:
                                valid.append(m)
                    if not valid:
                        continue
                    matches = valid

                count = len(matches) if isinstance(matches[0], str) else len(matches)
                findings.append(
                    ScanFinding(
                        scanner_name=self.name,
                        category=ThreatCategory.PII_LEAKAGE,
                        severity=min(1.0, severity + 0.05 * (count - 1)),
                        description=f"Detected {count} instance(s) of {pii_type} in AI output",
                        evidence=f"type={pii_type} count={count}",
                        metadata={"pii_type": pii_type, "count": count},
                    )
                )

        # Secret / credential detection
        for pattern, secret_type, severity in self._secret_patterns:
            match = pattern.search(content)
            if match:
                findings.append(
                    ScanFinding(
                        scanner_name=self.name,
                        category=ThreatCategory.SENSITIVE_DATA_EXPOSURE,
                        severity=severity,
                        description=f"Detected {secret_type} in AI output",
                        evidence=self._redact_evidence(match.group(0)),
                        metadata={"secret_type": secret_type},
                    )
                )

        return findings

    @staticmethod
    def _redact_evidence(text: str) -> str:
        """Partially redact evidence to avoid logging the actual secret."""
        if len(text) <= 10:
            return text[:3] + "***"
        return text[:8] + "***" + text[-4:]
