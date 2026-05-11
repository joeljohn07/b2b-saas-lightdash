# Setup

How to bring up the Lightdash stack locally and connect it to the sibling [`b2b-saas-dbt`](https://github.com/joeljohn07/b2b-saas-dbt) project.

## Prerequisites

| Requirement | Why |
|---|---|
| Docker + Docker Compose | Runs the Lightdash app and its Postgres metadata backend |
| `gcloud` CLI authenticated | BigQuery auth for the dbt project (local dev) |
| The dbt project cloned and built | Lightdash reads the dbt manifest |
| ~2 GB free disk | Postgres volume + Lightdash image |

Verify each:

```bash
docker --version            # 24+ recommended
docker compose version      # v2+

gcloud auth list            # confirms an active account
gcloud auth application-default login   # one-time, if not done

# Confirm the dbt project is a sibling of this repo
ls ~/Agentic/projects/b2b-saas-dbt/dbt_project.yml
```

If the dbt project hasn't been built yet, follow [`b2b-saas-dbt/RUNBOOK.md`](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/RUNBOOK.md) first — Lightdash needs a parsed dbt manifest to discover models.

## First-time setup

```bash
# 1. Clone (if you haven't already)
cd ~/Agentic/projects
git clone https://github.com/joeljohn07/b2b-saas-lightdash.git
cd b2b-saas-lightdash

# 2. Copy the env template and fill in secrets
cp .env.example .env

# 3. Generate a real LIGHTDASH_SECRET and edit .env
openssl rand -hex 32
# paste into LIGHTDASH_SECRET in .env

# Set PGPASSWORD to something non-default in .env

# 4. Bring up the stack
docker compose up -d

# 5. Tail logs until Lightdash is ready
docker compose logs -f lightdash
# Look for "Server started on port 8080"
```

Open <http://localhost:8080>. You'll be prompted to create the first admin user.

## Creating the Lightdash project

After signing in:

1. **Create a new project.** Project name: `b2b-saas`. Project type: BigQuery.
2. **Warehouse connection.**
   - **GCP project ID:** your BigQuery project (same one the dbt project writes to).
   - **Location:** `EU` (matches the dbt project default; change if your dbt profile uses a different region).
   - **Authentication:** "Application Default Credentials" if your `~/.config/gcloud` was mounted (default in `docker-compose.yml`); "Service Account JSON" otherwise — paste the key contents.
3. **dbt project configuration.**
   - **Type:** `dbt local server`.
   - **Project directory:** `/usr/app/dbt` (this is where the sibling repo is mounted inside the container).
   - **Target:** `dev`.
4. **Test connection.** Lightdash will run `dbt parse` against the mounted project. On success it discovers all models with `meta.dimension` / `meta.metric` annotations and turns them into explores.

Once the project is created, the data warehouse, dbt manifest, and Lightdash UI are wired together. Explores under "Browse" mirror the dbt mart models.

## What you should see

A working setup has:

- Explores for every dbt mart model with `meta` annotations.
- The lineage graph for any explore shows the upstream intermediate and staging models (read from the dbt manifest).
- Tests defined in dbt show up in the model's "Tests" tab in Lightdash.
- Column descriptions are inherited from dbt doc tags — no re-authoring.

Note: until [#393](https://github.com/joeljohn07/agentic-hub/issues/393) ships, the dbt mart models won't have Lightdash `meta` annotations yet, so explores will appear but with default dimensions only (no curated metrics). The Lightdash project setup still works; it just won't have explore-level curation until then.

## Troubleshooting

### `docker compose up` fails with `port 8080 already in use`

Another service is using port 8080. Either stop it, or change `LIGHTDASH_PORT` in `.env` to a free port (the container still listens on 8080 internally).

### Lightdash logs show `EHOSTUNREACH` connecting to Postgres

The `db` service didn't come up in time. The `depends_on: condition: service_healthy` guard should handle this; if it doesn't, run `docker compose down` and try again. If it persists, check `docker compose logs db` for errors during initial schema creation.

### Lightdash project creation fails on "test dbt connection"

Most common causes:

1. **`/usr/app/dbt` empty** — the sibling repo is not mounted. Confirm `ls ~/Agentic/projects/b2b-saas-dbt/dbt_project.yml` works on the host. The compose file's volume mount expects `~/Agentic/projects/b2b-saas-dbt` to exist as a sibling of this repo.
2. **`dbt parse` fails inside the container** — the dbt project itself doesn't parse. Reproduce on the host: `cd ~/Agentic/projects/b2b-saas-dbt && dbt parse`.
3. **dbt packages not installed** — Lightdash needs the contents of `dbt_packages/` to resolve `dbt-utils` and similar. Run `dbt deps` in the dbt project before bringing up Lightdash.

### BigQuery authentication failures

For local dev, the `~/.config/gcloud` volume mount provides ADC. Verify on the host:

```bash
gcloud auth application-default print-access-token
```

If that fails, run `gcloud auth application-default login`. If it succeeds on the host but Lightdash can't auth, the mount may have stale credentials — restart the stack: `docker compose down && docker compose up -d`.

For production, never mount gcloud — use a service-account JSON key entered in the Lightdash UI, with `roles/bigquery.dataViewer` and `roles/bigquery.jobUser` on the dbt project's BQ project.

### Container can't reach BigQuery (network errors)

Corporate networks sometimes block outbound HTTPS to `*.googleapis.com`. Test from inside the container:

```bash
docker compose exec lightdash curl -sI https://bigquery.googleapis.com
```

A 200 or 404 response is fine (means the host is reachable). Connection refused / timeouts indicate an egress block.

## Tearing down

```bash
# Stop the stack, keep data
docker compose down

# Stop + delete the Postgres metadata (Lightdash projects, users, dashboards)
docker compose down -v
```

The `down -v` form is irreversible — projects, users, and saved dashboards are lost. Use it only when you genuinely want a fresh start.

## Deployment Notes (not yet automated)

Production deployment to a VPS would mirror this compose stack with three differences:

1. Replace gcloud ADC mount with a service-account key.
2. Front the Lightdash service with a reverse proxy (nginx, Caddy) terminating TLS.
3. Set `SITE_URL` to the public domain.

Full VPS deployment automation is out of scope for this ticket — tracked separately.

## See Also

- [`docker-compose.yml`](../docker-compose.yml) — the stack definition.
- [`.env.example`](../.env.example) — environment variable contract.
- [`docs/architecture.md`](architecture.md) — position in the 3-repo stack.
- [`b2b-saas-dbt/RUNBOOK.md`](https://github.com/joeljohn07/b2b-saas-dbt/blob/main/RUNBOOK.md) — set up the dbt project first.
