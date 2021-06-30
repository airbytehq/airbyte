# Step 3: Define Inputs

Each connector declares the inputs it needs to read data from the underlying data source. This is the Airbyte Protocol's `spec` operation.

The simplest way to implement this is by creating a `.json` file in `source_<name>/spec.json` which describes your connector's inputs according to the [ConnectorSpecification](https://github.com/airbytehq/airbyte/blob/master/airbyte-protocol/models/src/main/resources/airbyte_protocol/airbyte_protocol.yaml#L211) schema. This is a good place to start when developing your source. Using JsonSchema, define what the inputs are \(e.g. username and password\). Here's [an example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-freshdesk/source_freshdesk/spec.json) of what the `spec.json` looks like for the Freshdesk API source.

For more details on what the spec is, you can read about the Airbyte Protocol [here](https://docs.airbyte.io/understanding-airbyte/airbyte-specification).

The generated code that Airbyte provides, handles implementing the `spec` method for you. It assumes that there will be a file called `spec.json` in the same directory as `source.py`. If you have declared the necessary JsonSchema in `spec.json` you should be done with this step.

Given that we'll pulling currency data for our example source, we'll define the following `spec.json`:

```text
{
  "documentationUrl": "https://docs.airbyte.io/integrations/sources/exchangeratesapi",
  "connectionSpecification": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Python Http Tutorial Spec",
    "type": "object",
    "required": ["start_date", "base"],
    "additionalProperties": false,
    "properties": {
      "start_date": {
        "type": "string",
        "description": "Start getting data from that date.",
        "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}$",
        "examples": ["%Y-%m-%d"]
      },
      "base": {
        "type": "string",
        "examples": ["USD", "EUR"],
        "description": "ISO reference currency. See <a href=\"https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html\">here</a>."
      }
    }
  }
}
```

In addition to metadata, we define two inputs:

* `start_date`: The beginning date to start tracking currency exchange rates from
* `base`: The currency whose rates we're interested in tracking

