---
description: 'This connector extracts "collections" from Webflow'
---

# Webflow

Webflow is a CMS system that is used for publishing websites and blogs. This connector returns data that is made available by [Webflow APIs](https://developers.webflow.com/).

Webflow uses [Collections](https://developers.webflow.com/#collections) to store different kinds of information. A collection can be "Blog Posts", or "Blog Authors", etc. Collection names are not pre-defined, the number of collections is not known in advance, and the schema for each collection may be different.

This connector dynamically figures out which collections are available, creates the schema for each collection based on data extracted from Webflow, and creates an [Airbyte Stream](https://docs.airbyte.com/connector-development/cdk-python/full-refresh-stream/) for each collection.

# Webflow credentials

You should be able to create a Webflow `API key` (aka `API token`) as described in [Intro to the Webflow API](https://university.webflow.com/lesson/intro-to-the-webflow-api). The Webflow connector uses the Webflow API v1 and therefore will require a legacy v1 API key.

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

You will need to provide the `Site ID` and `API key` to the Webflow connector in order for it to pull data from your Webflow site.

# Related tutorial

If you are interested in learning more about the Webflow API and implementation details of this connector, you may wish to consult the [tutorial about how to build a connector to extract data from the Webflow API](https://airbyte.com/tutorials/extract-data-from-the-webflow-api).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                |
| :------ | :--------- | :------------------------------------------------------- | :--------------------------------------------------------------------- |
| 0.1.3   | 2022-12-11 | [33315](https://github.com/airbytehq/airbyte/pull/33315) | Updates CDK to latest version and adds additional properties to schema |
| 0.1.2   | 2022-07-14 | [14689](https://github.com/airbytehq/airbyte/pull/14689) | Webflow added IDs to streams                                           |
| 0.1.1   | 2022-06-22 | [13617](https://github.com/airbytehq/airbyte/pull/13617) | Updates Spec Documentation URL                                         |
| 0.1.0   | 2022-06-22 | [13617](https://github.com/airbytehq/airbyte/pull/13617) | Initial release                                                        |
