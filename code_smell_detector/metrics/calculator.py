"""Metric calculations for code smell detection."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

from radon.complexity import cc_visit
from radon.metrics import h_visit


@dataclass(slots=True)
class FunctionMetrics:
    """Metrics extracted for a function or method."""

    name: str
    lines_of_code: int
    cyclomatic_complexity: int
    parameter_count: int
    max_nesting_depth: int
    boolean_operator_count: int
    conditional_branch_count: int
    elif_chain_length: int


@dataclass(slots=True)
class ClassMetrics:
    """Metrics extracted for a class definition."""

    name: str
    lines_of_code: int
    method_count: int
    field_count: int
    public_method_count: int


class MetricsCalculator:
    """Utility for computing AST and text-based metrics."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.source_lines = source.splitlines()

    def calculate_function_metrics(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionMetrics:
        """Return metrics for a function or method node."""
        loc = _node_loc(node)
        complexity = self._cyclomatic_complexity(node)
        parameter_count = _parameter_count(node)

        analyzer = _ControlFlowAnalyzer()
        analyzer.visit(node)

        return FunctionMetrics(
            name=node.name,
            lines_of_code=loc,
            cyclomatic_complexity=complexity,
            parameter_count=parameter_count,
            max_nesting_depth=analyzer.max_depth,
            boolean_operator_count=analyzer.boolean_operator_count,
            conditional_branch_count=analyzer.conditional_branch_count,
            elif_chain_length=analyzer.max_elif_chain,
        )

    def calculate_class_metrics(self, node: ast.ClassDef) -> ClassMetrics:
        """Return metrics for a class node."""
        loc = _node_loc(node)
        methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        assignments = [
            n
            for n in node.body
            if isinstance(n, (ast.Assign, ast.AnnAssign))
            and not isinstance(getattr(n, "value", None), ast.Call)
        ]
        public_methods = [m for m in methods if not m.name.startswith("_")]

        return ClassMetrics(
            name=node.name,
            lines_of_code=loc,
            method_count=len(methods),
            field_count=len(assignments),
            public_method_count=len(public_methods),
        )

    def duplicated_code_blocks(self, min_lines: int = 6) -> Dict[Tuple[int, int], int]:
        """
        Detect duplicated blocks using hashing of normalized line windows.

        Returns mapping of (start_line, end_line) to occurrence count for windows
        that appear more than once.
        """
        normalized = [_normalize_line(line) for line in self.source_lines]

        windows = {}
        for idx in range(0, len(normalized) - min_lines + 1):
            window = tuple(normalized[idx : idx + min_lines])
            if all(not line for line in window):
                continue
            windows.setdefault(window, []).append(idx)

        occurrences: Dict[Tuple[int, int], int] = {}
        for positions in windows.values():
            if len(positions) < 2:
                continue
            for pos in positions:
                occurrences[(pos + 1, pos + min_lines)] = len(positions)
        return occurrences

    def _cyclomatic_complexity(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        """Extract cyclomatic complexity using radon."""
        complexities = {(block.name, block.lineno): block.complexity for block in cc_visit(self.source)}
        key = (node.name, getattr(node, "lineno", 0))
        return complexities.get(key, 1)


def _node_loc(node: ast.AST) -> int:
    """Return physical lines of code for a node."""
    if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
        return int(node.end_lineno) - int(node.lineno) + 1
    return 0


def _parameter_count(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Return total parameter count for a function node."""
    args = node.args
    total = len(args.args) + len(args.kwonlyargs)
    if args.vararg:
        total += 1
    if args.kwarg:
        total += 1
    # Remove implicit self/cls for methods
    if args.args and isinstance(node.parent, ast.ClassDef):
        total -= 1
    return max(total, 0)


class _ControlFlowAnalyzer(ast.NodeVisitor):
    """Collect conditional and boolean metrics."""

    def __init__(self) -> None:
        self.current_depth = 0
        self.max_depth = 0
        self.boolean_operator_count = 0
        self.conditional_branch_count = 0
        self.max_elif_chain = 0

    def generic_visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            child.parent = node  # type: ignore[attr-defined]
            self.visit(child)

    def visit_If(self, node: ast.If) -> None:
        self.conditional_branch_count += 1
        self._record_depth(node)
        self.boolean_operator_count += _count_boolean_ops(node.test)
        self.max_elif_chain = max(self.max_elif_chain, _elif_chain_length(node))
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_For(self, node: ast.For) -> None:
        self._record_depth(node)
        self.generic_visit(node)
        self.current_depth -= 1

    visit_While = visit_For
    visit_With = visit_For
    visit_Try = visit_For

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.boolean_operator_count += len(node.values) - 1
        self.generic_visit(node)

    def _record_depth(self, node: ast.AST) -> None:
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)


def _elif_chain_length(node: ast.If) -> int:
    """Return length of elif chain for a given if statement."""
    length = 0
    current = node
    while current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
        length += 1
        current = current.orelse[0]
    return length


def _count_boolean_ops(node: ast.AST) -> int:
    """Count boolean operators in a condition expression."""
    counter = 0
    for child in ast.walk(node):
        if isinstance(child, ast.BoolOp):
            counter += len(child.values) - 1
    return counter


def _normalize_line(line: str) -> str:
    """Normalize source line for duplication comparison."""
    return line.strip()


def attach_parents(tree: ast.AST) -> None:
    """Attach parent references to AST nodes for easier traversal."""
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent  # type: ignore[attr-defined]


def parse_python_file(path: Path) -> Tuple[ast.Module, str]:
    """Parse a Python file and return the AST module alongside the source code."""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    attach_parents(tree)
    return tree, source


def iter_py_files(root: Path, exclusions: Iterable[str]) -> Iterable[Path]:
    """Yield Python files under root respecting exclusion patterns."""
    from pathspec import PathSpec

    spec = PathSpec.from_lines("gitwildmatch", exclusions)

    for path in root.rglob("*.py"):
        relative = path.relative_to(root)
        if spec.match_file(str(relative)):
            continue
        yield path


def halstead_volume(source: str) -> float:
    """Return Halstead volume using radon metrics."""
    analyzed = h_visit(source)
    if not analyzed:
        return 0.0
    return float(sum(item.volume for item in analyzed))

