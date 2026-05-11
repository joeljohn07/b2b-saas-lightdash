# Joins

How facts and dimensions connect in the Lightdash explorer.

## Where joins are declared

Lightdash auto-discovers join paths from the FK `relationships` tests on the dbt models. Every fact-to-dimension join in the b2b-saas-dbt marts is covered by a `relationships:` test in the relevant `_models.yml`, so Lightdash builds its explore graph without any manual join configuration on this side.

This is intentional. The metric-ownership rule (see [`docs/metric-ownership.md`](metric-ownership.md)) says the dbt repo is the single authority for what connects to what. Declaring joins in Lightdash YAML would create two sources of truth that drift.

## Conformed join paths

The star schema converges on three conformed dimensions plus a date dimension:

| Fact / dim source | FK column | Joins to | On |
|---|---|---|---|
| All facts | `user_key` | `dim_users` | `user_key` |
| All facts | `account_key` | `dim_accounts` | `account_key` |
| All facts | `*_date_key` | `dim_date` | `date_key` |
| `fct_signups`, `fct_marketing_spend`, `fct_sessions` (utm) | `channel_key` / `first_touch_channel_key` / `last_touch_channel_key` | `dim_channels` | `channel_key` |
| `fct_sessions` | `session_key` | `dim_sessions` | `session_key` |
| `fct_experiment_exposures` | `experiment_key` | `dim_experiments` | `experiment_key` |
| `fct_experiment_exposures` | `(user_key, experiment_key)` | `bridge_user_experiments` | `(user_key, experiment_key)` |

## Role-playing date keys

Several facts have multiple date FKs that all resolve to the same `dim_date`:

| Fact | Role-played date keys |
|---|---|
| `fct_sessions` | `session_date_key` |
| `fct_signups` | `signup_date_key` |
| `fct_activations` | `activation_date_key` |
| `fct_subscriptions` | `event_date_key` |
| `fct_mrr_movements` | `movement_date_key` |
| `fct_invoices` | `issued_date_key` |
| `fct_marketing_spend` | `spend_date_key` |
| `fct_support_tickets` | `created_date_key` |
| `fct_retention_cohorts` | `cohort_week_date_key`, `period_end_date_key` |
| `fct_feature_usage` | `usage_date_key` |
| `fct_experiment_exposures` | `exposure_date_key` |

Lightdash treats each role-playing key as a distinct join — so an analyst can pick "by signup month" vs "by activation month" independently in the same explore.

## Drill-down paths

The combination of conformed dimensions and role-playing date keys produces the following drill-down patterns out of the box:

- **From any fact, drill into user**: `dim_users` reveals signup channel, activation status, engagement state.
- **From any fact, drill into account**: `dim_accounts` reveals plan, MRR, health score, lifecycle stage.
- **From any time aggregate, drill into date**: `dim_date` reveals calendar week, month, quarter, fiscal period.
- **From any acquisition or attribution context, drill into channel**: `dim_channels` reveals channel attributes.

## Adding a new join

If a new mart needs a join that isn't covered by an existing `relationships:` test:

1. **Add the FK column** to the dbt mart model (a `*_key` column referencing the dimension).
2. **Add a `relationships:` test** in the relevant `_models.yml`, severity `warn`, with `warn_if: ">0"` and `error_if: ">10"` (matching the [severity policy](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/quality-gates.md) from the dbt repo).
3. **Verify in Lightdash**: re-run `dbt parse` to refresh the manifest, then refresh the project in Lightdash. The new join appears automatically.

Do not declare joins in this repo's YAML. The dbt manifest is the source of truth.

## See Also

- [`docs/governance-principles.md`](governance-principles.md) — overall consumption-layer rules.
- [`docs/metric-ownership.md`](metric-ownership.md) — the dbt-as-authority principle.
- [`b2b-saas-dbt/docs/quality-gates.md`](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/quality-gates.md) — FK severity policy.
- [`b2b-saas-dbt/docs/architecture.md`](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/docs/architecture.md) — dimensional modeling guidelines + DAG rules.
