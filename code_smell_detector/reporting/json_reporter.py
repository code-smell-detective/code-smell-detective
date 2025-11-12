"""JSON reporting utilities."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List

from ..data_models import AnalysisReport, Severity, SmellInstance


class JsonReporter:
    """Generate JSON reports from analysis results."""

    def to_dict(self, report: AnalysisReport) -> Dict[str, object]:
        smells_summary = _summarize_smells(report.smells)

        return {
            "analysis_metadata": report.metrics_summary.get("analysis_metadata", {}),
            "health_score": {
                "overall": f"{report.health_score}/100",
                "breakdown": {
                    "complexity": f"{report.health_breakdown.complexity}/100",
                    "coupling": f"{report.health_breakdown.coupling}/100",
                    "cohesion": f"{report.health_breakdown.cohesion}/100",
                    "duplication": f"{report.health_breakdown.duplication}/100",
                    "solid_compliance": f"{report.health_breakdown.solid_compliance}/100",
                },
            },
            "smells_summary": smells_summary,
            "detected_smells": [_smell_to_dict(smell) for smell in report.smells],
            "metrics_summary": {k: v for k, v in report.metrics_summary.items() if k != "analysis_metadata"},
            "recommendations": report.recommendations,
        }

    def write(self, report: AnalysisReport, output_path: str | Path) -> None:
        """Write report to JSON file."""
        data = self.to_dict(report)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _smell_to_dict(smell: SmellInstance) -> Dict[str, object]:
    return {
        "type": smell.smell_type,
        "category": smell.category,
        "severity": smell.severity.value,
        "location": {
            "file": str(smell.location.file),
            "line_start": smell.location.line_start,
            "line_end": smell.location.line_end,
            "class": smell.location.class_name,
            "method": smell.location.function_name,
        },
        "metrics": smell.metrics,
        "solid_violations": list(smell.solid_violations),
        "recommended_patterns": list(smell.recommended_patterns),
        "description": smell.description,
        "refactoring_steps": list(smell.refactoring_steps),
    }


def _summarize_smells(smells: Iterable[SmellInstance]) -> Dict[str, object]:
    smells = list(smells)
    severity_counter = Counter(smell.severity for smell in smells)
    category_counter = Counter(smell.category for smell in smells)
    return {
        "total_smells": len(smells),
        "by_severity": {severity.value: severity_counter.get(severity, 0) for severity in Severity},
        "by_category": dict(category_counter),
    }

