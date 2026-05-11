"""Validate lightdash.yml structure and required keys.

This test runs without a live Lightdash instance — it only verifies that
the config file is parseable and asserts the contract that downstream CI
and human reviewers depend on.
"""
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = REPO_ROOT / "lightdash.yml"


def _config():
    """Parse the project's lightdash.yml. Fails the test if the file is missing or malformed."""
    assert CONFIG_PATH.exists(), f"lightdash.yml not found at {CONFIG_PATH}"
    return yaml.safe_load(CONFIG_PATH.read_text())


def test_config_parses_as_yaml():
    """lightdash.yml must be valid YAML."""
    data = _config()
    assert isinstance(data, dict), "lightdash.yml must be a mapping at the top level"


def test_config_has_required_top_level_keys():
    """The Lightdash project config requires version, project_dir, warehouse, and target."""
    data = _config()
    for key in ("version", "project_dir", "warehouse", "target"):
        assert key in data, f"lightdash.yml missing required top-level key: {key}"


def test_warehouse_block_is_bigquery():
    """This project is BigQuery-only. Catching a misconfigured warehouse type early
    prevents wasted Lightdash startup time and confusing error messages downstream."""
    data = _config()
    assert data["warehouse"]["type"] == "bigquery", "warehouse.type must be 'bigquery'"


def test_project_dir_points_to_sibling_dbt_repo():
    """lightdash.yml points at the sibling b2b-saas-dbt project via a relative path.
    See decisions.md (2026-05-11 dbt-as-sibling entry) for rationale."""
    data = _config()
    assert data["project_dir"] == "../b2b-saas-dbt", (
        "project_dir must be '../b2b-saas-dbt' — see decisions.md for rationale"
    )


def test_project_dir_relative_path_resolves():
    """The resolved sibling path should match the expected layout. Doesn't require
    the sibling to actually exist (CI may not check it out), just that the path
    resolution itself works."""
    data = _config()
    resolved = (REPO_ROOT / data["project_dir"]).resolve()
    assert resolved.name == "b2b-saas-dbt"
