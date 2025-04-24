# Check and error handling

In this section, we'll implement the check operation, and implement error handling to surface the
user-friendly messages when failing due to authentication errors.

Let's first implement the check operation.

This operation verifies that the input configuration supplied by the user can be used to connect to
the underlying data source.

Use the following command to run the check operation:

```bash
poetry run source-survey-monkey-demo check --config secrets/config.json
```

The command succeed, but it'll succeed even if the config is invalid. We should modify the check so
it fails if the connector is unable to pull any record a stream.

We'll do this by trying to read a single record from the stream, and fail the connector could not
read any.

```python
# import the following libraries
from airbyte_cdk.models import AirbyteMessage, SyncMode
```

```python
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        first_stream = next(iter(self.streams(config)))

        stream_slice = next(iter(first_stream.stream_slices(sync_mode=SyncMode.full_refresh)))

        try:
            read_stream = first_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
            first_record = None
            while not first_record:
                first_record = next(read_stream)
                if isinstance(first_record, AirbyteMessage):
                    if first_record.type == "RECORD":
                        first_record = first_record.record
                        return True, None
                    else:
                        first_record = None
            return True, None
        except Exception as e:
            return False, f"Unable to connect to the API with the provided credentials - {str(e)}"
```

Next, we'll improve the error handling.

First, we'll disable the availability strategy. Availability strategies are a legacy concept used to
filter out streams that might not be available given a user's permissions.
```python
# import this library
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
```

```python
    @property
    def availability_strategy(self) -> Optional[AvailabilityStrategy]:
        return None

```

Instead of using an availability strategy, we'll raise a config error if we're unable to
authenticate:
```python
# import the following library
from airbyte_cdk.utils.traced_exception import AirbyteTracedException, FailureType
```

```python
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        # https://api.surveymonkey.com/v3/docs?shell#error-codes
        if response_json.get("error") in (1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018):
            internal_message = "Unauthorized credentials. Response: {response_json}"
            external_message = "Can not get metadata with unauthorized credentials. Try to re-authenticate in source settings."
            raise AirbyteTracedException(
                message=external_message, internal_message=internal_message, failure_type=FailureType.config_error
            )
        elif self._data_field:
            yield from response_json[self._data_field]
        else:
            yield from response_json
```

The `external_message` will be displayed to the end-user, while the `internal_message` will be
logged for troubleshooting purposes.

In the [next section](./5-discover.md), we'll implement the discover operation.
