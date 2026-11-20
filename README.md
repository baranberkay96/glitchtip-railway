# Deploy and Host GlitchTip with Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/glitchtip-7-error-tracking-sentry-compat?referralCode=20H68q)

GlitchTip is open-source (MIT) error tracking that accepts events from the Sentry SDKs, plus performance monitoring, uptime checks and logs. This community template runs GlitchTip 7 with PostgreSQL 18, Valkey for the task queue and cache, a Railway Bucket for uploaded source maps and debug files, and a superuser created on the first start.

## About Hosting GlitchTip

GlitchTip speaks the Sentry protocol: point any Sentry SDK (JavaScript, Python, Go, PHP, Ruby, Java, .NET, mobile) at a GlitchTip DSN and errors arrive with stack traces, breadcrumbs and releases. Since version 7 it runs as one process per replica: a granian server that serves the web app and the ingest API and also works the task queue and the scheduler, so there is no separate worker to keep in step. Hosting it well still needs a database that survives redeploys, a broker, object storage for source maps, and an administrator account that exists before strangers find the sign-up page. This template wires all of that up, waits for Postgres before migrating, creates the first superuser from generated credentials, and keeps open sign-up off.

## Common Use Cases

- Self-hosted error tracking for web, mobile and backend apps using the standard Sentry SDKs
- Performance monitoring (transactions, spans) without per-event SaaS pricing
- Uptime monitoring of websites and APIs with alerts, plus heartbeat checks for cron jobs
- Readable stack traces for minified JavaScript through uploaded source maps (`sentry-cli`)
- Keeping error data and personal data in an EU or private infrastructure you control

## Dependencies for GlitchTip Hosting

- GlitchTip 7.0.0 (built from the official `glitchtip/glitchtip` image, pinned by digest)
- PostgreSQL 18 (included, Railway's `postgres-ssl` image with a volume)
- Valkey 9.2 (included, password-protected, volume for the queue)
- A Railway Bucket (included) for uploaded files

### Deployment Dependencies

- GlitchTip documentation: https://glitchtip.com/documentation
- Installation and settings: https://glitchtip.com/documentation/install
- Source: https://gitlab.com/glitchtip/glitchtip-backend
- Sentry SDKs: https://docs.sentry.io/platforms/
- Railway Storage Buckets: https://docs.railway.com/storage-buckets

### Implementation Details

| Service | Source | Purpose |
|---|---|---|
| GlitchTip | this repo, `services/glitchtip` (`FROM glitchtip/glitchtip:7.0.0`) | Web app, API, event ingest, task worker and scheduler (port 8000, public) |
| Postgres | `ghcr.io/railwayapp-templates/postgres-ssl:18` | Events, issues, users; volume |
| Valkey | `valkey/valkey:9.2.0-alpine` | Task queue and cache, append-only file on a volume |
| Bucket | Railway Bucket | Source maps, debug files and other uploads (S3) |

**First login**

1. Open the **GlitchTip** service → Variables and copy `GLITCHTIP_ADMIN_EMAIL` (default `admin@example.com`) and `GLITCHTIP_ADMIN_PASSWORD`.
2. Open the public domain and log in. Create an organization, then a project for your app; GlitchTip shows its DSN.
3. Configure the Sentry SDK with that DSN, for example `Sentry.init({ dsn: "https://{key}@{your-domain}/{project-id}" })`.
4. Change the admin e-mail and password under Profile. To reset a forgotten password, set `GLITCHTIP_ADMIN_PASSWORD`, set `GLITCHTIP_ADMIN_RESET_PASSWORD=true`, redeploy, then set it back to `false`.

A password shorter than 8 characters typed into the deploy form is not used: the superuser gets a random password nobody knows and the log explains how to set a real one. The deploy itself does not fail.

**Inviting people.** Open sign-up is off (`ENABLE_USER_REGISTRATION=false`). Invite members from the organization settings. Invitations are sent by e-mail, so configure e-mail first, or set `ENABLE_USER_REGISTRATION=true` for a moment while your team signs up.

**E-mail (optional).** Without e-mail settings GlitchTip runs with e-mail disabled (no alerts by mail, no password-reset mails). Railway's Hobby plan blocks outbound SMTP, so an HTTP provider is the reliable option. Add to the GlitchTip service, for example for Postmark: `EMAIL_BACKEND=anymail.backends.postmark.EmailBackend` and `POSTMARK_SERVER_TOKEN={token}`; Mailgun, SendGrid, Brevo, Mailjet and SparkPost work the same way (see GlitchTip's install docs). On Pro you can use SMTP with `EMAIL_URL=smtp+tls://{user}:{password}@{host}:587`. Set `DEFAULT_FROM_EMAIL` to a sender your provider accepts.

**Apps in the same project** can send events over the private network to `http://glitchtip.railway.internal:8000`, but the DSN GlitchTip shows uses the public domain, which also works.

**Scaling.** Every GlitchTip replica serves HTTP and works the task queue, so scale out by raising replicas (Settings → Deploy), or raise `GRANIAN_WORKERS` on a larger service. GlitchTip keeps nothing on local disk. Event retention is `GLITCHTIP_RETENTION_DAYS` (90). Plan for about 0.4 GB RAM per GlitchTip process at idle (measured 371 MB), more under load; the Trial plan's 1 GB per service is enough for small projects only.

**Custom domain.** Update `GLITCHTIP_DOMAIN` and add the domain to `CSRF_TRUSTED_ORIGINS`, then redeploy. Existing DSNs keep the old host until you copy the new ones.

**Versions.** The GlitchTip tag and digest are in `services/glitchtip/Dockerfile`; migrations run on every start (`manage.py init_database`, safe with several replicas). Read the CHANGELOG before a major upgrade. Postgres and Valkey images are pinned in `template.json`.

### Why Deploy GlitchTip on Railway?

Railway runs GlitchTip, its database, queue and storage as one project on a private network, with HTTPS on a generated or custom domain. You pay for what the services use, add replicas with a slider when traffic grows, and keep your error data in infrastructure you control instead of a per-event SaaS plan.
