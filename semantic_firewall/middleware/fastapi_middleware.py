"""
FastAPI Middleware - Transparent request/response scanning for AI endpoints.

Integrates the Semantic Firewall into any FastAPI application as middleware,
scanning inbound requests and outbound responses through the scanner pipeline.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Callable, Sequence

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from semantic_firewall.core.engine import SemanticFirewallEngine
from semantic_firewall.core.models import FirewallPolicy, ScanVerdict, TrafficDirection

logger = logging.getLogger("semantic_firewall.middleware")


class SemanticFirewallMiddleware(BaseHTTPMiddleware):
    """
    FastAPI/Starlette middleware that scans AI traffic through the Semantic Firewall.

    Usage:
        from fastapi import FastAPI
        from semantic_firewall import SemanticFirewallMiddleware, SemanticFirewallEngine

        app = FastAPI()
        engine = SemanticFirewallEngine()
        # ... register scanners on engine ...
        app.add_middleware(SemanticFirewallMiddleware, engine=engine)
    """

    def __init__(
        self,
        app: Any,
        engine: SemanticFirewallEngine,
        protected_paths: Sequence[str] | None = None,
        excluded_paths: Sequence[str] | None = None,
        block_status_code: int = 403,
        scan_request_body: bool = True,
        scan_response_body: bool = True,
        max_body_size: int = 1_000_000,  # 1MB
    ) -> None:
        super().__init__(app)
        self.engine = engine
        self.protected_paths = list(protected_paths) if protected_paths else None
        self.excluded_paths = list(excluded_paths or ["/health", "/metrics", "/docs", "/openapi.json"])
        self.block_status_code = block_status_code
        self.scan_request_body = scan_request_body
        self.scan_response_body = scan_response_body
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path

        # Skip excluded paths
        if any(path.startswith(ep) for ep in self.excluded_paths):
            return await call_next(request)

        # If protected_paths is set, only scan those paths
        if self.protected_paths and not any(
            path.startswith(pp) for pp in self.protected_paths
        ):
            return await call_next(request)

        context = {
            "source_ip": request.client.host if request.client else None,
            "endpoint": path,
            "method": request.method,
            "user_id": request.headers.get("X-User-ID"),
            "session_id": request.headers.get("X-Session-ID"),
        }

        # --- INBOUND SCAN (request) ---
        if self.scan_request_body and request.method in ("POST", "PUT", "PATCH"):
            body = await self._read_body(request)
            if body:
                inbound_result = await self.engine.scan(
                    content=body,
                    direction=TrafficDirection.INBOUND,
                    context=context,
                )

                if inbound_result.blocked:
                    logger.warning(
                        "BLOCKED inbound request to %s | scan_id=%s risk=%.2f",
                        path,
                        inbound_result.scan_id[:8],
                        inbound_result.aggregate_risk_score,
                    )
                    return self._blocked_response(
                        inbound_result.scan_id,
                        "inbound",
                        inbound_result.aggregate_risk_score,
                        [f.description for f in inbound_result.findings[:3]],
                    )

                # Attach scan metadata to request state for downstream use
                request.state.inbound_scan = inbound_result

        # --- Call the actual endpoint ---
        response = await call_next(request)

        # --- OUTBOUND SCAN (response) ---
        if self.scan_response_body and response.status_code == 200:
            response_body = await self._read_response_body(response)
            if response_body:
                outbound_result = await self.engine.scan(
                    content=response_body,
                    direction=TrafficDirection.OUTBOUND,
                    context=context,
                )

                # Add scan headers to response
                response.headers["X-Firewall-Scan-ID"] = outbound_result.scan_id
                response.headers["X-Firewall-Verdict"] = outbound_result.verdict.value

                if outbound_result.blocked:
                    logger.warning(
                        "BLOCKED outbound response from %s | scan_id=%s risk=%.2f",
                        path,
                        outbound_result.scan_id[:8],
                        outbound_result.aggregate_risk_score,
                    )
                    return self._blocked_response(
                        outbound_result.scan_id,
                        "outbound",
                        outbound_result.aggregate_risk_score,
                        [f.description for f in outbound_result.findings[:3]],
                    )

                # If response was read, we need to reconstruct it
                return Response(
                    content=response_body.encode("utf-8"),
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type,
                )

        return response

    async def _read_body(self, request: Request) -> str | None:
        """Read request body up to max size."""
        try:
            body = await request.body()
            if len(body) > self.max_body_size:
                logger.debug("Request body exceeds max size, skipping scan")
                return None
            return body.decode("utf-8", errors="replace")
        except Exception:
            logger.debug("Failed to read request body")
            return None

    async def _read_response_body(self, response: Response) -> str | None:
        """Read response body for scanning."""
        try:
            body_chunks = []
            total_size = 0
            async for chunk in response.body_iterator:
                if isinstance(chunk, bytes):
                    body_chunks.append(chunk)
                else:
                    body_chunks.append(chunk.encode("utf-8"))
                total_size += len(body_chunks[-1])
                if total_size > self.max_body_size:
                    return None
            full_body = b"".join(body_chunks)
            return full_body.decode("utf-8", errors="replace")
        except Exception:
            logger.debug("Failed to read response body")
            return None

    def _blocked_response(
        self,
        scan_id: str,
        direction: str,
        risk_score: float,
        reasons: list[str],
    ) -> JSONResponse:
        """Return a standardized blocked response."""
        return JSONResponse(
            status_code=self.block_status_code,
            content={
                "error": "Request blocked by Semantic Firewall",
                "scan_id": scan_id,
                "direction": direction,
                "risk_score": round(risk_score, 3),
                "reasons": reasons,
            },
            headers={
                "X-Firewall-Scan-ID": scan_id,
                "X-Firewall-Verdict": "block",
            },
        )
