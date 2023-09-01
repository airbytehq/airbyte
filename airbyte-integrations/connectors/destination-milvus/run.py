# load examples/messages_10k.json
import json

from destination_milvus import DestinationMilvus
from airbyte_cdk.models import ConfiguredAirbyteCatalog, AirbyteMessage


def load():
    with open('examples/messages_10k.jsonl', 'r') as f:
        return [AirbyteMessage(**json.loads(line)) for line in f.readlines()]

examples_messages_10k_json = load()

# load config
with open('secrets/config.json', 'r') as f:
    config = json.load(f)

# load catalog
with open('examples/configured_catalog.json', 'r') as f:
    catalog = json.load(f)

dest = DestinationMilvus()

list(dest.write(config, ConfiguredAirbyteCatalog(**catalog), examples_messages_10k_json))

