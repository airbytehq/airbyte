# Secondary Features

The CDK offers other features that make writing HTTP APIs a breeze.

## Authentication

The CDK supports token and OAuth2.0 authentication via the `TokenAuthenticator` and `Oauth2Authenticator` classes
respectively. Both authentication strategies are identical in that they place the api token in the `Authorization`
header. The `OAuth2Authenticator` goes an additional step further and has mechanisms to, given a refresh token,
refresh the current access token. Note that the `OAuth2Authenticator` currently only supports refresh tokens
and not the full OAuth2.0 loop.

Using either authenticator is as simple as passing the created authenticator into the relevant `HTTPStream`
constructor. Here is an [example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L242) from the Stripe API.

## Pagination

Most APIs, when facing a large call, tend to return the results in pages. The CDK accommodates paging
via the `next_page_token` function. This function is meant to extract the next page "token" from the latest
response. The contents of a "token" are completely up to the developer: it can be an ID, a page number, a partial URL etc.. The CDK will continue making requests as long as the `next_page_token` function. The CDK will continue making requests as long as the `next_page_token` continues returning
non-`None` results. This can then be used in the `request_params` and other methods in `HttpStream` to page through API responses. Here is an
[example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L41) from the Stripe API.

## Rate Limiting

The CDK, by default, will conduct exponential backoff on the HTTP code 429 and any 5XX exceptions,
and fail after 5 tries.

Retries are governed by the `should_retry` and the `backoff_time` methods. Override these methods to
customise retry behavior. Here is an [example](https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-slack/source_slack/source.py#L72) from the Slack API.

Note that Airbyte will always attempt to make as many requests as possible and only slow down if there are
errors. It is not currently possible to specify a rate limit Airbyte should adhere to when making requests.