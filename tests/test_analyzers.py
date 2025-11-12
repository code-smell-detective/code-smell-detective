from __future__ import annotations

import shutil
from pathlib import Path

from code_smell_detector.analyzers.class_level import LargeClassAnalyzer
from code_smell_detector.analyzers.duplication import DuplicatedCodeAnalyzer
from code_smell_detector.analyzers.method_level import (
    ComplexConditionalAnalyzer,
    LongMethodAnalyzer,
    LongParameterListAnalyzer,
)
from code_smell_detector.config import DetectorConfig
from code_smell_detector.core import CodeSmellDetector
from code_smell_detector.metrics.calculator import MetricsCalculator, parse_python_file


SAMPLE_FILE = Path(__file__).resolve().parents[1] / "code_smell_detector" / "samples" / "problematic_module.py"


def load_sample_module():
    module, source = parse_python_file(SAMPLE_FILE)
    calculator = MetricsCalculator(source)
    config = DetectorConfig()
    return module, calculator, config


def test_long_method_analyzer_detects_smell():
    module, calculator, config = load_sample_module()
    analyzer = LongMethodAnalyzer()
    smells = analyzer.analyze(module, str(SAMPLE_FILE), calculator, config)
    assert any(smell.smell_type == "Long Method" for smell in smells)


def test_long_parameter_list_analyzer_detects_smell():
    module, calculator, config = load_sample_module()
    analyzer = LongParameterListAnalyzer()
    smells = analyzer.analyze(module, str(SAMPLE_FILE), calculator, config)
    assert any(smell.smell_type == "Long Parameter List" for smell in smells)


def test_complex_conditional_analyzer_detects_smell():
    module, calculator, config = load_sample_module()
    analyzer = ComplexConditionalAnalyzer()
    smells = analyzer.analyze(module, str(SAMPLE_FILE), calculator, config)
    assert any(smell.smell_type == "Complex Conditional" for smell in smells)


def test_large_class_analyzer_detects_smell():
    module, calculator, config = load_sample_module()
    analyzer = LargeClassAnalyzer()
    smells = analyzer.analyze(module, str(SAMPLE_FILE), calculator, config)
    assert any(smell.smell_type == "Large Class" for smell in smells)


def test_duplicated_code_analyzer_detects_smell():
    module, calculator, config = load_sample_module()
    analyzer = DuplicatedCodeAnalyzer()
    smells = analyzer.analyze(module, str(SAMPLE_FILE), calculator, config)
    assert any(smell.smell_type == "Duplicated Code" for smell in smells)


def test_detector_generates_report(tmp_path: Path):
    sample_dir = tmp_path / "codebase"
    sample_dir.mkdir()
    shutil.copy(SAMPLE_FILE, sample_dir / "problematic_module.py")

    detector = CodeSmellDetector()
    report = detector.analyze_codebase(sample_dir)

    smell_types = {smell.smell_type for smell in report.smells}
    expected = {
        "Long Method",
        "Long Parameter List",
        "Complex Conditional",
        "Large Class",
        "Duplicated Code",
    }

    assert expected.issubset(smell_types)
    assert report.health_score <= 100

