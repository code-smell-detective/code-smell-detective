"""Command line interface for the Code Smell Detector."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import click

from ..config import DetectorConfig, ConfigurationError
from ..core import CodeSmellDetector
from ..reporting.json_reporter import JsonReporter


@click.group()
def app() -> None:
    """Code Smell Detector CLI."""


@app.command("analyze")
@click.argument("codebase_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to configuration YAML file.",
)
@click.option(
    "--format",
    "formats",
    default="json",
    help="Comma-separated list of output formats (json).",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Directory to write reports to (defaults to configuration value).",
)
def analyze_command(
    codebase_path: Path,
    config_path: Optional[Path],
    formats: str,
    output_dir: Optional[Path],
) -> None:
    """Analyze a Python codebase for code smells."""
    detector, config = _create_detector(config_path)
    report = detector.analyze_codebase(codebase_path)

    output_formats = [fmt.strip() for fmt in formats.split(",") if fmt.strip()]
    output_directory = output_dir or config.output_directory

    if "json" in output_formats:
        reporter = JsonReporter()
        reporter.write(report, Path(output_directory) / "analysis-report.json")
        click.echo(f"JSON report written to {output_directory}/analysis-report.json")

    click.echo(f"Health Score: {report.health_score}/100")
    click.echo(f"Detected smells: {len(report.smells)}")


@app.command("health-score")
@click.argument("codebase_path", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to configuration YAML file.",
)
def health_score_command(codebase_path: Path, config_path: Optional[Path]) -> None:
    """Calculate health score without generating reports."""
    detector, _ = _create_detector(config_path)
    report = detector.analyze_codebase(codebase_path)
    click.echo(f"{report.health_score}/100")


def _create_detector(config_path: Optional[Path]) -> tuple[CodeSmellDetector, DetectorConfig]:
    if config_path:
        try:
            config = DetectorConfig.from_yaml(config_path)
        except ConfigurationError as exc:
            raise click.ClickException(str(exc)) from exc
    else:
        config = DetectorConfig()

    detector = CodeSmellDetector(config)
    return detector, config

