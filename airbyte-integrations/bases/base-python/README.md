# Airbyte Python Connector Development Framework (CDK)

TODO use text from Davin's PR


## Getting started
Generate an empty connector using the code generator. First clone the Airbyte repository then from the repository root run
```
cd airbyte-integrations/connector-templates/generator
npm run generate
```

then follow the interactive prompt. 

You can follow the tutorial for creating an HTTP tutorial here

### Airbyte Specification
Find the reference docs for the Airbyte Specification (the interface for how sources and destinations interact) [here](https://docs.airbyte.io/architecture/airbyte-specification).


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
 
