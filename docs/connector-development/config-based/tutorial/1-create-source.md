# Step 1: Generate the source connector project locally

Let's start by cloning the Airbyte repository:

```bash
git clone git@github.com:airbytehq/airbyte.git
cd airbyte
```

Airbyte provides a code generator which bootstraps the scaffolding for our connector.

```bash
cd airbyte-integrations/connector-templates/generator
./generate.sh
```

This will bring up an interactive helper application. Use the arrow keys to pick a template from the list. Select the `Low-code Source` template and then input the name of your connector. The application will create a new directory in `airbyte/airbyte-integrations/connectors/` with the name of your new connector.
The generator will create a new module for your connector with the name `source-<connector-name>`.

```
Configuration Based Source
Source name: exchange-rates-tutorial
```

For this walkthrough, we'll refer to our source as `exchange-rates-tutorial`.

## Next steps

Next, [we'll install dependencies required to run the connector](2-install-dependencies.md)

## More readings

- [Connector generator](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connector-templates/generator/README.md)
