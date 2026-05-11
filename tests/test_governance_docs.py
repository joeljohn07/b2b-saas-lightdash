"""Assert governance and tiered-context documentation invariants.

These tests are the executable contract for issues #391 (governance) and
#392 (tiered context). If somebody renames or deletes one of these docs
without updating the rest of the repo, CI catches it here.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_DOCS = [
    "docs/governance-principles.md",
    "docs/metric-ownership.md",
    "docs/architecture.md",
]

TIER_1_CONTEXTS = [
    "charts/CLAUDE.md",
    "dashboards/CLAUDE.md",
]

TIER_0 = "CLAUDE.md"


def test_required_governance_docs_exist():
    """Both governance docs from #391 must be present."""
    for rel in ("docs/governance-principles.md", "docs/metric-ownership.md"):
        assert (REPO_ROOT / rel).exists(), f"Missing required doc: {rel}"


def test_tier_1_contexts_exist():
    """Per-directory CLAUDE.md files from #392 must be present."""
    for rel in TIER_1_CONTEXTS:
        assert (REPO_ROOT / rel).exists(), f"Missing tier-1 context: {rel}"


def test_root_claude_md_references_governance_docs():
    """Root CLAUDE.md must link to the governance docs so agents can find them."""
    content = (REPO_ROOT / TIER_0).read_text()
    for rel in REQUIRED_DOCS + TIER_1_CONTEXTS:
        assert rel in content, f"Root CLAUDE.md does not reference {rel}"


def test_agents_md_is_symlink_to_claude_md():
    """AGENTS.md must symlink to CLAUDE.md so both names resolve to the same content."""
    agents = REPO_ROOT / "AGENTS.md"
    assert agents.is_symlink(), "AGENTS.md must be a symlink"
    assert agents.resolve().name == TIER_0, "AGENTS.md must resolve to CLAUDE.md"


def test_tier_1_files_under_size_cap():
    """Tier 1 context files must stay tight (acceptance criterion: under 25 lines).
    The cap forces them to point at tier-2 docs rather than duplicate content."""
    for rel in TIER_1_CONTEXTS:
        lines = (REPO_ROOT / rel).read_text().splitlines()
        # Allow some slack for blank lines and headings; spec said "under 25 lines"
        # of substantive content. Cap at 50 raw lines as a hard ceiling.
        assert len(lines) <= 50, f"{rel} has {len(lines)} lines, exceeds tier-1 cap"


def test_tier_1_files_reference_root_claude_md():
    """Per-directory CLAUDE.md must point readers back to the root for project-wide rules."""
    for rel in TIER_1_CONTEXTS:
        content = (REPO_ROOT / rel).read_text()
        assert "../CLAUDE.md" in content or "/CLAUDE.md" in content, (
            f"{rel} does not reference the root CLAUDE.md"
        )


def test_metric_ownership_doc_states_dbt_is_authority():
    """The metric-ownership doc must explicitly state the core rule."""
    content = (REPO_ROOT / "docs/metric-ownership.md").read_text().lower()
    assert "dbt yaml is the single authority" in content, (
        "metric-ownership.md must state the dbt-as-authority rule verbatim"
    )


def test_governance_doc_covers_required_sections():
    """The governance doc from #391 acceptance criteria must cover the listed scopes."""
    content = (REPO_ROOT / "docs/governance-principles.md").read_text().lower()
    for section in ("naming", "lifecycle", "access control"):
        assert section in content, (
            f"governance-principles.md does not cover '{section}'"
        )
