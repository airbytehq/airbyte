# Step 5: Incremental Reads

We now have a working implementation of a connector reading the latest exchange rates for a given currency.
In this section, we'll update the source to read historical data instead of only reading the latest exchange rates.

According to the API documentation, we can read the exchange rate for a specific date by querying the `"/exchangerates_data/{date}"` endpoint instead of `"/exchangerates_data/latest"`.

We'll now add a `start_date` property to the connector.

First we'll update the spec block in `source_exchange_rates_tutorial/exchange_rates_tutorial.yaml`

```yaml
spec: 
  documentation_url: https://docs.airbyte.io/integrations/sources/exchangeratesapi
  connection_specification:
    $schema: http://json-schema.org/draft-07/schema#
    title: exchangeratesapi.io Source Spec
    type: object
    required:
      - start_date
      - access_key
      - base
    additionalProperties: true
    properties:
      start_date:
        type: string
        description: Start getting data from that date.
        pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$
        examples:
          - YYYY-MM-DD
      access_key:
        type: string
        description: >-
          Your API Access Key. See <a
          href="https://exchangeratesapi.io/documentation/">here</a>. The key is
          case sensitive.
        airbyte_secret: true
      base:
        type: string
        description: >-
          ISO reference currency. See <a
          href="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html">here</a>.
        examples:
          - EUR
          - USD
```

Then we'll set the `start_date` to last week in our connection config in `secrets/config.json`.
Let's add a start_date field to `secrets/config.json`.
The file should look like

```json
{
  "access_key": "<your_access_key>",
  "start_date": "2022-07-26",
  "base": "USD"
}
```

where the start date should be 7 days in the past.

And we'll update the `path` in the connector definition to point to `/{{ config.start_date }}`.
Note that we are setting a default value because the `check` operation does not know the `start_date`. We'll default to hitting `/exchangerates_data/latest`:

```yaml
definitions:
  <...>
  rates_stream:
    $ref: "*ref(definitions.base_stream)"
    $options:
      name: "rates"
      primary_key: "date"
      path: "/exchangerates_data/{{config['start_date'] or 'latest'}}"
```

You can test these changes by executing the `read` operation:

```bash
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

By reading the output record, you should see that we read historical data instead of the latest exchange rate.
For example:
> "historical": true, "base": "USD", "date": "2022-07-18"

The connector will now always read data for the start date, which is not exactly what we want.
Instead, we would like to iterate over all the dates between the `start_date` and today and read data for each day.

We can do this by adding a `DatetimeStreamSlicer` to the connector definition, and update the `path` to point to the stream_slice's `start_date`:

More details on the stream slicers can be found [here](../understanding-the-yaml-file/stream-slicers.md).

Let's first define a stream slicer at the top level of the connector definition:

```yaml
definitions:
  requester:
    <...>
  stream_slicer:
    type: "DatetimeStreamSlicer"
    start_datetime:
      datetime: "{{ config['start_date'] }}"
      datetime_format: "%Y-%m-%d"
    end_datetime:
      datetime: "{{ now_utc() }}"
      datetime_format: "%Y-%m-%d %H:%M:%S.%f+00:00"
    step: "P1D"
    datetime_format: "%Y-%m-%d"
    cursor_granularity: "P1D"
    cursor_field: "{{ options['stream_cursor_field'] }}"
```

and refer to it in the stream's retriever.
This will generate slices from the start time until the end time, where each slice is exactly one day.
The start time is defined in the config file, while the end time is defined by the `now_utc()` macro, which will evaluate to the current date in the current timezone at runtime. See the section on [string interpolation](../advanced-topics.md#string-interpolation) for more details.

Note that we're also setting the `stream_cursor_field` in the stream's `$options` so it can be accessed by the `StreamSlicer`:

```yaml
definitions:
  <...>
  rates_stream:
    $ref: "*ref(definitions.base_stream)"
    $options:
      name: "rates"
      primary_key: "date"
      path: "/exchangerates_data/{{config['start_date'] or 'latest'}}"
      stream_cursor_field: "date"
```

We'll also update the retriever to user the stream slicer:

```yaml
definitions:
  <...>
  retriever:
    <...>
    stream_slicer:
      $ref: "*ref(definitions.stream_slicer)"
```

This will generate slices from the start time until the end time, where each slice is exactly one day.
The start time is defined in the config file, while the end time is defined by the `now_utc()` macro, which will evaluate to the current date in the current timezone at runtime. See the section on [string interpolation](../advanced-topics.md#string-interpolation) for more details.

Finally, we'll update the path to point to the `stream_slice`'s start_time

```yaml
definitions:
  <...>
  rates_stream:
    $ref: "*ref(definitions.base_stream)"
    $options:
      name: "rates"
      primary_key: "date"
      path: "/exchangerates_data/{{stream_slice['start_time'] or 'latest'}}"
      stream_cursor_field: "date"
