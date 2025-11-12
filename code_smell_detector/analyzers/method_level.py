"""Method-level code smell analyzers."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Dict, Iterable

from ..config import DetectorConfig
from ..data_models import CodeLocation, Severity, SmellDefinition, SmellInstance
from ..metrics.calculator import FunctionMetrics, MetricsCalculator
from .base import BaseAnalyzer


class LongMethodAnalyzer(BaseAnalyzer):
    """Detects long and complex methods."""

    def get_definition(self, config: DetectorConfig) -> SmellDefinition:
        return SmellDefinition(
            name="Long Method",
            category="Method-Level",
            thresholds=config.thresholds["long_method"],
            solid_violations=["SRP"],
            recommended_patterns=["Extract Method", "Template Method", "Strategy"],
        )

    def analyze_module(
        self,
        module: ast.Module,
        filepath: str,
        calculator: MetricsCalculator,
        config: DetectorConfig,
    ) -> Iterable[SmellInstance]:
        definition = self.get_definition(config)
        for function in _iter_functions(module):
            metrics = calculator.calculate_function_metrics(function)
            if _is_long_method(metrics, definition.thresholds):
                yield SmellInstance(
                    smell_type=definition.name,
                    category=definition.category,
                    severity=_long_method_severity(metrics),
                    location=_location_from_node(filepath, function),
                    metrics=_function_metrics_dict(metrics),
                    solid_violations=definition.solid_violations,
                    recommended_patterns=definition.recommended_patterns,
                    description=(
                        f"Function '{function.name}' is {metrics.lines_of_code} LOC with "
                        f"cyclomatic complexity {metrics.cyclomatic_complexity}."
                    ),
                    refactoring_steps=[
                        "Add characterization tests to lock current behaviour.",
                        "Extract blocks with distinct responsibilities into new methods.",
                        "Replace complex conditional branches with strategy objects if applicable.",
                    ],
                )


class LongParameterListAnalyzer(BaseAnalyzer):
    """Detects functions with long parameter lists."""

    def get_definition(self, config: DetectorConfig) -> SmellDefinition:
        return SmellDefinition(
            name="Long Parameter List",
            category="Method-Level",
            thresholds=config.thresholds["long_parameter_list"],
            solid_violations=["SRP"],
            recommended_patterns=["Parameter Object", "Builder", "Facade"],
        )

    def analyze_module(
        self,
        module: ast.Module,
        filepath: str,
        calculator: MetricsCalculator,
        config: DetectorConfig,
    ) -> Iterable[SmellInstance]:
        definition = self.get_definition(config)
        threshold = definition.thresholds["parameter_count"]
        for function in _iter_functions(module):
            metrics = calculator.calculate_function_metrics(function)
            if metrics.parameter_count > threshold:
                severity = _parameter_severity(metrics.parameter_count)
                yield SmellInstance(
                    smell_type=definition.name,
                    category=definition.category,
                    severity=severity,
                    location=_location_from_node(filepath, function),
                    metrics=_function_metrics_dict(metrics),
                    solid_violations=definition.solid_violations,
                    recommended_patterns=definition.recommended_patterns,
                    description=(
                        f"Function '{function.name}' accepts {metrics.parameter_count} parameters "
                        f"(allowed: {threshold})."
                    ),
                    refactoring_steps=[
                        "Identify groups of parameters that always appear together.",
                        "Introduce parameter objects or aggregate types.",
                        "Update callers to use new abstractions.",
                    ],
                )


class ComplexConditionalAnalyzer(BaseAnalyzer):
    """Detects complex conditional logic."""

    def get_definition(self, config: DetectorConfig) -> SmellDefinition:
        return SmellDefinition(
            name="Complex Conditional",
            category="Method-Level",
            thresholds=config.thresholds["complex_conditional"],
            solid_violations=["OCP"],
            recommended_patterns=["Strategy", "State", "Chain of Responsibility", "Specification"],
        )

    def analyze_module(
        self,
        module: ast.Module,
        filepath: str,
        calculator: MetricsCalculator,
        config: DetectorConfig,
    ) -> Iterable[SmellInstance]:
        definition = self.get_definition(config)
        for function in _iter_functions(module):
            metrics = calculator.calculate_function_metrics(function)
            if _is_complex_conditional(metrics, definition.thresholds):
                severity = _conditional_severity(metrics, definition.thresholds)
                yield SmellInstance(
                    smell_type=definition.name,
                    category=definition.category,
                    severity=severity,
                    location=_location_from_node(filepath, function),
                    metrics=_function_metrics_dict(metrics),
                    solid_violations=definition.solid_violations,
                    recommended_patterns=definition.recommended_patterns,
                    description=(
                        f"Function '{function.name}' has nesting depth {metrics.max_nesting_depth}, "
                        f"{metrics.boolean_operator_count} boolean operators, and "
                        f"{metrics.conditional_branch_count} branches."
                    ),
                    refactoring_steps=[
                        "Replace complex conditionals with polymorphism or strategy objects.",
                        "Extract guard clauses or helper predicates.",
                        "Document business rules in dedicated specification objects.",
                    ],
                )


def _iter_functions(module: ast.Module) -> Iterable[ast.FunctionDef | ast.AsyncFunctionDef]:
    """Yield functions and methods from the module."""
    for node in ast.walk(module):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node


def _function_metrics_dict(metrics: FunctionMetrics) -> Dict[str, int]:
    return {
        "lines_of_code": metrics.lines_of_code,
        "cyclomatic_complexity": metrics.cyclomatic_complexity,
        "parameter_count": metrics.parameter_count,
        "max_nesting_depth": metrics.max_nesting_depth,
        "boolean_operator_count": metrics.boolean_operator_count,
        "conditional_branch_count": metrics.conditional_branch_count,
        "elif_chain_length": metrics.elif_chain_length,
    }


def _is_long_method(metrics: FunctionMetrics, thresholds: Dict[str, int]) -> bool:
    return (
        metrics.lines_of_code > thresholds["lines_of_code"]
        or metrics.cyclomatic_complexity > thresholds["cyclomatic_complexity"]
        or metrics.max_nesting_depth > thresholds["nesting_depth"]
    )


def _long_method_severity(metrics: FunctionMetrics) -> Severity:
    loc = metrics.lines_of_code
    complexity = metrics.cyclomatic_complexity
    nesting = metrics.max_nesting_depth

    if loc > 100 or complexity > 30 or nesting > 6:
        return Severity.CRITICAL
    if loc > 50 or complexity > 20 or nesting > 5:
        return Severity.HIGH
    if loc > 30 or complexity > 15 or nesting > 4:
        return Severity.MEDIUM
    return Severity.LOW


def _parameter_severity(count: int) -> Severity:
    if count > 10:
        return Severity.CRITICAL
    if count > 7:
        return Severity.HIGH
    if count > 5:
        return Severity.MEDIUM
    return Severity.LOW


def _is_complex_conditional(metrics: FunctionMetrics, thresholds: Dict[str, int]) -> bool:
    return (
        metrics.max_nesting_depth > thresholds["nesting_depth"]
        or metrics.boolean_operator_count > thresholds["boolean_operators"]
        or metrics.conditional_branch_count > thresholds["conditional_branches"]
        or metrics.elif_chain_length > thresholds["elif_chain_length"]
    )


def _conditional_severity(metrics: FunctionMetrics, thresholds: Dict[str, int]) -> Severity:
    depth = metrics.max_nesting_depth
    booleans = metrics.boolean_operator_count
    branches = metrics.conditional_branch_count

    if depth > thresholds["nesting_depth"] + 2 or booleans > 20 or branches > 10:
        return Severity.CRITICAL
    if depth > thresholds["nesting_depth"] + 1 or booleans > 12 or branches > 8:
        return Severity.HIGH
    if depth > thresholds["nesting_depth"] or booleans > 7 or branches > 6:
        return Severity.MEDIUM
    return Severity.LOW


def _location_from_node(filepath: str, node: ast.AST) -> CodeLocation:
    return CodeLocation(
        file=Path(filepath),
        line_start=getattr(node, "lineno", 0),
        line_end=getattr(node, "end_lineno", getattr(node, "lineno", 0)),
        class_name=_enclosing_class(node),
        function_name=getattr(node, "name", None),
    )


def _enclosing_class(node: ast.AST) -> str | None:
    parent = getattr(node, "parent", None)
    while parent is not None:
        if isinstance(parent, ast.ClassDef):
            return parent.name
        parent = getattr(parent, "parent", None)
    return None

