# Step 1: Creating the Source

Airbyte provides a code generator which bootstraps the scaffolding for our connector.

```bash
$ cd airbyte-integrations/connector-templates/generator # assumes you are starting from the root of the Airbyte project.
# Install NPM from https://www.npmjs.com/get-npm if you don't have it
$ ./generate.sh
```

This will bring up an interactive helper application. Use the arrow keys to pick a template from the list. Select the `Python HTTP API Source` template and then input the name of your connector. The application will create a new directory in airbyte/airbyte-integrations/connectors/ with the name of your new connector.

For this walk-through we will refer to our source as `python-http-example`. The finalized source code for this tutorial can be found [here](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-python-http-tutorial).

The source we will build in this tutorial will pull data from the [Rates API](https://exchangeratesapi.io/), a free and open API which documents historical exchange rates for fiat currencies.

