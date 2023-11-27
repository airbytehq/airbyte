import json
import logging
import tempfile

from contextlib import redirect_stdout
from io import StringIO
from itertools import groupby
from pathlib import Path
from typing import Any, List, Mapping, Optional, Union

from airbyte_cdk.entrypoint import launch
from airbyte_cdk.logger import AirbyteLogFormatter, init_logger
from airbyte_protocol.models import AirbyteMessage, Type


class CommandOutput:
    def __init__(self, messages):
        self._messages_per_type = {message_type: list(messages_for_type) for message_type, messages_for_type in groupby((AirbyteMessage.parse_obj(json.loads(message)) for message in messages), lambda message: message.type)}

    @property
    def records(self) -> List[AirbyteMessage]:
        return self._messages_per_type[Type.RECORD]


def read(source, config, catalog):
    log_capture_buffer = StringIO()
    stream_handler = logging.StreamHandler(log_capture_buffer)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.formatter = AirbyteLogFormatter()
    # This seems odd as not all sources need to use the logger name `airbyte` for a source to work
    logger = init_logger("airbyte")
    logger.addHandler(stream_handler)

    with tempfile.TemporaryDirectory() as tmp_directory:
        with redirect_stdout(log_capture_buffer):
            tmp_directory_path = Path(tmp_directory)
            launch(
                source,
                [
                    "read",
                    "--config",
                    make_file(tmp_directory_path / "config.json", config),
                    "--catalog",
                    make_file(tmp_directory_path / "catalog.json", catalog.json()),
                ],
            )
            captured = log_capture_buffer.getvalue().split("\n")[:-1]
            return CommandOutput(captured)


def make_file(path: Path, file_contents: Optional[Union[str, Mapping[str, Any], List[Mapping[str, Any]]]]) -> str:
    if isinstance(file_contents, str):
        path.write_text(file_contents)
    else:
        path.write_text(json.dumps(file_contents))
    return str(path)
