# Step 5: Testing

We should make sure the connector respects the Airbyte specifications before we start using it in production.
This can be done by executing the Source-Acceptance Tests (SAT).

These tests will assert the most basic functionalities work as expected and are configured in `acceptance-test-config`.

Before running the tests, we'll create an invalid config to make sure the `check` operation fails if the credentials are wrong, and an abnormal state to verify the connector's behavior when running with an abnormal state.

Update `integration_tests/invalid_config.json` with this content

```
{"access_key": "<invalid_key>", "start_date": "2022-07-21", "base": "USD"}
```

and `integration_tests/abnormal_state.json` with

```
{
  "rates": {
    "date": "2999-12-31"
  }
}

```

You can build the connector's docker image and run the acceptance tests by running the following commands:

```
docker build . -t airbyte/source-exchange-rates-tutorial:dev
python -m pytest integration_tests -p integration_tests.acceptance
```

1 test should be failing

```
airbyte-integrations/bases/source-acceptance-test/source_acceptance_test/tests/test_core.py:183 TestConnection.test_check[inputs1]
```

This test is failing because the `check` operation is succeeding even with invalid credentials.
This can be confirmed by running

```
python main.py check --config integration_tests/invalid_config.json
```

The `--debug` flag can be used to inspect the response:

```
python main.py check --debug --config integration_tests/invalid_config.json
```

You should see a message similar to this one:

```
{"type": "DEBUG", "message": "Receiving response", "data": {"headers": "{'Date': 'Thu, 28 Jul 2022 17:56:31 GMT', 'Content-Type': 'application/json; Charset=UTF-8', 'Transfer-Encoding': 'chunked', 'Connection': 'keep-alive', 'cache-control': 'no-cache', 'access-control-allow-methods': 'GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS', 'access-control-allow-origin': '*', 'x-blocked-at-loadbalancer': '1', 'CF-Cache-Status': 'DYNAMIC', 'Expect-CT': 'max-age=604800, report-uri=\"https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct\"', 'Report-To': '{\"endpoints\":[{\"url\":\"https:\\\\/\\\\/a.nel.cloudflare.com\\\\/report\\\\/v3?s=MpyuXqiuxH%2FEA1%2F75CQiP4bPOt0DKeg9utWdBShkseCK9f4G8R9K126fe65nIvsKWQVGMTou%2BeTRCq%2FCzgoxr2B1BT%2Bm3l6i0DFDu5sYAqHAWzd9pSoqJZ6jktjQgB5D%2BqG7jQvhIDnK\"}],\"group\":\"cf-nel\",\"max_age\":604800}', 'NEL': '{\"success_fraction\":0,\"report_to\":\"cf-nel\",\"max_age\":604800}', 'Server': 'cloudflare', 'CF-RAY': '731f7df109709e68-SJC', 'Content-Encoding': 'gzip'}", "status": "200", "body": "{\n  \"success\": false,\n  \"error\": {\n    \"code\": 101,\n    \"type\": \"invalid_access_key\",\n    \"info\": \"You have not supplied a valid API Access Key. [Technical Support: support@apilayer.com]\"\n  }\n}\n"}}
```

The endpoint is returning a 200 HTTP response, but the message contains an error, which our connector isn't handling.

This can be fixed by adding an error handler to the requester:

```
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.exchangeratesapi.io/v1/"
  http_method: "GET"
  request_options_provider:
    request_parameters:
      access_key: "{{ config.access_key }}"
      base: "{{ config.base }}"
  error_handler:
    response_filters:
      - action: FAIL
        predicate: "{{ 'error' in response }}"
```

The `check` operation should now fail

```
python main.py check --debug --config integration_tests/invalid_config.json
```

and the acceptance tests should pass

```
docker build . -t airbyte/source-exchange-rates-tutorial:dev
python -m pytest integration_tests -p integration_tests.acceptance
```

Here is the full connector definition for reference:

```
schema_loader:
  class_name: airbyte_cdk.sources.declarative.schema.json_schema.JsonSchema
  name: "rates"
  file_path: "./source_exchange_rates_tutorial/schemas/{{ options.name }}.json"
selector:
  type: RecordSelector
  extractor:
    type: JelloExtractor
    transform: "[_]"
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.exchangeratesapi.io/v1/"
  http_method: "GET"
  request_options_provider:
    request_parameters:
      access_key: "{{ config.access_key }}"
      base: "{{ config.base }}"
stream_slicer:
  type: "DatetimeStreamSlicer"
  start_datetime:
    datetime: "{{ config.start_date }}"
    datetime_format: "%Y-%m-%d"
  end_datetime:
    datetime: "{{ now_local() }}"
    datetime_format: "%Y-%m-%d %H:%M:%S.%f"
  step: "1d"
  datetime_format: "%Y-%m-%d"
  cursor_field: "{{ options.cursor_field }}"
retriever:
  type: SimpleRetriever
  name: "{{ options['name'] }}"
  primary_key: "{{ options['primary_key'] }}"
  record_selector:
    ref: "*ref(selector)"
  paginator:
    type: NoPagination
rates_stream:
  type: DeclarativeStream
  $options:
    name: "rates"
    cursor_field: "date"
  primary_key: "date"
  schema_loader:
    ref: "*ref(schema_loader)"
  retriever:
    ref: "*ref(retriever)"
    stream_slicer:
      ref: "*ref(stream_slicer)"
    requester:
      ref: "*ref(requester)"
      path:
        type: "InterpolatedString"
        string: "{{ stream_slice.start_date }}"
        default: "/latest"
      error_handler:
        response_filters:
          - predicate: "{{'error' in response}}"
            action: FAIL
streams:
  - "*ref(rates_stream)"
check:
  type: CheckStream
  stream_names: ["rates"]
```

## Next steps:

Next, we'll add the connector to the [Airbyte platform](https://docs.airbyte.com/connector-development/tutorials/cdk-tutorial-python-http/use-connector-in-airbyte).

## Read more:

- [Error handling](../error-handling.md)
- [Pagination](../pagination.md)
- [Testing connectors](../../testing-connectors/README.md)