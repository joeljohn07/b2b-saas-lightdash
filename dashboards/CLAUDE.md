# Dashboards — Tier 1 Context

Rules for dashboard composition. Read [`/CLAUDE.md`](../CLAUDE.md) first; this applies on top.

## Naming

`<domain>_<purpose>` — e.g., `product_funnel_overview`, `retention_cohort_analysis`, `executive_summary`. Full convention in [`/docs/governance-principles.md`](../docs/governance-principles.md).

## Structure

- **One question per dashboard.** A dashboard that answers two unrelated questions should be two dashboards.
- **Maximum ~8 tiles.** Beyond that, split. The constraint is reader attention, not screen real estate.
- **At least one time filter,** defaulting to the last 90 days. No dashboard ships with no temporal scope.
- **Tile layout top-to-bottom, summary-to-detail.** Headline KPIs at the top, supporting breakdowns below, drill-down tables at the bottom.

## Drill-Down

Every dashboard with aggregated tiles has at least one detail tile where a viewer can see the underlying rows. Aggregates without drill-downs are unverifiable.

## Filters

Filters should be:

- Discoverable — visible without scrolling.
- Defaulted to sensible values (last 90 days, all plans).
- Documented in the dashboard description if non-obvious.

## Never

- A dashboard with no consumer or decision attached.
- Tiles that sum at one grain joined to tiles that sum at another (e.g., session-level next to user-level).
- A dashboard that pulls numbers from charts in Personal Space.
