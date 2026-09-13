from __future__ import annotations

import sys
import traceback
from datetime import UTC, datetime

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import (
    AirbyteErrorTraceMessage,
    AirbyteMessage,
    AirbyteMessageSerializer,
    AirbyteTraceMessage,
    TraceType,
    Type,
)
from orjson import dumps

from source_sap.source import SourceSap


def _build(args: list[str]) -> SourceSap:
    catalog_path = AirbyteEntrypoint.extract_catalog(args)
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    return SourceSap(
        SourceSap.read_catalog(catalog_path) if catalog_path else None,
        SourceSap.read_config(config_path) if config_path else None,
        SourceSap.read_state(state_path) if state_path else None,
    )


def run() -> None:
    args = sys.argv[1:]
    try:
        source = _build(args)
    except Exception:
        # A failure before the source exists still has to reach the platform as
        # a trace message rather than a bare stack trace on stderr.
        print(
            dumps(
                AirbyteMessageSerializer.dump(
                    AirbyteMessage(
                        type=Type.TRACE,
                        trace=AirbyteTraceMessage(
                            type=TraceType.ERROR,
                            emitted_at=datetime.now(tz=UTC).timestamp() * 1000,
                            error=AirbyteErrorTraceMessage(
                                message="Could not start the SAP source. Check the config, catalog and state files.",
                                stack_trace=traceback.format_exc(),
                            ),
                        ),
                    )
                )
            ).decode()
        )
        raise
    launch(source, args)


if __name__ == "__main__":
    run()
