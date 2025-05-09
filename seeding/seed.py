import csv, json
from datetime import datetime
import re
import os
import django
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "policounter.settings")
django.setup()


# ─── CONFIG ───────────────────────────────────────────────────────────────────
CITIES_CSV    = 'seeding/worldcities.csv'
EVENTS_CSV    = 'seeding/events.csv'
SHEET_EVENTS_CSV = 'seeding/sheet_events.csv'  # Yogi events
FIXTURE_FILE  = 'fixtures/data.json'
APP_LABEL     = 'counter'

# map your free-text Method → choices
METHOD_MAP = {
    'hand count using clicker': 'CLICKER',
    'eyeball estimate':         'EYEBALL',
    'ai model prediction':      'AI',
}

# ─── STATE ────────────────────────────────────────────────────────────────────
fixtures = []
# Dictionary to track all location keys we've seen
location_keys = {}
# Start with fresh PKs based on database-independent logic
loc_pk = 1
event_pk = 1
obs_pk = 1

# use one "now" timestamp for all created_at's
NOW_ISO = datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

# ─── Utility ────────────────────────────────────────────────────────────────────

def parse_date_flexibly(raw_date):
    """Parse a date string flexibly, returning ISO format or raising ValueError"""
    raw_date = raw_date.strip()

    # Skip recurring patterns like "Tuesdays"
    if re.search(r'(every|first|second|third|fourth|last|\bmon|\btue|\bwed|\bthu|\bfri|\bsat|\bsun)', raw_date, re.I):
        raise ValueError(f"Recurring pattern (not a date): {raw_date}")

    # Skip malformed or multi-date strings
    if not re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', raw_date):
        raise ValueError(f"Unrecognized or ambiguous date: {raw_date}")

    try:
        from dateutil import parser as dateparser
        return dateparser.parse(raw_date).date().isoformat()
    except Exception:
        raise ValueError(f"Unparsable date: {raw_date}")


def get_or_create_fixture(model, unique_key, fields, lookup_dict, pk_counter):
    """
    Get or create a fixture record.
    - model: Django model string
    - unique_key: hashable key to detect duplicates
    - fields: dict of field data
    - lookup_dict: dict mapping unique keys to pk
    - pk_counter: int reference for generating new PKs

    Returns: (pk, updated pk_counter)
    """
    if unique_key in lookup_dict:
        pk = lookup_dict[unique_key]
        return pk, pk_counter
    else:
        pk = pk_counter
        fixtures.append({
            "model": f"{APP_LABEL}.{model}",
            "pk": pk,
            "fields": fields
        })
        lookup_dict[unique_key] = pk
        return pk, pk_counter + 1

# ─── 1) LOCATIONS ─────────────────────────────────────────────────────────────
print("Creating locations...")
unique_locations = set()

