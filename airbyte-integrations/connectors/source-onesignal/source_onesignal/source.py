#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterator, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import SyncMode, ConfiguredAirbyteStream, AirbyteMessage
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig

from .streams import Apps, Devices, Notifications, Outcomes


class SourceOnesignal(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = TokenAuthenticator(config["user_auth_key"], "Basic")
            stream = Apps(authenticator=authenticator, config=config)
            records = stream.read_records(sync_mode=SyncMode.full_refresh)
            next(records)
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}")

        authenticator = TokenAuthenticator(config["user_auth_key"], "Basic")
        args = { "authenticator": authenticator, "config": config }
        apps = Apps(**args)
        args = { "parent": apps, **args }

        return [apps, Devices(**args), Notifications(**args), Outcomes(**args)]

    # Override AbstractSource._read_incremental() function to emit an extra state
    # message after finishing syncing the whole stream.
    # It is for updating the maximum cursor field date state, because the cursor
    # time isn't sorted across stream slices. There is no way to get the
    # maximum cursor field time unless reading until the end of the stream.
    # This is a dirty hack and might be removed if HttpStream provided an
    # end-of-synching-stream event hook in the future.
    # This hack only applies to incremental streams, that is, Devices and Notifications.
    def _read_incremental(
        self,
        logger: AirbyteLogger,
        stream: Stream,
        configured_stream: ConfiguredAirbyteStream,
        connector_state: MutableMapping[str, Any],
        internal_config: InternalConfig,
    ) -> Iterator[AirbyteMessage]:
        yield from super()._read_incremental(logger, stream, configured_stream, connector_state, internal_config)

        stream_name = configured_stream.stream.name
        stream_state = connector_state.get(stream_name, {})
        state_date = stream_state.get(stream.cursor_field, stream.start_date)
        stream_state = { stream.cursor_field: max(state_date, stream.max_cursor_time) }

        yield self._checkpoint_state(stream_name, stream_state, connector_state, logger)
