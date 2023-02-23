# Step 6: Read Data

Describing schemas is good and all, but at some point we have to start reading data! So let's get to work. But before, let's describe what we're about to do:

The `HttpStream` superclass, like described in the [concepts documentation](../../concepts/http-streams.md), is facilitating reading data from HTTP endpoints. It contains built-in functions or helpers for:

* authentication
* pagination
* handling rate limiting or transient errors
* and other useful functionality

In order for it to be able to do this, we have to provide it with a few inputs:

* the URL base and path of the endpoint we'd like to hit
* how to parse the response from the API
* how to perform pagination

Optionally, we can provide additional inputs to customize requests:

* request parameters and headers
* how to recognize rate limit errors, and how long to wait \(by default it retries 429 and 5XX errors using exponential backoff\)
* HTTP method and request body if applicable
* configure exponential backoff policy

Backoff policy options:

* `retry_factor` Specifies factor for exponential backoff policy \(by default is 5\)
* `max_retries` Specifies maximum amount of retries for backoff policy \(by default is 5\)
* `raise_on_http_errors` If set to False, allows opting-out of raising HTTP code exception \(by default is True\)

There are many other customizable options - you can find them in the [`airbyte_cdk.sources.streams.http.HttpStream`](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/streams/http/http.py) class.

So in order to read data from the exchange rates API, we'll fill out the necessary information for the stream to do its work. First, we'll implement a basic read that just reads the last day's exchange rates, then we'll implement incremental sync using stream slicing.

Let's begin by pulling data for the last day's rates by using the `/latest` endpoint:

```python
class ExchangeRates(HttpStream):
    url_base = "https://api.apilayer.com/exchangerates_data/"

    primary_key = None

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.base = config['base']
        self.apikey = config['apikey']


    def path(
        self, 
        stream_state: Mapping[str, Any] = None, 
        stream_slice: Mapping[str, Any] = None, 
        next_page_token: Mapping[str, Any] = None
    ) -> str:
        # The "/latest" path gives us the latest currency exchange rates
        return "latest"  

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        # The api requires that we include apikey as a header so we do that in this method
        return {'apikey': self.apikey}

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

This may look big, but that's just because there are lots of \(unused, for now\) parameters in these methods \(those can be hidden with Python's `**kwargs`, but don't worry about it for now\). Really we just added a few lines of "significant" code:

1. Added a constructor `__init__` which stores the `base` currency to query for and the `apikey` used for authentication.
2. `return {'base': self.base}` to add the `?base=<base-value>` query parameter to the request based on the `base` input by the user.
3. `return {'apikey': self.apikey}` to add the header `apikey=<apikey-string>` to the request based on the `apikey` input by the user.
4. `return [response.json()]` to parse the response from the API to match the schema of our schema `.json` file.
5. `return "latest"` to indicate that we want to hit the `/latest` endpoint of the API to get the latest exchange rate data.

Let's also pass the config specified by the user to the stream class:

```python
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = NoAuth()
        return [ExchangeRates(authenticator=auth, config=config)]
```

We're now ready to query the API!

To do this, we'll need a [ConfiguredCatalog](https://docs.airbyte.io/understanding-airbyte/beginners-guide-to-catalog#configuredairbytecatalog). We've prepared one [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/docs/tutorials/http_api_source_assets/configured_catalog.json) -- download this and place it in `sample_files/configured_catalog.json`. Then run:

```text
 python main.py read --config sample_files/config.json --catalog sample_files/configured_catalog.json
```

you should see some output lines, one of which is a record from the API:

```text
{"type": "RECORD", "record": {"stream": "exchange_rates", "data": {"base": "USD", "rates": {"GBP": 0.7196938353, "HKD": 7.7597848573, "IDR": 14482.4824162185, "ILS": 3.2412081092, "DKK": 6.1532478279, "INR": 74.7852709971, "CHF": 0.915763343, "MXN": 19.8439387671, "CZK": 21.3545717832, "SGD": 1.3261894911, "THB": 31.4398014067, "HRK": 6.2599917253, "EUR": 0.8274720728, "MYR": 4.0979726934, "NOK": 8.3043442284, "CNY": 6.4856433595, "BGN": 1.61836988, "PHP": 48.3516756309, "PLN": 3.770872983, "ZAR": 14.2690111709, "CAD": 1.2436905254, "ISK": 124.9482829954, "BRL": 5.4526272238, "RON": 4.0738932561, "NZD": 1.3841125362, "TRY": 8.3101365329, "JPY": 108.0182043856, "RUB": 74.9555647497, "KRW": 1111.7583781547, "USD": 1.0, "AUD": 1.2840711626, "HUF": 300.6206040546, "SEK": 8.3829540753}, "date": "2021-04-26"}, "emitted_at": 1619498062000}}
```

There we have it - a stream which reads data in just a few lines of code!

We theoretically _could_ stop here and call it a connector. But let's give adding incremental sync a shot.

## Adding incremental sync

To add incremental sync, we'll do a few things: 
1. Pass the `start_date` param input by the user into the stream. 
2. Declare the stream's `cursor_field`. 
3. Declare the stream's property `_cursor_value` to hold the state value
4. Add `IncrementalMixin` to the list of the ancestors of the stream and implement setter and getter of the `state`.
5. Implement the `stream_slices` method. 
6. Update the `path` method to specify the date to pull exchange rates for. 
7. Update the configured catalog to use `incremental` sync when we're testing the stream.

We'll describe what each of these methods do below. Before we begin, it may help to familiarize yourself with how incremental sync works in Airbyte by reading the [docs on incremental](https://docs.airbyte.io/architecture/connections/incremental-append).

To keep things concise, we'll only show functions as we edit them one by one.

Let's get the easy parts out of the way and pass the `start_date`:

```python
def streams(self, config: Mapping[str, Any]) -> List[Stream]:
    auth = NoAuth()
    # Parse the date from a string into a datetime object
    start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
    return [ExchangeRates(authenticator=auth, config=config, start_date=start_date)]
