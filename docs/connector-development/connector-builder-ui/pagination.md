# Pagination

Pagination is a mechanism used by APIs in which data is split up into "pages" when returning results, so that the entire response data doesn't need to be returned all at once.

The Connector Builder offers a Pagination section which implements the most common pagination methods used by APIs. When enabled, the connector will use the pagination configuration you have provided to request consecutive pages of data from the API until there are no more pages to fetch.

If your API doesn't support pagination, simply leave the Pagination section disabled.

## Pagination methods

Check the documentation of the API you want to integrate to find which type of pagination is uses. Many API docs have a "Pagination" or "Paging" section that describes this.

The following pagination mechanisms are supported in the connector builder:

- [Offset Increment](#offset-increment)
- [Page Increment](#page-increment)
- [Cursor Pagination](#cursor-pagination)

Select the matching pagination method for your API and check the sections below for more information about individual methods. If none of these pagination methods work for your API, you will need to use the [low-code CDK](../config-based/low-code-cdk-overview) or [Python CDK](../cdk-python/) instead.

### Offset Increment

If your API paginates using offsets, the API docs will likely contain one of the following keywords:

- `offset`
- `limit`

In this method of pagination, the "limit" specifies the maximum number of records to return per page, while the "offset" indicates the starting position or index from which to retrieve records.

For example, say that the API has the following dataset:

```
[
  {"id": 1, "name": "Product A"},
  {"id": 2, "name": "Product B"},
  {"id": 3, "name": "Product C"},
  {"id": 4, "name": "Product D"},
  {"id": 5, "name": "Product E"}
]
```

Then the API may take in a request like this: `GET https://api.example.com/products?limit=2&offset=3`, which could result in the following response:

```
{
  "data": [
    {"id": 4, "name": "Product D"},
    {"id": 5, "name": "Product E"}
  ]
}
```

Normally, the caller of the API would need to implement some logic to then increment the `offset` by the `limit` amount and then submit another call with the updated `offset`, and continue on this pattern until all of the records have been retrieved.

The Offset Increment pagination mode in the Connector Builder does this for you. So you just need to decide on a `limit` value to set (the general recommendation is to use the largest limit that the API supports in order to minimize the number of API requests), and configure how the limit and offset are injected into the HTTP requests. Most APIs accept these values as query parameters like in the above example, but this can differ depending on the API. If an API does not accept a `limit`, then the injection configuration for the limit can be disabled

Either way, your connector will automatically increment the `offset` for subsequent requests based on the number of records it receives, and will continue until it receives fewer records than the limit you configured.

So for the example API and dataset above, you could apply the following Pagination configurations in the Connector Builder:

<iframe width="640" height="548" src="https://www.loom.com/embed/ec18b3c4e6db4007b4ef10ee808ab873" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

- Mode: `Offset Increment`
- Limit: `2`
- Inject limit into outgoing HTTP request:
  - Inject into: `request_parameter`
  - Field name: `limit`
- Inject offset into outgoing HTTP request:
  - Inject into: `request_parameter`
  - Field name: `offset`

and this would cause your connector to make the following requests to the API in order to paginate through all of its data:

```
GET https://api.example.com/products?limit=2&offset=0
  -> [
       {"id": 1, "name": "Product A"},
       {"id": 2, "name": "Product B"}
     ]

GET https://api.example.com/products?limit=2&offset=2
  -> [
       {"id": 3, "name": "Product C"},
       {"id": 4, "name": "Product D"}
     ]

GET https://api.example.com/products?limit=3&offset=4
  -> [
       {"id": 5, "name": "Product E"}
     ]
     // less than 2 records returned -> stop
```

The Connector Builder currently supports injecting these values into the query parameters (i.e. request parameters), headers, or body.

#### Examples

The following APIs accept offset and limit pagination values as query parameters like in the above example:

- [Spotify API](https://developer.spotify.com/documentation/web-api/concepts/api-calls#pagination)
- [GIPHY API](https://developers.giphy.com/docs/api/endpoint#trending)
- [Twilio SendGrid API](https://docs.sendgrid.com/api-reference/how-to-use-the-sendgrid-v3-api/responses#pagination)

### Page Increment

If your API paginates using page increments, the API docs will likely contain one of the following keywords:

- `page size` / `page_size` / `pagesize` / `per_page`
- `page number` / `page_number` / `pagenum` / `page`

In this method of pagination, the "page size" specifies the maximum number of records to return per request, while the "page number" indicates the specific page of data to retrieve.

This is similar to Offset Increment pagination, but instead of increasing the offset parameter by the number of records per page for the next request, the page number is simply increased by one to fetch the next page, iterating through all of them.

For example, say that the API has the following dataset:

```
[
  {"id": 1, "name": "Product A"},
  {"id": 2, "name": "Product B"},
  {"id": 3, "name": "Product C"},
  {"id": 4, "name": "Product D"},
  {"id": 5, "name": "Product E"},
  {"id": 6, "name": "Product F"}
]
```

Then the API may take in a request like this: `GET https://api.example.com/products?page_size=2&page=1`, which could result in the following response:

```
{
  "data": [
    {"id": 1, "name": "Product A"},
    {"id": 2, "name": "Product B"}
  ]
}
```

then incrementing the `page` by 1 to call it with `GET https://api.example.com/products?page_size=2&page=2` would result in:

```
{
  "data": [
    {"id": 3, "name": "Product C"},
    {"id": 4, "name": "Product D"}
  ]
}
```

and so on.

The Connector Builder abstracts this away so that you only need to decide what page size to set (the general recommendation is to use the largest limit that the API supports in order to minimize the number of API requests), what the starting page number should be (usually either 0 or 1 dependent on the API), and how the page size and number are injected into the API requests. Similar to Offset Increment pagination, the page size injection can be disabled if the API does not accept a page size value.

Either way, your connector will automatically increment the page number by 1 for each subsequent request, and continue until it receives fewer records than the page size you configured.

So for the example API and dataset above, you could apply the following configurations in the Connector Builder:

<iframe width="640" height="554" src="https://www.loom.com/embed/c6187b4e21534b9a825e93a002c33d06" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

- Mode: `Page Increment`
- Page size: `3`
- Start from page: `1`
- Inject page size into outgoing HTTP request:
  - Inject into: `request_parameter`
  - Field name: `page_size`
- Inject page number into outgoing HTTP request:
  - Inject into: `request_parameter`
  - Field name: `page`

and this would cause your connector to make the following requests to the API in order to paginate through all of its data:

```
GET https://api.example.com/products?page_size=2&page=1
  -> [
       {"id": 1, "name": "Product A"},
       {"id": 2, "name": "Product B"}
     ]

GET https://api.example.com/products?page_size=2&page=2
  -> [
       {"id": 3, "name": "Product C"},
       {"id": 4, "name": "Product D"}
     ]

GET https://api.example.com/products?page_size=3&page=3
  -> [
       {"id": 5, "name": "Product E"}
     ]
     // less than 2 records returned -> stop
```

The Connector Builder currently supports injecting these values into the query parameters (i.e. request parameters), headers, or body.

#### Examples

The following APIs accept page size/num paagination values as query parameters like in the above example"

- [WooCommerce API](https://woocommerce.github.io/woocommerce-rest-api-docs/#pagination)
- [FreshDesk API](https://developers.freshdesk.com/api/)

### Cursor Pagination

If your API paginates using cursor pagination, the API docs will likely contain one of the following keywords:

- `cursor`
- `link`
- `next_token`

In this method of pagination, some identifier (e.g. a timestamp or record ID) is used to navigate through the API's records, rather than relying on fixed indices or page numbers like in the above methods. When making a request, clients provide a cursor value, and the API returns a subset of records starting from the specified cursor, along with the cursor for the next page. This can be especially helpful in preventing issues like duplicate or skipped records that can arise when using the above pagination methods.

Using the [Twitter API](https://developer.twitter.com/en/docs/twitter-api/pagination) as an example, a request is made to the `/tweets` endpoint, with the page size (called `max_results` in this case) set to 100. This will return a response like

```
{
  "data": [
    {
      "created_at": "2020-12-11T20:44:52.000Z",
      "id": "1337498609819021312",
      "text": "Thanks to everyone who tuned in today..."
    },
    {
      "created_at": "2020-05-06T17:24:31.000Z",
      "id": "1258085245091368960",
      "text": "It’s now easier to understand Tweet impact..."
    },
    ...

  ],
  "meta": {
    ...
    "result_count": 100,
    "next_token": "7140w"
  }
}
```

The `meta.next_token` value of that response can then be set as the `pagination_token` in the next request, causing the API to return the next 100 tweets.

To integrate with such an API in the Connector Builder, you must configure how this "Next page cursor" is obtained for each request. In most cases, the next page cursor is either part of the response body or part of the HTTP headers. Select the respective type and define the property (or nested property) that holds the cursor value, for example "`meta`, `next_token`" for the twitter API.

You can also configure how the cursor value is injected into the API Requests. In the above example, this would be set as a `request_parameter` with the field name `pagination_token`, but this is dependent on the API - check the docs to see if they describe how to set the cursor/token for subsequent requests. For cursor pagination, if `path` is selected as the `Inject into` option, then the entire request URL for the subsequent request will be replaced by the cursor value. This can be useful for APIs that return a full URL that should be requested for the next page of results, such as the [GitHub API](https://docs.github.com/en/rest/guides/using-pagination-in-the-rest-api?apiVersion=2022-11-28).

<iframe width="640" height="563" src="https://www.loom.com/embed/c4f657153baa407b993bfadf6ea51532" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>

The "Page size" can optionally be specified as well; if so, how this page size gets injected into the HTTP requests can be configured similar to the above pagination methods.

When using the "response" or "headers" option for obtaining the next page cursor, the connector will stop requesting more pages as soon as no value can be found at the specified location. In some situations, this is not sufficient. If you need more control over how to obtain the cursor value and when to stop requesting pages, use the "custom" option and specify the "stop condition" using a jinja placeholder. For example if your API also has a boolean `more_results` property included in the response to indicate if there are more items to be retrieved, the stop condition should be `{{ response.more_results is false }}`

:::info

One potential variant of cursor pagination is an API that takes in some sort of record identifier to "start after". For example, the [PartnerStack API](https://docs.partnerstack.com/docs/partner-api#pagination) endpoints accept a `starting_after` parameter to which a record `key` is supposed to be passed.

In order to configure cursor pagination for this API in the connector builder, you will need to extract the `key` off of the last record returned by the previous request, using a "custom" next page cursor.
This can be done in a couple different ways:

1. If you want to access fields on the records that you have defined through the record selector, you can use the `{{ last_records }}` object; so accessing the `key` field of the last record would look like `{{ last_records[-1]['key'] }}`. The `[-1]` syntax points to the last item in that `last_records` array.
2. If you want to instead access a field on the raw API response body (e.g. your record selector filtered out the field you need), then you can use the `{{ response }}` object; so accessing the `key` field of the last item would look like `{{ response['data']['items'][-1]['key'] }}`.

This API also has a boolean `has_more` property included in the response to indicate if there are more items to be retrieved, so the stop condition in this case should be `{{ response.data.has_more is false }}`.

:::

#### Examples

The following APIs implement cursor pagination in various ways:

- [Twitter API](https://developer.twitter.com/en/docs/twitter-api/pagination) - includes `next_token` IDs in its responses which are passed in as query parameters to subsequent requests
- [GitHub API](https://docs.github.com/en/rest/guides/using-pagination-in-the-rest-api?apiVersion=2022-11-28) - includes full-URL `link`s to subsequent pages of results
- [FourSquare API](https://location.foursquare.com/developer/reference/pagination) - includes full-URL `link`s to subsequent pages of results

## Custom parameter injection

Using the "Inject page size / limit / offset into outgoing HTTP request" option in the pagination form works for most cases, but sometimes the API has special requirements that can't be handled this way:

- The API requires to add a prefix or a suffix to the actual value
- Multiple values need to be put together in a single parameter
- The value needs to be injected into the URL path
- Some conditional logic needs to be applied

To handle these cases, disable injection in the pagination form and use the generic parameter section at the bottom of the stream configuration form to freely configure query parameters, headers and properties of the JSON body, by using jinja expressions and [available variables](/connector-development/config-based/understanding-the-yaml-file/reference/#/variables). You can also use these variables as part of the URL path.

For example the [Prestashop API](https://devdocs.prestashop-project.org/8/webservice/cheat-sheet/#list-options) requires to set offset and limit separated by a comma into a single query parameter (`?limit=<offset>,<limit>`)
For this case, you can use the `next_page_token` variable to configure a query parameter with key `limit` and value `{{ next_page_token['next_page_token'] or '0' }},50` to inject the offset from the pagination strategy and a hardcoded limit of 50 into the same parameter.
