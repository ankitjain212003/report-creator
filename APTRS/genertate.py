import json
import os

# ✅ Correct path to your input JSON file
with open('location_api/fixture/cities.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixture = []
state_ids = {}
state_pk = 1
city_pk = 1

for entry in data:
    state_name = entry['state']
    city_name = entry['name']

    # Add state if not already added
    if state_name not in state_ids:
        fixture.append({
            "model": "location_api.state",
            "pk": state_pk,
            "fields": {
                "name": state_name
            }
        })
        state_ids[state_name] = state_pk
        state_pk += 1

    # Add city
    fixture.append({
        "model": "location_api.city",
        "pk": city_pk,
        "fields": {
            "name": city_name,
            "state": state_ids[state_name]
        }
    })
    city_pk += 1

# ✅ Save to a different output file to avoid overwrite errors
os.makedirs('location_api/fixtures', exist_ok=True)

with open('location_api/fixtures/states_and_cities.json', 'w', encoding='utf-8') as f:
    json.dump(fixture, f, ensure_ascii=False, indent=2)

print("✅ Fixture generated successfully: location_api/fixtures/states_and_cities.json")
