# Getting Started

:warning: This framework is in [alpha](https://docs.airbyte.com/project-overview/product-release-stages/#alpha). It is still in active development and may include backward-incompatible changes. Please share feedback and requests directly with us at feedback@airbyte.io :warning:

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
This can be done by signing up for the Free tier plan on [Exchange Rates API](https://exchangeratesapi.io/):

1. Visit https://exchangeratesapi.io and click "Get free API key" on the top right
2. You'll be taken to https://apilayer.com -- finish the sign up process, signing up for the free tier
3. Once you're signed in, visit https://apilayer.com/marketplace/exchangerates_data-api#documentation-tab and click "Live Demo"
4. Inside that editor, you'll see an API key. This is your API key.

## Requirements

- An Exchange Rates API key
- Python >= 3.9
- Docker must be running
- NodeJS

## Next Steps

Next, we'll [create a Source using the connector generator.](1-create-source.md)