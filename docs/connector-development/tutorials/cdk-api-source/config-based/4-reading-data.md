# Step 3: Reading data

Now that we're able to authenticate to the source API, we'll want to extract data from the responses.
Let's first add the stream to the configured catalog in `source-exchange-rates-tutorial/integration_tests/configured_catalog.json`
```
{
  "streams": [
    {
      "stream": {
        "name": "rates",
        "json_schema": {},
        "supported_sync_modes": [
          "full_refresh"
        ]
      },
      "sync_mode": "full_refresh",
      "destination_sync_mode": "overwrite"
    }
  ]
}
```


Let's define the stream schema in `source-exchange-rates-tutorial/source_exchange_rates_tutorial/schemas/rates.json`
Note that we're only going to sync exchanges rates with CAD, EUR, and USD for simplicity. Other currencies can be added to the schema as needed.
```
{
  "type": "object",
  "required": [
    "base",
    "date",
    "rates"
  ],
  "properties": {
    "base": {
      "type": "string"
    },
    "date": {
      "type": "string"
    },
    "rates": {
      "type": "object",
      "properties": {
        "CAD": {
          "type": [
            "null",
            "number"
          ]
        },
        "EUR": {
          "type": [
            "null",
            "number"
          ]
        },
        "USD": {
          "type": [
            "null",
            "number"
          ]
        }
      }
    }
  }
}
```

Next, we'll update the record selection to wrap the single record returned in the response in an array,
and set the primary key to "date"
```
rates_stream:
  options:
    name: "rates"
    primary_key: "date"
    url_base: "https://api.exchangeratesapi.io/v1/"
    schema_loader:
      file_path: "./source_exchange_rates_tutorial/schemas/{{name}}.json"
    retriever:
      requester:
        path: "/latest"
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

Finally, we also need to add the start date to the config file
echo '{"access_key": "<your-access-key>", "start_date": "2022-01-01", "base": "USD"}'  > secrets/config.json


Reading from the source can be done by running the `read` operation
```
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

The logs should show that 1 record was read from the stream.
```
{"type": "LOG", "log": {"level": "INFO", "message": "Read 1 records from rates stream"}}
{"type": "LOG", "log": {"level": "INFO", "message": "Finished syncing rates"}}
```

## Next steps
We now have a working implementation of a connector reading the latest exchange rates for a given currency.
We can stop here and move on to productionizing this source,
 or we can ([enhance the connector to read data for a given date, which will enable us to backfill the stream with historical data.](5-iterating.md)
## TODO: point to the next steps...