# From events CSV
try:
    with open(EVENTS_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            city = row.get('City', '').strip()
            state = row.get('State', '').strip()
            country = row.get('Country', '').strip()
            if city and state and country:
                unique_locations.add((city, state, country))
except FileNotFoundError:
    print(f"Warning: {EVENTS_CSV} not found, skipping")

# From sheet events CSV
try:
    with open(SHEET_EVENTS_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            city = row.get('City', '').strip()
            state = 'Indiana'
            country = 'United States'
            if city:
                unique_locations.add((city, state, country))
except FileNotFoundError:
    print(f"Warning: {SHEET_EVENTS_CSV} not found, skipping")

# Manual location
manual_event_location = ("Indianapolis", "Indiana", "United States")
unique_locations.add(manual_event_location)

# From worldcities
try:
    with open(CITIES_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            city = row['city_ascii'].strip()
            state = row['admin_name'].strip()
            country = row['country'].strip()
            unique_locations.add((city, state, country))
except FileNotFoundError:
    print(f"Warning: {CITIES_CSV} not found, skipping")

# Create fixtures
for city, state, country in sorted(unique_locations):
    if not city or not country:
        continue

    location_key = (city, state, country)
    fields = {
        "city": city,
        "state": state,
        "country": country,
        "created_at": NOW_ISO,
    }
    loc_pk_id, loc_pk = get_or_create_fixture("location", location_key, fields, location_keys, loc_pk)

print(f"✓ Created {len(location_keys)} unique locations")

# ─── 2) EVENTS + OBSERVATIONS ─────────────────────────────────────────────────
print("Creating events and observations...")
event_lookup = {}

try:
    with open(EVENTS_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            name = row['Event Name'].strip()
            date = row['Date'].strip()

            if not name or not date:
                print(f"⚠️ Skipping event with missing name or date: {row}")
                continue

            try:
                cnt = float(row['Count'])
            except (ValueError, KeyError):
                print(f"⚠️ Skipping event with invalid count: {row}")
                continue

            method = METHOD_MAP.get(row.get('Method', '').lower(), 'CLICKER')
            who = row.get('Who', '').strip() or None

            city = row.get('City', '').strip()
            state = row.get('State', '').strip()
            country = row.get('Country', '').strip()
            loc_key = (city, state, country)

            if not loc_key[0] or not loc_key[2] or loc_key not in location_keys:
                print(f"⚠️ Skipping event with unknown location: {loc_key}")
                continue

            loc_id = location_keys[loc_key]
            ev_key = (name, date, loc_id)

            ev_fields = {
                "name": name,
                "date": date,
                "location": loc_id,
                "created_at": NOW_ISO,
            }
            ev_id, event_pk = get_or_create_fixture("event", ev_key, ev_fields, event_lookup, event_pk)

            obs_fields = {
                "event": ev_id,
                "count": cnt,
                "timestamp": f"{date}T12:00:00Z",
                "method": method,
                "observer": who,
                "created_at": NOW_ISO,
            }
            _, obs_pk = get_or_create_fixture("observation", (ev_id, cnt, method, who, date), obs_fields, {}, obs_pk)

except FileNotFoundError:
    print(f"Warning: {EVENTS_CSV} not found, skipping")

# ─── 2A) SHEET-BASED EVENTS ───────────────────────────────────────────────────
try:
    with open(SHEET_EVENTS_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            name = row.get('Event Name', '').strip()
            city = row.get('City', '').strip()

            if not name or not city:
                print(f"⚠️ Skipping sheet event with missing name or city: {row}")
                continue

            state = "Indiana"
            country = "United States"
            loc_key = (city, state, country)

            if loc_key not in location_keys:
                print(f"⚠️ Skipping sheet event with unknown location: {loc_key}")
                continue

            try:
                date = parse_date_flexibly(row['Date'])
            except (ValueError, KeyError) as e:
                print(f"⚠️ Skipping sheet event: {e}")
                continue

            loc_id = location_keys[loc_key]
            ev_key = (name, date, loc_id)
            ev_fields = {
                "name": name,
                "date": date,
                "location": loc_id,
                "created_at": NOW_ISO,
            }
            _, event_pk = get_or_create_fixture("event", ev_key, ev_fields, event_lookup, event_pk)
except FileNotFoundError:
    print(f"Warning: {SHEET_EVENTS_CSV} not found, skipping")

# ─── 2B) MANUAL EVENT AND OBSERVATIONS ─────────────────────────────────────────
print("Creating manual event and observations...")
manual_event_name = "50501 Protest"
manual_event_date = "2025-04-19"
manual_loc_id = location_keys.get(manual_event_location)

if not manual_loc_id:
    print(f"⚠️ Manual location not found: {manual_event_location}")
else:
    manual_event_key = (manual_event_name, manual_event_date, manual_loc_id)
    manual_event_fields = {
        "name": manual_event_name,
        "date": manual_event_date,
        "location": manual_loc_id,
        "created_at": NOW_ISO,
    }
    manual_event_id, event_pk = get_or_create_fixture("event", manual_event_key, manual_event_fields, event_lookup, event_pk)

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
        obs_fields = {
            "event": manual_event_id,
            "count": count,
            "timestamp": f"{manual_event_date}T12:00:00Z",
            "method": "AI",
            "observer": None,
            "input_image": "inputs/3ec5d7a4baaf4881ba433f714f7e4cc5_signal-2025-04-19-170902.jpeg",
            "density_map": f"density_maps/{density}",
            "model_name": model,
            "weight_selection": weight,
            "created_at": NOW_ISO,
        }
        obs_key = (manual_event_id, count, model, weight)
        _, obs_pk = get_or_create_fixture("observation", obs_key, obs_fields, {}, obs_pk)

# ─── 3) DUMP FIXTURE ───────────────────────────────────────────────────────────
with open(FIXTURE_FILE, 'w', encoding='utf-8') as out:
    json.dump(fixtures, out, indent=2)

print(f"✅ Wrote {len(fixtures)} records to {FIXTURE_FILE}")
print(f"  - {len(location_keys)} locations")
print(f"  - {len(event_lookup)} events")
print(f"  - {len(fixtures) - len(location_keys) - len(event_lookup)} observations")
