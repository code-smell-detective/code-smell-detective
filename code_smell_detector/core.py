"""Core orchestrator for the Code Smell Detector."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List

import ast

from .analyzers.class_level import LargeClassAnalyzer
from .analyzers.duplication import DuplicatedCodeAnalyzer
from .analyzers.method_level import (
    ComplexConditionalAnalyzer,
    LongMethodAnalyzer,
    LongParameterListAnalyzer,
)
from .analyzers.base import BaseAnalyzer
from .config import DetectorConfig
from .data_models import AnalysisReport, HealthBreakdown, Severity, SmellInstance
from .metrics.calculator import MetricsCalculator, iter_py_files, parse_python_file


@dataclass(slots=True)
class _MetricsAccumulator:
    function_count: int = 0
    class_count: int = 0
    total_function_loc: int = 0
    total_class_loc: int = 0
    total_complexity: int = 0
    max_complexity: int = 0

    def register_function(self, metrics) -> None:
        self.function_count += 1
        self.total_function_loc += metrics.lines_of_code
        self.total_complexity += metrics.cyclomatic_complexity
        self.max_complexity = max(self.max_complexity, metrics.cyclomatic_complexity)

    def register_class(self, metrics) -> None:
        self.class_count += 1
        self.total_class_loc += metrics.lines_of_code

    def average_complexity(self) -> float:
        if self.function_count == 0:
            return 0.0
        return self.total_complexity / self.function_count

    def average_function_loc(self) -> float:
        if self.function_count == 0:
            return 0.0
        return self.total_function_loc / self.function_count

    def average_class_loc(self) -> float:
        if self.class_count == 0:
            return 0.0
        return self.total_class_loc / self.class_count


class CodeSmellDetector:
    """Main entry point for analyzing a codebase."""

    def __init__(self, config: DetectorConfig | None = None) -> None:
        self.config = config or DetectorConfig()
        self.analyzers: List[BaseAnalyzer] = [
            LongMethodAnalyzer(),
            LongParameterListAnalyzer(),
            ComplexConditionalAnalyzer(),
            LargeClassAnalyzer(),
            DuplicatedCodeAnalyzer(),
        ]

    def analyze_codebase(self, path: str | Path) -> AnalysisReport:
        """Analyze a codebase and return an analysis report."""
        target_path = Path(path).resolve()
        if not target_path.exists():
            raise FileNotFoundError(f"Codebase path does not exist: {target_path}")

        accumulator = _MetricsAccumulator()
        smells: List[SmellInstance] = []

        exclusions = list(self.config.exclusions.get("paths", ()))
        exclusions += [f for f in self.config.exclusions.get("files", ())]

        files = list(iter_py_files(target_path, exclusions))

        for filepath in files:
            module, source = parse_python_file(filepath)
            calculator = MetricsCalculator(source)
            self._register_metrics(module, calculator, accumulator)
            for analyzer in self.analyzers:
                smells.extend(
                    analyzer.analyze(module, str(filepath), calculator, self.config)
                )

        metrics_summary = self._build_metrics_summary(target_path, files, accumulator)
        health_breakdown, health_score = self._calculate_health(smells, accumulator)
        recommendations = self._build_recommendations(smells)

        return AnalysisReport(
            smells=smells,
            metrics_summary=metrics_summary,
            health_score=health_score,
            health_breakdown=health_breakdown,
            recommendations=recommendations,
        )

    def _register_metrics(
        self,
        module: ast.Module,
        calculator: MetricsCalculator,
        accumulator: _MetricsAccumulator,
    ) -> None:
        for node in ast.walk(module):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                metrics = calculator.calculate_function_metrics(node)
                accumulator.register_function(metrics)
            elif isinstance(node, ast.ClassDef):
                metrics = calculator.calculate_class_metrics(node)
                accumulator.register_class(metrics)

    def _build_metrics_summary(
        self,
        root: Path,
        files: List[Path],
        accumulator: _MetricsAccumulator,
    ) -> Dict[str, object]:
        return {
            "analysis_metadata": {
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "codebase_path": str(root),
                "total_files_analyzed": len(files),
            },
            "average_cyclomatic_complexity": round(accumulator.average_complexity(), 2),
            "average_function_loc": round(accumulator.average_function_loc(), 2),
            "average_class_loc": round(accumulator.average_class_loc(), 2),
            "max_cyclomatic_complexity": accumulator.max_complexity,
            "function_count": accumulator.function_count,
            "class_count": accumulator.class_count,
        }

    def _calculate_health(
        self,
        smells: Iterable[SmellInstance],
        accumulator: _MetricsAccumulator,
    ) -> tuple[HealthBreakdown, int]:
        severity_weights = {
            Severity.CRITICAL: 35,
            Severity.HIGH: 20,
            Severity.MEDIUM: 10,
            Severity.LOW: 5,
        }
        penalty = sum(severity_weights[smell.severity] for smell in smells)
        health_score = max(0, 100 - penalty)

        complexity_score = max(0, 100 - int(accumulator.average_complexity() * 5))
        coupling_score = 80  # placeholder for future phases
        cohesion_score = 75
        duplication_penalty = sum(
            smell.metrics.get("duplicate_line_count", 0)
            for smell in smells
            if smell.smell_type == "Duplicated Code"
        )
        duplication_score = max(0, 100 - duplication_penalty)
        solid_penalty = sum(
            5 for smell in smells if smell.solid_violations
        )
        solid_score = max(0, 100 - solid_penalty)

        breakdown = HealthBreakdown(
            complexity=complexity_score,
            coupling=coupling_score,
            cohesion=cohesion_score,
            duplication=duplication_score,
            solid_compliance=solid_score,
        )

        return breakdown, health_score

    def _build_recommendations(self, smells: List[SmellInstance]) -> List[Dict[str, object]]:
        critical_smells = [sm for sm in smells if sm.severity in {Severity.CRITICAL, Severity.HIGH}]
        recommendations: List[Dict[str, object]] = []

        for smell in critical_smells[:5]:
            recommendations.append(
                {
                    "priority": smell.severity.value,
                    "smell_type": smell.smell_type,
                    "location": str(smell.location.file),
                    "recommendation": f"Address {smell.smell_type} at {smell.location.file}:{smell.location.line_start}",
                    "impact": "HIGH" if smell.severity == Severity.CRITICAL else "MEDIUM",
                }
            )
        return recommendations

