# Python CDK Speedrun: Creating a Source

## CDK Speedrun \(HTTP API Source Creation [Any%](https://en.wikipedia.org/wiki/Speedrun#:~:text=Any%25%2C%20or%20fastest%20completion%2C,the%20game%20to%20its%20fullest.&text=Specific%20requirements%20for%20a%20100,different%20depending%20on%20the%20game.) Route\)

This is a blazing fast guide to building an HTTP source connector. Think of it as the TL;DR version of [this tutorial.](cdk-tutorial-python-http/getting-started.md)

## Dependencies

1. Python &gt;= 3.9
2. Docker
3. NodeJS

#### Generate the Template

```bash
$ cd airbyte-integrations/connector-templates/generator # start from repo root
$ ./generate.sh
```

Select the `Python HTTP API Source` and name it `python-http-example`.

#### Create Dev Environment

```bash
cd ../../connectors/source-python-http-example
python -m venv .venv # Create a virtual environment in the .venv directory
source .venv/bin/activate
pip install -r requirements.txt
```

### Define Connector Inputs

```bash
cd source_python_http_example
```

We're working with the Exchange Rates API, so we need to define our input schema to reflect that. Open the `spec.json` file here and replace it with:

```javascript
{
  "documentationUrl": "https://docs.airbyte.io/integrations/sources/exchangeratesapi",
  "connectionSpecification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Python Http Example Spec",
    "type": "object",
    "required": ["start_date", "currency_base"],
    "properties": {
      "start_date": {
        "type": "string",
        "description": "Start getting data from that date.",
        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
        "examples": ["%Y-%m-%d"]
      },
      "base": {
        "type": "string",
        "examples": ["USD", "EUR"],
        "description": "ISO reference currency. See <a href=\"https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html\">here</a>."
      }
    }
  }
}
```

Ok, let's write a function that checks the inputs we just defined. Nuke the `source.py` file. Now add this code to it. For a crucial time skip, we're going to define all the imports we need in the future here.

```python
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import NoAuth

class SourcePythonHttpExample(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        accepted_currencies = {
            "USD",
            "JPY",
            "BGN",
            "CZK",
            "DKK",
        }  # there are more currencies but let's assume these are the only allowed ones
        input_currency = config["base"]
        if input_currency not in accepted_currencies:
            return False, f"Input currency {input_currency} is invalid. Please input one of the following currencies: {accepted_currencies}"
        else:
            return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        # Parse the date from a string into a datetime object.
        start_date = datetime.strptime(config["start_date"], "%Y-%m-%d")
        
        # NoAuth just means there is no authentication required for this API and is included for completeness.
        # Skip passing an authenticator if no authentication is required.
        # Other authenticators are available for API token-based auth and Oauth2. 
        auth = NoAuth()
        return [ExchangeRates(authenticator=auth, base=config["base"], start_date=start_date)]
```

Test it.

```bash
cd ..
mkdir sample_files
echo '{"start_date": "2021-04-01", "base": "USD"}'  > sample_files/config.json
echo '{"start_date": "2021-04-01", "base": "BTC"}'  > sample_files/invalid_config.json
python main.py check --config sample_files/config.json
python main.py check --config sample_files/invalid_config.json
```

Expected output:

```text
> python main.py check --config sample_files/config.json
{"type": "CONNECTION_STATUS", "connectionStatus": {"status": "SUCCEEDED"}}

> python main.py check --config sample_files/invalid_config.json
{"type": "CONNECTION_STATUS", "connectionStatus": {"status": "FAILED", "message": "Input currency BTC is invalid. Please input one of the following currencies: {'DKK', 'USD', 'CZK', 'BGN', 'JPY'}"}}
```

### Define your Stream

In your `source.py` file, add this `ExchangeRates` class. This stream represents an endpoint you want to hit.

```python
from airbyte_cdk.sources.streams.http import HttpStream

class ExchangeRates(HttpStream):
    url_base = "https://api.exchangeratesapi.io/"

    # Set this as a noop.
    primary_key = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination, so we return None to indicate there are no more pages in the response
        return None

    def path(
        self, 
    ) -> str:
        return ""  # TODO

    def parse_response(
        self,
    ) -> Iterable[Mapping]:
        return None  # TODO
```

Now download [this file](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/docs/tutorials/http_api_source_assets/exchange_rates.json). Name it `exchange_rates.json` and place it in `/source_python_http_example/schemas`. It defines your output schema.

Test your discover function. You should receive a fairly large JSON object in return.

```bash
python main.py discover --config sample_files/config.json
```

### Reading Data from the Source

Update your `ExchangeRates` class to implement the required functions as follows:

```python
class ExchangeRates(HttpStream):
    url_base = "https://api.exchangeratesapi.io/"

    primary_key = None

    def __init__(self, base: str, **kwargs):
        super().__init__()
        self.base = base


    def path(
            self,
            stream_state: Mapping[str, Any] = None,
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> str:
        # The "/latest" path gives us the latest currency exchange rates
        return "latest"

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        # The api requires that we include the base currency as a query param so we do that in this method
        return {'base': self.base}

    def parse_response(
            self,
            response: requests.Response,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        # The response is a simple JSON whose schema matches our stream's schema exactly, 
        # so we just return a list containing the response
        return [response.json()]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # The API does not offer pagination, 
        # so we return None to indicate there are no more pages in the response
        return None
```

Update your `streams` method in your `SourcePythonHttpExample` class to use the currency base passed in from the stream above.

```python
def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        return [ExchangeRates(authenticator=auth, base=config['base'])]
```

We now need a catalog that defines all of our streams. We only have one, `ExchangeRates`. Download that file [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/docs/tutorials/http_api_source_assets/configured_catalog.json). Place it in `/sample_files` named as `configured_catalog.json`.

Let's read some data.

```bash
python main.py read --config sample_files/config.json --catalog sample_files/configured_catalog.json
```

If all goes well, containerize it so you can use it in the UI:

```bash
docker build . -t airbyte/source-python-http-example:dev
```

You're done. Stop the clock :\)

