---
description: 'This connector extracts "collections" from Webflow'
---

# Sources

Webflow is used for publishing Airbyte's blogs, and provides several APIs. The APIs that are used by this connector to extract information from Webflow are described in [Webflow Developers documentation](https://developers.webflow.com/). 

Webflow uses [Collections](https://developers.webflow.com/#collections) to store different kinds of information. A collection can be "Blog Posts", or "Blog Authors", etc. Collection names are not pre-defined, the number of collections is not known in advance, and the schema for each collection may be different. Therefore this connector dynamically figures our which collections are available and downloads the schema for each collection from Webflow. Each collection is mapped to an [Airbyte Streams](https://docs.airbyte.com/connector-development/cdk-python/full-refresh-stream/). 

# Webflow credentials
You should be able to create a Webflow  `API key` (aka `API token`) by logging in to Webflow with your browser, and navigating to a URL such as:

`https://webflow.com/dashboard/sites/<your-site-name>/integrations`

Once you have the `API Key`, you can confirm a [list of available sites](https://developers.webflow.com/#sites) and get their `_id` by executing the following:

```
curl https://api.webflow.com/sites \
  -H "Authorization: Bearer <your API Key>" \
  -H "accept-version: 1.0.0"
```

Which should respond with something similar to:

```
[{"_id":"<redacted>","createdOn":"2021-03-26T15:46:04.032Z","name":"Airbyte","shortName":"airbyte-dev","lastPublished":"2022-06-09T12:55:52.533Z","previewUrl":"https://screenshots.webflow.com/sites/<redacted>.png","timezone":"America/Los_Angeles","database":"<redacted>"}]%             
```

After receiving the `site id`, you can create a file `secrets/config.json` conforming to the fields expected in `source_webflow/spec.yaml` file.
(Note that any directory named `secrets` is git-ignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information).

See `integration_tests/sample_config.json` for a sample config file that you can use as a template for entering in your `site id` and your `Webflow API Key`. 