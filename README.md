# b2b-saas-lightdash

The BI consumption layer for the [b2b-saas-dbt](https://github.com/joeljohn07/b2b-saas-dbt) analytics project.

This is the second of three repos in the same fictional B2B SaaS analytics stack:

| Repo | Role | Status |
|---|---|---|
| [`b2b-saas-dbt`](https://github.com/joeljohn07/b2b-saas-dbt) | Data foundation — staging, intermediate, marts in a Kimball star schema on BigQuery | **v0.1.0 shipped** ([live docs](https://joeljohn07.github.io/b2b-saas-dbt/)) |
| `b2b-saas-lightdash` (this repo) | BI consumption — Lightdash explores, dashboards, MCP surface | **Scaffold** |
| `analytics-agent` (planned) | Agentic Q&A over BigQuery + dbt + Lightdash | Not yet started |

## Why a Separate Repo

The metric contract — what an "active user" or "signup" means — lives in `b2b-saas-dbt`. This repo is where those metrics become *consumable*: explores configured for self-service analysis, dashboards built for specific business questions, and a Lightdash MCP server that lets agents answer metric questions without re-deriving them.

Keeping consumption separate from definition is the same boundary every healthy analytics org draws. It also means the dbt project can be reviewed and adopted independently of the BI choice — a team that uses Looker, Metabase, or Cube can take the dbt repo and skip this one.

## Why Lightdash

- **dbt-native.** Lightdash reads dimensions and metrics directly from dbt model `meta:` configuration. Metric definitions stay in the dbt repo where the SQL lives; Lightdash adds the consumption layer without forking definitions.
- **Open-source self-hostable.** Docker Compose runs the whole stack locally — no SaaS dependency for the portfolio.
- **MCP server first-class.** Lightdash exposes an MCP server that answers metric questions over the same semantic layer that powers the dashboards. Agents and dashboards share one source of truth.

## What's Here

- **Self-hostable Docker stack** — `docker-compose.yml` runs Lightdash + a Postgres metadata backend. See [`docs/setup.md`](docs/setup.md) for the cold-start walkthrough.
- **Governance** — chart and dashboard lifecycle, naming conventions, anti-patterns: [`docs/governance-principles.md`](docs/governance-principles.md).
- **Metric ownership** — the dbt-as-single-authority rule and what (rarely) lives in Lightdash: [`docs/metric-ownership.md`](docs/metric-ownership.md).
- **Architecture** — position in the 3-repo stack, data flow, what this repo doesn't do: [`docs/architecture.md`](docs/architecture.md).
- **Tiered context** — root [`CLAUDE.md`](CLAUDE.md) for project-wide rules, per-directory [`charts/CLAUDE.md`](charts/CLAUDE.md) and [`dashboards/CLAUDE.md`](dashboards/CLAUDE.md) for tier-1 rules.
- **Tests** — 22 contract tests covering config, governance, and compose structure.

## Quick Start

```bash
cp .env.example .env       # then edit secrets
docker compose up -d
open http://localhost:8080
```

Full setup including BigQuery auth and connecting to the sibling dbt project: [`docs/setup.md`](docs/setup.md).

## What's Coming

Tracked in `agentic-hub` orchestration tickets:

| Ticket | Scope |
|---|---|
| #390 | Docker Compose + environment config |
| #391 | Governance principles |
| #392 | AGENTS.md / tiered context (foundation) |
| #393 | Lightdash table + join configuration on dbt models |
| #402 | Product funnel dashboard |
| #403 | Retention dashboard |
| #404 | Attribution dashboard |
| #405 | Executive summary dashboard |
| #410 | Lightdash MCP server setup |
| #411 | Verified-answers eval ground truth |
| #412 | Lightdash agent skills |

## See Also

- [b2b-saas-dbt — architecture](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/architecture.md)
- [b2b-saas-dbt — metric contract](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/metric-contract.md)
- [b2b-saas-dbt — live dbt docs](https://joeljohn07.github.io/b2b-saas-dbt/)
