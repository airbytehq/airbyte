#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import io
import json
from unittest.mock import patch

from destination_typesense.destination import DestinationTypesense


RECORD = {
    "type": "RECORD",
    "record": {"stream": "products", "data": {"id": "1", "title": "Typesense"}, "emitted_at": 1_791_302_400_000},
}

STREAM_STATE = {
    "type": "STATE",
    "state": {
        "type": "STREAM",
        "stream": {"stream_descriptor": {"name": "products"}, "stream_state": {"updated_at": "2026-11-01"}},
        "sourceStats": {"recordCount": 1.0},
        "id": 42,
    },
}

GLOBAL_STATE = {
    "type": "STATE",
    "state": {
        "type": "GLOBAL",
        "global": {
            "shared_state": {"lsn": 123},
            "stream_states": [{"stream_descriptor": {"name": "products"}, "stream_state": {"updated_at": "2026-11-01"}}],
        },
        "id": "abc",
    },
}

LEGACY_STATE = {
    "type": "STATE",
    "state": {"type": "LEGACY", "data": {"products": {"updated_at": "2026-11-01"}}, "id": 44},
}

CATALOG = {
    "streams": [
        {
            "stream": {"name": "products", "json_schema": {"type": "object"}, "supported_sync_modes": ["incremental"]},
            "sync_mode": "incremental",
            "destination_sync_mode": "append",
        }
    ]
}


def test_write_echoes_state_messages_with_their_id(tmp_path, capsys):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"api_key": "key", "host": "localhost"}))
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(CATALOG))
    states = [STREAM_STATE, GLOBAL_STATE, LEGACY_STATE]
    stdin = io.TextIOWrapper(io.BytesIO("\n".join(json.dumps(message) for message in [RECORD, *states]).encode()))

    with patch("sys.stdin", stdin), patch("destination_typesense.destination.Client"):
        DestinationTypesense().run(["write", "--config", str(config_path), "--catalog", str(catalog_path)])

    output = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [message for message in output if message["type"] == "STATE"] == states
