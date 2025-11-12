"""Class-level smell analyzers."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Iterable

from ..config import DetectorConfig
from ..data_models import CodeLocation, Severity, SmellDefinition, SmellInstance
from ..metrics.calculator import ClassMetrics, MetricsCalculator
from .base import BaseAnalyzer


class LargeClassAnalyzer(BaseAnalyzer):
    """Detects large or god classes."""

    def get_definition(self, config: DetectorConfig) -> SmellDefinition:
        return SmellDefinition(
            name="Large Class",
            category="Class-Level",
            thresholds=config.thresholds["large_class"],
            solid_violations=["SRP"],
            recommended_patterns=["Extract Class", "Facade", "Mediator", "Repository"],
        )

    def analyze_module(
        self,
        module: ast.Module,
        filepath: str,
        calculator: MetricsCalculator,
        config: DetectorConfig,
    ) -> Iterable[SmellInstance]:
        definition = self.get_definition(config)
        for class_node in (n for n in ast.walk(module) if isinstance(n, ast.ClassDef)):
            metrics = calculator.calculate_class_metrics(class_node)
            if _is_large_class(metrics, definition.thresholds):
                severity = _large_class_severity(metrics, definition.thresholds)
                yield SmellInstance(
                    smell_type=definition.name,
                    category=definition.category,
                    severity=severity,
                    location=_class_location(filepath, class_node),
                    metrics=_class_metrics_dict(metrics),
                    solid_violations=definition.solid_violations,
                    recommended_patterns=definition.recommended_patterns,
                    description=(
                        f"Class '{class_node.name}' has {metrics.lines_of_code} LOC, "
                        f"{metrics.method_count} methods, and {metrics.field_count} fields."
                    ),
                    refactoring_steps=[
                        "Group related responsibilities and extract classes accordingly.",
                        "Introduce facades or mediators to simplify public APIs.",
                        "Ensure public method count reflects cohesive responsibility.",
                    ],
                )


def _is_large_class(metrics: ClassMetrics, thresholds: dict[str, int]) -> bool:
    return (
        metrics.lines_of_code > thresholds["lines_of_code"]
        or metrics.method_count > thresholds["method_count"]
        or metrics.field_count > thresholds["field_count"]
        or metrics.public_method_count > thresholds.get("public_method_count", 15)
    )


def _large_class_severity(metrics: ClassMetrics, thresholds: dict[str, int]) -> Severity:
    if metrics.lines_of_code > 1200 or metrics.method_count > 60:
        return Severity.CRITICAL
    if metrics.lines_of_code > 800 or metrics.method_count > 40:
        return Severity.HIGH
    if metrics.lines_of_code > 500 or metrics.method_count > 30:
        return Severity.MEDIUM
    return Severity.LOW


def _class_metrics_dict(metrics: ClassMetrics) -> dict[str, int]:
    return {
        "lines_of_code": metrics.lines_of_code,
        "method_count": metrics.method_count,
        "field_count": metrics.field_count,
        "public_method_count": metrics.public_method_count,
    }


def _class_location(filepath: str, node: ast.ClassDef) -> CodeLocation:
    return CodeLocation(
        file=Path(filepath),
        line_start=node.lineno,
        line_end=node.end_lineno or node.lineno,
        class_name=node.name,
    )

