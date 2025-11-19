# Code Smell Detective

<img width="1536" height="1024" alt="Image" src="https://github.com/user-attachments/assets/c7704d08-beb5-4550-b15e-f6605955467c" />
Code Smell Detective is a Python application that analyzes a codebase and detects code smells
following the specification in `CODE_SMELL_FRAMEWORK.md` (which is outside of this repository). It provides static analysis, severity
assessment, SOLID principle mapping, and actionable reporting for the Phase 1 (MVP) scope.

## Features

- AST-based parsing of Python source files
- Core analyzers for:
  - Long Method
  - Long Parameter List
  - Complex Conditional
  - Large Class
  - Duplicated Code
- Configurable thresholds via YAML
- JSON reporting and health score calculation
- Command-line interface

## Getting Started

```bash
pip install -e .
```

Run the analyzer against a codebase:

```bash
code-smell-detector analyze ./examples --config code_smell_detector/samples/code_smell_config.yaml

# or analyze your own project
code-smell-detector analyze /path/to/python/project --config code_smell_detector/samples/code_smell_config.yaml
```

Generate only the health score:

```bash
code-smell-detector health-score ./examples

# or calculate the score for your own project
code-smell-detector health-score /path/to/python/project
```

Reports are written to `./code_smell_reports/analysis-report.json` by default.

## Running Tests

```bash
pip install -e ".[dev]"
pytest
```

## Project Structure

- `code_smell_detector/` – application source code
  - `analyzers/` – smell analyzers
  - `metrics/` – metric calculations
  - `reporting/` – report generators
  - `cli/` – command-line interface
  - `samples/` – sample configuration and code
- `examples/` – ready-to-analyze sample codebases
- `tests/` – unit tests

## Next Steps

Future enhancements (Phase 2+) include richer metrics, additional smell detectors, HTML/Markdown
reports, health score weighting configuration, and integration with version control history.
