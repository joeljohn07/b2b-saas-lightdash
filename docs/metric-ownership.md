# Metric Ownership

Where each metric in the Lightdash project resolves to its source of truth. The rule has one sentence: **dbt YAML is the single authority for metric definitions.** Everything else is detail.

## The Rule

Every metric exposed in a Lightdash explore or dashboard maps to exactly one of:

1. **A column on a dbt mart model** with `meta.metric` annotation. The SQL that produces the number lives in the dbt repo; Lightdash surfaces it.
2. **A Lightdash custom measure** that aggregates a dbt-produced column. Limited to genuinely runtime calculations (e.g., user-pivoted ratios) that cannot be expressed in dbt without explosion of pre-aggregated tables.

Anything else is a violation. If a metric appears in Lightdash that doesn't map to (1) or (2), that's a bug to fix on the dbt side.

## Where Things Live

| Concept | Authored in | Consumed in | Example |
|---|---|---|---|
| Metric SQL | `b2b-saas-dbt/models/marts/**/*.sql` | dbt build → BigQuery materialised table | `fct_mrr_movements.mrr_delta` |
| Metric description | `b2b-saas-dbt/models/marts/marts.md` (doc tags) | Inherited by Lightdash via the dbt manifest | `{% docs col_mrr_delta %}` |
| Metric tags / metadata | `b2b-saas-dbt/models/marts/**/_models.yml` `meta:` block | Read by Lightdash at parse time | `owner: analytics, tier: 1` |
| Lightdash dimension / metric annotation | `b2b-saas-dbt/models/marts/**/_models.yml` `meta.dimension` / `meta.metric` | Lightdash table config | `meta.metric.type: sum` |
| Lightdash explore joins | This repo (Lightdash YAML) | Lightdash explore configuration | Join `fct_sessions` ↔ `dim_users` on `user_key` |
| Lightdash-only measures | This repo, inside Lightdash YAML | Surfaced only in Lightdash, never written to BigQuery | A ratio computed at query time across two fact tables |
| Charts and dashboards | Lightdash (UI or YAML export) | Lightdash app + MCP server | `product_funnel_overview` dashboard |

## Pass-Through Descriptions

When a column flows unchanged from dbt to Lightdash, its description is inherited from the dbt doc tag automatically. **Never re-author** the description in Lightdash — that creates two sources of truth that drift.

The only time Lightdash gets its own description is for a Lightdash-only measure (case 2 above). In that case, the description is authored once in the Lightdash YAML where the measure is defined.

## What Counts as a Lightdash-Only Measure

This is the exception, not the rule. Use sparingly.

A Lightdash-only measure is justified when **all of** the following are true:

1. The aggregation is runtime — it depends on filters or dimensions chosen at query time.
2. Pre-computing it in dbt would require an unreasonable number of pre-aggregated tables (e.g., one per filter combination).
3. The measure does not introduce a new business definition. It only re-aggregates a column that already has a canonical dbt definition.

Concrete examples (hypothetical, none built yet):

- **Justified.** "Conversion rate" calculated at query time as `count(activations) / count(signups)` where both numerator and denominator are dbt columns and the user picks the time window in Lightdash.
- **Not justified.** A custom SQL measure that defines what counts as an "activation" — that belongs in `fct_activations` in dbt.

When in doubt, push the calculation back to dbt and let Lightdash consume the result.

## Reviewing a New Metric

Before merging a PR that exposes a new metric in Lightdash:

1. **Find the dbt source.** What column on what model produces the number?
2. **Check the doc tag.** Does the column have a `{% docs %}` block in `marts.md`? If not, that's the first fix — add it on the dbt side.
3. **Check the metric contract.** Is the metric in `b2b-saas-dbt/docs/metric-contract.md`? If it's a new headline metric, the contract needs updating in a paired PR before this one ships.
4. **Verify the boundary.** Does the Lightdash config redefine any SQL? If yes, push it back to dbt.

## When Metrics Disagree

If a number in a Lightdash chart contradicts a number from a direct BigQuery query, the BigQuery query is right and the chart is wrong. The chart is the consumer, not the source. Investigate:

- Is the chart joining at the wrong grain? (Check `fanout` tests in the dbt repo for the expected grain.)
- Is the chart filtering differently from what the title implies? (Check the explore configuration.)
- Has the dbt model behaviour changed without the chart being updated? (Check `decisions.md` in the dbt repo for recent changes.)

The fix is always on the chart side. Don't "correct" by adding ad-hoc SQL to the Lightdash measure.

## See Also

- [`docs/governance-principles.md`](governance-principles.md) — chart/dashboard lifecycle and naming.
- [`docs/architecture.md`](architecture.md) — the position of this repo in the 3-repo stack.
- [`b2b-saas-dbt` metric contract](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/metric-contract.md) — canonical metric definitions.
- [`b2b-saas-dbt` doc-block convention](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/doc-block-convention.md) — how dbt doc tags work.
