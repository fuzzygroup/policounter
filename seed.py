import csv
import json
from pathlib import Path
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CITIES_CSV    = 'worldcities.csv'
EVENTS_CSV    = 'events.csv'
FIXTURE_FILE  = Path('fixtures') / 'data.json'
APP_LABEL     = 'counter'   # ← change this to your real app name

# map your free-text Method → choices
METHOD_MAP = {
    'hand count using clicker': 'CLICKER',
    'eyeball estimate':         'EYEBALL',
    'ai model prediction':      'AI',
}

# ─── STATE ────────────────────────────────────────────────────────────────────
fixtures           = []
location_lookup    = {}  # (city, state, country) -> pk
event_lookup       = {}  # (name, date, loc_pk)    -> pk

loc_pk             = 1
event_pk           = 1
obs_pk             = 1

# use one “now” timestamp for all created_at’s so the JSON is consistent
NOW_ISO = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

# ─── 1) LOCATIONS ─────────────────────────────────────────────────────────────
with open(CITIES_CSV, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        city    = row['city_ascii'].strip()
        state   = row['admin_name'].strip()
        country = row['country'].strip()
        key     = (city, state, country)
        if key in location_lookup:
            continue

        fixtures.append({
            "model": f"{APP_LABEL}.location",
            "pk": loc_pk,
            "fields": {
                "city":       city,
                "state":      state,
                "country":    country,
                "created_at": NOW_ISO,
            }
        })
        location_lookup[key] = loc_pk
        loc_pk += 1

# ─── 2) EVENTS + OBSERVATIONS ─────────────────────────────────────────────────
with open(EVENTS_CSV, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        name    = row['Event Name'].strip()
        date    = row['Date'].strip()             # YYYY-MM-DD
        cnt     = float(row['Count'])
        method  = METHOD_MAP.get(row['Method'].lower(), 'CLICKER')
        who     = row['Who'].strip() or None

        # match your event location
        city    = row.get('City','').strip()
        state   = row.get('State','').strip()
        country = row.get('Country','').strip()
        loc_key = (city, state, country)

        if loc_key not in location_lookup:
            raise RuntimeError(f"Unknown location for event: {loc_key}")

        loc_id = location_lookup[loc_key]

        ev_key = (name, date, loc_id)
        if ev_key not in event_lookup:
            fixtures.append({
                "model": f"{APP_LABEL}.event",
                "pk": event_pk,
                "fields": {
                    "name":       name,
                    "date":       date,
                    "location":   loc_id,
                    "created_at": NOW_ISO,
                }
            })
            event_lookup[ev_key] = event_pk
            event_pk += 1

        ev_id = event_lookup[ev_key]

        fixtures.append({
            "model": f"{APP_LABEL}.observation",
            "pk": obs_pk,
            "fields": {
                "event":       ev_id,
                "count":       cnt,
                "timestamp":   f"{date}T12:00:00Z",
                "method":      method,
                "observer":    who,
                "prediction":  None,
                "created_at":  NOW_ISO,
            }
        })
        obs_pk += 1

# ─── 3) DUMP FIXTURE ───────────────────────────────────────────────────────────
FIXTURE_FILE.parent.mkdir(exist_ok=True)
with open(FIXTURE_FILE, 'w', encoding='utf-8') as out:
    json.dump(fixtures, out, indent=2)

print(f"✅ Wrote {len(fixtures)} records to {FIXTURE_FILE}")
