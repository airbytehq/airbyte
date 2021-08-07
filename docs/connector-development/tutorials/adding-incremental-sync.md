# Adding Incremental Sync to a Source

## Overview

This tutorial will assume that you already have a working source. If you do not, feel free to refer to the [Building a Toy Connector](building-a-python-source.md) tutorial. This tutorial will build directly off the example from that article. We will also assume that you have a basic understanding of how Airbyte's Incremental-Append replication strategy works. We have a brief explanation of it [here](../../understanding-airbyte/connections/incremental-append.md).

## Update Catalog in `discover`

First we need to identify a given stream in the Source as supporting incremental. This information is declared in the catalog that the `discover` method returns. You will notice in the stream object contains a field called `supported_sync_modes`. If we are adding incremental to an existing stream, we just need to add `"incremental"` to that array. This tells Airbyte that this stream can either be synced in an incremental fashion. In practice, this will mean that in the UI, a user will have the ability to configure this type of sync.

In the example we used in the Toy Connector tutorial, the `discover` method would not look like this. Note: that "incremental" has been added to the `support_sync_modes` array. We also set `source_defined_cursor` to `True` to declare that the Source knows what field to use for the cursor, in this case the date field, and does not require user input. Nothing else has changed.

```python
def discover():
    catalog = {
        "streams": [{
            "name": "stock_prices",
            "supported_sync_modes": ["full_refresh", "incremental"],
            "source_defined_cursor": True,
            "json_schema": {
                "properties": {
                    "date": {
                        "type": "string"
                    },
                    "price": {
                        "type": "number"
                    },
                    "stock_ticker": {
                        "type": "string"
                    }
                }
            }
        }]
    }
    airbyte_message = {"type": "CATALOG", "catalog": catalog}
    print(json.dumps(airbyte_message))
```

## Update `read`

Next we will adapt the `read` method that we wrote previously. We need to change three things.

First, we need to pass it information about what data was replicated in the previous sync. In Airbyte this is called a `state` object. The structure of the state object is determined by Source. This means that each Source can construct a state object that makes sense to it and does not need to worry about adhering to any other convention. That being said, a pretty typical structure for a state object is a map of stream name to the last value in the cursor field for that stream.

In this case we might choose something like this:

```javascript
{
  "stock_prices": "2020-02-01"
}
```

The second change we need to make to the `read` method is to use the state object so that we only emit new records. This stock ticker API does not give us control over how we query it, so we will have to filter out records that we already replicated within the Source.

Lastly, we need to emit an updated state object, so that the next time this Source runs we do not resend messages that we have already sent.

Here's what our updated source would look like.

```python
def read(config, catalog, state):
    # Assert required configuration was provided
    if "api_key" not in config or "stock_ticker" not in config:
        log("Input config must contain the properties 'api_key' and 'stock_ticker'")
        sys.exit(1)

    # Find the stock_prices stream if it is present in the input catalog
    stock_prices_stream = None
    for configured_stream in catalog["streams"]:
        if configured_stream["stream"]["name"] == "stock_prices":
            stock_prices_stream = configured_stream

    if stock_prices_stream is None:
        log("No streams selected")
        return

    # If we've made it this far, all the configuration is good and we can pull the last 7 days of market data
    api_key = config["api_key"]
    stock_ticker = config["stock_ticker"]
    response = _call_api(f"/stock/{stock_ticker}/chart/7d", api_key)
    # max_date starts at the value from the incoming state object. None if there was no previous state.
    max_date = state.get("stock_prices")
    if response.status_code != 200:
        # In a real scenario we'd handle this error better :)
        log("Failure occurred when calling IEX API")
        sys.exit(1)
    else:
        # Sort the stock prices ascending by date then output them one by one as AirbyteMessages
        prices = sorted(response.json(), key=lambda record: to_datetime(record["date"]))
        for price in prices:
            data = {"date": price["date"], "stock_ticker": price["symbol"], "price": price["close"]}
            record = {"stream": "stock_prices", "data": data, "emitted_at": int(datetime.datetime.now().timestamp()) * 1000}
            output_message = {"type": "RECORD", "record": record}

            if stock_prices_stream["sync_mode"] == "incremental":
                # Filter records that are older than the last state.
                # If no previous state, filter nothing.
                state_date = to_datetime(state.get("stock_prices"))
                if state_date and state_date > to_datetime(data["date"]):
                    continue
                # If this record has the greatest date value so far, bump
                # max_date.
                if not max_date or to_datetime(max_date) < to_datetime(data["date"]):
                    max_date = data["date"]

            print(json.dumps(output_message))

        # Emit new state message.
        if stock_prices_stream["sync_mode"] == "incremental":
            output_message = {"type": "STATE", "state": {"data": {"stock_prices": max_date}}}
            print(json.dumps(output_message))

def to_datetime(date):
    if date:
        return datetime.datetime.strptime(date, '%Y-%m-%d')
    else:
        return None
```

That's all you need to do to add incremental functionality to the stock ticker Source. Incremental definitely requires more configurability than full refresh, so your implementation may deviate slightly depending on whether your cursor field is source defined or user-defined. If you think you are running into one of those cases, check out our [incremental](../../understanding-airbyte/connections/incremental-append.md) documentation for more information on different types of configuration.

