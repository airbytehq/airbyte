# Step 3: Connecting to the API

We're now ready to start implementing the connector.

The code generator already created a boilerplate connector definition in  `source-exchange-rates-tutorial/source_exchange_rates_tutorial/exchange_rates_tutorial.yaml`

```
schema_loader:
  type: JsonSchema
  file_path: "./source_exchange_rates_tutorial/schemas/{{ name }}.json"
selector:
  type: RecordSelector
  extractor:
    type: JelloExtractor
    transform: "_"
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: TODO "your_api_base_url"
  http_method: "GET"
  authenticator:
    type: TokenAuthenticator
    token: "{{ config['api_key'] }}"
retriever:
  type: SimpleRetriever
  name: "{{ options['name'] }}"
  primary_key: "{{ options['primary_key'] }}"
  record_selector:
    ref: "*ref(selector)"
  paginator:
    type: NoPagination
  state:
    class_name: airbyte_cdk.sources.declarative.states.dict_state.DictState
customers_stream:
  type: DeclarativeStream
  options:
    name: "customers"
  primary_key: "id"
  schema_loader:
    ref: "*ref(schema_loader)"
  retriever:
    ref: "*ref(retriever)"
    requester:
      ref: "*ref(requester)"
      path: TODO "your_endpoint_path"
streams:
  - "*ref(customers_stream)"
check:
  type: CheckStream
  stream_names: ["customers_stream"]
```

Let's fill this out these TODOs with the information found in the [Exchange Rates API docs](https://exchangeratesapi.io/documentation/)

1. First, let's rename the stream from `customers` to `rates.

```
rates_stream:
  type: DeclarativeStream
  options:
    name: "rates"
```

and update the references in the streams list and check block

```
streams:
  - "*ref(rates_stream)"
check:
  type: CheckStream
  stream_names: ["rates_stream"]
```

2. Next we'll set the base url.
   According to the API documentation, the base url is `"https://api.exchangeratesapi.io/v1/"`.
   This can be set in the requester definition.

```
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.exchangeratesapi.io/v1/"
```

3. We can fetch the latest data by submitting a request to "/latest". This path is specific to the stream, so we'll set within the `rates_stream` definition.

```
rates_stream:
  type: DeclarativeStream
  options:
    name: "rates"
  primary_key: "id"
  schema_loader:
    ref: "*ref(schema_loader)"
  retriever:
    ref: "*ref(retriever)"
    requester:
      ref: "*ref(requester)"
      path: "/latest"
```

4. Next, we'll set up the authentication.
   The Exchange Rates API requires an access key, which we'll need to make accessible to our connector.
   We'll configure the connector to use this access key by setting the access key in a request parameter and pointing to a field in the config, which we'll populate in the next step:

```
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.exchangeratesapi.io/v1/"
  http_method: "GET"
  request_options_provider:
    request_parameters:
      access_key: "{{ config.access_key }}"
```

5. According to the ExchangeRatesApi documentation, we can specify the base currency of interest in a request parameter:

```
request_options_provider:
  request_parameters:
    access_key: "{{ config.access_key }}"
    base: "{{ config.base }}"
```

6. Let's populate the config so the connector can access the access key and base currency.
   First, we'll add these properties to the connector spec in
   `source-exchange-rates-tutorial/source_exchange_rates_tutorial/spec.yaml`

```
documentationUrl: https://docs.airbyte.io/integrations/sources/exchangeratesapi
connectionSpecification:
  $schema: http://json-schema.org/draft-07/schema#
  title: exchangeratesapi.io Source Spec
  type: object
  required:
    - access_key
    - base
  additionalProperties: false
  properties:
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

7. We also need to fill in the connection config in the `secrets/config.json`
   Because of the sensitive nature of the access key, we recommend storing this config in the `secrets` directory because it is ignored by git.

```
echo '{"access_key": "<your_access_key>", "base": "USD"}'  > secrets/config.json
```

We can now run the `check` operation, which verifies the connector can connect to the API source.

```
python main.py check --config secrets/config.json
```

which should now succeed with logs similar to:

```
{"type": "LOG", "log": {"level": "INFO", "message": "Check succeeded"}}
{"type": "CONNECTION_STATUS", "connectionStatus": {"status": "SUCCEEDED"}}
```

## Next steps

Next, we'll [extract the records from the response](4-reading-data.md)