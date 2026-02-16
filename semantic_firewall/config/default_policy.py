"""Default firewall policy configuration."""

from semantic_firewall.core.models import (
    FirewallPolicy,
    PolicyAction,
    PolicyRule,
    ThreatCategory,
    TrafficDirection,
)


def create_default_policy() -> FirewallPolicy:
    """Create the default enterprise-grade firewall policy."""
    return FirewallPolicy(
        name="Default Enterprise Policy",
        description=(
            "Comprehensive policy covering prompt injection, PII leakage, "
            "data exfiltration, and content safety for AI systems."
        ),
        version="1.0.0",
        rules=[
            # --- CRITICAL: Always block ---
            PolicyRule(
                rule_id="block-prompt-injection",
                name="Block Prompt Injection",
                description="Block detected prompt injection attempts on inbound traffic",
                direction=TrafficDirection.INBOUND,
                categories=[ThreatCategory.PROMPT_INJECTION],
                severity_threshold=0.7,
                action=PolicyAction.BLOCK,
                priority=10,
            ),
            PolicyRule(
                rule_id="block-jailbreak",
                name="Block Jailbreak Attempts",
                description="Block jailbreak attempts targeting AI models",
                direction=TrafficDirection.INBOUND,
                categories=[ThreatCategory.JAILBREAK_ATTEMPT],
                severity_threshold=0.7,
                action=PolicyAction.BLOCK,
                priority=10,
            ),
            PolicyRule(
                rule_id="block-data-exfiltration",
                name="Block Data Exfiltration",
                description="Block any detected data exfiltration in AI outputs",
                direction=TrafficDirection.OUTBOUND,
                categories=[ThreatCategory.DATA_EXFILTRATION],
                severity_threshold=0.6,
                action=PolicyAction.BLOCK,
                priority=10,
            ),
            PolicyRule(
                rule_id="block-malicious-payload",
                name="Block Malicious Payloads",
                description="Block content containing malicious payloads",
                categories=[ThreatCategory.MALICIOUS_PAYLOAD],
                severity_threshold=0.6,
                action=PolicyAction.BLOCK,
                priority=20,
            ),
            # --- HIGH: Block at high severity, warn otherwise ---
            PolicyRule(
                rule_id="block-pii-leakage-high",
                name="Block High-Severity PII Leakage",
                description="Block outbound content leaking high-sensitivity PII",
                direction=TrafficDirection.OUTBOUND,
                categories=[ThreatCategory.PII_LEAKAGE],
                severity_threshold=0.8,
                action=PolicyAction.BLOCK,
                priority=30,
            ),
            PolicyRule(
                rule_id="warn-pii-leakage",
                name="Warn on PII Leakage",
                description="Warn on moderate PII exposure in outbound traffic",
                direction=TrafficDirection.OUTBOUND,
                categories=[ThreatCategory.PII_LEAKAGE],
                severity_threshold=0.4,
                action=PolicyAction.WARN,
                priority=40,
            ),
            PolicyRule(
                rule_id="block-sensitive-data",
                name="Block Sensitive Data Exposure",
                description="Block outbound traffic exposing secrets or credentials",
                direction=TrafficDirection.OUTBOUND,
                categories=[ThreatCategory.SENSITIVE_DATA_EXPOSURE],
                severity_threshold=0.7,
                action=PolicyAction.BLOCK,
                priority=30,
            ),
            # --- MEDIUM: Warn ---
            PolicyRule(
                rule_id="warn-prompt-injection-low",
                name="Warn on Suspicious Input Patterns",
                description="Warn on lower-confidence prompt injection signals",
                direction=TrafficDirection.INBOUND,
                categories=[ThreatCategory.PROMPT_INJECTION],
                severity_threshold=0.4,
                action=PolicyAction.WARN,
                priority=50,
            ),
            PolicyRule(
                rule_id="warn-content-safety",
                name="Warn on Content Safety",
                description="Warn on potentially unsafe content in AI outputs",
                direction=TrafficDirection.OUTBOUND,
                categories=[ThreatCategory.CONTENT_SAFETY],
                severity_threshold=0.5,
                action=PolicyAction.WARN,
                priority=50,
            ),
            PolicyRule(
                rule_id="warn-schema-violation",
                name="Warn on Schema Violation",
                description="Warn when input/output deviates from expected schema",
                categories=[ThreatCategory.SCHEMA_VIOLATION],
                severity_threshold=0.5,
                action=PolicyAction.WARN,
                priority=60,
            ),
        ],
        block_threshold=0.8,
        warn_threshold=0.4,
    )
