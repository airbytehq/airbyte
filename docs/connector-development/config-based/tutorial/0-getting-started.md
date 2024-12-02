# Getting Started

## Summary

Throughout this tutorial, we'll walk you through the creation of an Airbyte source to read and extract data from an HTTP API.

We'll build a connector reading data from the Exchange Rates API, but the steps apply to other HTTP APIs you might be interested in integrating with.

The API documentations can be found [here](https://apilayer.com/marketplace/exchangerates_data-api).
In this tutorial, we will read data from the following endpoints:

- `Latest Rates Endpoint`
- `Historical Rates Endpoint`

With the end goal of implementing a `Source` with a single `Stream` containing exchange rates going from a base currency to many other currencies.
The output schema of our stream will look like the following:

```json
{
  "base": "USD",
  "date": "2022-07-15",
  "rates": {
    "CAD": 1.28,
    "EUR": 0.98
  }
}
```

## Exchange Rates API Setup

Before we get started, you'll need to generate an API access key for the Exchange Rates API.
This can be done by signing up for the Free tier plan on [Exchange Rates Data API](https://apilayer.com/marketplace/exchangerates_data-api), not [Exchange Rates API](https://exchangeratesapi.io/):

1. Visit https://apilayer.com/ and click "Sign In" on the top
2. Finish the sign up process, signing up for the free tier
3. Once you're signed in, visit https://apilayer.com/marketplace/exchangerates_data-api and click "Subscribe" for free
4. On the top right, you'll see an API key. This is your API key.

## Requirements

- An Exchange Rates API key
- Python >= 3.10
- [Poetry](https://python-poetry.org/)
- Docker must be running
- [`airbyte-ci`](https://github.com/airbytehq/airbyte/blob/master/airbyte-ci/connectors/pipelines/README.md#L1) CLI

## Next Steps

Next, we'll [create a Source using the connector generator.](1-create-source.md)
