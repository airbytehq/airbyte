# Step 5: Incremental Reads

We now have a working implementation of a connector reading the latest exchange rates for a given currency.
In this section, we'll update the source to read historical data instead of only reading the latest exchange rates.

According to the API documentation, we can read the exchange rate for a specific date by querying the `"/exchangerates_data/{date}"` endpoint instead of `"/exchangerates_data/latest"`.

We'll now add a `start_date` property to the connector.

First we'll update the spec `source_exchange_rates_tutorial/spec.yaml`

```yaml
documentationUrl: https://docs.airbyte.io/integrations/sources/exchangeratesapi
connectionSpecification:
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
streams:
  - type: DeclarativeStream
    $options:
      name: "rates"
    primary_key: "rates"
    schema_loader:
      $ref: "*ref(definitions.schema_loader)"
    retriever:
      $ref: "*ref(definitions.retriever)"
      requester:
        $ref: "*ref(definitions.requester)"
        path: "/exchangerates_data/{{config['start_date'] or 'latest'}}"
```

You can test these changes by executing the `read` operation:

```bash
$ python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

By reading the output record, you should see that we read historical data instead of the latest exchange rate.
For example:
> "historical": true, "base": "USD", "date": "2022-07-18"

The connector will now always read data for the start date, which is not exactly what we want.
Instead, we would like to iterate over all the dates between the `start_date` and today and read data for each day.

We can do this by adding a `DatetimeStreamSlicer` to the connector definition, and update the `path` to point to the stream_slice's `start_date`:

More details on the stream slicers can be found [here](../stream-slicers.md).

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
      datetime: "{{ now_local() }}"
      datetime_format: "%Y-%m-%d %H:%M:%S.%f"
    step: "1d"
    datetime_format: "%Y-%m-%d"
    cursor_field: "{{ options['stream_cursor_field'] }}"
  retriever:
    <...>
```

and refer to it in the stream's retriever.
This will generate slices from the start time until the end time, where each slice is exactly one day.
The start time is defined in the config file, while the end time is defined by the `now_local()` macro, which will evaluate to the current date in the current timezone at runtime. See the section on [string interpolation](../yaml-structure.md#string-interpolation) for more details.

Note that we're also setting the `stream_cursor_field` in the stream's `$options` so it can be accessed by the `StreamSlicer`:

```yaml
streams:
  - type: DeclarativeStream
    $options:
      name: "rates"
      stream_cursor_field: "date"
    primary_key: "rates"
    <...>
```

We'll also update the retriever to user the stream slicer:

```yaml
definitions:
  <...>
  retriever:
    type: SimpleRetriever
    <...>
    stream_slicer:
      $ref: "*ref(definitions.stream_slicer)"
```

Finally, we'll update the path to point to the `stream_slice`'s start_time

```yaml
streams:
  - type: DeclarativeStream
    <...>
    retriever:
      $ref: "*ref(definitions.retriever)"
      requester:
        $ref: "*ref(definitions.requester)"
        path: "/exchangerates_data/{{stream_slice['start_time'] or 'latest'}}"
```

The full connector definition should now look like `./source_exchange_rates_tutorial/exchange_rates_tutorial.yaml`:

```yaml
version: "0.1.0"

definitions:
  schema_loader:
    type: JsonSchema
    file_path: "./source_exchange_rates_tutorial/schemas/{{ options['name'] }}.json"
  selector:
    type: RecordSelector
    extractor:
      type: DpathExtractor
      field_pointer: [ ]
  requester:
    type: HttpRequester
    name: "{{ options['name'] }}"
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
      datetime: "{{ now_local() }}"
      datetime_format: "%Y-%m-%d %H:%M:%S.%f"
    step: "1d"
    datetime_format: "%Y-%m-%d"
    cursor_field: "{{ options['stream_cursor_field'] }}"
  retriever:
    type: SimpleRetriever
    $options:
      url_base: "https://api.apilayer.com"
    name: "{{ options['name'] }}"
    primary_key: "{{ options['primary_key'] }}"
    record_selector:
      $ref: "*ref(definitions.selector)"
    paginator:
      type: NoPagination
    stream_slicer:
      $ref: "*ref(definitions.stream_slicer)"

streams:
  - type: DeclarativeStream
    $options:
      name: "rates"
      stream_cursor_field: "date"
    primary_key: "rates"
    schema_loader:
      $ref: "*ref(definitions.schema_loader)"
    retriever:
      $ref: "*ref(definitions.retriever)"
      requester:
        $ref: "*ref(definitions.requester)"
        path: "/exchangerates_data/{{stream_slice['start_time'] or 'latest'}}"
check:
  type: CheckStream
  stream_names: [ "rates" ]

```

Running the `read` operation will now read all data for all days between start_date and now:

```bash
$ python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
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
$ python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json --state integration_tests/sample_state.json
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
- [Stream slicers](../stream-slicers.md)
- [Stream slices](../../cdk-python/stream-slices.md)