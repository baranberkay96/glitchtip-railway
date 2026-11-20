# GlitchTip 7 Error Tracking (Sentry-Compatible): Railway template spec

## Listing

| Field | Value |
|---|---|
| Name | **GlitchTip 7 Error Tracking (Sentry-Compatible)** (46 chars; 7 = GlitchTip major of the pinned 7.0.0) |
| Description | Sentry-compatible errors, performance and uptime monitoring. (60 chars) |
| Category | Observability |
| Icon | `https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/glitchtip.svg` (200, image/svg+xml) |

## Base market templates

| Market template | Active | What it does | Kept | Problems fixed |
|---|---|---|---|---|
| `glitchtip` "GlitchTip" (leader, by the GlitchTip team) | 97 | `glitchtip/glitchtip:6` with auto patch updates, all-in-one start, `bin/run-migrate.sh` pre-deploy, Postgres 17, Redis 8.2, Railway Bucket | all-in-one process, Bucket for uploads, `/_health/` healthcheck, registration off | Still on 6.x (7.0.0 is current); `GLITCHTIP_MAX_EVENT_LIFE_DAYS` renamed in 7; floating tag; no first-user bootstrap (an admin has to be created by hand, e.g. `createsuperuser` over `railway ssh`); `I_PAID_FOR_GLITCHTIP=paas` hides the donation notice; no CSRF origin for the HTTPS proxy; Redis instead of Valkey |
| `AMx6AD` "GlitchTip" | 29 | `glitchtip:latest`, `sleep 10 && migrate && start.sh`, healthcheck `/login` | nothing | floating tag; `sleep 10` race with Postgres; no storage; `REDIS_PRIVATE_URL` / `DATABASE_PRIVATE_URL` (deprecated variables) |
| `glitchtip-railway` | 0 | separate web and worker (`SERVER_ROLE=worker`), DuckDB cold storage, Bucket | Bucket wiring | **The worker service no longer starts on 7.0** (`bin/start.sh` refuses `SERVER_ROLE=worker`); floating tag |

Upstream checked: `glitchtip-backend` v7.0.0 (see NOTICE.md).

## Pinned versions (checked 2026-11-20)

| Component | Image | Released |
|---|---|---|
| GlitchTip | `glitchtip/glitchtip:7.0.0@sha256:c245745b4179667da3aebd73fb8d4f1fd918f7d68ba07d1fd73ea688933b6e01` | 2026-11-09 |
| Postgres | `ghcr.io/railwayapp-templates/postgres-ssl:18` (Railway's maintained tag) | — |
| Valkey | `valkey/valkey:9.2.0-alpine@sha256:c8e2d17498838af5d91e12eb7c11220b3434a7b7131a333e3af52ad5e0b80882` | 2026-11 |

**Why 7.0.0 and not 6.2.6:** 7.0.0 is the current stable; 6.x gets no further releases. 7 runs one process per replica (web + task worker + scheduler), so the template has no worker service: GlitchTip 7 refuses one.

## Services

### GlitchTip
- Source: repo `baranberkay96/glitchtip-railway`, `/services/glitchtip` (official image + `glitchtip-railway.sh` + `railway_setup.py`).
- Start: wait for Postgres (`GLITCHTIP_DB_WAIT_SECONDS`, 600) → `manage.py init_database` (migrations, partitions; advisory lock, safe with replicas) → superuser bootstrap → `bin/start.sh` with `SKIP_INIT=true`.
- Superuser bootstrap: only while no superuser exists; invalid e-mail → `admin@example.com`; password outside 8–128 chars → random unusable password + log hint (Rule 8.29); `GLITCHTIP_ADMIN_RESET_PASSWORD=true` resets the password; a replica race is caught.
- Public domain → 8000, healthcheck `/_health/` (900 s: migrations of a large database run before the server starts), restart ALWAYS, no volume (uploads go to the Bucket).
- Listener `GRANIAN_HOST=::`.

### Postgres
Railway `postgres-ssl:18`, volume `/var/lib/postgresql/data`, GlitchTip connects over the private network (`DATABASE_URL`). GlitchTip 7 needs PostgreSQL 15+.

### Valkey
`valkey-server --requirepass … --appendonly yes --save 60 1 --maxmemory-policy noeviction`, volume `/data`. Queue messages survive restarts; `noeviction` keeps queued tasks from being evicted under memory pressure.

### Bucket
Railway Bucket: `DEFAULT_FILE_STORAGE` switches to S3 automatically when `AWS_S3_ENDPOINT_URL` is set (GlitchTip settings). Region via `AWS_DEFAULT_REGION` (boto3).

## Resource estimate

Measured idle on Railway (2026-11-20, after one test event and an upload): GlitchTip 371 MB, Postgres 82 MB, Valkey 16 MB, about 0.47 GB in total ≈ $5/month RAM plus small volumes; busy installs grow with event volume (ingest concurrency 12 per process). Trial (1 GB/service) works for small projects; Hobby recommended.

## Improvements over market templates

1. GlitchTip 7.0.0 pinned by digest; Postgres 18; Valkey instead of Redis.
2. First superuser created from generated variables (login works right after deploy), with fail-closed password handling and a reset switch.
3. Start waits for Postgres instead of racing it; migrations run once per start under GlitchTip's lock.
4. CSRF trusted origin and `GLITCHTIP_DOMAIN` from the Railway domain; open sign-up and org creation off.
5. Valkey with AOF and `noeviction` for the task queue.
6. Documented e-mail via HTTP providers (Anymail) for plans without SMTP.

## Verification checklist

- [ ] All services SUCCESS, `/_health/` 200.
- [ ] Log in with `GLITCHTIP_ADMIN_EMAIL` / `GLITCHTIP_ADMIN_PASSWORD`; create organization + project; DSN shown.
- [ ] Send a test event to the DSN store endpoint → issue appears (task queue works).
- [ ] Upload a file (debug file / source map) → object in the Bucket.
- [ ] Redeploy GlitchTip → data and login persist, bootstrap skipped.
- [ ] Short admin password → deploy succeeds, login locked, log explains.

## Open questions

- Cold storage (`GLITCHTIP_ENABLE_DUCKDB`) is new in 6.x/7 and left off; it could move old events to the Bucket.
