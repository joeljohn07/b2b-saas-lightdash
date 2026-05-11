# Governance Principles

How charts and dashboards are created, reviewed, retired, and named in this Lightdash project. These rules are deliberately simple — this is a portfolio repo with one author — but they encode the same patterns a real analytics team would use.

## Single Source of Metric Truth

Every metric resolves to one definition in [`b2b-saas-dbt`](https://github.com/joeljohn07/b2b-saas-dbt). Lightdash never redefines what a "signup" or an "active user" is — it surfaces the columns that dbt already produces.

The boundary:

| Lives in `b2b-saas-dbt` | Lives in this repo |
|---|---|
| Metric SQL (the column definition) | Lightdash explore configuration |
| Metric description (in dbt doc tags) | Lightdash-only measures with rationale |
| Tests for metric correctness | Charts and dashboards that consume metrics |
| Schema contracts | Saved queries and links between dashboards |

Full ownership rules: [`docs/metric-ownership.md`](metric-ownership.md).

## Chart Lifecycle

**Creation.** A chart is created in Lightdash either by saving an exploration result or by being built explicitly in a dashboard tile. Every chart must have:

- A descriptive name following the naming convention below.
- A one-line description in Lightdash's chart metadata.
- A clear owner (in this single-author repo, the owner is `analytics`; in a real team, the team or person who consumes it).
- A space — never a chart in "Personal Space" for production use.

**Review.** Charts shipped on a dashboard are reviewed at PR time. The reviewer checks: does the chart answer a real question, does the title match what it shows, are filters justified, and is the underlying metric definition the canonical dbt one?

**Deprecation.** When a chart becomes redundant, rename it with a `[DEPRECATED] ` prefix and add a deprecation date in the description. Delete after 30 days unless a stakeholder asks otherwise. Don't silently delete charts — somebody likely bookmarked them.

## Dashboard Lifecycle

**Creation.** A dashboard answers one question or supports one workflow. If a draft dashboard accumulates more than ~8 tiles, it probably needs splitting. Every dashboard has a description and at least one filter that scopes time.

**Review.** Dashboards are reviewed once at creation and re-reviewed when:

- A consumer reports that a number looks wrong.
- An upstream dbt change is flagged as potentially breaking (see exposures in `b2b-saas-dbt/models/marts/exposures.yml`).
- Six months elapse without a change — a stale dashboard signals that nobody is using it.

**Deprecation.** Same as charts: rename with `[DEPRECATED] `, give it 30 days, then remove.

## Naming Conventions

### Charts

Pattern: `<domain>_<metric>_<viz-type>`

Examples:
- `funnel_conversion_rate_line`
- `revenue_mrr_movement_bar`
- `retention_cohort_heatmap`
- `engagement_dau_wau_ratio_kpi`

Vocabulary:
- **domain** — one of `funnel`, `revenue`, `engagement`, `retention`, `attribution`, `support`.
- **metric** — the headline thing being shown (mirrors the metric contract).
- **viz-type** — `line`, `bar`, `kpi`, `table`, `heatmap`, `funnel`, `pie` (rare).

### Dashboards

Pattern: `<domain>_<purpose>`

Examples:
- `product_funnel_overview`
- `revenue_movements_monthly`
- `retention_cohort_analysis`
- `executive_summary`

### Spaces

Organised by domain, mirroring the marts subdirectories in dbt:

| Space | Contents |
|---|---|
| `Product` | Funnel, engagement, feature usage, sessions |
| `Revenue` | MRR movements, invoices, subscriptions |
| `Growth` | Retention cohorts, marketing spend, attribution |
| `Support` | Tickets, CSAT, account health |
| `Executive` | Cross-functional summaries |

## Access Control

This portfolio project is single-user. In a real deployment:

- The Lightdash admin role is restricted to the analytics team.
- Editor access is granted per-space. Most stakeholders are viewers.
- The Lightdash MCP server (planned, #410) exposes the same semantic surface to agents — access controls there mirror the human access controls.
- PII columns (flagged via `meta.pii: true` on the dbt side) are masked or excluded from non-admin views. Since the synthetic dataset has `pii: false` everywhere, no masking is needed here.

## Chart Anti-Patterns

The reviewer's job is to catch these:

1. **A chart that re-derives a metric.** If a Lightdash custom SQL measure replicates logic that exists in `int_*` or `fct_*`, push the calculation back to dbt.
2. **A "what" question with no "so what".** A chart with no clear consumer or decision attached is dead weight. Either find the consumer or kill the chart.
3. **A chart that gets its numbers from two different grain levels.** Sums at session grain joined to sums at user grain produce nonsense. Use the existing fanout tests as a guide for what to never do in a chart.
4. **A dashboard with no time filter.** Every dashboard has at least one time filter, default to last 90 days.

## See Also

- [`docs/metric-ownership.md`](metric-ownership.md) — dbt vs Lightdash ownership boundary.
- [`docs/architecture.md`](architecture.md) — overall position in the 3-repo stack.
- [`CLAUDE.md`](../CLAUDE.md) — project rules and non-negotiables.
- [`b2b-saas-dbt` metric contract](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/metric-contract.md) — the canonical metric definitions.
