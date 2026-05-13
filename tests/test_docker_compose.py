"""Validate docker-compose.yml structure and the .env.example contract.

Doesn't require Docker to be running — only parses the YAML and asserts
contract invariants that a downstream reader (or a deployment script) can
depend on.
"""
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"
ENV_EXAMPLE_PATH = REPO_ROOT / ".env.example"


def _compose():
    assert COMPOSE_PATH.exists(), f"docker-compose.yml not found at {COMPOSE_PATH}"
    return yaml.safe_load(COMPOSE_PATH.read_text())


def _env_example_keys():
    assert ENV_EXAMPLE_PATH.exists(), f".env.example not found at {ENV_EXAMPLE_PATH}"
    keys = set()
    for line in ENV_EXAMPLE_PATH.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            keys.add(line.split("=", 1)[0])
    return keys


def test_compose_parses_as_yaml():
    data = _compose()
    assert isinstance(data, dict)


def test_compose_defines_required_services():
    """The stack needs the Lightdash app, its Postgres backend, MinIO for
    S3-compatible result storage, and a one-shot init container that
    creates the results bucket."""
    data = _compose()
    services = data.get("services", {})
    for required in ("lightdash", "db", "minio", "minio-init"):
        assert required in services, f"docker-compose.yml missing service: {required}"


def test_lightdash_s3_env_points_to_minio():
    """Lightdash 0.2914+ needs S3-compatible storage for BigQuery result
    pagination. Without these env vars, queries succeed but result rendering
    errors with: Native pagination not supported. Please configure S3 Storage."""
    data = _compose()
    env = data["services"]["lightdash"].get("environment", {})
    assert env.get("S3_ENDPOINT") == "http://minio:9000", (
        f"S3_ENDPOINT must point to in-network minio (got '{env.get('S3_ENDPOINT')}')"
    )
    assert env.get("S3_BUCKET") == "lightdash-results", (
        f"S3_BUCKET must be lightdash-results (got '{env.get('S3_BUCKET')}')"
    )
    assert env.get("S3_FORCE_PATH_STYLE") == "true", (
        "S3_FORCE_PATH_STYLE must be true for MinIO"
    )
    # The public endpoint is required for presigned URLs to work in the browser
    # (the in-network http://minio:9000 isn't reachable from outside Docker).
    assert env.get("S3_PUBLIC_ENDPOINT") == "http://localhost:9000", (
        "S3_PUBLIC_ENDPOINT must point at localhost so browser-facing presigned URLs resolve"
    )


def test_lightdash_service_uses_official_image():
    data = _compose()
    image = data["services"]["lightdash"].get("image", "")
    assert image.startswith("lightdash/lightdash"), (
        f"lightdash service must use the official lightdash/lightdash image, got '{image}'"
    )


def test_lightdash_platform_pinned_to_amd64():
    """The official Lightdash image is amd64-only. Pinning the platform forces
    QEMU emulation on Apple Silicon — slow but functional. Without this, the
    pull fails with `no matching manifest for linux/arm64`. Drop the pin on
    amd64 hosts for native speed."""
    data = _compose()
    platform = data["services"]["lightdash"].get("platform", "")
    assert platform == "linux/amd64", (
        f"lightdash service must pin platform to linux/amd64 (got '{platform}')"
    )


def test_dbt_log_and_target_paths_redirected():
    """The dbt subprocess Lightdash spawns wants to write logs and a target/
    directory. The project mount is read-only (deliberately), so logs and
    target must be redirected to writable /tmp paths. Without this, the
    Lightdash 'Test & deploy' step fails with:
        OSError: [Errno 30] Read-only file system: '/usr/app/dbt/logs/dbt.log'"""
    data = _compose()
    env = data["services"]["lightdash"].get("environment", {})
    assert env.get("DBT_LOG_PATH", "").startswith("/tmp/"), (
        f"DBT_LOG_PATH must redirect to /tmp/... (got '{env.get('DBT_LOG_PATH')}')"
    )
    assert env.get("DBT_TARGET_PATH", "").startswith("/tmp/"), (
        f"DBT_TARGET_PATH must redirect to /tmp/... (got '{env.get('DBT_TARGET_PATH')}')"
    )


def test_lightdash_depends_on_db_with_healthcheck():
    """Lightdash crashes if it tries to connect to Postgres before Postgres is ready,
    so depends_on must include a service_healthy condition."""
    data = _compose()
    depends = data["services"]["lightdash"].get("depends_on", {})
    # depends_on can be a list or a dict — the healthcheck-aware form is a dict
    assert isinstance(depends, dict), "lightdash depends_on must be a dict (healthcheck form)"
    assert depends.get("db", {}).get("condition") == "service_healthy", (
        "lightdash must wait for db with service_healthy condition"
    )


def test_db_service_has_healthcheck():
    data = _compose()
    db = data["services"]["db"]
    assert "healthcheck" in db, "db service must declare a healthcheck"
    # The pg_isready test is what makes depends_on: service_healthy meaningful
    test = db["healthcheck"]["test"]
    test_str = " ".join(test) if isinstance(test, list) else str(test)
    assert "pg_isready" in test_str, "db healthcheck should use pg_isready"


def test_dbt_project_mounted_as_sibling():
    """The Lightdash container expects the dbt project at /usr/app/dbt.
    The mount source must be the sibling b2b-saas-dbt directory.

    Mount is read-write (not :ro) because `dbt deps` needs to refresh
    dbt_packages/ inside the project. Run artifacts (logs, target/) are
    redirected to /tmp via DBT_LOG_PATH/DBT_TARGET_PATH env vars to keep
    the host working tree clean — see test_dbt_log_and_target_paths_redirected."""
    data = _compose()
    volumes = data["services"]["lightdash"].get("volumes", [])
    dbt_mount = next((v for v in volumes if "/usr/app/dbt" in v), None)
    assert dbt_mount is not None, "lightdash must mount the dbt project at /usr/app/dbt"
    assert dbt_mount.startswith("../b2b-saas-dbt"), (
        f"dbt mount source must be the sibling repo, got '{dbt_mount}'"
    )


def test_env_example_documents_required_vars():
    """Every env var Lightdash reads from .env must appear in .env.example."""
    required = {
        "LIGHTDASH_SECRET",
        "PGUSER",
        "PGPASSWORD",
        "PGDATABASE",
        "SITE_URL",
        "LIGHTDASH_PORT",
    }
    documented = _env_example_keys()
    missing = required - documented
    assert not missing, f".env.example missing required keys: {missing}"


def test_env_example_does_not_contain_real_secrets():
    """The example file must use placeholder values, not real credentials."""
    content = ENV_EXAMPLE_PATH.read_text()
    # Placeholder strings we expect
    assert "replace-with-random-64-char-hex-string" in content
    assert "replace-with-strong-password" in content
    # Negative checks: catch common patterns of real keys leaking into the template
    assert "BEGIN PRIVATE KEY" not in content
    assert "BEGIN RSA PRIVATE KEY" not in content


def test_setup_doc_exists_and_mentions_first_steps():
    setup = REPO_ROOT / "docs/setup.md"
    assert setup.exists(), "docs/setup.md must exist"
    content = setup.read_text().lower()
    # Sanity-check the doc actually walks setup
    for keyword in ("docker compose", "lightdash_secret", "gcloud"):
        assert keyword in content, f"docs/setup.md must mention '{keyword}'"
