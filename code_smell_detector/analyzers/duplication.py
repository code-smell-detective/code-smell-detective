"""Duplication smell analyzers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..config import DetectorConfig
from ..data_models import CodeLocation, Severity, SmellDefinition, SmellInstance
from ..metrics.calculator import MetricsCalculator
from .base import BaseAnalyzer


class DuplicatedCodeAnalyzer(BaseAnalyzer):
    """Detects duplicated code blocks within a file."""

    def get_definition(self, config: DetectorConfig) -> SmellDefinition:
        return SmellDefinition(
            name="Duplicated Code",
            category="Duplication",
            thresholds=config.thresholds["duplicated_code"],
            solid_violations=["DRY"],
            recommended_patterns=["Extract Method", "Template Method", "Strategy"],
        )

    def analyze_module(
        self,
        module,
        filepath: str,
        calculator: MetricsCalculator,
        config: DetectorConfig,
    ) -> Iterable[SmellInstance]:
        # module parameter unused: duplication detection is text/token based
        del module
        definition = self.get_definition(config)
        threshold_lines = definition.thresholds["min_duplicate_lines"]
        occurrences = calculator.duplicated_code_blocks(min_lines=threshold_lines)

        for (start, end), count in occurrences.items():
            severity = _duplication_severity(count, end - start + 1)
            yield SmellInstance(
                smell_type=definition.name,
                category=definition.category,
                severity=severity,
                location=CodeLocation(file=Path(filepath), line_start=start, line_end=end),
                metrics={
                    "duplicate_line_count": end - start + 1,
                    "occurrences": count,
                },
                solid_violations=definition.solid_violations,
                recommended_patterns=definition.recommended_patterns,
                description=(
                    f"Block duplicated {count} times covering lines {start}-{end} "
                    f"(minimum {threshold_lines} lines)."
                ),
                refactoring_steps=[
                    "Identify duplicated logic and extract shared functionality.",
                    "Introduce template or strategy pattern if variations exist.",
                    "Write regression tests before refactoring.",
                ],
            )


def _duplication_severity(occurrences: int, line_count: int) -> Severity:
    if occurrences > 5 or line_count > 40:
        return Severity.CRITICAL
    if occurrences > 3 or line_count > 20:
        return Severity.HIGH
    if occurrences > 2 or line_count > 10:
        return Severity.MEDIUM
    return Severity.LOW

