#!/bin/sh
# glitchtip-railway: start wrapper for GlitchTip on Railway.
#   1. waits for Postgres (services start in parallel on Railway),
#   2. runs `manage.py init_database` (migrations; advisory lock, safe with replicas),
#   3. creates the first superuser from GLITCHTIP_ADMIN_EMAIL / GLITCHTIP_ADMIN_PASSWORD
#      (never fails the start; see railway_setup.py),
#   4. starts GlitchTip's own bin/start.sh with SKIP_INIT=true.
set -eu

log() { printf '[glitchtip-railway] %s\n' "$*"; }

cd /code
python /usr/local/lib/glitchtip-railway/railway_setup.py wait-db
log "initialising the database (migrations)"
python manage.py init_database
python /usr/local/lib/glitchtip-railway/railway_setup.py admin \
  || log "WARNING: superuser bootstrap failed (see above); GlitchTip starts anyway"

export SKIP_INIT=true
log "starting GlitchTip ${GLITCHTIP_VERSION:-?} on ${GRANIAN_HOST:-0.0.0.0}:${PORT:-8000}"
exec ./bin/start.sh
