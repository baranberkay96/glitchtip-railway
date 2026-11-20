# NOTICE

This is a community template for running GlitchTip on Railway. It is not affiliated with or endorsed by Burke Software and Consulting LLC (the GlitchTip maintainers), Functional Software, Inc. (Sentry) or Railway. "Sentry" is a trademark of Functional Software, Inc.; it is used here only to describe protocol compatibility. This file is a summary for attribution, not legal advice.

## Software the template runs (unmodified)

| Component | Version | Source | License |
|---|---|---|---|
| GlitchTip (backend + bundled frontend) | 7.0.0, image `glitchtip/glitchtip:7.0.0@sha256:c245745b4179667da3aebd73fb8d4f1fd918f7d68ba07d1fd73ea688933b6e01` | https://gitlab.com/glitchtip/glitchtip-backend, https://gitlab.com/glitchtip/glitchtip-frontend | MIT, Copyright (c) Burke Software and Consulting LLC; third-party notices in the upstream `NOTICE.md` |
| PostgreSQL | 18, `ghcr.io/railwayapp-templates/postgres-ssl:18` | https://github.com/railwayapp-templates/postgres-ssl | PostgreSQL License; Railway image MIT |
| Valkey | 9.2.0, `valkey/valkey:9.2.0-alpine@sha256:c8e2d17498838af5d91e12eb7c11220b3434a7b7131a333e3af52ad5e0b80882` | https://github.com/valkey-io/valkey | BSD-3-Clause |

GlitchTip is not patched. The image gets two files, `glitchtip-railway.sh` and `railway_setup.py`, which wait for Postgres, run GlitchTip's own `manage.py init_database`, create the first superuser and then run the image's `bin/start.sh`.

## Files written for this template

`services/glitchtip/Dockerfile`, `glitchtip-railway.sh`, `railway_setup.py`, `template.json`, `TEMPLATE.md` and `README.md` were written for this template. The Postgres service definition follows Railway's own Postgres template. No file or text was copied from the marketplace templates listed in TEMPLATE.md.

## Upstream files and versions checked (2026-11-20)

- `glitchtip-backend` at tag `v7.0.0` (2026-11-09): `CHANGELOG` (single-process model, PostgreSQL 15 minimum, renamed retention variables), `bin/start.sh`, `bin/run-all-in-one.sh`, `bin/run-migrate.sh`, `bin/run-worker.sh`, `glitchtip/settings.py` (database, Valkey, S3, e-mail/Anymail, registration, CSRF and cookie settings), `glitchtip/urls.py` and `glitchtip/views.py` (`/_health/`), `apps/users/models.py` (e-mail login, `create_superuser`).
- Docker Hub `glitchtip/glitchtip` tags (7.0.0 = latest on 2026-11-20), image config (`/code`, user `app`, `CMD ./bin/start.sh`, port 8000).
