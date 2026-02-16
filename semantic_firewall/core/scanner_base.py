"""Base class for all Semantic Firewall scanners."""

from __future__ import annotations

import abc
from typing import Any

from semantic_firewall.core.models import ScanFinding, TrafficDirection


class BaseScanner(abc.ABC):
    """Abstract base class that all scanners must implement."""

    def __init__(self, name: str, enabled: bool = True) -> None:
        self.name = name
        self.enabled = enabled

    @abc.abstractmethod
    def supported_directions(self) -> set[TrafficDirection]:
        """Return which traffic directions this scanner handles."""

    @abc.abstractmethod
    async def scan(
        self,
        content: str,
        direction: TrafficDirection,
        context: dict[str, Any] | None = None,
    ) -> list[ScanFinding]:
        """
        Scan content and return a list of findings.

        Args:
            content: The text content to scan.
            direction: Whether this is inbound or outbound traffic.
            context: Optional metadata (user_id, session, endpoint, etc.)

        Returns:
            A list of ScanFinding objects. Empty list means no issues found.
        """

    def applies_to(self, direction: TrafficDirection) -> bool:
        """Check if this scanner applies to the given direction."""
        return self.enabled and direction in self.supported_directions()
