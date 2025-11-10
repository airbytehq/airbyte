import json
from components import AmazonGrafanaSource

with open("config.json") as f:
    config = json.load(f)

source = AmazonGrafanaSource(manifest_path="manifest.yaml", config=config)

print("Pobieranie danych użytkowników (token tworzony automatycznie)...")

# Pobierz strumienie z konfiguracją
streams = source.streams(config)

# Znajdź strumień 'users' (lub pierwszy jeśli jest jeden)
users_stream = next((s for s in streams if s.name == "users"), streams[0])

records = list(users_stream.read_records())

print(f"Pobrano {len(records)} rekordów:")

for record in records:
    print(record)