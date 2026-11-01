# Copyright (c) 2026 Albert Wong
# SPDX-License-Identifier: MIT
import json
import signal
import sys
from tempfile import TemporaryDirectory

from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import AirbyteMessage, AirbyteMessageSerializer, Type

from .source import SourceRedisAdbc


def _terminate(signum, frame):
    # Raise through active context managers to release readers and cursors.
    raise KeyboardInterrupt


def message_to_json(message):
    envelope = AirbyteMessageSerializer.dump(message)
    if message.type == Type.RECORD:
        # CDK 7.45.0 uses serpyco omit_none=True, which also removes nulls
        # inside arbitrary record dictionaries. Omit optional envelope fields,
        # then restore the converted record data, including nested NULLs.
        envelope["record"]["data"] = message.record.data
    return json.dumps(envelope, ensure_ascii=False, allow_nan=False)


def launch(source, args):
    """Use the pinned CDK's parser, validation and command handlers.

    Its run() hardcodes the default serializer, so dispatch here to preserve
    explicit NULL record values. Never monkeypatch the CDK's global serializer.
    """
    entrypoint = AirbyteEntrypoint(source)
    parsed = entrypoint.parse_args(args)
    if parsed.command is None:
        raise SystemExit("Expected spec, check, discover or read")
    spec = source.spec(entrypoint.logger)
    if parsed.command == "spec":
        print(message_to_json(AirbyteMessage(type=Type.SPEC, spec=spec)), flush=True)
        return
    with TemporaryDirectory() as temp_dir:
        config = source.configure(source.read_config(parsed.config), temp_dir)
        if parsed.command == "check":
            messages = entrypoint.check(spec, config)
        elif parsed.command == "discover":
            messages = entrypoint.discover(spec, config)
        else:
            messages = entrypoint.read(spec, config, source.read_catalog(parsed.catalog), source.read_state(parsed.state))
        try:
            for message in messages:
                print(message_to_json(message), flush=True)
        finally:
            messages.close()


def main():
    signal.signal(signal.SIGTERM, _terminate)
    launch(SourceRedisAdbc(), sys.argv[1:])


if __name__ == "__main__":
    main()
