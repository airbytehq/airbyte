# Concurrent

In this section, we'll improve the connector performance by reading multiple stream slices in
parallel.

Let's update the source. The bulk of the change is changing its parent class to
`ConcurrentSourceAdapter`, and updating its `__init__` method so it's properly initialized. This
requires a little bit of boilerplate:

```python
# import the following libraries
import logging
import pendulum
from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.models import Level
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter, ConcurrentSource
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message.repository import InMemoryMessageRepository
```

```python
class SourceSurveyMonkeyDemo(ConcurrentSourceAdapter):
    message_repository = InMemoryMessageRepository(Level(AirbyteLogFormatter.level_mapping[_logger.level]))

    def __init__(self, config: Optional[Mapping[str, Any]], state: Optional[Mapping[str, Any]]):
        if config:
            concurrency_level = min(config.get("num_workers", _DEFAULT_CONCURRENCY), _MAX_CONCURRENCY)
        else:
            concurrency_level = _DEFAULT_CONCURRENCY
        _logger.info(f"Using concurrent cdk with concurrency level {concurrency_level}")
        concurrent_source = ConcurrentSource.create(
            concurrency_level, concurrency_level // 2, _logger, self._slice_logger, self.message_repository
        )
        super().__init__(concurrent_source)
        self._config = config
        self._state = state

    def _get_slice_boundary_fields(self, stream: Stream, state_manager: ConnectorStateManager) -> Optional[Tuple[str, str]]:
        return ("start_date", "end_date")
```

We'll also need to update the `streams` method to wrap the streams in an adapter class to enable
concurrency.
```python
# import the following libraries
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField, ConcurrentCursor, FinalStateCursor
```


```python
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(config["access_token"])

        survey_stream = SurveyMonkeyBaseStream(name="surveys", path="/v3/surveys", primary_key="id", data_field="data", authenticator=auth, cursor_field="date_modified")
        synchronous_streams = [
            survey_stream,
            SurveyMonkeySubstream(name="survey_responses", path="/v3/surveys/{stream_slice[id]}/responses/", primary_key="id", authenticator=auth, parent_stream=survey_stream)
        ]
        state_manager = ConnectorStateManager(stream_instance_map={s.name: s for s in synchronous_streams}, state=self._state)

        configured_streams = []

        for stream in synchronous_streams:

            if stream.cursor_field:
                cursor_field = CursorField(stream.cursor_field)
                legacy_state = state_manager.get_stream_state(stream.name, stream.namespace)
                cursor = ConcurrentCursor(
                    stream.name,
                    stream.namespace,
                    legacy_state,
                    self.message_repository,
                    state_manager,
                    stream.state_converter,
                    cursor_field,
                    self._get_slice_boundary_fields(stream, state_manager),
                    pendulum.from_timestamp(_START_DATE),
                    EpochValueConcurrentStreamStateConverter.get_end_provider()
                )
            else:
                cursor = FinalStateCursor(stream.name, stream.namespace, self.message_repository)
            configured_streams.append (
                StreamFacade.create_from_stream(stream,
                                                self,
                                                _logger,
                                                legacy_state,
                                                cursor)
                )
        return configured_streams
```

The most interesting piece from this block is the use of `ConcurrentCursor` to support concurrent
state management.

The survey responses stream does not support incremental reads, so it's using a `FinalStateCursor`
instead. The rest of the code change is mostly boilerplate.

We'll also add a state converter to the `SurveyMonkeyBaseStream` to describe how the state cursor is
formatted. We'll use the `EpochValueConcurrentStreamStateConverter` since the `get_updated_state`
method returns the cursor as a timestamp

```python
# import the following library
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import EpochValueConcurrentStreamStateConverter
```

```
state_converter = EpochValueConcurrentStreamStateConverter()
```

Next we'll add a few missing constants:

```
_DEFAULT_CONCURRENCY = 10
_MAX_CONCURRENCY = 10
_RATE_LIMIT_PER_MINUTE = 120
_logger = logging.getLogger("airbyte")
```

---

:::info

The substream isn't entirely concurrent because its stream_slices definition reads records from the
parent stream concurrently:

```python
    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for _slice in self._parent_stream.stream_slices():
            for parent_record in self._parent_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=_slice):
                yield parent_record
```

This can be solved by implementing the connector using constructs from the concurrent CDK directly
instead of wrapping synchronous streams in an adapter. This is left outside of the scope of this
tutorial because no production connectors currently implement this.

:::

We'll now enable throttling to avoid going over the API rate limit. You can do this by configuring a
moving window rate limit policy for the `SurveyMonkeyBaseStream` class:

```python
# import the following libraries
from airbyte_cdk.sources.streams.call_rate import MovingWindowCallRatePolicy, HttpAPIBudget, Rate
```

```python
class SurveyMonkeyBaseStream(HttpStream, ABC):
    def __init__(self, name: str, path: str, primary_key: Union[str, List[str]], data_field: Optional[str], cursor_field: Optional[str],
**kwargs: Any) -> None:
        self._name = name
        self._path = path
        self._primary_key = primary_key
        self._data_field = data_field
        self._cursor_field = cursor_field
        super().__init__(**kwargs)

        policies = [
            MovingWindowCallRatePolicy(
                rates=[Rate(limit=_RATE_LIMIT_PER_MINUTE, interval=datetime.timedelta(minutes=1))],
                matchers=[],
            ),
        ]
        api_budget = HttpAPIBudget(policies=policies)
        super().__init__(api_budget=api_budget, **kwargs)
```

Finally, update the `run.py` file to properly instantiate the class. Most of this code is
boilerplate code and isn't specific to the Survey Monkey connector.

```python
#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import sys
import traceback
from datetime import datetime
from typing import List

from airbyte_cdk.entrypoint import AirbyteEntrypoint, launch
from airbyte_cdk.models import AirbyteErrorTraceMessage, AirbyteMessage, AirbyteTraceMessage, TraceType, Type

from .source import SourceSurveyMonkeyDemo

def _get_source(args: List[str]):
    config_path = AirbyteEntrypoint.extract_config(args)
    state_path = AirbyteEntrypoint.extract_state(args)
    try:
        return SourceSurveyMonkeyDemo(
            SourceSurveyMonkeyDemo.read_config(config_path) if config_path else None,
            SourceSurveyMonkeyDemo.read_state(state_path) if state_path else None,
        )
    except Exception as error:
        print(
            AirbyteMessage(
                type=Type.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.ERROR,
                    emitted_at=int(datetime.now().timestamp() * 1000),
                    error=AirbyteErrorTraceMessage(
                        message=f"Error starting the sync. This could be due to an invalid configuration or catalog. Please contact Support for assistance. Error: {error}",
                        stack_trace=traceback.format_exc(),
                    ),
                ),
            ).json()
        )
        return None



def run():
    args = sys.argv[1:]
    source = _get_source(args)
    launch(source, args)
```

You can now run a read operation again. The connector will read multiple partitions concurrently
instead of looping through all of them sequentially.

```bash
poetry run source-survey-monkey-demo read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

We're now done! We implemented a Python connector covering many features:

- Fast and reproducible integration tests
- Authentication errors are detected and labeled as such
- One stream supports incremental reads
- One stream depends on another stream

The final code can be found [here](https://github.com/girarda/airbyte/tree/survey_monkey_demo)
