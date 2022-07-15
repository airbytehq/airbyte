# Step 3: Connecting to the API

We're now ready to start implementing the connector.


The first step is ensure the connector can connect to the API source.


This can be done by running the `check` operation, which verifies the connector can connect to the API source.
```
python main.py  check
```
It should fail with the following error, which is expected because we haven't implemented anything yet
```
Config validation error: 'TODO' is a required property
```

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

1. First, let's name the stream "rates"
```
rates_stream:
  options:
    name: "rates"
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
  - "*ref(rates_stream)"
check:
  stream_names:
    - "rates"
```

2. Next we'll set the base url and the API path.
According to the API documentation, the base url is "https://api.exchangeratesapi.io/v1/" and we can fetch the latest data by submitting a request to "/latest".
```
rates_stream:
  options:
    name: "rates"
    primary_key: "<TODO>"
    url_base: "https://api.exchangeratesapi.io/v1/"
    schema_loader:
      file_path: "./source_exchange_rates_tutorial/schemas/{{name}}.json"
    retriever:
      requester:
        path: "/latest"
        authenticator:
          type: "TokenAuthenticator"
          token: "<TODO>"
      record_selector:
        extractor:
          transform: "_"

streams:
  - "*ref(rates_stream)"
check:
  stream_names:
    - "rates"
```
1. Next, we'll set up the authentication.
The Exchange Rates API requires an access key, which we'll need to make accessible to our connector.
We'll configure the connector to use this access key by setting the access key in a request parameter and pointing to a field in the config, which we'll populate in the next step:
```
rates_stream:
  options:
    name: "rates"
    primary_key: "<TODO>"
    url_base: "https://api.exchangeratesapi.io/v1/"
    schema_loader:
      file_path: "./source_exchange_rates_tutorial/schemas/{{name}}.json"
    retriever:
      requester:
        path: "/latest"
        request_options_provider:
          request_parameters:
            access_key: "{{ config.access_key }}"
      record_selector:
        extractor:
          transform: "_"

streams:
  - "*ref(rates_stream)"
check:
  stream_names:
    - "rates"
```

