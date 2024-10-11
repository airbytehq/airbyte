# Slab
This directory contains the manifest-only connector for `source-slab`.

Slab source connector for ingesting data from the slab API.
Slab is a platform to easily create, organise, and discover knowledge for your entire organisation, from non-technical to tech-savvy. https://slab.com/

In order to use this source, you must first create an account and log in. 
The API uses a bearer token which can be obtained by navigating to Settings -&gt; Developer -&gt; Admin Token.
You must be on a the business plan to obtain a token.
Slab uses Graphql API and this connector streams the `users`, `posts` and `topics` endpoints. Find more information about the API here https://studio.apollographql.com/public/Slab/variant/current/home 

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
This will create a dev image (`source-slab:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-slab build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-slab test
```

