# Airbyte Python Connector Development Framework (CDK)

The Airbyte Python CDK is a framework for rapidly developing production-grade Airbyte connectors.
The CDK currently offers helpers specific for creating Airbyte source connectors for: 
* HTTP APIs (REST APIs, GraphQL, etc..)
* Singer Taps
* Generic Python sources (anything not covered by the above)

The CDK provides an improved developer experience by providing basic implementation structure and abstracting away low-level glue boilerplate. 

This document is a general introduction to the CDK. Readers should have basic familiarity with the [Airbyte Specification](https://docs.airbyte.io/understanding-airbyte/airbyte-specification) (the interface for how sources and destinations interact) before proceeding. 

## Getting started
Generate an empty connector using the code generator. First clone the Airbyte repository then from the repository root run
```
cd airbyte-integrations/connector-templates/generator
./generate.sh
```

then follow the interactive prompt. Next, find all `TODO`s in the generated project directory -- they're accompanied by lots of comments explaining what you'll need to do in order to implement your connector. Upon completing all TODOs properly, you should have a functioning connector. 

Additionally, you can follow [this tutorial](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/docs/tutorials/http_api_source.md) for a complete walkthrough of creating an HTTP connector using the Airbyte CDK.

### Concepts & Documentation
See the [overview docs](./docs/concepts/overview.md) for a tour through what the API offers.

### Example Connectors

**HTTP Connectors**: 
* [Exchangerates API](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-exchange-rates/source_exchange_rates/source.py)
* [Stripe](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py)
* [Slack](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-slack/source_slack/source.py)

**Singer connectors**:
* [Salesforce](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-salesforce-singer/source_salesforce_singer/source.py)
* [Github](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-github-singer/source_github_singer/source.py)

**Simple Python connectors using the barebones `Source` abstraction**: 
* [Google Sheets](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-google-sheets/google_sheets_source/google_sheets_source.py)
* [Mailchimp](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-mailchimp/source_mailchimp/source.py)
 
