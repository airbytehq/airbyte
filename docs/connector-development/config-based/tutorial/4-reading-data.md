# Step 4: Reading data

Now that we're able to authenticate to the source API, we'll want to select data from the HTTP responses.
Let's first add the stream to the configured catalog in `source-exchange-rates-tutorial/integration_tests/configured_catalog.json`

```json
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

The configured catalog declares the sync modes supported by the stream (full refresh or incremental).
See the [catalog guide](https://docs.airbyte.io/understanding-airbyte/beginners-guide-to-catalog) for more information.

Let's define the stream schema in `source-exchange-rates-tutorial/source_exchange_rates_tutorial/schemas/rates.json`

You can download the JSON file describing the output schema with all currencies [here](https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-cdk/python/docs/tutorials/http_api_source_assets/exchange_rates.json) for convenience and place it in `schemas/`.

```bash
curl https://raw.githubusercontent.com/airbytehq/airbyte/master/airbyte-cdk/python/docs/tutorials/http_api_source_assets/exchange_rates.json > source_exchange_rates_tutorial/schemas/rates.json
```

We can also delete the boilerplate schema files

```bash
rm source_exchange_rates_tutorial/schemas/customers.json
rm source_exchange_rates_tutorial/schemas/employees.json
```

As an alternative to storing the stream's data schema to the `schemas/` directory, we can store it inline in the YAML file, by including the optional `schema_loader` key and associated schema in the entry for each stream. More information on how to define a stream's schema in the YAML file can be found [here](../understanding-the-yaml-file/yaml-overview.md).

Reading from the source can be done by running the `read` operation

```bash
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json
```

The logs should show that 1 record was read from the stream.

```
{"type": "LOG", "log": {"level": "INFO", "message": "Read 1 records from rates stream"}}
{"type": "LOG", "log": {"level": "INFO", "message": "Finished syncing rates"}}
```

The `--debug` flag can be set to print out debug information, including the outgoing request and its associated response

```bash
python main.py read --config secrets/config.json --catalog integration_tests/configured_catalog.json --debug
```

## Next steps

We now have a working implementation of a connector reading the latest exchange rates for a given currency.
We're however limited to only reading the latest exchange rate value.
Next, we'll [enhance the connector to read data for a given date, which will enable us to backfill the stream with historical data](5-incremental-reads.md).

## More readings

- [Record selector](../understanding-the-yaml-file/record-selector.md)
- [Catalog guide](https://docs.airbyte.io/understanding-airbyte/beginners-guide-to-catalog)
