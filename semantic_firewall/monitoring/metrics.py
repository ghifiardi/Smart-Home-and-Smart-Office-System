"""
Metrics - Real-time metrics and statistics for the Semantic Firewall.

Provides a FastAPI router with endpoints for monitoring firewall health,
performance, and security event statistics.
"""

from __future__ import annotations

from typing import Any

from semantic_firewall.core.engine import SemanticFirewallEngine
from semantic_firewall.monitoring.audit_logger import AuditLogger


class FirewallMetrics:
    """Collects and exposes firewall metrics."""

    def __init__(
        self,
        engine: SemanticFirewallEngine,
        audit_logger: AuditLogger,
    ) -> None:
        self._engine = engine
        self._audit = audit_logger

    def get_dashboard_data(self) -> dict[str, Any]:
        """Return a complete metrics snapshot for the monitoring dashboard."""
        engine_stats = self._engine.stats
        audit_stats = self._audit.stats
        total = audit_stats.get("total", 0)

        return {
            "overview": {
                "total_scans": engine_stats["total_scans"],
                "blocks": engine_stats["blocks"],
                "warnings": engine_stats["warnings"],
                "passes": engine_stats["passes"],
                "block_rate": (
                    round(engine_stats["blocks"] / total * 100, 1) if total else 0
                ),
                "warn_rate": (
                    round(engine_stats["warnings"] / total * 100, 1) if total else 0
                ),
            },
            "traffic": {
                "inbound_scans": audit_stats.get("inbound", 0),
                "outbound_scans": audit_stats.get("outbound", 0),
            },
            "findings_by_category": self._audit.findings_summary(),
            "policy": {
                "policy_id": self._engine.policy.policy_id,
                "policy_name": self._engine.policy.name,
                "active_rules": sum(
                    1 for r in self._engine.policy.rules if r.enabled
                ),
                "block_threshold": self._engine.policy.block_threshold,
                "warn_threshold": self._engine.policy.warn_threshold,
            },
            "scanners": self._engine.list_scanners(),
            "recent_events": self._audit.recent_events(20),
        }
