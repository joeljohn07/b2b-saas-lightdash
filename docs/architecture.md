# Architecture

How this repo fits with `b2b-saas-dbt` and the planned `analytics-agent`.

## Position in the Stack

```
        ┌────────────────────────────────────────────────────────────┐
        │                     BigQuery (raw + dbt outputs)            │
        └─────────────────▲───────────────────────▲──────────────────┘
                          │                       │
                ┌─────────┴─────────┐   ┌─────────┴───────────┐
                │   b2b-saas-dbt    │   │  b2b-saas-lightdash │
                │   ───────────     │   │  ──────────────     │
                │   staging ─►      │   │   reads dbt         │
                │   intermediate ─► │   │   manifest +        │
                │   marts (star)    │   │   meta annotations  │
                │   contracts +     │   │                     │
                │   tests           │   │   explores +        │
                │                   │   │   dashboards +      │
                │   metric          │   │   MCP server        │
                │   definitions     │   │                     │
                └───────┬───────────┘   └──────────┬──────────┘
                        │                          │
                        └──────────┬───────────────┘
                                   │
                          ┌────────▼─────────┐
                          │ analytics-agent  │  (planned)
                          │  Q&A via MCP     │
                          └──────────────────┘
```

## What Each Layer Owns

### `b2b-saas-dbt`

- All metric definitions, expressed as columns in `fct_` / `dim_` / `bridge_` models.
- Doc tags for every column.
- The `meta:` configuration that Lightdash reads: `owner`, `pii`, `sla`, `tier`, plus the per-column `meta.dimension` / `meta.metric` annotations that will be added as the foundation phase ships (#393).
- Source-of-truth metric contract in `docs/metric-contract.md`.

### `b2b-saas-lightdash` (this repo)

- Lightdash project config (`lightdash.yml`) pointing at the sibling dbt repo.
- Dashboards built from the explores Lightdash auto-generates from dbt models.
- Lightdash-only measures (rare — see CLAUDE.md for when these are allowed).
- The MCP server (planned, #410) that exposes the same semantic layer to agents.
- Verified-answers eval set (#411) for testing agent behaviour.

### `analytics-agent` (not yet started)

- Conversational Q&A surface backed by three MCPs: BigQuery (raw queries), dbt (lineage / docs), Lightdash (metrics).
- Will live in its own repo when work begins.

## Data Flow

A user asks "what's our 4-week activation rate by acquisition channel?"

1. **Lightdash** receives the question via UI or MCP.
2. **Lightdash** identifies the explore — joins `fct_activations` ↔ `fct_signups` on `user_key`, with `dim_channels` as a dimension.
3. **Lightdash** generates a SQL query against the dbt marts in BigQuery.
4. **BigQuery** runs the query against `fct_signups`, `fct_activations`, `dim_channels` — all materialised tables built by dbt.
5. Result returns to Lightdash, then to the UI or MCP caller.

The metric definition itself (what counts as an activation, the activation window, the acquisition-channel attribution rule) is all baked into the dbt models. Lightdash assembles and serves; it does not redefine.

## What This Repo Doesn't Do

- It does not query raw sources. Lightdash reads only `fct_` / `dim_` / `bridge_` and (where exposed) `agg_` / `rpt_` / `mart_` models.
- It does not materialise data — that's dbt's job.
- It does not own metric semantics — those live in `b2b-saas-dbt/docs/metric-contract.md`.

## Cross-Repo Coordination

When dbt changes break a downstream dashboard:

1. The dbt repo's `contract.enforced: true` on `fct_`/`dim_`/`bridge_` models catches schema-shape breaks at the dbt side.
2. The exposures declared in `b2b-saas-dbt/models/marts/exposures.yml` document the consumer dependency.
3. A breaking change in dbt should ship together with the corresponding Lightdash update — same workday, ideally same PR pair.

## See Also

- [`README.md`](../README.md) — repo intro and current status.
- [`CLAUDE.md`](../CLAUDE.md) — project rules.
- [`b2b-saas-dbt` architecture](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/architecture.md)
- [`b2b-saas-dbt` metric contract](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/metric-contract.md)
- [`b2b-saas-dbt` data boundary](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/data-boundary.md)
