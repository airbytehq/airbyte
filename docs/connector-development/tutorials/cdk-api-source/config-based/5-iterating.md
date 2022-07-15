# Step 5: Iterating
FIXME: this needs a better title i think

According to the API documentation, we can read the exchange rate for a specific date by querying the "/{date}" endpoint instead of "/latest".

We'll now add a `start_date`property to the connector to support reading historical data.

First we'll update the spec
```
documentationUrl: https://docs.airbyte.io/integrations/sources/exchangeratesapi
connectionSpecification:
  $schema: http://json-schema.org/draft-07/schema#
  title: exchangeratesapi.io Source Spec
  type: object
  required:
    - start_date
    - access_key
    - base
  additionalProperties: false
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

Then we'll update our connection config
echo '{"access_key": "<your-access-key>", "start_date": "2022-01-01", "base": "USD"}'  > secrets/config.json

Then we'll update the path in the connector definition:
```
rates_stream:
  options:
    name: "rates"
    primary_key: ""
    url_base: "https://api.exchangeratesapi.io/v1/"
    schema_loader:
      file_path: "./source_exchange_rates_tutorial/schemas/{{name}}.json"
    retriever:
      requester:
        path: "{{ config.start_date }}"
        request_options_provider:
          request_parameters:
            access_key: "{{ config.access_key }}"
            base: "{{ config.base }}"
      record_selector:
        extractor:
          transform: "[_]"

streams:
  - "*ref(rates_stream)"
check:
  stream_names:
    - "rates"
```

We're now always reading data for the start date, which is not exactly what we want.
Instead, we would like to iterate over all the dates between the start_date and today and read data for each day.

We can do this by adding a DatetimeStreamSlicer to the connector definition, and update the path to point to the stream_slice's start_date:
```
rates_stream:
  options:
    name: "rates"
    primary_key: ""
    url_base: "https://api.exchangeratesapi.io/v1/"
    schema_loader:
      file_path: "./source_exchange_rates_tutorial/schemas/{{name}}.json"
    retriever:
      requester:
        path: "{{ stream_slice.start_date }}"
        request_options_provider:
          request_parameters:
            access_key: "{{ config.access_key }}"
            base: "{{ config.base }}"
      record_selector:
        extractor:
          transform: "[_]"
      stream_slicer:
        type: "DatetimeStreamSlicer"
        start_datetime:
          datetime: "{{ config.start_date }}"
          datetime_format: "%Y-%m-%d"
        end_datetime:
          datetime: "{{ now_local() }}"
          datetime_format: "%Y-%m-%d %H:%M:%S.%f"
        step: "1d"
        cursor_field: "date"
        datetime_format: "%Y-%m-%d"

streams:
  - "*ref(rates_stream)"
check:
  stream_names:
    - "rates"
```

Running the `read` operation will now read all data for all days between start_date and now:
```
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

The operation should now output more than one record:
```
{"type": "LOG", "log": {"level": "INFO", "message": "Read 196 records from rates stream"}}
```

## Supporting incremental syncs
Instead of always reading data for all dates, we would like the connector to only read data for dates we haven't read yet.
This can be achieved by updating the catalog to run in incremental mode:
```
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

We can simulate incremental syncs by creating a state file containing the last state produced by the `read` operation.
`source-exchange-rates-tutorial/integration_tests/sample_state.json`:
```
{
  "rates": {
    "date": "2022-07-15"
  }
}
```

Running the `read` operation will now only read data for dates later than the given state:
```
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json --state integration_tests/sample_state.json
```

There shouldn't be any data read if the state is today's date:
```
{"type": "LOG", "log": {"level": "INFO", "message": "Setting state of rates stream to {'date': '2022-07-15'}"}}
{"type": "LOG", "log": {"level": "INFO", "message": "Read 0 records from rates stream"}}
```

## Next steps:
Next, we'll add the connector to the Airbyte platform.