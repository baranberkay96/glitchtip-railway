"""Railway helpers for GlitchTip, run by glitchtip-railway before the server starts.

    railway_setup.py wait-db   wait until Postgres accepts connections (GLITCHTIP_DB_WAIT_SECONDS)
    railway_setup.py admin     create the first superuser from GLITCHTIP_ADMIN_EMAIL/_PASSWORD

The admin step never raises on bad input (STANDARD 8.29):
- an invalid e-mail falls back to admin@example.com with a warning;
- a password shorter than 8 or longer than 128 characters is never set: a new superuser
  gets a random password nobody knows (log in only after fixing the variable and setting
  GLITCHTIP_ADMIN_RESET_PASSWORD=true), an existing one keeps its password.
- once any superuser exists, nothing changes unless GLITCHTIP_ADMIN_RESET_PASSWORD=true,
  which sets the password of GLITCHTIP_ADMIN_EMAIL to GLITCHTIP_ADMIN_PASSWORD.
No password is ever printed.
"""
import os
import re
import secrets
import sys
import time

sys.path.insert(0, "/code")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "glitchtip.settings")

DEFAULT_EMAIL = "admin@example.com"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD, MAX_PASSWORD = 8, 128


def log(message: str) -> None:
    print(f"[glitchtip-railway] {message}", flush=True)


def wait_seconds() -> int:
    raw = os.environ.get("GLITCHTIP_DB_WAIT_SECONDS", "600")
    if raw.isdigit() and 0 <= int(raw) <= 7200:
        return int(raw)
    log(f"WARNING: GLITCHTIP_DB_WAIT_SECONDS='{raw}' is not 0-7200; using 600")
    return 600


def wait_db() -> None:
    import django

    django.setup()
    from django.db import connection

    deadline = time.monotonic() + wait_seconds()
    while True:
        try:
            connection.ensure_connection()
            connection.close()
            log("Postgres is reachable")
            return
        except Exception as err:  # noqa: BLE001 - any connection error means "not yet"
            if time.monotonic() > deadline:
                log(f"ERROR: Postgres not reachable: {type(err).__name__}: {err}")
                sys.exit(1)
            log(f"waiting for Postgres ({type(err).__name__})")
            connection.close()
            time.sleep(5)


def truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes", "on")


def admin() -> None:
    import django

    django.setup()
    from django.contrib.auth import get_user_model
    from django.db import IntegrityError

    user_model = get_user_model()
    email = os.environ.get("GLITCHTIP_ADMIN_EMAIL", "").strip().lower()
    password = os.environ.get("GLITCHTIP_ADMIN_PASSWORD", "")
    reset = truthy("GLITCHTIP_ADMIN_RESET_PASSWORD")
    if not email:
        log("GLITCHTIP_ADMIN_EMAIL is empty: no superuser bootstrap")
        return
    if not EMAIL_RE.match(email):
        log(f"WARNING: GLITCHTIP_ADMIN_EMAIL is not an e-mail address; using {DEFAULT_EMAIL}")
        email = DEFAULT_EMAIL
    usable = MIN_PASSWORD <= len(password) <= MAX_PASSWORD
    if not usable:
        log(f"WARNING: GLITCHTIP_ADMIN_PASSWORD must be {MIN_PASSWORD}-{MAX_PASSWORD} characters; it is not used.")

    user = user_model.objects.filter(email__iexact=email).first()
    if user_model.objects.filter(is_superuser=True).exists():
        if reset and user is not None:
            if usable:
                user.set_password(password)
                user.is_active = True
                user.save(update_fields=["password", "is_active"])
                log(f"password of {email} reset from GLITCHTIP_ADMIN_PASSWORD; set GLITCHTIP_ADMIN_RESET_PASSWORD=false again")
            else:
                log(f"WARNING: password of {email} left unchanged (fix GLITCHTIP_ADMIN_PASSWORD first)")
        elif reset:
            log(f"WARNING: GLITCHTIP_ADMIN_RESET_PASSWORD=true but no user {email} exists; nothing changed")
        else:
            log("a superuser already exists; bootstrap skipped")
        return

    if user is not None:
        user.is_staff = user.is_superuser = user.is_active = True
        user.save(update_fields=["is_staff", "is_superuser", "is_active"])
        log(f"existing user {email} promoted to superuser (password unchanged)")
        return

    try:
        user_model.objects.create_superuser(email=email, password=password if usable else secrets.token_urlsafe(32))
    except IntegrityError:
        log(f"superuser {email} was created by another replica")
        return
    if usable:
        log(f"superuser {email} created; log in with GLITCHTIP_ADMIN_PASSWORD")
    else:
        log(f"WARNING: superuser {email} created with a random password nobody knows (login locked).")
        log("WARNING: set GLITCHTIP_ADMIN_PASSWORD (8+ characters) and GLITCHTIP_ADMIN_RESET_PASSWORD=true, then redeploy.")


def main(argv: list[str]) -> None:
    command = argv[1] if len(argv) > 1 else ""
    if command == "wait-db":
        wait_db()
    elif command == "admin":
        admin()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv)
