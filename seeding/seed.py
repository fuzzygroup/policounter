import csv
import json
from datetime import datetime
from dateutil import parser as dateparser
import re
import os
import django
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "policounter.settings")  # Replace with your real settings path
django.setup()

from counter.models import Location

# ─── CONFIG ───────────────────────────────────────────────────────────────────
CITIES_CSV    = 'seeding/worldcities.csv'
EVENTS_CSV    = 'seeding/events.csv'
SHEET_EVENTS_CSV = 'seeding/sheet_events.csv'  # Yogi events
FIXTURE_FILE  = 'fixtures/data.json'
APP_LABEL     = 'counter'   # ← change this to your real app name

# map your free-text Method → choices
METHOD_MAP = {
    'hand count using clicker': 'CLICKER',
    'eyeball estimate':         'EYEBALL',
    'ai model prediction':      'AI',
}

# ─── STATE ────────────────────────────────────────────────────────────────────
fixtures           = []
location_lookup = {
    (loc.city.strip(), loc.state.strip(), loc.country.strip()): loc.pk
    for loc in Location.objects.all()
}
loc_pk = max(location_lookup.values(), default=0) + 1

event_lookup       = {}  # (name, date, loc_pk)    -> pk

loc_pk             = 1
event_pk           = 1
obs_pk             = 1

# use one “now” timestamp for all created_at’s so the JSON is consistent
NOW_ISO = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'


# ─── Utility ────────────────────────────────────────────────────────────────────

def parse_date_flexibly(raw_date):
    raw_date = raw_date.strip()

    # Skip recurring patterns like "Tuesdays"
    if re.search(r'(every|first|second|third|fourth|last|\bmon|\btue|\bwed|\bthu|\bfri|\bsat|\bsun)', raw_date, re.I):
        raise ValueError(f"Recurring pattern (not a date): {raw_date}")

    # Skip malformed or multi-date strings
    if not re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', raw_date):
        raise ValueError(f"Unrecognized or ambiguous date: {raw_date}")

    try:
        return dateparser.parse(raw_date).date().isoformat()
    except Exception:
        raise ValueError(f"Unparsable date: {raw_date}")


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
                "created_at":  NOW_ISO,
            }
        })
        obs_pk += 1

# ─── 2A) SHEET-BASED EVENTS (no observation data) ─────────────────────────────
with open(SHEET_EVENTS_CSV, newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        name     = row['Event Name'].strip()
        city     = row['City'].strip()
        state    = "Indiana"
        country  = 'United States'  # default for now; adjust if needed
        loc_key  = (city, state, country)
        date = None
        try:
            date = parse_date_flexibly(row['Date'])
        except ValueError as e:
            print(f"⚠️  Skipping event: {e}")
            continue

        if loc_key not in location_lookup:
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
            location_lookup[loc_key] = loc_pk
            print(f'appending {loc_key}')
            loc_pk += 1

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


# ─── 2B) MANUAL EVENT AND OBSERVATIONS ─────────────────────────────────────────

manual_event_name = "50501 Protest"
manual_event_date = "2025-04-19"
manual_event_location = ("Indianapolis", "Indiana", "United States")  # adjust if needed

if manual_event_location not in location_lookup:
    raise RuntimeError(f"Manual location not found: {manual_event_location}")
manual_loc_id = location_lookup[manual_event_location]

manual_event_key = (manual_event_name, manual_event_date, manual_loc_id)
if manual_event_key not in event_lookup:
    fixtures.append({
        "model": f"{APP_LABEL}.event",
        "pk": event_pk,
        "fields": {
            "name":       manual_event_name,
            "date":       manual_event_date,
            "location":   manual_loc_id,
            "created_at": NOW_ISO,
        }
    })
    event_lookup[manual_event_key] = event_pk
    event_pk += 1

manual_event_id = event_lookup[manual_event_key]

manual_observations = [
    ("CSRNet", "SHA", 906.04, "3ec5d7a4baaf4881ba433f714f7e4cc5_density_map.png"),
    ("CSRNet", "SHB", 1106.04, "3ec5d7a4baaf4881ba433f714f7e4cc5_density_map_smpOKk2.png"),
    ("Bay", "SHA", 684.31, "3ec5d7a4baaf4881ba433f714f7e4cc5_density_map_eEI3eh8.png"),
    ("Bay", "SHB", 652.99, "3ec5d7a4baaf4881ba433f714f7e4cc5_density_map_8BmD9At.png"),
    ("Bay", "QNRF", 644.90, "3ec5d7a4baaf4881ba433f714f7e4cc5_density_map_Ua1O2o2.png"),
    ("DM-Count", "SHA", 707.24, "3ec5d7a4baaf4881ba433f714f7e4cc5_density_map_SYHKvc4.png"),
    ("DM-Count", "SHB", 789.51, "3ec5d7a4baaf4881ba433f714f7e4cc5_density_map_LfOBQ0t.png"),
    ("DM-Count", "QNRF", 622.22, "3ec5d7a4baaf4881ba433f714f7e4cc5_density_map_PKfPGmE.png"),
    ("SFANet", "SHB", 744.87, "3ec5d7a4baaf4881ba433f714f7e4cc5_density_map_15FunSA.png"),
]

for model, weight, count, density in manual_observations:
    fixtures.append({
        "model": f"{APP_LABEL}.observation",
        "pk": obs_pk,
        "fields": {
            "event":           manual_event_id,
            "count":           count,
            "timestamp":       f"{manual_event_date}T12:00:00Z",
            "method":          "AI",
            "observer":        None,
            "input_image":     "inputs/3ec5d7a4baaf4881ba433f714f7e4cc5_signal-2025-04-19-170902.jpeg",
            "density_map":     f'density_maps/{density}',
            "model_name":      model,
            "weight_selection": weight,
            "created_at":      NOW_ISO,
        }
    })
    obs_pk += 1


# ─── 3) DUMP FIXTURE ───────────────────────────────────────────────────────────
with open(FIXTURE_FILE, 'w', encoding='utf-8') as out:
    json.dump(fixtures, out, indent=2)

print(f"✅ Wrote {len(fixtures)} records to {FIXTURE_FILE}")
