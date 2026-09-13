"""A connector image without its ERPL extensions still passes `spec`.

`spec` reads a YAML file; it never opens DuckDB, so it cannot distinguish a
working image from one whose extensions were dropped somewhere in the build --
which is exactly what happens if the artefacts stop arriving through the
`erpl-extensions` dependency, since Airbyte's image template copies only
/usr/local and /airbyte/integration_code out of its builder stage.

`check` against an unreachable SAP host is the cheap discriminator: it has to
load the extensions before it can fail at the network, so the *kind* of failure
tells us which of the two we have. It needs no credentials and no SAP system,
which is why it is the one connection case Airbyte's CI still runs.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INVALID_CONFIG = HERE / "invalid_config.json"
INIT_FAILURE = "Failed to initialise the ERPL extensions"


def _messages(image: str) -> list[dict]:
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{INVALID_CONFIG}:/tmp/config.json:ro",
            image,
            "check",
            "--config",
            "/tmp/config.json",
        ],
        capture_output=True,
        text=True,
        timeout=600,
    )
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip().startswith("{")]


@pytest.mark.image_tests
def test_check_fails_at_sap_not_at_the_extensions(connector_image_override: str | None) -> None:
    # The CDK's plugin owns --connector-image; default to what bin/build-image.sh tags.
    messages = _messages(connector_image_override or "airbyte/source-sap:dev")
    assert messages, "the image produced no Airbyte messages at all"

    text = json.dumps(messages)
    assert INIT_FAILURE not in text, (
        "the image starts but cannot load the ERPL extensions -- the artefacts did not "
        "survive the build. Check that erpl-extensions is a resolved dependency."
    )

    statuses = [m["connectionStatus"]["status"] for m in messages if m.get("type") == "CONNECTION_STATUS"]
    traces = [m for m in messages if m.get("type") == "TRACE"]
    assert statuses or traces, "check neither reported a status nor traced an error"
    if statuses:
        assert statuses[0] == "FAILED", "an unreachable host must not check out as succeeded"
