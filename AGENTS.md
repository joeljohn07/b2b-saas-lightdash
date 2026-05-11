# AGENTS.md — b2b-saas-lightdash

## What This Project Does
Lightdash BI layer on top of b2b-saas-dbt — dashboards, semantic exposure, agent-ready MCP surface

## Non-Negotiables
1. No secrets in code or workspace files
2. No new dependencies without preinstall security audit
3. TDD for all modules: failing test → smallest fix → green → refactor
4. Conventional commits: feat:, fix:, refactor:, docs:, test:, chore:
5. Keep project independently workable from repo root (tests/run/docs local to repo)

## TDD Default
1. Write failing test first
2. Make the smallest change to pass
3. Refactor while green
4. Repeat in small slices

## Data Backend
- Default: BigQuery (hub analytics pipeline). Contract: `~/Agentic/docs/integrations/bigquery-event-contract.md`
- Pipeline: `~/Agentic/tools/agentic/bigquery-analytics.sh` (provision | ingest | validate)
- Guardrails: partition by date, require_partition_filter, byte cap, dead-letter table. No PII/secrets in BQ.
- Use Postgres only when BQ doesn't fit (relational CRUD, low-latency, offline-first).

## Useful Commands
```
echo 'No test runner configured — add your test command here'
```
