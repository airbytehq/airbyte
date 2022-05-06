#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.cac.factory import LowCodeComponentFactory


class CheckStream:
    # FIXME: needs to implemeent an interface
    def __init__(self, stream_config, vars, config):
        print(f"stream_config: {stream_config}")
        streamconfig = stream_config["stream"]
        print(f"stremconfig.config: {streamconfig}")
        self._stream_config = stream_config
        print(f"created chck stream with: {self._stream_config}")

    def check_connection(self, config):
        try:
            print(f"stream: {self._stream_config}")
            stream = LowCodeComponentFactory().build(self._stream_config["stream"], self._stream_config.get("vars", {}), config)
            print("stream was created!!!!!")
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except Exception as error:
            return False, f"Unable to connect to stream {self._stream_config} - {error}"
