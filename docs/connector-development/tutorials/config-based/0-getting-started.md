# Getting Started

## Summary

Throughout this tutorial, we'll walk you through the creation an Airbyte source to read data from an HTTP API.

We'll build a connector reading data from the Exchange Rates API, but the steps we'll go through will apply to other HTTP APIs you might be interested in integrating with.

The API documentations can be found [here](https://exchangeratesapi.io/documentation/).
In this tutorial, we will read data from the following endpoints:

- `Latest Rates Endpoint`
- `Historical Rates Endpoint`

With the end goal of implementing a Source with a single `Stream` containing exchange rates going from a base currency to many other currencies.
The output schema of our stream will look like

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

Before we can get started, you'll need to generate an API access key for the Exchange Rates API.
This can be done by signing up for the Free tier plan on [Exchange Rates API](https://exchangeratesapi.io/).

## Requirements

- Python >= 3.9
- Docker
- NodeJS

## Next Steps

Next, we'll [create a Source using the connector generator.](1-create-source.md)