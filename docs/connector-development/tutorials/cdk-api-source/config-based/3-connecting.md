# Step 3: Connecting to the API

We're now ready to start implementing the connector.

The code generator already created a boilerplate connector definition in  `source-exchange-rates-tutorial/source_exchange_rates_tutorial/connector_definition.yaml`

```
<TODO>_stream:
  options:
    name: "<TODO>"
    primary_key: "<TODO>"
    url_base: "<TODO>"
    schema_loader:
      file_path: "./source_exchange_rates_tutorial/schemas/{{name}}.json"
    retriever:
      requester:
        path: "<TODO>"
        authenticator:
          type: "TokenAuthenticator"
          token: "<TODO>"
      record_selector:
        extractor:
          transform: "<TODO>"

streams:
  - "*ref(<TODO>_stream)"
check:
  stream_names:
    - "<TODO>>"

```

Let's fill this out these TODOs with the information found in the exchange rates api docs https://exchangeratesapi.io/documentation/

1. First, let's name the stream "rates".

```
rates_stream:
  options:
    name: "rates"
```

and update the references in the streams list and check block

```
streams:
  - "*ref(rates_stream)"
check:
  stream_names:
    - "rates"
```

2. Next we'll set the base url and the API path.
   According to the API documentation, the base url is "https://api.exchangeratesapi.io/v1/" and we can fetch the latest data by submitting a request to "/latest".

```
    url_base: "https://api.exchangeratesapi.io/v1/"
    retriever:
      requester:
        path: "/latest"
```

3. Next, we'll set up the authentication.
   The Exchange Rates API requires an access key, which we'll need to make accessible to our connector.
   We'll configure the connector to use this access key by setting the access key in a request parameter and pointing to a field in the config, which we'll populate in the next step:

> > > > > > > FIXME: while writing this, I'm thinking it would make sense to have a few simple Authenticator wrapper classes
> > > > > > None, BasicAuth, Bearer Token,ApiKey, OAuth2
> > > > > > > The alternate connector definition could look like

```
requester:
  authenticator:
    api_key: "{{ config.access_key }}"
    pass_by: "request_parameters"
```

<<<<<<<<<

```
    retriever:
      requester:
        path: "/latest"
        request_options_provider:
          request_parameters:
            access_key: "{{ config.access_key }}"
```

4. According to the ExchangeRatesApi documentation, we can specify the base currency we're interested in in a request parameter:

```
        request_options_provider:
          request_parameters:
            access_key: "{{ config.access_key }}"
            base: "{{ config.base }}"
      record_selector:
        extractor:
          transform: "_"
```

5. Let's populate the config so the connector can access the access key and base currency.
   First, we'll add these properties to the connect spec in
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

We also need to fill in the connection config in the `secrets/config.json`
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