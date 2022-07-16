# Step  1: Create the Source

Let's start by cloning the Airbyte repository

```
git clone git@github.com:airbytehq/airbyte.git
```

Airbyte provides a code generator which bootstraps the scaffolding for our connector.

```
cd airbyte-integrations/connector-templates/generator
./generate.sh
```

This will bring up an interactive helper application. Use the arrow keys to pick a template from the list. Select the <FIXME: update this when the template generator exists...> template and then input the name of your connector. The application will create a new directory in airbyte/airbyte-integrations/connectors/ with the name of your new connector.

```
Python HTTP API Source
Source name: exchange-rates-tutorial
```

For this walkthrough, we'll refer to our source as `exchange-rates-tutorial`. The complete source code for this tutorial can be found here <FIXME: there should be a link to the complete tutorial?

## Temporary instructions

These are temporary instructions to run the tutorial until the generator and the refactored stream slicers are in master:

```
git checkout alex/tutorialIncremental
pip install -e airbyte-cdk/python/
```

Then paste the content to the files

1. `airbyte-integrations/connectors/source-exchange-rates-tutorial/source_exchange_rates_tutorial/connector_definition.yaml`

```
<TODO>_stream:
  options:
    name: "<TODO>"
    primary_key: "<TODO>"
    url_base: "<TODO>"
    schema_loader:
      file_path: "./source_exchange_rates_tutorial/schemas/{{name}}.json"
    retriever:
      requester:
        path: "<TODO>"
      record_selector:
        extractor:
          transform: "<TODO>"

streams:
  - "*ref(<TODO>_stream)"
check:
  stream_names:
    - "<TODO>>"
```

2. `airbyte-integrations/connectors/source-exchange-rates-tutorial/source_exchange_rates_tutorial/source.py`

```

#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class SourceExchangeRatesTutorial(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "./source_exchange_rates_tutorial/connector_definition.yaml"})
```

## Next steps

Next, [we'll install dependencies required to run the connector](./2-install-dependencies.md)
