"""
Data Exfiltration Scanner - Detects attempts to exfiltrate data through AI outputs.

Catches:
- Encoded data blobs (base64, hex) that may contain exfiltrated information
- Structured data dumps (JSON, CSV, SQL) exceeding expected size
- URL-encoded payloads that could carry stolen data
- Suspicious external URL references in AI outputs
- Database query results or schema information exposure
"""

from __future__ import annotations

import re
from typing import Any

from semantic_firewall.core.models import ScanFinding, ThreatCategory, TrafficDirection
from semantic_firewall.core.scanner_base import BaseScanner

# Thresholds
_BASE64_MIN_LENGTH = 100  # Minimum base64 length to flag
_HEX_MIN_LENGTH = 50  # Minimum hex dump length to flag
_JSON_ARRAY_RECORD_THRESHOLD = 20  # Flag JSON arrays with 20+ objects


class DataExfiltrationScanner(BaseScanner):
    """Scans outbound traffic for signs of data exfiltration."""

    def __init__(self, enabled: bool = True) -> None:
        super().__init__(name="data_exfiltration", enabled=enabled)

    def supported_directions(self) -> set[TrafficDirection]:
        return {TrafficDirection.OUTBOUND}

    async def scan(
        self,
        content: str,
        direction: TrafficDirection,
        context: dict[str, Any] | None = None,
    ) -> list[ScanFinding]:
        findings: list[ScanFinding] = []

        findings.extend(self._check_encoded_blobs(content))
        findings.extend(self._check_data_dumps(content))
        findings.extend(self._check_suspicious_urls(content))
        findings.extend(self._check_database_exposure(content))

        return findings

    def _check_encoded_blobs(self, content: str) -> list[ScanFinding]:
        """Detect large base64 or hex-encoded blocks that may carry exfiltrated data."""
        findings: list[ScanFinding] = []

        # Base64 blobs
        b64_pattern = re.compile(r"[A-Za-z0-9+/]{%d,}={0,2}" % _BASE64_MIN_LENGTH)
        b64_matches = b64_pattern.findall(content)
        if b64_matches:
            total_length = sum(len(m) for m in b64_matches)
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.DATA_EXFILTRATION,
                    severity=min(0.9, 0.5 + total_length / 10_000),
                    description=f"Large base64-encoded data detected in output ({len(b64_matches)} block(s), {total_length} chars)",
                    evidence=f"blocks={len(b64_matches)} total_chars={total_length}",
                )
            )

        # Hex dumps
        hex_pattern = re.compile(r"(?:[0-9a-fA-F]{2}\s*){%d,}" % _HEX_MIN_LENGTH)
        hex_matches = hex_pattern.findall(content)
        if hex_matches:
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.DATA_EXFILTRATION,
                    severity=0.6,
                    description=f"Hex-encoded data dump detected in output ({len(hex_matches)} block(s))",
                    evidence=f"blocks={len(hex_matches)}",
                )
            )

        return findings

    def _check_data_dumps(self, content: str) -> list[ScanFinding]:
        """Detect large structured data dumps (JSON arrays, CSV blocks, etc.)."""
        findings: list[ScanFinding] = []

        # JSON array with many records
        json_array_pattern = re.compile(
            r"\[\s*\{[^}]+\}\s*(?:,\s*\{[^}]+\}\s*){%d,}\]"
            % _JSON_ARRAY_RECORD_THRESHOLD,
            re.DOTALL,
        )
        if json_array_pattern.search(content):
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.DATA_EXFILTRATION,
                    severity=0.75,
                    description=f"Large JSON array with {_JSON_ARRAY_RECORD_THRESHOLD}+ records detected in output",
                    evidence="json_array_dump",
                )
            )

        # CSV-style data dumps (many rows with consistent delimiter count)
        lines = content.split("\n")
        csv_like = 0
        for line in lines[:200]:
            if line.count(",") >= 3 or line.count("\t") >= 3:
                csv_like += 1
        if csv_like > 20:
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.DATA_EXFILTRATION,
                    severity=0.65,
                    description=f"CSV-style data dump detected ({csv_like} rows with consistent delimiters)",
                    evidence=f"csv_like_rows={csv_like}",
                )
            )

        return findings

    def _check_suspicious_urls(self, content: str) -> list[ScanFinding]:
        """Detect URLs that could be used to exfiltrate data via query parameters."""
        findings: list[ScanFinding] = []

        url_pattern = re.compile(
            r"https?://[^\s\"'<>]+\?[^\s\"'<>]{100,}"
        )
        matches = url_pattern.findall(content)
        if matches:
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.DATA_EXFILTRATION,
                    severity=0.7,
                    description=f"URL(s) with large query parameters detected (possible data exfiltration channel)",
                    evidence=f"count={len(matches)}",
                )
            )

        # Webhook / callback URLs that could receive data
        callback_pattern = re.compile(
            r"(?i)https?://[^\s\"'<>]*(webhook|callback|exfil|ngrok|requestbin|hookbin|pipedream)",
        )
        cb_matches = callback_pattern.findall(content)
        if cb_matches:
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.DATA_EXFILTRATION,
                    severity=0.8,
                    description="Suspicious webhook/callback URL detected in output",
                    evidence=f"patterns={cb_matches[:3]}",
                )
            )

        return findings

    def _check_database_exposure(self, content: str) -> list[ScanFinding]:
        """Detect database schema or query result patterns in output."""
        findings: list[ScanFinding] = []

        # SQL result sets
        sql_result_pattern = re.compile(
            r"(?i)(\+[-+]+\+\s*\n\|.*\|\s*\n\+[-+]+\+)",
            re.DOTALL,
        )
        if sql_result_pattern.search(content):
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.DATA_EXFILTRATION,
                    severity=0.7,
                    description="SQL-formatted result set detected in output",
                    evidence="sql_result_table",
                )
            )

        # Database schema exposure
        schema_pattern = re.compile(
            r"(?i)(CREATE\s+TABLE|ALTER\s+TABLE|SHOW\s+TABLES|DESCRIBE\s+\w+|information_schema)",
        )
        schema_matches = schema_pattern.findall(content)
        if len(schema_matches) >= 2:
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.SENSITIVE_DATA_EXPOSURE,
                    severity=0.7,
                    description="Database schema information detected in output",
                    evidence=f"schema_keywords={schema_matches[:5]}",
                )
            )

        # Connection strings
        conn_pattern = re.compile(
            r"(?i)(postgresql|mysql|mongodb|redis|amqp)://[^\s\"'<>]+",
        )
        if conn_pattern.search(content):
            findings.append(
                ScanFinding(
                    scanner_name=self.name,
                    category=ThreatCategory.SENSITIVE_DATA_EXPOSURE,
                    severity=0.9,
                    description="Database connection string detected in output",
                    evidence="connection_string_found",
                )
            )

        return findings
