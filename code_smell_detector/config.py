"""Configuration handling for the Code Smell Detector."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional

import yaml


class ConfigurationError(Exception):
    """Raised when configuration cannot be loaded or is invalid."""


DEFAULT_THRESHOLDS: Dict[str, Dict[str, Any]] = {
    "long_method": {
        "lines_of_code": 20,
        "cyclomatic_complexity": 10,
        "nesting_depth": 3,
    },
    "large_class": {
        "lines_of_code": 300,
        "method_count": 20,
        "field_count": 15,
    },
    "long_parameter_list": {
        "parameter_count": 4,
    },
    "duplicated_code": {
        "min_duplicate_lines": 6,
        "similarity_threshold": 0.85,
    },
    "complex_conditional": {
        "nesting_depth": 3,
        "boolean_operators": 5,
        "conditional_branches": 5,
        "elif_chain_length": 4,
    },
}


@dataclass(slots=True)
class DetectorConfig:
    """Configuration model for the Code Smell Detector."""

    thresholds: Dict[str, Dict[str, Any]] = field(
        default_factory=lambda: DEFAULT_THRESHOLDS.copy()
    )
    exclusions: Dict[str, Iterable[str]] = field(
        default_factory=lambda: {
            "paths": ("**/tests/**", "**/__pycache__/**", "**/venv/**"),
            "files": (),
        }
    )
    output_formats: Iterable[str] = field(default_factory=lambda: ("json",))
    output_directory: Path = field(default_factory=lambda: Path("./code_smell_reports"))

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "DetectorConfig":
        """Create configuration from dictionary data."""
        thresholds = _merge_thresholds(raw.get("thresholds"), DEFAULT_THRESHOLDS)
        exclusions = raw.get("exclusions") or {}
        output = raw.get("reporting") or {}

        return cls(
            thresholds=thresholds,
            exclusions={
                "paths": tuple(exclusions.get("paths") or ()),
                "files": tuple(exclusions.get("files") or ()),
            },
            output_formats=tuple(output.get("output_formats") or ("json",)),
            output_directory=Path(output.get("output_directory") or "./code_smell_reports"),
        )

    @classmethod
    def from_yaml(cls, path: str | Path) -> "DetectorConfig":
        """Load configuration from a YAML file."""
        config_path = Path(path)
        if not config_path.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")

        try:
            content = config_path.read_text(encoding="utf-8")
            data = yaml.safe_load(content) or {}
        except yaml.YAMLError as exc:
            msg = f"Unable to parse configuration file {config_path}: {exc}"
            raise ConfigurationError(msg) from exc

        if not isinstance(data, MutableMapping):
            raise ConfigurationError("Configuration must be a mapping at the top level.")

        return cls.from_dict(data)


def _merge_thresholds(
    provided: Optional[Mapping[str, Any]], defaults: Mapping[str, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """Merge provided thresholds with defaults, ensuring every key is present."""
    merged: Dict[str, Dict[str, Any]] = {}
    provided = provided or {}
    for key, default_value in defaults.items():
        custom = provided.get(key) if isinstance(provided, Mapping) else None
        if custom is None:
            merged[key] = dict(default_value)
            continue
        merged[key] = {**default_value, **custom}
    return merged

