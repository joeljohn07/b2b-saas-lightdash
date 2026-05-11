# Charts — Tier 1 Context

Rules for individual chart definitions. Read [`/CLAUDE.md`](../CLAUDE.md) first for project-level rules; this file applies on top of those.

## Naming

`<domain>_<metric>_<viz-type>` — e.g., `funnel_conversion_rate_line`, `revenue_mrr_movement_bar`. Full vocabulary in [`/docs/governance-principles.md`](../docs/governance-principles.md).

## Required Metadata

Every saved chart carries:

- A name following the convention above.
- A one-line description that states what the chart shows and (briefly) why it matters.
- An owner — `analytics` for this single-author repo; team or person in a real deployment.
- A space — one of `Product`, `Revenue`, `Growth`, `Support`, `Executive`. Never "Personal Space" for charts that anybody else will see.

## When to Create vs Reuse

Before saving a new chart, check whether an existing chart already answers the same question with a different visualisation. Prefer:

1. **Reusing an existing chart** at a different time window or filter.
2. **Switching the viz on an existing chart** if the data is right but the visual is wrong.
3. **Creating a new chart** only when the underlying query or grain genuinely differs.

A repo with three "MRR by month" charts that all show the same data is a maintenance burden.

## Never

- Define a metric in custom SQL that already exists in dbt — see [`/docs/metric-ownership.md`](../docs/metric-ownership.md).
- Save a chart in Personal Space and link it from a dashboard.
- Ship a chart whose title doesn't match the columns it shows.
