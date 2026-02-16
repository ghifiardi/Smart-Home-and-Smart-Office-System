"""
Monitoring API - FastAPI router exposing firewall metrics and management endpoints.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse

from semantic_firewall.core.engine import SemanticFirewallEngine
from semantic_firewall.core.models import FirewallPolicy, ScanVerdict, TrafficDirection
from semantic_firewall.monitoring.audit_logger import AuditLogger
from semantic_firewall.monitoring.metrics import FirewallMetrics


def create_monitoring_router(
    engine: SemanticFirewallEngine,
    audit_logger: AuditLogger,
) -> APIRouter:
    """Create a FastAPI router with firewall monitoring endpoints."""

    router = APIRouter(prefix="/firewall", tags=["Semantic Firewall"])
    metrics = FirewallMetrics(engine=engine, audit_logger=audit_logger)

    @router.get("/health")
    async def health() -> dict[str, Any]:
        return {
            "status": "healthy",
            "scanners_registered": len(engine.list_scanners()),
            "policy_active": engine.policy.enabled,
            "policy_name": engine.policy.name,
        }

    @router.get("/metrics")
    async def get_metrics() -> dict[str, Any]:
        return metrics.get_dashboard_data()

    @router.get("/stats")
    async def get_stats() -> dict[str, Any]:
        return engine.stats

    @router.get("/scanners")
    async def list_scanners() -> dict[str, Any]:
        return {"scanners": engine.list_scanners()}

    @router.get("/policy")
    async def get_policy() -> dict[str, Any]:
        p = engine.policy
        return {
            "policy_id": p.policy_id,
            "name": p.name,
            "description": p.description,
            "version": p.version,
            "enabled": p.enabled,
            "rules": [
                {
                    "rule_id": r.rule_id,
                    "name": r.name,
                    "enabled": r.enabled,
                    "direction": r.direction.value if r.direction else "both",
                    "action": r.action.value,
                    "severity_threshold": r.severity_threshold,
                    "priority": r.priority,
                }
                for r in p.rules
            ],
            "block_threshold": p.block_threshold,
            "warn_threshold": p.warn_threshold,
        }

    @router.get("/audit/recent")
    async def recent_audit(count: int = 50) -> dict[str, Any]:
        return {"events": audit_logger.recent_events(min(count, 200))}

    @router.get("/audit/findings")
    async def findings_summary() -> dict[str, Any]:
        return {"findings_by_category": audit_logger.findings_summary()}

    @router.post("/scan/test")
    async def test_scan(
        content: str,
        direction: TrafficDirection = TrafficDirection.INBOUND,
    ) -> dict[str, Any]:
        """Run a test scan without blocking — useful for policy tuning."""
        result = await engine.scan(
            content=content,
            direction=direction,
            context={"endpoint": "/firewall/scan/test", "test_mode": True},
        )
        return {
            "scan_id": result.scan_id,
            "direction": result.direction.value,
            "verdict": result.verdict.value,
            "risk_score": result.aggregate_risk_score,
            "findings": [
                {
                    "scanner": f.scanner_name,
                    "category": f.category.value,
                    "severity": f.severity,
                    "description": f.description,
                    "evidence": f.evidence,
                }
                for f in result.findings
            ],
            "latency_ms": result.latency_ms,
        }

    @router.get("/dashboard", response_class=HTMLResponse)
    async def dashboard() -> str:
        """Serve the monitoring dashboard."""
        from semantic_firewall.monitoring.dashboard import render_dashboard

        return render_dashboard()

    return router
