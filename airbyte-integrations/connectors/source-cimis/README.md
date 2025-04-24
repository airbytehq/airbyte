# CIMIS
This directory contains the manifest-only connector for `source-cimis`.

The California Irrigation Management Information System (CIMIS) is a program unit in the Water Use and Efficiency Branch, Division of Regional Assistance, California Department of Water Resources (DWR) that manages a network of over 145 automated weather stations in California. CIMIS was developed in 1982 by DWR and the University of California, Davis (UC Davis). It was designed to assist irrigators in managing their water resources more efficiently. Efficient use of water resources benefits Californians by saving water, energy, and money.

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
This will create a dev image (`source-cimis:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-cimis build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-cimis test
```

