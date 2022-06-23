---
description: 'This connector extracts "collections" from Webflow'
---

# Webflow

Webflow is used for publishing Airbyte's blogs, and this connector returns data that is made available by [Webflow APIs](https://developers.webflow.com/). 

Webflow uses [Collections](https://developers.webflow.com/#collections) to store different kinds of information. A collection can be "Blog Posts", or "Blog Authors", etc. Collection names are not pre-defined, the number of collections is not known in advance, and the schema for each collection may be different. 

This connector dynamically figures our which collections are available, creates the schema for each collection based on data extracted from Webflow, and creates an [Airbyte Stream](https://docs.airbyte.com/connector-development/cdk-python/full-refresh-stream/) for each collection. 

# Webflow credentials
You should be able to create a Webflow  `API key` (aka `API token`) as described in [Intro to the Webflow API](https://university.webflow.com/lesson/intro-to-the-webflow-api). 

Once you have the `API Key`/`API token`, you can confirm a [list of available sites](https://developers.webflow.com/#sites) and get their `_id` by executing the following:

```
curl https://api.webflow.com/sites \
  -H "Authorization: Bearer <your API Key>" \
  -H "accept-version: 1.0.0"
```

Which should respond with something similar to:

```
[{"_id":"<redacted>","createdOn":"2021-03-26T15:46:04.032Z","name":"Airbyte","shortName":"airbyte-dev","lastPublished":"2022-06-09T12:55:52.533Z","previewUrl":"https://screenshots.webflow.com/sites/<redacted>","timezone":"America/Los_Angeles","database":"<redacted>"}]
```

After retrieving your `site id`, you can create a file `secrets/config.json` conforming to the fields expected in `source_webflow/spec.yaml` file.
(Note that any directory named `secrets` is git-ignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information in this folder).

See [integration_tests/sample_config.json](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-webflow/integration_tests/sample_config.json) for a sample config file that you can use as a template for entering in your `site id` and your `Webflow API Key`. 

| Version | Date | Pull Request | Subject |
| :--- | :--- | :--- | :--- |
| 0.1.0 | 2022-06-22 | [13617](https://github.com/airbytehq/airbyte/pull/13617) | Initial release |
| 0.1.1 | 2022-06-22 | [13617](https://github.com/airbytehq/airbyte/pull/13617) | Update Spec Documentation URL |


