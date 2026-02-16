"""
Factory - Convenience functions to create a fully-configured Semantic Firewall.
"""

from __future__ import annotations

from semantic_firewall.core.engine import SemanticFirewallEngine
from semantic_firewall.core.models import FirewallPolicy
from semantic_firewall.monitoring.audit_logger import AuditLogger
from semantic_firewall.scanners.content_safety import ContentSafetyScanner
from semantic_firewall.scanners.data_exfiltration import DataExfiltrationScanner
from semantic_firewall.scanners.input_validation import InputValidationScanner
from semantic_firewall.scanners.malicious_payload import MaliciousPayloadScanner
from semantic_firewall.scanners.pii_detector import PIIDetectorScanner
from semantic_firewall.scanners.prompt_injection import PromptInjectionScanner


def create_firewall(
    policy: FirewallPolicy | None = None,
    log_dir: str = "logs/semantic_firewall",
    enable_audit: bool = True,
) -> tuple[SemanticFirewallEngine, AuditLogger]:
    """
    Create a fully-configured Semantic Firewall with all scanners registered.

    Returns:
        A tuple of (engine, audit_logger) ready to use.

    Example:
        engine, audit_logger = create_firewall()

        # Use standalone:
        result = await engine.scan("user input here", TrafficDirection.INBOUND)

        # Or as FastAPI middleware:
        from semantic_firewall.middleware.fastapi_middleware import SemanticFirewallMiddleware
        app.add_middleware(SemanticFirewallMiddleware, engine=engine)

        # Add monitoring endpoints:
        from semantic_firewall.monitoring.api import create_monitoring_router
        app.include_router(create_monitoring_router(engine, audit_logger))
    """
    audit_logger = AuditLogger(log_dir=log_dir, log_to_file=enable_audit)

    engine = SemanticFirewallEngine(
        policy=policy,
        audit_callback=audit_logger.log,
    )

    # Register all scanners
    engine.register_scanner(PromptInjectionScanner())
    engine.register_scanner(MaliciousPayloadScanner())
    engine.register_scanner(InputValidationScanner())
    engine.register_scanner(PIIDetectorScanner())
    engine.register_scanner(DataExfiltrationScanner())
    engine.register_scanner(ContentSafetyScanner())

    return engine, audit_logger
