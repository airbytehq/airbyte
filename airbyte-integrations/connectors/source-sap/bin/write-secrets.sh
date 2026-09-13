#!/usr/bin/env bash
# Write secrets/config.json from the same environment the e2e suite uses.
#
# Airbyte's standard connector tests (integration_tests/) read their config from
# secrets/config.json, which is gitignored and therefore absent on a fresh
# checkout -- so without this the standard suite silently never runs.
set -euo pipefail
cd "$(dirname "$0")/.."

: "${ERPL_SAP_ASHOST:?set the SAP environment first (see bin/test-e2e.sh)}"
mkdir -p secrets

python3 - <<'PY'
import json
import os
import pathlib
import subprocess

# The standard connector tests run the image on Docker's default bridge, where
# "localhost" is the container, not the host. The bridge gateway reaches SAP
# from both the host and a container, so it works for every caller.
ashost = os.environ["ERPL_SAP_ASHOST"]
if ashost in ("localhost", "127.0.0.1"):
    ashost = os.environ.get("ERPL_SAP_DOCKER_ASHOST") or (
        subprocess.run(
            ["docker", "network", "inspect", "bridge",
             "--format", "{{(index .IPAM.Config 0).Gateway}}"],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
        or ashost
    )

config = {
    "ashost": ashost,
    "sysnr": os.environ.get("ERPL_SAP_SYSNR", "00"),
    "client": os.environ.get("ERPL_SAP_CLIENT", "001"),
    "user": os.environ.get("ERPL_SAP_USER", "DEVELOPER"),
    "password": os.environ.get("ERPL_SAP_PASSWORD", ""),
    "lang": os.environ.get("ERPL_SAP_LANG", "EN"),
    "concurrency": 2,
    "protocol": {"mode": "rfc", "table_pattern": "SFLIGHT"},
}
base_url = os.environ.get("ERPL_SAP_BASE_URL")
if base_url:
    config["base_url"] = base_url.replace("localhost", ashost).replace("127.0.0.1", ashost)

path = pathlib.Path("secrets/config.json")
path.write_text(json.dumps(config, indent=2) + "\n")
path.chmod(0o600)
print(f"wrote {path}")
PY