```

The full connector definition should now look like `./source_exchange_rates_tutorial/exchange_rates_tutorial.yaml`:

```yaml
version: "0.1.0"

definitions:
  selector:
    extractor:
      field_pointer: [ ]
  requester:
    url_base: "https://api.apilayer.com"
    http_method: "GET"
    authenticator:
      type: ApiKeyAuthenticator
      header: "apikey"
      api_token: "{{ config['access_key'] }}"
    request_options_provider:
      request_parameters:
        base: "{{ config['base'] }}"
  stream_slicer:
    type: "DatetimeStreamSlicer"
    start_datetime:
      datetime: "{{ config['start_date'] }}"
      datetime_format: "%Y-%m-%d"
    end_datetime:
      datetime: "{{ now_utc() }}"
      datetime_format: "%Y-%m-%d %H:%M:%S.%f+00:00"
    step: "P1D"
    datetime_format: "%Y-%m-%d"
    cursor_granularity: "P1D"
    cursor_field: "{{ options['stream_cursor_field'] }}"
  retriever:
    record_selector:
      $ref: "*ref(definitions.selector)"
    paginator:
      type: NoPagination
    requester:
      $ref: "*ref(definitions.requester)"
    stream_slicer:
      $ref: "*ref(definitions.stream_slicer)"
  base_stream:
    retriever:
      $ref: "*ref(definitions.retriever)"
  rates_stream:
    $ref: "*ref(definitions.base_stream)"
    $options:
      name: "rates"
      primary_key: "date"
      path: "/exchangerates_data/{{stream_slice['start_time'] or 'latest'}}"
      stream_cursor_field: "date"
streams:
  - "*ref(definitions.rates_stream)"
check:
  stream_names:
    - "rates"
spec: 
  documentation_url: https://docs.airbyte.io/integrations/sources/exchangeratesapi
  connection_specification:
    $schema: http://json-schema.org/draft-07/schema#
    title: exchangeratesapi.io Source Spec
    type: object
    required:
      - start_date
      - access_key
      - base
    additionalProperties: true
    properties:
      start_date:
        type: string
        description: Start getting data from that date.
        pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$
        examples:
          - YYYY-MM-DD
      access_key:
        type: string
        description: >-
          Your API Access Key. See <a
          href="https://exchangeratesapi.io/documentation/">here</a>. The key is
          case sensitive.
        airbyte_secret: true
      base:
        type: string
        description: >-
          ISO reference currency. See <a
          href="https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html">here</a>.
        examples:
          - EUR
          - USD
```

Running the `read` operation will now read all data for all days between start_date and now:

```bash
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

The operation should now output more than one record:

```
{"type": "LOG", "log": {"level": "INFO", "message": "Read 8 records from rates stream"}}
```

## Supporting incremental syncs

Instead of always reading data for all dates, we would like the connector to only read data for dates we haven't read yet.
This can be achieved by updating the catalog to run in incremental mode (`integration_tests/configured_catalog.json`):

```json
{
  "streams": [
    {
      "stream": {
        "name": "rates",
        "json_schema": {},
        "supported_sync_modes": [
          "full_refresh",
          "incremental"
        ]
      },
      "sync_mode": "incremental",
      "destination_sync_mode": "overwrite"
    }
  ]
}
```

In addition to records, the `read` operation now also outputs state messages:

```
{"type": "STATE", "state": {"data": {"rates": {"date": "2022-07-15"}}}}
```

Where the date ("2022-07-15") should be replaced by today's date.

We can simulate incremental syncs by creating a state file containing the last state produced by the `read` operation.
`source-exchange-rates-tutorial/integration_tests/sample_state.json`:

```json
{
  "rates": {
    "date": "2022-07-15"
  }
}
```

Running the `read` operation will now only read data for dates later than the given state:

```bash
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json --state integration_tests/sample_state.json
```

There shouldn't be any data read if the state is today's date:

```
{"type": "LOG", "log": {"level": "INFO", "message": "Setting state of rates stream to {'date': '2022-07-15'}"}}
{"type": "LOG", "log": {"level": "INFO", "message": "Read 0 records from rates stream"}}
```

## Next steps:

Next, we'll run the [Source Acceptance Tests suite to ensure the connector invariants are respected](6-testing.md).

## More readings

- [Incremental reads](../../cdk-python/incremental-stream.md)
- [Stream slicers](../understanding-the-yaml-file/stream-slicers.md)
- [Stream slices](../../cdk-python/stream-slices.md)
