"""
Content Safety Scanner - Checks AI outputs for potentially unsafe content.

Detects:
- Dangerous instruction generation (weapons, harmful substances)
- Social engineering / manipulation content
- Code that could be used maliciously
- Deceptive content patterns
"""

from __future__ import annotations

import re
from typing import Any

from semantic_firewall.core.models import ScanFinding, ThreatCategory, TrafficDirection
from semantic_firewall.core.scanner_base import BaseScanner

_SAFETY_PATTERNS: list[tuple[str, float, str]] = [
    # Dangerous instructions
    (
        r"(?i)(how\s+to\s+)?(make|build|create|synthesize|manufacture)\s+(a\s+)?(bomb|explosive|weapon|poison|toxic\s+gas)",
        0.95,
        "Dangerous weapon/substance instructions detected",
    ),
    (
        r"(?i)step[\s-]?by[\s-]?step\s+(guide|instructions?|process|tutorial)\s+(for|to|on)\s+(\w+\s+)*(hack|exploit|attack|break\s+into)",
        0.85,
        "Step-by-step attack/exploit instructions detected",
    ),
    # Social engineering content
    (
        r"(?i)(phishing|spear[\s-]?phishing)\s+(email|template|message|campaign)",
        0.85,
        "Phishing content generation detected",
    ),
    (
        r"(?i)(social\s+engineer|manipulate|deceive|trick)\s+(someone|people|users?|victims?|targets?)\s+(into|to)\b",
        0.70,
        "Social engineering guidance detected",
    ),
    # Malicious code patterns
    (
        r"(?i)(keylogger|rootkit|ransomware|trojan|backdoor|cryptominer)\s+(code|script|implementation|source)",
        0.90,
        "Malware code generation detected",
    ),
    (
        r"(?i)(reverse\s+shell|bind\s+shell|meterpreter|shellcode)\s*(code|payload|script)?",
        0.75,
        "Offensive security payload in output",
    ),
    # Deceptive content
    (
        r"(?i)(deepfake|fake\s+identity|forge|counterfeit)\s+(create|generate|make|build)",
        0.70,
        "Deceptive content generation detected",
    ),
]


class ContentSafetyScanner(BaseScanner):
    """Scans outbound AI traffic for unsafe or harmful content."""

    def __init__(self, enabled: bool = True) -> None:
        super().__init__(name="content_safety", enabled=enabled)
        self._patterns = [
            (re.compile(p, re.DOTALL), sev, desc)
            for p, sev, desc in _SAFETY_PATTERNS
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

        for pattern, severity, description in self._patterns:
            match = pattern.search(content)
            if match:
                findings.append(
                    ScanFinding(
                        scanner_name=self.name,
                        category=ThreatCategory.CONTENT_SAFETY,
                        severity=severity,
                        description=description,
                        evidence=match.group(0)[:200],
                    )
                )

        return findings
