# Step 5: Incremental Reads

We now have a working implementation of a connector reading the latest exchange rates for a given currency.
In this section, we'll update the source to read historical data instead of only reading the latest exchange rates.

According to the API documentation, we can read the exchange rate for a specific date by querying the `"/exchangerates_data/{date}"` endpoint instead of `"/exchangerates_data/latest"`.

We'll now add a `start_date` property to the connector.

First we'll update the spec block in `source_exchange_rates_tutorial/manifest.yaml`

```yaml
spec:
  documentation_url: https://docs.airbyte.com/integrations/sources/exchangeratesapi
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
    $ref: "#/definitions/base_stream"
    $parameters:
      name: "rates"
      primary_key: "date"
      path: "/exchangerates_data/{{config['start_date'] or 'latest'}}"
```

You can test these changes by executing the `read` operation:

```bash
poetry run source-exchange-rates-tutorial read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

By reading the output record, you should see that we read historical data instead of the latest exchange rate.
For example:

> "historical": true, "base": "USD", "date": "2022-07-18"

The connector will now always read data for the start date, which is not exactly what we want.
Instead, we would like to iterate over all the dates between the `start_date` and today and read data for each day.

We can do this by adding a `DatetimeBasedCursor` to the connector definition, and update the `path` to point to the stream_slice's `start_date`:

More details on incremental syncs can be found [here](../understanding-the-yaml-file/incremental-syncs.md).

Let's first define a datetime cursor at the top level of the connector definition:

```yaml
definitions:
  datetime_cursor:
    type: "DatetimeBasedCursor"
    start_datetime:
      datetime: "{{ config['start_date'] }}"
      datetime_format: "%Y-%m-%d"
    end_datetime:
      datetime: "{{ now_utc() }}"
      datetime_format: "%Y-%m-%d %H:%M:%S.%f+00:00"
    step: "P1D"
    datetime_format: "%Y-%m-%d"
    cursor_granularity: "P1D"
    cursor_field: "date"
```

and refer to it in the stream.

This will generate time windows from the start time until the end time, where each window is exactly one day.
The start time is defined in the config file, while the end time is defined by the `now_utc()` macro, which will evaluate to the current date in the current timezone at runtime. See the section on [string interpolation](../advanced-topics/string-interpolation.md) for more details.

```yaml
definitions:
  <...>
  rates_stream:
    $ref: "#/definitions/base_stream"
    $parameters:
      name: "rates"
      primary_key: "date"
      path: "/exchangerates_data/{{config['start_date'] or 'latest'}}"
```

We'll also update the base stream to use the datetime cursor:

```yaml
definitions:
  <...>
  base_stream:
    <...>
    incremental_sync:
      $ref: "#/definitions/datetime_cursor"
```

Finally, we'll update the path to point to the `stream_slice`'s start_time

```yaml
definitions:
  <...>
  rates_stream:
    $ref: "#/definitions/base_stream"
    $parameters:
      name: "rates"
      primary_key: "date"
      path: "/exchangerates_data/{{stream_slice['start_time'] or 'latest'}}"
```

The full connector definition should now look like `./source_exchange_rates_tutorial/manifest.yaml`:

```yaml
version: "0.1.0"

definitions:
  selector:
    extractor:
      field_path: []
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
  datetime_cursor:
    type: "DatetimeBasedCursor"
    start_datetime:
      datetime: "{{ config['start_date'] }}"
      datetime_format: "%Y-%m-%d"
    end_datetime:
      datetime: "{{ now_utc() }}"
      datetime_format: "%Y-%m-%d %H:%M:%S.%f+00:00"
    step: "P1D"
    datetime_format: "%Y-%m-%d"
    cursor_granularity: "P1D"
    cursor_field: "date"
  retriever:
    record_selector:
      $ref: "#/definitions/selector"
    paginator:
      type: NoPagination
    requester:
      $ref: "#/definitions/requester"
  base_stream:
    incremental_sync:
      $ref: "#/definitions/datetime_cursor"
    retriever:
      $ref: "#/definitions/retriever"
  rates_stream:
    $ref: "#/definitions/base_stream"
    $parameters:
      name: "rates"
      primary_key: "date"
      path: "/exchangerates_data/{{stream_slice['start_time'] or 'latest'}}"
streams:
  - "#/definitions/rates_stream"
check:
  stream_names:
    - "rates"
spec:
  documentation_url: https://docs.airbyte.com/integrations/sources/exchangeratesapi
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
poetry run source-exchange-rates-tutorial read --config secrets/config.json --catalog integration_tests/configured_catalog.json
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
        "supported_sync_modes": ["full_refresh", "incremental"]
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
poetry run source-exchange-rates-tutorial read --config secrets/config.json --catalog integration_tests/configured_catalog.json --state integration_tests/sample_state.json
```

There shouldn't be any data read if the state is today's date:

```
{"type": "LOG", "log": {"level": "INFO", "message": "Setting state of rates stream to {'date': '2022-07-15'}"}}
{"type": "LOG", "log": {"level": "INFO", "message": "Read 0 records from rates stream"}}
```

## Next steps:

Next, we'll run the [Connector Acceptance Tests suite to ensure the connector invariants are respected](6-testing.md).

## More readings

- [Incremental syncs](../understanding-the-yaml-file/incremental-syncs.md)
- [Partition routers](../understanding-the-yaml-file/partition-router.md)
- [Stream slices](../../cdk-python/stream-slices.md)
