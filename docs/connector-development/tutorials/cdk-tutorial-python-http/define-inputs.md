# Step 3: Define Inputs

Each connector declares the inputs it needs to read data from the underlying data source. This is the Airbyte Protocol's `spec` operation.

The simplest way to implement this is by creating a `spec.yaml` file in `source_<name>/spec.yaml` which describes your connector's inputs according to the [ConnectorSpecification](https://github.com/airbytehq/airbyte/blob/master/docs/understanding-airbyte/airbyte-protocol.md#spec) schema. This is a good place to start when developing your source. Using JsonSchema, define what the inputs are \(e.g. username and password\). Here's [an example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/spec.yaml) of what the `spec.yaml` looks like for the Stripe API source.

For more details on what the spec is, you can read about the Airbyte Protocol [here](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol).

The generated code that Airbyte provides, handles implementing the `spec` method for you. It assumes that there will be a file called `spec.yaml` in the same directory as `source.py`. If you have declared the necessary JsonSchema in `spec.yaml` you should be done with this step.

Given that we'll pulling currency data for our example source, we'll define the following `spec.yaml`:

```yaml
documentationUrl: https://docs.airbyte.com/integrations/sources/exchangeratesapi
connectionSpecification:
  $schema: http://json-schema.org/draft-07/schema#
  title: Python Http Tutorial Spec
  type: object
  required:
    - apikey
    - start_date
    - base
  properties:
    apikey:
      type: string
      description: API access key used to retrieve data from the Exchange Rates API.
      airbyte_secret: true
    start_date:
      type: string
      description: Start getting data from that date.
      pattern: ^[0-9]{4}-[0-9]{2}-[0-9]{2}$
      examples:
        - "%Y-%m-%d"
    base:
      type: string
      examples:
        - USD
        - EUR
      description: "ISO reference currency. See <a href=\"https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html\">here</a>."
```

In addition to metadata, we define three inputs:

* `apikey`: The API access key used to authenticate requests to the API
* `start_date`: The beginning date to start tracking currency exchange rates from
* `base`: The currency whose rates we're interested in tracking

