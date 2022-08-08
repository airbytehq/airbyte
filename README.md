# Airbyte

Plenty currently uses [StitchData](https://www.stitchdata.com/) to replicate replicate disparate sources of data to a central location. This closed-source solution makes it difficult to create custom solutions for edge cases. The modern open-source solution and alternative is [Airbyte](https://airbyte.com/) which boast impressive community support, financial momentum and developer support.

This repository is a fork of the [core-codebase](./README-original.md) which means that Plenty can develop custom connectors using a well designed API and always update the core technology via a PR. This also gives Plenty the chance to contribute back to the open-source community.

Find out more at [Airbyte Open Source Quickstart](https://docs.airbyte.com/category/airbyte-open-source-quickstart).

## Connector Development

Airbyte provides a [python SDK](https://docs.airbyte.com/connector-development/tutorials/building-a-python-source) to aid in building a source.

As an example, see the [Compusense Connector README](./airbyte-integrations/connectors/source-compusense/README.md). You can call methods in the connector as shown below.

```bash
# Compusense Connector example (after setting up with generator)
cd airbyte-integrations/connectors/source-compusense 

# Activate connector specific environment
source .venv/bin/activate

# Check connector specs
python main.py spec
```
