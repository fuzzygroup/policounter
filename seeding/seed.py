import csv
import json
from datetime import datetime
import re
import os
import django
import sys
from django.db import connection

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "policounter.settings")
django.setup()

from counter.models import Location

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


# ─── Clear the existing data ───────────────────────────────────────────────────
# Check if we're using MySQL (which has different truncate behavior)
is_mysql = connection.vendor == 'mysql'

if is_mysql:
    # For MySQL, we need to disable foreign key checks temporarily
    with connection.cursor() as cursor:
        cursor.execute('SET FOREIGN_KEY_CHECKS=0;')
        cursor.execute('TRUNCATE TABLE counter_observation;')
        cursor.execute('TRUNCATE TABLE counter_event;')
        cursor.execute('TRUNCATE TABLE counter_location;')
        cursor.execute('SET FOREIGN_KEY_CHECKS=1;')
else:
    # For PostgreSQL and others
    with connection.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE counter_observation CASCADE;')
        cursor.execute('TRUNCATE TABLE counter_event CASCADE;')
        cursor.execute('TRUNCATE TABLE counter_location CASCADE;')

print("✓ Cleared existing data")

# ─── 1) LOCATIONS ─────────────────────────────────────────────────────────────
print("Creating locations...")
# First, collect all unique locations from both CSVs
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
            state = 'Indiana'  # Default state for sheet events
            country = 'United States'  # Default country
            if city:
                unique_locations.add((city, state, country))
except FileNotFoundError:
    print(f"Warning: {SHEET_EVENTS_CSV} not found, skipping")

# Add manual event location
manual_event_location = ("Indianapolis", "Indiana", "United States")
unique_locations.add(manual_event_location)

# Add cities from worldcities.csv
try:
    with open(CITIES_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            city = row['city_ascii'].strip()
            state = row['admin_name'].strip()
            country = row['country'].strip()
            unique_locations.add((city, state, country))
except FileNotFoundError:
    print(f"Warning: {CITIES_CSV} not found, skipping")

# Now create fixtures for all unique locations
for city, state, country in sorted(unique_locations):
    if not city or not country:  # Skip invalid locations
        continue

    location_key = (city, state, country)
    if location_key not in location_keys:
        fixtures.append({
            "model": f"{APP_LABEL}.location",
            "pk": loc_pk,
            "fields": {
                "city": city,
                "state": state,
                "country": country,
                "created_at": NOW_ISO,
            }
        })
        location_keys[location_key] = loc_pk
        loc_pk += 1

print(f"✓ Created {len(location_keys)} unique locations")

# ─── 2) EVENTS + OBSERVATIONS ─────────────────────────────────────────────────
print("Creating events and observations...")
event_lookup = {}  # (name, date, loc_pk) -> pk

# Process main events CSV
try:
    with open(EVENTS_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            name = row['Event Name'].strip()
            date = row['Date'].strip()  # YYYY-MM-DD

            # Skip if critical data is missing
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

            # match your event location
            city = row.get('City', '').strip()
            state = row.get('State', '').strip()
            country = row.get('Country', '').strip()
            loc_key = (city, state, country)

            # Skip if location is invalid
            if not loc_key[0] or not loc_key[2] or loc_key not in location_keys:
                print(f"⚠️ Skipping event with unknown location: {loc_key}")
                continue

            loc_id = location_keys[loc_key]

            ev_key = (name, date, loc_id)
            if ev_key not in event_lookup:
                fixtures.append({
                    "model": f"{APP_LABEL}.event",
                    "pk": event_pk,
                    "fields": {
                        "name": name,
                        "date": date,
                        "location": loc_id,
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
                    "event": ev_id,
                    "count": cnt,
                    "timestamp": f"{date}T12:00:00Z",
                    "method": method,
                    "observer": who,
                    "created_at": NOW_ISO,
                }
            })
            obs_pk += 1
except FileNotFoundError:
    print(f"Warning: {EVENTS_CSV} not found, skipping")

# ─── 2A) SHEET-BASED EVENTS (no observation data) ─────────────────────────────
try:
    with open(SHEET_EVENTS_CSV, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            name = row.get('Event Name', '').strip()
            city = row.get('City', '').strip()

            # Skip if critical data is missing
            if not name or not city:
                print(f"⚠️ Skipping sheet event with missing name or city: {row}")
                continue

            state = "Indiana"
            country = 'United States'
            loc_key = (city, state, country)

            # Skip if location is invalid
            if loc_key not in location_keys:
                print(f"⚠️ Skipping sheet event with unknown location: {loc_key}")
                continue

            # Parse date
            date = None
            try:
                date = parse_date_flexibly(row['Date'])
            except (ValueError, KeyError) as e:
                print(f"⚠️ Skipping sheet event: {e}")
                continue

            loc_id = location_keys[loc_key]
            ev_key = (name, date, loc_id)

            if ev_key not in event_lookup:
                fixtures.append({
                    "model": f"{APP_LABEL}.event",
                    "pk": event_pk,
                    "fields": {
                        "name": name,
                        "date": date,
                        "location": loc_id,
                        "created_at": NOW_ISO,
                    }
                })
                event_lookup[ev_key] = event_pk
                event_pk += 1
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
    if manual_event_key not in event_lookup:
        fixtures.append({
            "model": f"{APP_LABEL}.event",
            "pk": event_pk,
            "fields": {
                "name": manual_event_name,
                "date": manual_event_date,
                "location": manual_loc_id,
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
                "event": manual_event_id,
                "count": count,
                "timestamp": f"{manual_event_date}T12:00:00Z",
                "method": "AI",
                "observer": None,
                "input_image": "inputs/3ec5d7a4baaf4881ba433f714f7e4cc5_signal-2025-04-19-170902.jpeg",
                "density_map": f'density_maps/{density}',
                "model_name": model,
                "weight_selection": weight,
                "created_at": NOW_ISO,
            }
        })
        obs_pk += 1

# ─── 3) DUMP FIXTURE ───────────────────────────────────────────────────────────
with open(FIXTURE_FILE, 'w', encoding='utf-8') as out:
    json.dump(fixtures, out, indent=2)

print(f"✅ Wrote {len(fixtures)} records to {FIXTURE_FILE}")
print(f"  - {len(location_keys)} locations")
print(f"  - {len(event_lookup)} events")
print(f"  - {len(fixtures) - len(location_keys) - len(event_lookup)} observations")