4. We'll request data for a specific base currency, which can also be set in a request parameter:
```
rates_stream:
  options:
    name: "rates"
    primary_key: "<TODO>"
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
          transform: "_"

streams:
  - "*ref(rates_stream)"
check:
  stream_names:
    - "rates"
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
Next we'll add our access key to the `secrets/config.json`
Because of the sensitive nature of the access key, we recommend storing this config in the `secrets` directory because it is ignored by git. ## TODO: link to the gitignore.
```
echo '{"access_key": "<your_access_key>", "base": "USD"}'  > secrets/config.json
```



We can now run the `check`operation
```
python main.py check --config secrets/config.json
```
which should now succeed
```
{"type": "LOG", "log": {"level": "INFO", "message": "Check succeeded"}}
{"type": "CONNECTION_STATUS", "connectionStatus": {"status": "SUCCEEDED"}}
```

In doubt, we can add the `--debug` flag to see the requests and responses
```
python main.py check --config secrets/config.json --debug
```

This will show the request sent
```
{"type": "DEBUG", "message": "Making outbound API request", "data": {"url": "https://api.exchangeratesapi.io/latest?access_key=****", "headers": "{'User-Agent': 'python-requests/2.28.0', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'}", "request_body": "None"}}
```
As well as the response received
```
{"type": "DEBUG", "message": "Receiving response", "data": {"headers": "{'Date': 'Fri, 15 Jul 2022 18:02:29 GMT', 'Content-Type': 'application/json; Charset=UTF-8', 'Transfer-Encoding': 'chunked', 'Connection': 'keep-alive', 'x-apilayer-transaction-id': '2dc9a690-c3aa-4712-a890-58d6876df6e2', 'access-control-allow-methods': 'GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS', 'access-control-allow-origin': '*', 'x-request-time': '0.011', 'CF-Cache-Status': 'DYNAMIC', 'Expect-CT': 'max-age=604800, report-uri=\"https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct\"', 'Report-To': '{\"endpoints\":[{\"url\":\"https:\\\\/\\\\/a.nel.cloudflare.com\\\\/report\\\\/v3?s=pODyagi4RGtgGwmIMBtTHsYYeUPBZcRlttLOixXWZ2Rl%2BDLU8QLXfuupTpTSWoOTdoFFMC1V9EaqkXc1rP3BtOTb29Cnm0h4VrX9LrrUvvET6UnlPHXvt%2Bg58iIhByaowhF7s55PFnlM\"}],\"group\":\"cf-nel\",\"max_age\":604800}', 'NEL': '{\"success_fraction\":0,\"report_to\":\"cf-nel\",\"max_age\":604800}', 'Server': 'cloudflare', 'CF-RAY': '72b468d01fab9453-SJC', 'Content-Encoding': 'gzip'}", "body": "{\"success\":true,\"timestamp\":1657907823,\"base\":\"EUR\",\"date\":\"2022-07-15\",\"rates\":{\"AED\":3.70151,\"AFN\":88.709769,\"ALL\":117.256492,\"AMD\":416.617835,\"ANG\":1.816774,\"AOA\":435.255575,\"ARS\":129.223106,\"AUD\":1.484189,\"AWG\":1.811403,\"AZN\":1.712353,\"BAM\":1.960118,\"BBD\":2.035452,\"BDT\":94.709572,\"BGN\":1.955879,\"BHD\":0.379904,\"BIF\":2075.369753,\"BMD\":1.007734,\"BND\":1.413884,\"BOB\":6.93056,\"BRL\":5.439646,\"BSD\":1.008105,\"BTC\":4.8425346e-5,\"BTN\":80.466917,\"BWP\":12.907763,\"BYN\":2.544466,\"BYR\":19751.59348,\"BZD\":2.032045,\"CAD\":1.313834,\"CDF\":2017.984854,\"CHF\":0.98546,\"CLF\":0.038375,\"CLP\":1058.876818,\"CNY\":6.809665,\"COP\":4436.57068,\"CRC\":688.506068,\"CUC\":1.007734,\"CUP\":26.704961,\"CVE\":110.506727,\"CZK\":24.502858,\"DJF\":179.094987,\"DKK\":7.443046,\"DOP\":55.031378,\"DZD\":148.297378,\"EGP\":19.02623,\"ERN\":15.116015,\"ETB\":52.616496,\"EUR\":1,\"FJD\":2.2475,\"FKP\":0.848852,\"GBP\":0.849974,\"GEL\":2.96302,\"GGP\":0.848852,\"GHS\":8.190717,\"GIP\":0.848852,\"GMD\":54.508269,\"GNF\":8744.628374,\"GTQ\":7.802568,\"GYD\":210.911357,\"HKD\":7.910866,\"HNL\":24.783212,\"HRK\":7.508602,\"HTG\":116.814525,\"HUF\":400.98809,\"IDR\":15112.841055,\"ILS\":3.491386,\"IMP\":0.848852,\"INR\":80.394531,\"IQD\":1471.393496,\"IRR\":42677.549923,\"ISK\":138.896425,\"JEP\":0.848852,\"JMD\":152.941415,\"JOD\":0.714469,\"JPY\":139.599448,\"KES\":119.164516,\"KGS\":81.595648,\"KHR\":4118.274122,\"KMF\":468.218604,\"KPW\":906.960917,\"KRW\":1330.743377,\"KWD\":0.310402,\"KYD\":0.840154,\"KZT\":485.952994,\"LAK\":15155.050806,\"LBP\":1524.234175,\"LKR\":362.934308,\"LRD\":153.681105,\"LSL\":15.962359,\"LTL\":2.975577,\"LVL\":0.609569,\"LYD\":4.912947,\"MAD\":10.523119,\"MDL\":19.476203,\"MGA\":4244.544699,\"MKD\":61.690564,\"MMK\":1866.590357,\"MNT\":3168.981928,\"MOP\":8.151356,\"MRO\":359.760994,\"MUR\":45.500423,\"MVR\":15.468596,\"MWK\":1034.704357,\"MXN\":20.709858,\"MYR\":4.483404,\"MZN\":64.323951,\"NAD\":15.962297,\"NGN\":418.612885,\"NIO\":36.145065,\"NOK\":10.261129,\"NPR\":128.754949,\"NZD\":1.635765,\"OMR\":0.388014,\"PAB\":1.008105,\"PEN\":3.937012,\"PGK\":3.598002,\"PHP\":56.729876,\"PKR\":212.467665,\"PLN\":4.780238,\"PYG\":6915.326882,\"QAR\":3.669165,\"RON\":4.939815,\"RSD\":117.290318,\"RUB\":58.448489,\"RWF\":1039.794491,\"SAR\":3.783963,\"SBD\":8.223081,\"SCR\":13.528929,\"SDG\":460.067554,\"SEK\":10.569612,\"SGD\":1.410405,\"SHP\":1.388055,\"SLL\":13271.861523,\"SOS\":589.019143,\"SRD\":22.681581,\"STD\":20858.06667,\"SVC\":8.821296,\"SYP\":2531.962243,\"SZL\":17.319385,\"THB\":36.881941,\"TJS\":10.383313,\"TMT\":3.537148,\"TND\":3.08719,\"TOP\":2.383342,\"TRY\":17.478545,\"TTD\":6.847278,\"TWD\":30.166831,\"TZS\":2350.036357,\"UAH\":29.787358,\"UGX\":3800.513405,\"USD\":1.007734,\"UYU\":41.42261,\"UZS\":11038.826802,\"VND\":23636.409442,\"VUV\":119.81561,\"WST\":2.742015,\"XAF\":657.40809,\"XAG\":0.053975,\"XAU\":0.000591,\"XCD\":2.723453,\"XDR\":0.771002,\"XOF\":657.395014,\"XPF\":114.025279,\"YER\":252.185356,\"ZAR\":17.208788,\"ZMK\":9070.861487,\"ZMW\":16.557819,\"ZWL\":324.490053}}", "status": "200"}}
```

## Next steps
Next, we'll [extract the records from the response](4-reading-data.md)