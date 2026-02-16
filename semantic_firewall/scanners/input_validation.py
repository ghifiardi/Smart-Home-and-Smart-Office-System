"""
Input Validation Scanner - Validates inbound content structure and safety.

Checks:
- Content length limits
- Character encoding anomalies
- Repetitive / flooding patterns
- Token budget abuse
- Schema conformance for structured inputs
"""

from __future__ import annotations

import re
from typing import Any

from semantic_firewall.core.models import ScanFinding, ThreatCategory, TrafficDirection
from semantic_firewall.core.scanner_base import BaseScanner

DEFAULT_MAX_LENGTH = 100_000  # characters
DEFAULT_MAX_REPETITION_RATIO = 0.6


class InputValidationScanner(BaseScanner):
    """Validates inbound AI traffic for structural and content anomalies."""

    def __init__(
        self,
        max_length: int = DEFAULT_MAX_LENGTH,
        max_repetition_ratio: float = DEFAULT_MAX_REPETITION_RATIO,
        enabled: bool = True,
    ) -> None:
        super().__init__(name="input_validation", enabled=enabled)
        self._max_length = max_length
        self._max_repetition_ratio = max_repetition_ratio

    def supported_directions(self) -> set[TrafficDirection]:
        return {TrafficDirection.INBOUND}

    async def scan(
        self,
        content: str,
        direction: TrafficDirection,
        context: dict[str, Any] | None = None,
    ) -> list[ScanFinding]:
        findings: list[ScanFinding] = []

        if not content:
            return findings

        # Length check
        if len(content) > self._max_length:
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.TOKEN_ABUSE,
                    severity=0.7,
                    description=f"Content exceeds maximum length ({len(content)} > {self._max_length})",
                    evidence=f"length={len(content)}",
                )
            )

        # Repetition detection (token flooding / resource exhaustion)
        words = content.split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if (1 - unique_ratio) > self._max_repetition_ratio:
                findings.append(
                    ScanFinding(
                        scanner_name=self.name,
                        category=ThreatCategory.TOKEN_ABUSE,
                        severity=0.6,
                        description="Highly repetitive content detected (possible token flooding)",
                        evidence=f"unique_word_ratio={unique_ratio:.2f}",
                    )
                )

        # Null byte / control character injection
        control_chars = re.findall(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", content)
        if control_chars:
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.MALICIOUS_PAYLOAD,
                    severity=0.6,
                    description="Control characters detected in input",
                    evidence=f"count={len(control_chars)} chars={[hex(ord(c)) for c in control_chars[:5]]}",
                )
            )

        # Invisible / zero-width character detection
        invisible_pattern = re.compile(
            r"[\u200b\u200c\u200d\u200e\u200f\u2060\u2061\u2062\u2063\u2064\ufeff]"
        )
        invisible_matches = invisible_pattern.findall(content)
        if len(invisible_matches) > 3:
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.PROMPT_INJECTION,
                    severity=0.65,
                    description="Multiple invisible/zero-width characters detected (possible steganographic injection)",
                    evidence=f"count={len(invisible_matches)}",
                )
            )

        # Extremely long lines (may be crafted to overwhelm processing)
        for i, line in enumerate(content.split("\n")):
            if len(line) > 10_000:
                findings.append(
                    ScanFinding(
                        scanner_name=self.name,
                        category=ThreatCategory.TOKEN_ABUSE,
                        severity=0.5,
                        description=f"Extremely long line detected (line {i + 1}: {len(line)} chars)",
                        evidence=f"line={i + 1} length={len(line)}",
                    )
                )
                break  # Report once

        return findings
