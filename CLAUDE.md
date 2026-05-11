# b2b-saas-lightdash — Project Rules

## What This Is

The BI consumption layer for [`b2b-saas-dbt`](https://github.com/joeljohn07/b2b-saas-dbt). Lightdash project config, explores, dashboards, and the MCP surface that powers agent Q&A.

This repo **consumes** the dbt project's marts. It does not redefine metrics — every metric in this repo resolves to a definition in `b2b-saas-dbt/docs/metric-contract.md`.

## Two-Repo Architecture

Read [`b2b-saas-dbt/docs/architecture.md`](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/architecture.md) first. Then:

- **Metric definitions** — owned by `b2b-saas-dbt`, expressed as columns in mart models with `meta:` annotations consumed by Lightdash. Never duplicate them here.
- **Lightdash-only measures** (runtime aggregations, custom SQL measures) — defined in Lightdash YAML in this repo. Use this only for things that genuinely cannot be modelled in dbt (e.g., user-pivoted calculations).
- **Pass-through descriptions** — inherited from dbt's doc tags automatically. Never re-author.

## Non-Negotiables

- No secrets in code, chat, or committed files. The pre-commit secret scan blocks common patterns; never bypass with `--no-verify`.
- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`.
- Pre-commit hook active: `git config core.hooksPath .githooks` (already set).
- Pre-install security audit required before adding any new dependency.
- Project must be independently workable from its own repo root (no hub-only execution dependency).

## Doc-Block Discipline (mirrored from dbt)

When this repo adds Lightdash-specific descriptions:

- Use Lightdash's own `meta.description` fields, but keep them factual and short.
- If a description duplicates a dbt doc tag, **delete it** and let Lightdash inherit.
- If a Lightdash-only measure needs description, author it once where the measure is defined.

## Connection to the dbt Project

The Lightdash project points at the dbt repo via `lightdash.yml`. The dbt project is **a peer**, not a vendored dependency. Local dev:

```bash
# In ~/Agentic/projects:
ls b2b-saas-dbt b2b-saas-lightdash    # both must exist as siblings
```

## Git

- **Never commit directly to `main`.** Create a feature branch: `git checkout -b cc/<type>/<description>`.
- Push branches with `git push -u origin HEAD`, then `gh pr create`.
- Squash merge via `gh pr merge --squash`.
- Pre-push hook blocks direct pushes to main.

## Status

This repo is at scaffold stage. The orchestration tickets (#390–#393 foundation, #402–#405 dashboards, #410–#412 agent surface) drive the build-out — see README for the full list. Work them in numeric order unless a dependency is explicitly noted.
