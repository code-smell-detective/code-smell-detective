"""Data models used by the Code Smell Detector."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


class Severity(str, Enum):
    """Severity levels for detected smells."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(slots=True)
class CodeLocation:
    """Location information for a smell instance."""

    file: Path
    line_start: int
    line_end: int
    class_name: Optional[str] = None
    function_name: Optional[str] = None


@dataclass(slots=True)
class SmellDefinition:
    """Definition metadata for a smell analyzer."""

    name: str
    category: str
    thresholds: Dict[str, Any]
    solid_violations: Iterable[str] = field(default_factory=list)
    recommended_patterns: Iterable[str] = field(default_factory=list)


@dataclass(slots=True)
class SmellInstance:
    """A detected code smell instance."""

    smell_type: str
    category: str
    severity: Severity
    location: CodeLocation
    metrics: Dict[str, Any]
    solid_violations: Iterable[str] = field(default_factory=list)
    recommended_patterns: Iterable[str] = field(default_factory=list)
    description: Optional[str] = None
    refactoring_steps: Iterable[str] = field(default_factory=list)


@dataclass(slots=True)
class HealthBreakdown:
    """Breakdown of health score components."""

    complexity: int
    coupling: int
    cohesion: int
    duplication: int
    solid_compliance: int


@dataclass(slots=True)
class AnalysisReport:
    """Complete analysis report for a codebase."""

    smells: List[SmellInstance]
    metrics_summary: Dict[str, Any]
    health_score: int
    health_breakdown: HealthBreakdown
    recommendations: List[Dict[str, Any]]

