# GlitchTip for Railway: the official image plus a start wrapper that waits for Postgres,
# initialises the database and creates the first superuser from the service variables.
#
# GlitchTip 7 runs one process (granian ASGI server + task worker + scheduler); scale it with
# replicas. Upgrade: bump the tag and digest (https://hub.docker.com/r/glitchtip/glitchtip/tags)
# after reading the CHANGELOG; migrations run on the next start.
FROM glitchtip/glitchtip:7.0.0@sha256:c245745b4179667da3aebd73fb8d4f1fd918f7d68ba07d1fd73ea688933b6e01

COPY --chmod=0755 glitchtip-railway.sh /usr/local/bin/glitchtip-railway
# 0755: BuildKit gives a directory it creates the same mode (STANDARD 8.22).
COPY --chmod=0755 railway_setup.py /usr/local/lib/glitchtip-railway/railway_setup.py

# Fail the build early if the image layout this wrapper relies on changes.
RUN set -eu; \
    sh -n /usr/local/bin/glitchtip-railway; \
    python -m py_compile /usr/local/lib/glitchtip-railway/railway_setup.py; \
    test -x /code/bin/start.sh; \
    test -f /code/manage.py; \
    test "${GLITCHTIP_VERSION}" = 7.0.0

WORKDIR /code
CMD ["/usr/local/bin/glitchtip-railway"]
