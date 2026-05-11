# Decision Log — b2b-saas-lightdash

## 2026-05-11: Initial setup

- Project created and scaffolded via `~/Agentic/tools/agentic/new-project.sh`.
- Description: Lightdash BI layer on top of b2b-saas-dbt — dashboards, semantic exposure, agent-ready MCP surface.
- Repo: https://github.com/joeljohn07/b2b-saas-lightdash (public).
- Registered as a submodule in `joeljohn07/agentic-hub`.

## 2026-05-11: Two-repo split (dbt + Lightdash separate)

**Why:** Metric definitions belong with the SQL that produces them; consumption (dashboards, MCP) belongs with the BI tool that serves them. Keeping them in separate repos makes the dbt project independently adoptable (a team using Looker or Metabase could take the dbt repo without this one), and prevents Lightdash-specific concerns from leaking into the data foundation.

**Alternatives considered:**
- Single mono-repo with `lightdash/` subdirectory — rejected: muddies the contract boundary, CI becomes harder to scope per-component.
- dbt Cloud's built-in semantic layer with no separate Lightdash project — rejected: portfolio specifically wants an OSS, self-hostable BI surface that exposes an MCP server.

## 2026-05-11: dbt is a sibling directory, not a vendored dependency

**Why:** `lightdash.yml` points at `../b2b-saas-dbt` relative to this repo's root. Developers clone both repos as siblings under `~/Agentic/projects/`. This avoids vendoring or git-submoduling the dbt project here, which would create version-pinning headaches and duplicate disk.

**Implications:**
- CI for this repo (planned) must check out the sibling dbt repo before invoking Lightdash commands.
- Local dev requires both repos cloned; documented in README.

## 2026-05-11: Metric authoring stays in dbt

**Why:** Every metric exposed in a Lightdash dashboard resolves to a column in a dbt mart model. Lightdash uses `meta.dimension` and `meta.metric` annotations on those columns to surface them; the SQL itself is in dbt.

**Implications:**
- This repo never contains a SQL definition of a metric.
- Lightdash-only measures (e.g., runtime user-pivoted aggregations) are allowed but described in Lightdash YAML, with a note pointing to why they couldn't live in dbt.
- Pass-through descriptions are inherited automatically — never re-author.
