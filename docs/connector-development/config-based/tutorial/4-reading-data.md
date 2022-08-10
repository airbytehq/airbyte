# Step 4: Reading data

Now that we're able to authenticate to the source API, we'll want to select data from the HTTP responses.
Let's first add the stream to the configured catalog in `source-exchange_rates-tutorial/integration_tests/configured_catalog.json`

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

Next, we'll update the record selection to wrap the single record returned by the source in an array in `source_exchange_rates_tutorial/exchange_rates_tutorial.yamlsource_exchange_rates_tutorial/exchange_rates_tutorial.yaml`

```yaml
definitions:
  <...>
  selector:
    type: RecordSelector
    extractor:
      type: JelloExtractor
      transform: "[_]" # wrap the single record returned by the API in an array
```

The transform is defined using the `Jello` syntax, which is a Python-based JQ alternative. More details on Jello can be found [here](https://github.com/kellyjonbrazil/jello).

Here is the complete connector definition for convenience:

```yaml
version: "0.1.0"

definitions:
  schema_loader:
    type: JsonSchema
    file_path: "./source_exchange_rates_tutorial/schemas/{{ options['name'] }}.json"
  selector:
    type: RecordSelector
    extractor:
      type: JelloExtractor
      transform: "[_]" # wrap the single record returned by the API in an array
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
        path: "/exchangerates_data/latest"
check:
  type: CheckStream
  stream_names: [ "rates" ]
```

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

- [Record selector](../record-selector.md)