# Step 5: Declare the Schema

The `discover` method of the Airbyte Protocol returns an `AirbyteCatalog`: an object which declares all the streams output by a connector and their schemas. It also declares the sync modes supported by the stream \(full refresh or incremental\). See the [catalog tutorial](https://docs.airbyte.io/understanding-airbyte/beginners-guide-to-catalog) for more information.

This is a simple task with the Airbyte CDK. For each stream in our connector we'll need to: 

1. Create a python `class` in `source.py` which extends `HttpStream`. 
2. Place a `<stream_name>.json` file in the `source_<name>/schemas/` directory. The name of the file should be the snake\_case name of the stream whose schema it describes, and its contents should be the JsonSchema describing the output from that stream.

Let's create a class in `source.py` which extends `HttpStream`. You'll notice there are classes with extensive comments describing what needs to be done to implement various connector features. Feel free to read these classes as needed. But for the purposes of this tutorial, let's assume that we are adding classes from scratch either by deleting those generated classes or editing them to match the implementation below.

We'll begin by creating a stream to represent the data that we're pulling from the Exchange Rates API:

```python
class ExchangeRates(HttpStream):
    url_base = "https://api.apilayer.com/exchangerates_data/"

    # Set this as a noop.
    primary_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination, so we return None to indicate there are no more pages in the response
        return None

    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""  # TODO

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        return None  # TODO
```

Note that this implementation is entirely empty -- we haven't actually done anything. We'll come back to this in the next step. But for now we just want to declare the schema of this stream. We'll declare this as a stream that the connector outputs by returning it from the `streams` method:

```python
from airbyte_cdk.sources.streams.http.auth import NoAuth

class SourcePythonHttpTutorial(AbstractSource):

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        ...

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # NoAuth just means there is no authentication required for this API and is included for completeness.
        # Skip passing an authenticator if no authentication is required.
        # Other authenticators are available for API token-based auth and Oauth2. 
        auth = NoAuth()  
        return [ExchangeRates(authenticator=auth)]
```

Having created this stream in code, we'll put a file `exchange_rates.json` in the `schemas/` folder. You can download the JSON file describing the output schema [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/docs/tutorials/http_api_source_assets/exchange_rates.json) for convenience and place it in `schemas/`.

With `.json` schema file in place, let's see if the connector can now find this schema and produce a valid catalog:

```text
python main.py discover --config secrets/config.json # this is not a mistake, the schema file is found by naming snake_case naming convention as specified above
```

you should see some output like:

```text
{"type": "CATALOG", "catalog": {"streams": [{"name": "exchange_rates", "json_schema": {"$schema": "http://json-schema.org/draft-04/schema#", "type": "object", "properties": {"base": {"type": "string"}, "rates": {"type": "object", "properties": {"GBP": {"type": "number"}, "HKD": {"type": "number"}, "IDR": {"type": "number"}, "PHP": {"type": "number"}, "LVL": {"type": "number"}, "INR": {"type": "number"}, "CHF": {"type": "number"}, "MXN": {"type": "number"}, "SGD": {"type": "number"}, "CZK": {"type": "number"}, "THB": {"type": "number"}, "BGN": {"type": "number"}, "EUR": {"type": "number"}, "MYR": {"type": "number"}, "NOK": {"type": "number"}, "CNY": {"type": "number"}, "HRK": {"type": "number"}, "PLN": {"type": "number"}, "LTL": {"type": "number"}, "TRY": {"type": "number"}, "ZAR": {"type": "number"}, "CAD": {"type": "number"}, "BRL": {"type": "number"}, "RON": {"type": "number"}, "DKK": {"type": "number"}, "NZD": {"type": "number"}, "EEK": {"type": "number"}, "JPY": {"type": "number"}, "RUB": {"type": "number"}, "KRW": {"type": "number"}, "USD": {"type": "number"}, "AUD": {"type": "number"}, "HUF": {"type": "number"}, "SEK": {"type": "number"}}}, "date": {"type": "string"}}}, "supported_sync_modes": ["full_refresh"]}]}}
```

It's that simple! Now the connector knows how to declare your connector's stream's schema. We declare only one stream since our source is simple, but the principle is exactly the same if you had many streams.

You can also dynamically define schemas, but that's beyond the scope of this tutorial. See the [schema docs](../../cdk-python/full-refresh-stream.md#defining-the-streams-schema) for more information.

