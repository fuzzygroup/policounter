import os
import json
import django
import sys
from django.db import connection
from django.db.models import Count

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "policounter.settings")
django.setup()

from counter.models import Location, Event, Observation

# ─── PART 1: Analyze existing data ───────────────────────────────────────────────
print("Analyzing existing data...")

# Count records
location_count = Location.objects.count()
event_count = Event.objects.count()
observation_count = Observation.objects.count()

print(f"Database contains:")
print(f"  - {location_count} locations")
print(f"  - {event_count} events")
print(f"  - {observation_count} observations")

# Check for duplicate locations
duplicates = Location.objects.values('city', 'state', 'country').annotate(count=Count('id')).filter(count__gt=1)

if duplicates.exists():
    print(f"\nFound {duplicates.count()} sets of duplicate locations:")
    for dup in duplicates:
        print(f"- {dup['city']}, {dup['state']}, {dup['country']} ({dup['count']} occurrences)")
        # List all instances
        instances = Location.objects.filter(city=dup['city'], state=dup['state'], country=dup['country'])
        for instance in instances:
            print(f"  ID: {instance.id}")
else:
    print("\nNo duplicate locations found.")

# ─── PART 2: Fix the fixtures ─────────────────────────────────────────────────
print("\nFixing fixtures...")

# Path to your fixtures file
FIXTURE_FILE = 'fixtures/data.json'
OUTPUT_FILE = 'fixtures/data_fixed.json'

# Load the fixtures
try:
    with open(FIXTURE_FILE, 'r', encoding='utf-8') as f:
        fixtures = json.load(f)

    print(f"Loaded {len(fixtures)} records from {FIXTURE_FILE}")
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"Error loading fixtures: {e}")
    sys.exit(1)

# Track seen locations to avoid duplicates
seen_locations = {}  # (city, state, country) -> pk

# Track location ids to update
location_id_map = {}  # old_pk -> new_pk

# Process all fixtures to identify location duplicates
location_fixtures = []
other_fixtures = []

for fixture in fixtures:
    if fixture['model'] == 'counter.location':
        fields = fixture['fields']
        location_key = (fields['city'], fields['state'], fields['country'])

        if location_key in seen_locations:
            # This is a duplicate location - map its ID to the existing one
            location_id_map[fixture['pk']] = seen_locations[location_key]
        else:
            # First time seeing this location
            seen_locations[location_key] = fixture['pk']
            location_fixtures.append(fixture)
    else:
        other_fixtures.append(fixture)

print(f"Found {len(location_id_map)} duplicate locations")

# Update references in events
location_reference_updates = 0
for fixture in other_fixtures:
    if fixture['model'] == 'counter.event':
        old_loc_id = fixture['fields']['location']
        if old_loc_id in location_id_map:
            fixture['fields']['location'] = location_id_map[old_loc_id]
            location_reference_updates += 1

print(f"Updated {location_reference_updates} event references to locations")

# Combine the unique locations with the updated other fixtures
fixed_fixtures = location_fixtures + other_fixtures

# Write the fixed fixtures
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(fixed_fixtures, f, indent=2)

print(f"Wrote {len(fixed_fixtures)} records to {OUTPUT_FILE}")
print(f"  - {len(location_fixtures)} unique locations")
print(f"  - {len(other_fixtures)} other records")

# ─── PART 3: Instructions for next steps ─────────────────────────────────────
print("\n=== WHAT TO DO NEXT ===")
print("1. If you want to clear the database and load fresh data:")
print("   - For MySQL: SET FOREIGN_KEY_CHECKS=0;")
print("                TRUNCATE TABLE counter_observation;")
print("                TRUNCATE TABLE counter_event;")
print("                TRUNCATE TABLE counter_location;")
print("                SET FOREIGN_KEY_CHECKS=1;")
print("   - For PostgreSQL: TRUNCATE TABLE counter_observation CASCADE;")
print("                     TRUNCATE TABLE counter_event CASCADE;")
print("                     TRUNCATE TABLE counter_location CASCADE;")
print("\n2. Load the fixed fixtures:")
print("   python manage.py loaddata fixtures/data_fixed.json")
print("\n3. Verify that all data was loaded correctly:")
print("   python manage.py shell")
print("   from counter.models import Location, Event, Observation")
print("   print(f\"Locations: {Location.objects.count()}\")")
print("   print(f\"Events: {Event.objects.count()}\")")
print("   print(f\"Observations: {Observation.objects.count()}\")")
