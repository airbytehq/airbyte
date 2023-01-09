# Connector Development Kit Concepts

This concepts section serves as a general introduction to the Python CDK. Readers will certainly benefit from a deeper understanding of the [Airbyte Specification](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/) before proceeding, but we do a quick overview of it in our basic concepts guide below.

### Basic Concepts
If you want to learn more about the classes required to implement an Airbyte Source, head to our [basic concepts doc](basic-concepts.md).

### Full Refresh Streams

If you have questions or are running into issues creating your first full refresh stream, head over to our [full refresh stream doc](full-refresh-stream.md). If you have questions about implementing a `path` or `parse_response` function, this doc is for you.

### Incremental Streams

Having trouble figuring out how to write a `stream_slices` function or aren't sure what a `cursor_field` is? Head to our [incremental stream doc](incremental-stream.md).

### Practical Tips
Airbyte recommends using the CDK template generator to develop with the CDK. The template generates
  created all the required scaffolding, with convenient TODOs, allowing developers to truly focus on
  implementing the API.

For tips on useful Python knowledge, see the [Python Concepts](./python-concepts.md) page.   

You can find a complete tutorial for implementing an HTTP source connector in [this tutorial](../tutorials/http_api_source.md)

### Examples

Those interested in getting their hands dirty can check out implemented APIs:

* [Exchange Rates API](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-exchange-rates/source_exchange_rates/source.py) (Incremental)
* [Stripe API](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py) (Incremental and Full-Refresh)
* [Slack API](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-slack/source_slack/source.py) (Incremental and Full-Refresh)
