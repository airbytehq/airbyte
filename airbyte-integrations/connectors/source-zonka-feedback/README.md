# Zonka Feedback
This directory contains the manifest-only connector for `source-zonka-feedback`.

This is the Zonka Feedback source that ingests data from the Zonka API.

Zonka Feedback simplifies CX, allowing you to start meaningful two-way conversations with customers via powerful surveys. Design stunning surveys in minutes, gather data from all touchpoints, understand customers better with AI analytics &amp; close the feedback loop — all within one powerful platform https://www.zonkafeedback.com/

To use this source, you must first create an account. Once logged in, click on Settings -&gt; Developers -&gt; API &amp; Data Center. Note down your Data center and generate your auth token. 

For more information about the API visit https://apidocs.zonkafeedback.com/#intro

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
This will create a dev image (`source-zonka-feedback:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-zonka-feedback build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-zonka-feedback test
```

