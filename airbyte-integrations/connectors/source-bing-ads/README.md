# Bing Ads
This directory contains the manifest-only connector for `source-bing-ads`.

## Documentation reference:
Visit `https://learn.microsoft.com/en-us/advertising/guides/?view=bingads-13` for API documentation

## Authentication setup
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/bing-ads)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the spec defined in `manifest.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `sample_files/sample_config.json` for a sample config file.

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
This will create a dev image (`source-bing-ads:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-bing-ads build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-bing-ads test
```

### Running as a docker container

Then run any of the connector commands as follows:

```
docker run --rm airbyte/source-bing-ads:dev spec
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-bing-ads:dev check --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets airbyte/source-bing-ads:dev discover --config /secrets/config.json
docker run --rm -v $(pwd)/secrets:/secrets -v $(pwd)/integration_tests:/integration_tests airbyte/source-bing-ads:dev read --config /secrets/config.json --catalog /integration_tests/configured_catalog.json
```
