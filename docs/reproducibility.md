# Reproducibility

## Environment

Create and activate a Python environment compatible with the project metadata, install the package and test dependencies, then run:

```bash
pytest
```

## Core validation

```bash
python scripts/run_aa.py
python scripts/run_workflow.py
```

## Research experiments

```bash
python scripts/run_sensitivity.py
python scripts/run_robustness.py
python scripts/run_risk_adjustment.py
python scripts/run_delay_sensitivity.py
python scripts/run_joint_surface.py
```

## Reporting

```bash
python scripts/build_research_report.py
python scripts/build_publication_outputs.py
```

Generated analysis artifacts are written beneath `results/`, which is intentionally ignored by Git.

## Portfolio check

```bash
python scripts/final_check.py
```

The final check verifies the expected repository structure and runs the full pytest suite.
