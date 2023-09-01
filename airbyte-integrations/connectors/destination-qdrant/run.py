# load examples/messages_10k.json
import json


def load():
    with open('examples/messages_10k.json', 'r') as f:
        return json.load(f)

dest = 