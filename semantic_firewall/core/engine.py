"""Core Semantic Firewall engine - orchestrates the scanner pipeline."""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
from typing import Any

from semantic_firewall.core.models import (
    AuditLogEntry,
    FirewallPolicy,
    PolicyAction,
    ScanFinding,
    ScanResult,
    ScanVerdict,
    TrafficDirection,
)
from semantic_firewall.core.scanner_base import BaseScanner

logger = logging.getLogger("semantic_firewall.engine")


class SemanticFirewallEngine:
    """
    The main engine that orchestrates scanning of AI traffic.

    Runs inbound and outbound content through a pipeline of scanners,
    aggregates findings, applies policy rules, and produces a verdict.
    """

    def __init__(
        self,
        policy: FirewallPolicy | None = None,
        audit_callback: Any | None = None,
    ) -> None:
        self._scanners: list[BaseScanner] = []
        self._policy = policy or self._default_policy()
        self._audit_callback = audit_callback
        self._scan_count = 0
        self._block_count = 0
        self._warn_count = 0
        logger.info(
            "SemanticFirewallEngine initialized with policy '%s'",
            self._policy.name,
        )

    @property
    def policy(self) -> FirewallPolicy:
        return self._policy

    @policy.setter
    def policy(self, new_policy: FirewallPolicy) -> None:
        self._policy = new_policy
        logger.info("Policy updated to '%s'", new_policy.name)

    @property
    def stats(self) -> dict[str, int]:
        return {
            "total_scans": self._scan_count,
            "blocks": self._block_count,
            "warnings": self._warn_count,
            "passes": self._scan_count - self._block_count - self._warn_count,
        }

    def register_scanner(self, scanner: BaseScanner) -> None:
        """Register a scanner in the pipeline."""
        self._scanners.append(scanner)
        logger.info("Registered scanner: %s", scanner.name)

    def remove_scanner(self, name: str) -> bool:
        """Remove a scanner by name. Returns True if found and removed."""
        before = len(self._scanners)
        self._scanners = [s for s in self._scanners if s.name != name]
        return len(self._scanners) < before

    def list_scanners(self) -> list[str]:
        """Return names of all registered scanners."""
        return [s.name for s in self._scanners]

    async def scan(
        self,
        content: str,
        direction: TrafficDirection,
        context: dict[str, Any] | None = None,
    ) -> ScanResult:
        """
        Run content through all applicable scanners and produce a verdict.

        Args:
            content: The text content to scan.
            direction: INBOUND (into AI) or OUTBOUND (from AI).
            context: Optional metadata dict.

        Returns:
            ScanResult with verdict, findings, and risk score.
        """
        start = time.monotonic()
        context = context or {}

        applicable = [s for s in self._scanners if s.applies_to(direction)]
        if not applicable:
            logger.debug("No scanners applicable for %s traffic", direction.value)
            return ScanResult(
                direction=direction,
                verdict=ScanVerdict.PASS,
                aggregate_risk_score=0.0,
                content_hash=self._hash(content),
                latency_ms=0.0,
                policy_id=self._policy.policy_id,
            )

        # Run all applicable scanners concurrently
        tasks = [scanner.scan(content, direction, context) for scanner in applicable]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_findings: list[ScanFinding] = []
        for scanner, result in zip(applicable, results):
            if isinstance(result, Exception):
                logger.error(
                    "Scanner '%s' raised an exception: %s", scanner.name, result
                )
                continue
            all_findings.extend(result)

        # Compute aggregate risk score
        risk_score = self._compute_risk_score(all_findings)

        # Apply policy to determine verdict
        verdict = self._apply_policy(all_findings, risk_score, direction)

        elapsed_ms = (time.monotonic() - start) * 1000

        scan_result = ScanResult(
            direction=direction,
            verdict=verdict,
            findings=all_findings,
            aggregate_risk_score=risk_score,
            content_hash=self._hash(content),
            latency_ms=round(elapsed_ms, 2),
            policy_id=self._policy.policy_id,
            metadata={"scanner_count": len(applicable)},
        )

        # Update stats
        self._scan_count += 1
        if verdict == ScanVerdict.BLOCK:
            self._block_count += 1
        elif verdict == ScanVerdict.WARN:
            self._warn_count += 1

        # Audit logging
        if self._audit_callback:
            entry = AuditLogEntry(
                scan_result=scan_result,
                source_ip=context.get("source_ip"),
                user_id=context.get("user_id"),
                session_id=context.get("session_id"),
                endpoint=context.get("endpoint"),
                action_taken=self._verdict_to_action(verdict),
                content_preview=content[:200] if content else None,
                request_size_bytes=len(content.encode("utf-8")) if content else 0,
            )
            try:
                await self._audit_callback(entry)
            except Exception:
                logger.exception("Audit callback failed")

        logger.info(
            "Scan %s | direction=%s verdict=%s risk=%.2f findings=%d latency=%.1fms",
            scan_result.scan_id[:8],
            direction.value,
            verdict.value,
            risk_score,
            len(all_findings),
            elapsed_ms,
        )

        return scan_result

    def _compute_risk_score(self, findings: list[ScanFinding]) -> float:
        """Aggregate risk score from all findings using weighted max + average."""
        if not findings:
            return 0.0
        severities = [f.severity for f in findings]
        max_severity = max(severities)
        avg_severity = sum(severities) / len(severities)
        # Weighted: 70% max, 30% average — a single high-severity finding
        # dominates, but multiple medium findings also raise the score.
        return min(1.0, 0.7 * max_severity + 0.3 * avg_severity)

    def _apply_policy(
        self,
        findings: list[ScanFinding],
        risk_score: float,
        direction: TrafficDirection,
    ) -> ScanVerdict:
        """Apply the firewall policy to determine the verdict."""
        if not self._policy.enabled:
            return ScanVerdict.PASS

        # Check explicit rules (sorted by priority)
        sorted_rules = sorted(self._policy.rules, key=lambda r: r.priority)
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            if rule.direction is not None and rule.direction != direction:
                continue

            matching = [
                f
                for f in findings
                if (not rule.categories or f.category in rule.categories)
                and f.severity >= rule.severity_threshold
            ]

            if matching:
                if rule.action == PolicyAction.BLOCK:
                    return ScanVerdict.BLOCK
                elif rule.action == PolicyAction.WARN:
                    return ScanVerdict.WARN

        # Fall back to threshold-based verdict
        if risk_score >= self._policy.block_threshold:
            return ScanVerdict.BLOCK
        elif risk_score >= self._policy.warn_threshold:
            return ScanVerdict.WARN

        return ScanVerdict.PASS

    @staticmethod
    def _hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def _verdict_to_action(verdict: ScanVerdict) -> PolicyAction:
        return {
            ScanVerdict.PASS: PolicyAction.ALLOW,
            ScanVerdict.WARN: PolicyAction.WARN,
            ScanVerdict.BLOCK: PolicyAction.BLOCK,
        }[verdict]

    @staticmethod
    def _default_policy() -> FirewallPolicy:
        from semantic_firewall.config.default_policy import create_default_policy

        return create_default_policy()
