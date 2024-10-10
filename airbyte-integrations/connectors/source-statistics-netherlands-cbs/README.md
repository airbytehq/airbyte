# Statistics Netherlands CBS
This directory contains the manifest-only connector for `source-statistics-netherlands-cbs`.

This connector is for fetching open statistical dataset of netherlands, the [CBS Opendata website](https://opendata.cbs.nl) provides dataset within several themes, Visit `https://opendata.cbs.nl/statline/portal.html?_la=en&amp;_catalog=CBS`, select a theme and click of API tab in left bar to find the link with dataset number which could be given as config for this connector

Example Open API Dataset : https://dataderden.cbs.nl/ODataApi/
Dataset Selection Website: https://opendata.cbs.nl/statline/portal.html?_la=en&amp;_catalog=CBS (Select a theme and click on API on left bar to find base number for dataset)

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-statistics-netherlands-cbs:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-statistics-netherlands-cbs build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-statistics-netherlands-cbs test
```

