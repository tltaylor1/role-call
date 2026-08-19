# Runbook

Operating procedures for a running role-call instance. Each procedure
is written to be followed exactly as printed, and each was run against
a live stack before it was written down.

## Backup

The database is the only state; the containers hold nothing worth
keeping. One command produces a dated, compressed dump:

```
docker compose exec -T postgres pg_dump -U rolecall -Fc rolecall > rolecall-$(date +%Y-%m-%d).dump
```

The dump contains every snapshot, observation, governance record,
campaign, and audit row. It contains password hashes and session token
hashes but no passwords and no tokens, because none are ever stored.
Store it where the database's readers are the only readers: the
observations inside it name every identity in the connected accounts,
which is reconnaissance material in the wrong hands.

## Restore

Restore replaces the running database. Stop the application first so
nothing writes mid-restore:

```
docker compose stop app
docker compose exec -T postgres pg_restore -U rolecall --clean --if-exists -d rolecall < rolecall-2026-08-19.dump
docker compose start app
```

The application migrates on start; restoring a dump taken by an older
schema is followed by that migration automatically, and a failed
migration stops the container rather than serving the wrong schema.

## Verify the backup

A backup that was never restored is a hope. Restore into a throwaway
database and count:

```
docker compose exec -T postgres createdb -U rolecall restore_drill
docker compose exec -T postgres pg_restore -U rolecall -d restore_drill < rolecall-2026-08-19.dump
docker compose exec -T postgres psql -U rolecall -d restore_drill -c "select count(*) from observations"
docker compose exec -T postgres dropdb -U rolecall restore_drill
```

The count matches the live table or the backup is not a backup.

## Retention

The record model is append-only by design: observations, governance
history, campaign decisions, and audit rows exist to answer questions
years later, so the data itself has no deletion schedule inside the
application. Retention is therefore a property of the backups: keep
daily dumps for thirty days and one dump per month for two years,
deleting older ones, which bounds disk while preserving the ability to
answer how any decision looked at the time it was made. An instance
holding a real organization's data follows that organization's records
schedule where it is stricter.

## The clean-slate reset

Development only. This deletes every imported snapshot, every
governance record, and the audit history:

```
docker compose down -v
docker compose up --build
```
