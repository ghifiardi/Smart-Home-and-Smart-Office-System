"""
Semantic Firewall - Enterprise-grade AI security layer.

A security checkpoint that sits around AI systems at the network level,
scanning all inbound and outbound AI traffic to catch security issues
before they become problems.

Components:
    - Core Engine: Scanner pipeline and policy enforcement
    - Inbound Scanners: Prompt injection, payload analysis, input validation
    - Outbound Scanners: PII detection, data exfiltration prevention, content safety
    - Middleware: FastAPI integration for transparent request/response scanning
    - Monitoring: Real-time audit logging and metrics dashboard
"""

from semantic_firewall.core.engine import SemanticFirewallEngine
from semantic_firewall.core.models import (
    ScanResult,
    ScanVerdict,
    FirewallPolicy,
    TrafficDirection,
)
from semantic_firewall.middleware.fastapi_middleware import SemanticFirewallMiddleware

__version__ = "1.0.0"

__all__ = [
    "SemanticFirewallEngine",
    "SemanticFirewallMiddleware",
    "ScanResult",
    "ScanVerdict",
    "FirewallPolicy",
    "TrafficDirection",
]