```

Let's also add this parameter to the constructor and declare the `cursor_field`:

```python
from datetime import datetime, timedelta
from airbyte_cdk.sources.streams import IncrementalMixin


class ExchangeRates(HttpStream, IncrementalMixin):
    url_base = "https://api.apilayer.com/exchangerates_data/"
    cursor_field = "date"
    primary_key = "date"

    def __init__(self, base: str, start_date: datetime, **kwargs):
        super().__init__()
        self.base = base
        self.start_date = start_date
        self._cursor_value = None
```

Declaring the `cursor_field` informs the framework that this stream now supports incremental sync. The next time you run `python main_dev.py discover --config sample_files/config.json` you'll find that the `supported_sync_modes` field now also contains `incremental`.

But we're not quite done with supporting incremental, we have to actually emit state! We'll structure our state object very simply: it will be a `dict` whose single key is `'date'` and value is the date of the last day we synced data from. For example, `{'date': '2021-04-26'}` indicates the connector previously read data up until April 26th and therefore shouldn't re-read anything before April 26th.

Let's do this by implementing the getter and setter for the `state` inside the `ExchangeRates` class.

```python
    @property
    def state(self) -> Mapping[str, Any]:
        if self._cursor_value:
            return {self.cursor_field: self._cursor_value.strftime('%Y-%m-%d')}
        else:
            return {self.cursor_field: self.start_date.strftime('%Y-%m-%d')}
    
    @state.setter
    def state(self, value: Mapping[str, Any]):
       self._cursor_value = datetime.strptime(value[self.cursor_field], '%Y-%m-%d')
```

Update internal state `cursor_value` inside `read_records` method

```python
    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(*args, **kwargs):
            if self._cursor_value:
                latest_record_date = datetime.strptime(record[self.cursor_field], '%Y-%m-%d')
                self._cursor_value = max(self._cursor_value, latest_record_date)
            yield record

```

This implementation compares the date from the latest record with the date in the current state and takes the maximum as the "new" state object.

We'll implement the `stream_slices` method to return a list of the dates for which we should pull data based on the stream state if it exists:

```python
    def _chunk_date_range(self, start_date: datetime) -> List[Mapping[str, Any]]:
        """
        Returns a list of each day between the start date and now.
        The return value is a list of dicts {'date': date_string}.
        """
        dates = []
        while start_date < datetime.now():
            dates.append({self.cursor_field: start_date.strftime('%Y-%m-%d')})
            start_date += timedelta(days=1)
        return dates

    def stream_slices(self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) -> Iterable[Optional[Mapping[str, Any]]]:
        start_date = datetime.strptime(stream_state[self.cursor_field], '%Y-%m-%d') if stream_state and self.cursor_field in stream_state else self.start_date
        return self._chunk_date_range(start_date)
```

Each slice will cause an HTTP request to be made to the API. We can then use the information present in the `stream_slice` parameter \(a single element from the list we constructed in `stream_slices` above\) to set other configurations for the outgoing request like `path` or `request_params`. For more info about stream slicing, see [the slicing docs](../../concepts/stream_slices.md).

In order to pull data for a specific date, the Exchange Rates API requires that we pass the date as the path component of the URL. Let's override the `path` method to achieve this:

```python
def path(self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None) -> str:
    return stream_slice['date']
```

With these changes, your implementation should look like the file [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-python-http-tutorial/source_python_http_tutorial/source.py).

The last thing we need to do is change the `sync_mode` field in the `sample_files/configured_catalog.json` to `incremental`:

```text
"sync_mode": "incremental",
```

We should now have a working implementation of incremental sync!

Let's try it out:

```text
python main.py read --config sample_files/config.json --catalog sample_files/configured_catalog.json
```

You should see a bunch of `RECORD` messages and `STATE` messages. To verify that incremental sync is working, pass the input state back to the connector and run it again:

```text
# Save the latest state to sample_files/state.json
python main.py read --config sample_files/config.json --catalog sample_files/configured_catalog.json | grep STATE | tail -n 1 | jq .state.data > sample_files/state.json

# Run a read operation with the latest state message
python main.py read --config sample_files/config.json --catalog sample_files/configured_catalog.json --state sample_files/state.json
```

You should see that only the record from the last date is being synced! This is acceptable behavior, since Airbyte requires at-least-once delivery of records, so repeating the last record twice is OK.

With that, we've implemented incremental sync for our connector!

````
