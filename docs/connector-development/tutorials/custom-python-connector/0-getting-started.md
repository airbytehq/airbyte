# Getting started

This tutorial will walk you through the creation of a custom Airbyte connector implemented with the
Python CDK. It assumes you're already familiar with Airbyte concepts and you've already built a
connector using the [Connector Builder](../../connector-builder-ui/tutorial.mdx).

The Python CDK should be used to implement connectors that require features that are not yet
available in the Connector Builder or in the low-code framework. You can use the
[Connector Builder compatibility guide](../../connector-builder-ui/connector-builder-compatibility.md)
to know whether it is suitable for your needs.

We'll build an connector for the Survey Monkey API, focusing on the `surveys` and `survey responses`
endpoints.

You can find the documentation for the API
[here](https://api.surveymonkey.com/v3/docs?shell#getting-started).

As a first step, follow the getting started instructions from the docs to register a draft app to
your account.

Next, we'll inspect the API docs to understand how the endpoints work.

## Surveys endpoint

The [surveys endpoint doc](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys)
shows that the endpoint URL is https://api.surveymonkey.com/v3/surveys and that the data is nested
in the response's "data" field.

It also shows there are two ways to iterate through the record pages. We could either keep a page
counter and increment it on every request, or use the link sent as part of the response in "links"
-> "next".

The two approaches are equivalent for the Survey Monkey API, but as a rule of thumb, it is
preferable to use the links provided by the API if it is available instead of reverse engineering
the mechanism. This way, we don't need to modify the connector if the API changes their pagination
mechanism, for instance, if they decide to implement server-side pagination.

:::info When available, server-side pagination should be preferred over client-side pagination
because it has lower risks of missing records if the collection is modified while the connector
iterates.

:::

The "Optional Query Strings for GET" section shows that the `perPage` parameter is important because
it’ll define how many records we can fetch with a single request. The maximum page size isn't
explicit from the docs. We'll use 1000 as a limit. When unsure, we recommend finding the limit
experimentally by trying multiple values.

Also note that we'll need to add the `include` query parameter to fetch all the properties, such as
`date_modified`, which we'll use as our cursor value.

The section also shows how to filter the data based on the record's timestamp, which will allow the
connector to read records incrementally. We'll use the `start_modified_at` and `end_modified_at` to
scope our requests.

We won't worry about the other query params as we won't filter by title or folder.

:::info

As a rule of thumb, it's preferable to fetch all the available data rather than ask the user to
specify which folder IDs they care about.

:::

## Survey responses

Next, we'll take a look at the
[documentation for the survey responses endpoint](https://api.surveymonkey.com/v3/docs?shell#api-endpoints-get-surveys-id-responses).
It shows that this endpoint depends on the `surveys` endpoint, since we'll need to first fetch the
surveys to fetch the responses.

It shows that the records are also nested in a "data" field. It's unclear from the examples if the
responses include a link to the next page. I already confirmed that's the case for you, but I'd
recommend validating this kind of assumption for any connector you plan on running in production.

We’re not going to worry about the custom variables because we want to pull all the data.

It’s worth noting that this stream won’t support incremental mode because there’s no timestamp to
filter on.

## Authentication

The [authentication section](https://api.surveymonkey.com/v3/docs?shell#authentication describes how
to authenticate to the API. Follow the instructions to obtain an access key. We'll then be able to
authenticate by passing a HTTP header in the format `Authorization: bearer YOUR_ACCESS_TOKEN`.

## Rate limits

The
[request and responses section](https://api.surveymonkey.com/v3/docs?shell#request-and-response-limits)
shows there’s a limit of 120 requests per minute, and of 500 requests per day.

We’ll handle the 120 requests per minute by throttling, but we’ll let the sync fail if it hits the
daily limit because we don’t want to let the sync spin for up to 24 hours without any reason.

We won’t worry about the increasing the rate limits.

## Error codes

The [Error Codes](https://api.surveymonkey.com/v3/docs?shell#error-codes) section shows the error
codes 1010-1018 represent authentication failures. These failures should be handled by the end-user,
and aren't indicative of a system failure. We'll therefore handle them explicitly so users know how
to resolve them should they occur.

## Putting it all together

We now know enough about how the API works:

| Stream           | URL                                                           | authentication                                | path to data | pagination                | cursor value  | time based filters                                 | query params                                                                                                 | rate limits            | user errors          |
| ---------------- | ------------------------------------------------------------- | --------------------------------------------- | ------------ | ------------------------- | ------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ---------------------- | -------------------- |
| surveys          | https://api.surveymonkey.com/v3/surveys                       | bearerAuthorization: bearer YOUR_ACCESS_TOKEN | data         | response -> links -> next | date_modified | start_modified_at and end_modified_at query params | include: response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats | 120 request per minute | error code 1010-1018 |
| survey responses | https://api.surveymonkey.com/v3/surveys/{survey_id}/responses | bearerAuthorization: bearer YOUR_ACCESS_TOKEN | data         | response -> links -> next | None          | None                                               | None                                                                                                         | 120 request per minute | error code 1010-1018 |

In the [next section](./1-environment-setup.md), we'll setup our development environment.
