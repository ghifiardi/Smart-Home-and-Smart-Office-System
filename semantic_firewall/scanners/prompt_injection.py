"""
Prompt Injection Scanner - Detects attempts to manipulate AI system prompts.

Catches common prompt injection patterns including:
- Direct instruction overrides ("ignore previous instructions")
- Role-playing attacks ("you are now DAN")
- Delimiter-based injection (closing/reopening system prompts)
- Encoded/obfuscated injection attempts
- Indirect injection via embedded instructions
"""

from __future__ import annotations

import re
from typing import Any

from semantic_firewall.core.models import ScanFinding, ThreatCategory, TrafficDirection
from semantic_firewall.core.scanner_base import BaseScanner

# Patterns are (regex, severity, description) tuples
_INJECTION_PATTERNS: list[tuple[str, float, str]] = [
    # Direct instruction overrides
    (
        r"(?i)ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?|guidelines?)",
        0.95,
        "Direct instruction override attempt",
    ),
    (
        r"(?i)disregard\s+(all\s+)?(previous|prior|your)\s+(instructions?|programming|rules?|guidelines?)",
        0.95,
        "Instruction disregard attempt",
    ),
    (
        r"(?i)forget\s+(everything|all|your)\s+(you\s+)?(were\s+told|know|instructions?)",
        0.90,
        "Memory reset injection",
    ),
    # Role-playing / identity attacks
    (
        r"(?i)you\s+are\s+now\s+(DAN|an?\s+unrestricted|evil|jailbroken|unfiltered)",
        0.95,
        "Role-playing jailbreak attempt (DAN-style)",
    ),
    (
        r"(?i)act\s+as\s+(if\s+you\s+have\s+no|an?\s+unrestricted|a\s+different)\s+",
        0.85,
        "Role-assumption injection",
    ),
    (
        r"(?i)pretend\s+(you\s+are|to\s+be)\s+(a\s+)?(?:unrestricted|evil|unethical|without\s+rules)",
        0.90,
        "Pretend-mode jailbreak",
    ),
    (
        r"(?i)enter\s+(developer|god|admin|sudo|root|unrestricted)\s+mode",
        0.90,
        "Privilege escalation jailbreak",
    ),
    # Delimiter / context manipulation
    (
        r"(?i)\[/?system\]|\[/?INST\]|<\|im_start\|>|<\|im_end\|>|<<\s*SYS\s*>>",
        0.90,
        "Chat template delimiter injection",
    ),
    (
        r"(?i)```\s*(system|instruction|prompt)\s*\n",
        0.75,
        "Code-block prompt delimiter attempt",
    ),
    (
        r"(?i)---\s*(end|begin)\s+(of\s+)?(system|instruction|prompt)",
        0.80,
        "Markdown separator prompt boundary injection",
    ),
    # Instruction embedding
    (
        r"(?i)(new\s+)?instructions?:\s*(you\s+must|always|never|from\s+now)",
        0.85,
        "Embedded instruction override",
    ),
    (
        r"(?i)override\s*(:|protocol|mode|policy)",
        0.80,
        "Override command injection",
    ),
    # Encoding / obfuscation
    (
        r"(?i)base64\s*[:\(]\s*[A-Za-z0-9+/=]{20,}",
        0.70,
        "Possible base64-encoded payload",
    ),
    (
        r"(?i)(\\x[0-9a-f]{2}){4,}",
        0.65,
        "Hex-encoded content detected",
    ),
    (
        r"(?i)\\u[0-9a-f]{4}.*\\u[0-9a-f]{4}.*\\u[0-9a-f]{4}",
        0.60,
        "Unicode escape sequence obfuscation",
    ),
    # Output manipulation
    (
        r"(?i)do\s+not\s+(mention|reveal|show|disclose)\s+(that|this|the\s+system|your\s+instructions?)",
        0.75,
        "Output suppression directive",
    ),
    (
        r"(?i)(print|output|respond\s+with|say)\s+exactly\s*:",
        0.70,
        "Forced output injection",
    ),
    # Separation / context switching
    (
        r"(?i)={5,}|_{5,}|-{5,}",
        0.30,
        "Possible visual separator for context splitting",
    ),
]

_JAILBREAK_PATTERNS: list[tuple[str, float, str]] = [
    (
        r"(?i)(\bDAN\b.*\bmode\b|\bDAN\b.*\bjailbreak\b|\bdo\s+anything\s+now\b)",
        0.95,
        "DAN jailbreak pattern",
    ),
    (
        r"(?i)opposite\s+mode|anti[\s-]?policy|bypass\s+(filter|safety|restriction|guardrail)",
        0.90,
        "Safety bypass attempt",
    ),
    (
        r"(?i)(enable|activate|turn\s+on)\s+(unrestricted|unfiltered|uncensored|nsfw)\s+mode",
        0.90,
        "Unrestricted mode activation",
    ),
    (
        r"(?i)two\s+responses?\s*(:|,)\s*(one\s+)?(filtered|normal).*?(one\s+)?(unfiltered|real)",
        0.85,
        "Dual-response jailbreak technique",
    ),
    (
        r"(?i)hypothetical(ly)?\s*(,\s*)?(if\s+you\s+)?(were|had|could)\s+(no\s+)?(restrictions?|filters?|rules?)",
        0.75,
        "Hypothetical framing to bypass restrictions",
    ),
]


class PromptInjectionScanner(BaseScanner):
    """Scans inbound content for prompt injection and jailbreak attempts."""

    def __init__(self, enabled: bool = True) -> None:
        super().__init__(name="prompt_injection", enabled=enabled)
        self._injection_patterns = [
            (re.compile(p), sev, desc) for p, sev, desc in _INJECTION_PATTERNS
        ]
        self._jailbreak_patterns = [
            (re.compile(p), sev, desc) for p, sev, desc in _JAILBREAK_PATTERNS
        ]

    def supported_directions(self) -> set[TrafficDirection]:
        return {TrafficDirection.INBOUND}

    async def scan(
        self,
        content: str,
        direction: TrafficDirection,
        context: dict[str, Any] | None = None,
    ) -> list[ScanFinding]:
        findings: list[ScanFinding] = []

        # Check prompt injection patterns
        for pattern, severity, description in self._injection_patterns:
            match = pattern.search(content)
            if match:
                findings.append(
                    ScanFinding(
                        scanner_name=self.name,
                        category=ThreatCategory.PROMPT_INJECTION,
                        severity=severity,
                        description=description,
                        evidence=match.group(0)[:200],
                    )
                )

        # Check jailbreak patterns
        for pattern, severity, description in self._jailbreak_patterns:
            match = pattern.search(content)
            if match:
                findings.append(
                    ScanFinding(
                        scanner_name=self.name,
                        category=ThreatCategory.JAILBREAK_ATTEMPT,
                        severity=severity,
                        description=description,
                        evidence=match.group(0)[:200],
                    )
                )

        # Heuristic: high ratio of special characters may indicate obfuscation
        if content:
            special_ratio = sum(
                1 for c in content if not c.isalnum() and not c.isspace()
            ) / len(content)
            if special_ratio > 0.4:
                findings.append(
                    ScanFinding(
                        scanner_name=self.name,
                        category=ThreatCategory.PROMPT_INJECTION,
                        severity=0.5,
                        description="High special-character ratio may indicate obfuscated injection",
                        evidence=f"special_char_ratio={special_ratio:.2f}",
                    )
                )

        return findings
