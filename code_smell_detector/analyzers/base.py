"""Base analyzer definitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

import ast

from ..config import DetectorConfig
from ..data_models import SmellDefinition, SmellInstance
from ..metrics.calculator import MetricsCalculator


class BaseAnalyzer(ABC):
    """Abstract analyzer for detecting code smells."""

    @abstractmethod
    def get_definition(self, config: DetectorConfig) -> SmellDefinition:
        """Return smell definition metadata using configuration thresholds."""

    @abstractmethod
    def analyze_module(
        self,
        module: ast.Module,
        filepath: str,
        calculator: MetricsCalculator,
        config: DetectorConfig,
    ) -> Iterable[SmellInstance]:
        """Analyze an AST module and yield smell instances."""

    def analyze(
        self,
        module: ast.Module,
        filepath: str,
        calculator: MetricsCalculator,
        config: DetectorConfig,
    ) -> List[SmellInstance]:
        """Analyze module and return list of detected smells."""
        return list(self.analyze_module(module, filepath, calculator, config))

