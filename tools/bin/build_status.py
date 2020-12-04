#!/usr/bin/env python3

from collections import defaultdict
import requests
import json

"""
Create tools/bin/secrets/build_status.json with the secret in the "build stat secrets" in LastPass
"""

with open('tools/bin/secrets/build_status.json') as f:
    secrets = json.load(f)

res = requests.get(f"https://kvdb.io/{secrets['bucket']}/?values=true&format=json",
                   auth=(secrets['secret_key'], '')).json()

connector_to_states = defaultdict(list)

for stat in res:
    connector = stat[0][0:stat[0].rfind('-')]
    run_id = stat[0][stat[0].rfind('-') + 1:len(stat[0])]
    status = stat[1][0:stat[1].rfind('-')]
    timestamp = stat[1][stat[1].rfind('-') + 1:len(stat[1])]
    connector_to_states[connector].append([timestamp, run_id, status])

print("-" * 81)


def get_terminal_link_str(text, url):
    return f"\u001b]8;;{url}\u001b\\{text}\u001b]8;;\u001b\\"


for connector, states in connector_to_states.items():
    sorted_states = sorted(states, key=lambda x: -1*int(x[0]))
    line_items = [connector]
    for i in range(0, 10):
        if i < len(sorted_states):
            state = sorted_states[i]
            timestamp = state[0]
            run_id = state[1]
            status = state[2]
            url = f"https://github.com/airbytehq/airbyte/actions/runs/{run_id}"

            if status == "success":
                line_items.append(get_terminal_link_str("✅", url))
            elif status == "in_progress":
                line_items.append(get_terminal_link_str("🕑", url))
            elif status == "failure":
                line_items.append(get_terminal_link_str("❌", url))
            else:
                print(f"ERROR: unknown status {status}")
                exit(1)
        else:
            line_items.append("⬜")
    print(
        "{:<50} {:<1} {:<1} {:<1} {:<1} {:<1} {:<1} {:<1} {:<1} {:<1} {:<1}".format(
            line_items[0],
            line_items[1],
            line_items[2],
            line_items[3],
            line_items[4],
            line_items[5],
            line_items[6],
            line_items[7],
            line_items[8],
            line_items[9],
            line_items[10]
        ))
    print("-" * 81)
