"""
Audit Logger - Persistent logging of all Semantic Firewall scan events.

Provides:
- JSON-structured audit log files
- In-memory ring buffer for recent events
- Statistics aggregation
- Configurable log rotation
"""

from __future__ import annotations

import json
import logging
import os
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from semantic_firewall.core.models import AuditLogEntry, ScanVerdict

logger = logging.getLogger("semantic_firewall.audit")


class AuditLogger:
    """
    Audit logger that persists firewall scan events.

    Maintains both a file-based audit trail and an in-memory ring buffer
    for fast access to recent events and real-time statistics.
    """

    def __init__(
        self,
        log_dir: str | Path = "logs/semantic_firewall",
        buffer_size: int = 1000,
        log_to_file: bool = True,
    ) -> None:
        self._log_dir = Path(log_dir)
        self._buffer: deque[AuditLogEntry] = deque(maxlen=buffer_size)
        self._log_to_file = log_to_file
        self._stats = {
            "total": 0,
            "blocks": 0,
            "warnings": 0,
            "passes": 0,
            "inbound": 0,
            "outbound": 0,
        }

        if self._log_to_file:
            self._log_dir.mkdir(parents=True, exist_ok=True)

    async def log(self, entry: AuditLogEntry) -> None:
        """Log an audit entry."""
        self._buffer.append(entry)
        self._update_stats(entry)

        if self._log_to_file:
            self._write_to_file(entry)

        if entry.scan_result.verdict == ScanVerdict.BLOCK:
            logger.warning(
                "AUDIT BLOCK | scan=%s endpoint=%s user=%s risk=%.2f",
                entry.scan_result.scan_id[:8],
                entry.endpoint,
                entry.user_id,
                entry.scan_result.aggregate_risk_score,
            )

    def _update_stats(self, entry: AuditLogEntry) -> None:
        self._stats["total"] += 1
        self._stats[entry.scan_result.direction.value] += 1
        verdict = entry.scan_result.verdict
        if verdict == ScanVerdict.BLOCK:
            self._stats["blocks"] += 1
        elif verdict == ScanVerdict.WARN:
            self._stats["warnings"] += 1
        else:
            self._stats["passes"] += 1

    def _write_to_file(self, entry: AuditLogEntry) -> None:
        """Append entry to daily log file as JSON line."""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = self._log_dir / f"firewall_audit_{date_str}.jsonl"

        record = {
            "entry_id": entry.entry_id,
            "timestamp": entry.timestamp.isoformat(),
            "scan_id": entry.scan_result.scan_id,
            "direction": entry.scan_result.direction.value,
            "verdict": entry.scan_result.verdict.value,
            "risk_score": entry.scan_result.aggregate_risk_score,
            "finding_count": len(entry.scan_result.findings),
            "findings": [
                {
                    "scanner": f.scanner_name,
                    "category": f.category.value,
                    "severity": f.severity,
                    "description": f.description,
                }
                for f in entry.scan_result.findings
            ],
            "source_ip": entry.source_ip,
            "user_id": entry.user_id,
            "endpoint": entry.endpoint,
            "action_taken": entry.action_taken.value,
            "latency_ms": entry.scan_result.latency_ms,
            "request_size_bytes": entry.request_size_bytes,
        }

        try:
            with open(log_file, "a") as f:
                f.write(json.dumps(record) + "\n")
        except OSError:
            logger.exception("Failed to write audit log")

    @property
    def stats(self) -> dict[str, int]:
        """Return current aggregate statistics."""
        return dict(self._stats)

    def recent_events(self, count: int = 50) -> list[dict[str, Any]]:
        """Return the most recent audit events as dicts."""
        events = list(self._buffer)[-count:]
        return [
            {
                "entry_id": e.entry_id,
                "timestamp": e.timestamp.isoformat(),
                "scan_id": e.scan_result.scan_id,
                "direction": e.scan_result.direction.value,
                "verdict": e.scan_result.verdict.value,
                "risk_score": e.scan_result.aggregate_risk_score,
                "finding_count": len(e.scan_result.findings),
                "endpoint": e.endpoint,
                "user_id": e.user_id,
            }
            for e in events
        ]

    def findings_summary(self) -> dict[str, int]:
        """Return a count of findings by category across recent events."""
        summary: dict[str, int] = {}
        for entry in self._buffer:
            for finding in entry.scan_result.findings:
                key = finding.category.value
                summary[key] = summary.get(key, 0) + 1
        return summary
