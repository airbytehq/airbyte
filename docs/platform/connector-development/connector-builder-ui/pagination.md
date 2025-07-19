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
- [Custom Pagination Strategy](#custom-pagination-strategy)

Select the matching pagination method for your API and check the sections below for more information about individual methods. If none of these pagination methods work for your API, you can implement a custom pagination strategy or use the [low-code CDK](../config-based/low-code-cdk-overview) or [Python CDK](../cdk-python/) instead.

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

The Connector Builder currently supports injecting these values into the query parameters (i.e. request parameters), headers, or body (JSON or form data).

#### Advanced Offset Increment Options

**Inject Offset on First Request**: By default, the first request doesn't include an offset parameter (assuming offset=0 is implicit). Enable this option if the API requires an explicit `offset=0` parameter in the first request.

**Interpolated Page Size**: You can use dynamic page sizes by setting the limit to an interpolated value:
- `{{ config['page_size'] }}` - Use a value from your connector configuration
- `"{{ config['page_size'] }}"` - Use a string interpolated value for APIs expecting string parameters

**Injection Options**: The limit and offset values can be injected into different parts of the HTTP request:
- **Request parameter**: Add as query parameters (most common)
- **Header**: Add as HTTP headers
- **Body (JSON)**: Add to the request body as JSON properties
- **Body (form data)**: Add to the request body as form data

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
GET https://api.example.com/products?page_size=3&page=1
  -> [
       {"id": 1, "name": "Product A"},
       {"id": 2, "name": "Product B"},
       {"id": 3, "name": "Product C"}
     ]

GET https://api.example.com/products?page_size=3&page=2
  -> [
       {"id": 4, "name": "Product D"},
       {"id": 5, "name": "Product E"},
       {"id": 6, "name": "Product F"}
     ]

GET https://api.example.com/products?page_size=3&page=3
  -> [
     ]
     // no records returned -> stop
```

The Connector Builder currently supports injecting these values into the query parameters (i.e. request parameters), headers, or body (JSON or form data).

#### Advanced Page Increment Options

**Start From Page**: Specify the initial page number. Use `0` for zero-based pagination (pages 0, 1, 2...) or `1` for one-based pagination (pages 1, 2, 3...). The default is `0`.

**Inject Page Number on First Request**: By default, the first request doesn't include a page parameter (assuming the first page is implicit). Enable this option if the API requires an explicit page number in the first request.

**Interpolated Page Size**: You can use dynamic page sizes by setting the page size to an interpolated value:
- `{{ config['page_size'] }}` - Use a value from your connector configuration
- `"{{ config['page_size'] }}"` - Use a string interpolated value for APIs expecting string parameters

**Zero-based vs One-based Pagination**: Different APIs use different page numbering schemes:

**Zero-based pagination** (Start From Page = 0):
- `GET /users?page=0&page_size=50` - First page
- `GET /users?page=1&page_size=50` - Second page

**One-based pagination** (Start From Page = 1):
- `GET /users?page=1&page_size=50` - First page
- `GET /users?page=2&page_size=50` - Second page

**Injection Options**: The page number and page size values can be injected into different parts of the HTTP request:
- **Request parameter**: Add as query parameters (most common)
- **Header**: Add as HTTP headers
- **Body (JSON)**: Add to the request body as JSON properties
- **Body (form data)**: Add to the request body as form data

#### Examples

The following APIs accept page size/num pagination values as query parameters like in the above example:

- [WooCommerce API](https://woocommerce.github.io/woocommerce-rest-api-docs/#pagination)
- [FreshDesk API](https://developers.freshdesk.com/api/)

### Cursor Pagination

If your API paginates using cursor pagination, the API docs will likely contain one of the following keywords:

- `cursor`
- `link`
- `next_token`

In this method of pagination, some identifier (e.g. a timestamp or record ID) is used to navigate through the API's records, rather than relying on fixed indices or page numbers like in the above methods. When making a request, clients provide a cursor value, and the API returns a subset of records starting from the specified cursor, along with the cursor for the next page. This can be especially helpful in preventing issues like duplicate or skipped records that can arise when using the above pagination methods.

Using the [Twitter API](https://developer.twitter.com/en/docs/twitter-api/pagination) as an example, a request is made to the `/tweets` endpoint, with the page size (called `max_results` in this case) set to 100. This will return a response like:

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

The "Page size" can optionally be specified as well; if so, how this page size gets injected into the HTTP requests can be configured similar to the above pagination methods.

When using the "response" or "headers" option for obtaining the next page cursor, the connector will stop requesting more pages as soon as no value can be found at the specified location. In some situations, this is not sufficient. If you need more control over how to obtain the cursor value and when to stop requesting pages, use the "custom" option and specify the "stop condition" using a jinja placeholder.

#### Advanced Cursor Pagination Features

**Cursor Value Context**: The cursor value template has access to the following context:
- `config` - Your connector configuration
- `headers` - Response headers (with parsed link header available as `headers.link`)
- `last_page_size` - Number of records in the current page
- `last_record` - The last record from the current page
- `response` - The full response body

**Stop Condition**: The stop condition is a template that determines when to stop paginating. Common patterns include:

- `{{ response.more_results is false }}` - Stop when a boolean flag indicates no more results
- `{{ response.pagination.next_cursor is none }}` - Stop when next_cursor is null
- `{{ not response.data }}` - Stop when data array is empty
- `{{ 'next' not in headers['link'] }}` - Stop when there's no 'next' link in headers
- `{{ response.data|length == 0 or response.pagination.next_cursor is none }}` - Complex condition combining multiple checks

**Page Size**: Even with cursor pagination, you can often specify how many records to return per page. Set this to optimize performance - larger page sizes mean fewer API calls but larger responses.

**Request Path vs Request Parameter**: There are two ways to inject cursor values:

- **Request Parameter** (most common): Adds the cursor as a query parameter, header, or body field
- **Request Path**: Replaces the entire URL path with the cursor value. This is useful when the API returns complete URLs for the next page, such as GitHub's API which returns full URLs in link headers.

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

### Custom Pagination Strategy

For APIs that use unique pagination mechanisms not covered by the standard methods (Offset Increment, Page Increment, or Cursor Pagination), you can implement a custom pagination strategy. This requires writing custom Python code as part of your connector implementation.

Custom pagination strategies are useful for:
- APIs with non-standard pagination mechanisms
- Complex pagination logic that requires custom calculations
- APIs that require special handling of pagination tokens or cursors
- Pagination methods that combine multiple approaches

To use a custom pagination strategy:

1. Set the **Pagination method** to "Custom Pagination Strategy"
2. Set the **Class Name** to the fully-qualified name of your custom class
3. The class name must follow the format: `source_<name>.<package>.<class_name>`

#### Implementation Requirements

Your custom pagination class must:
- Inherit from `PaginationStrategy` in the Airbyte CDK
- Implement the required methods for determining the next page token
- Be located in your connector's source code

#### Example

If you have a custom pagination class in your connector:

```python
# In source_myapi/components.py
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy import PaginationStrategy

class MyCustomPaginationStrategy(PaginationStrategy):
    def next_page_token(self, response, last_page_size, last_record, last_page_token_value):
        # Your custom pagination logic here
        # Return the next page token or None to stop pagination
        pass
    
    def get_page_size(self):
        # Return the page size for this strategy
        return self.page_size
```

Configure it in the Connector Builder as:
1. Set **Pagination method** to "Custom Pagination Strategy"
2. Set **Class Name** to `source_myapi.components.MyCustomPaginationStrategy`

When implementing custom pagination strategies, you have access to the same context as other pagination methods, including the response data, headers, and configuration values.

## Custom parameter injection

Using the "Inject page size / limit / offset into outgoing HTTP request" option in the pagination form works for most cases, but sometimes the API has special requirements that can't be handled this way:

- The API requires to add a prefix or a suffix to the actual value
- Multiple values need to be put together in a single parameter
- The value needs to be injected into the URL path
- Some conditional logic needs to be applied

To handle these cases, disable injection in the pagination form and use the generic parameter section at the bottom of the stream configuration form to freely configure query parameters, headers and properties of the JSON body, by using jinja expressions and [available variables](/platform/connector-development/config-based/understanding-the-yaml-file/reference/#/variables). You can also use these variables as part of the URL path.

For example the [Prestashop API](https://devdocs.prestashop-project.org/8/webservice/cheat-sheet/#list-options) requires to set offset and limit separated by a comma into a single query parameter (`?limit=<offset>,<limit>`)
For this case, you can use the `next_page_token` variable to configure a query parameter with key `limit` and value `{{ next_page_token['next_page_token'] or '0' }},50` to inject the offset from the pagination strategy and a hardcoded limit of 50 into the same parameter.

## Real-world Examples

### GitHub API (Link Header Pagination)
GitHub uses cursor pagination with link headers:

```
Link: <https://api.github.com/repos/octocat/Hello-World/issues?page=2>; rel="next",
      <https://api.github.com/repos/octocat/Hello-World/issues?page=5>; rel="last"
```

Configuration:
- **Pagination method**: Cursor Pagination
- **Cursor value**: `{{ headers.link.next.url }}`
- **Inject into**: Request path
- **Stop condition**: `{{ 'next' not in headers['link'] }}`

### Stripe API (Object-based Cursor)
Stripe uses the ID of the last object as a cursor:

```json
{
  "data": [{"id": "cus_123"}, {"id": "cus_456"}],
  "has_more": true
}
```

Configuration:
- **Pagination method**: Cursor Pagination
- **Cursor value**: `{{ last_record['id'] }}`
- **Cursor parameter name**: `starting_after`
- **Stop condition**: `{{ response.has_more is false }}`

### REST API with Zero-based Pages
A typical REST API with zero-based pagination:

Configuration:
- **Pagination method**: Page Increment
- **Start From Page**: 0
- **Page size**: 100
- **Inject Page Number on First Request**: Enabled (if API requires explicit page=0)

## Performance Recommendations

1. **Use the largest page size supported by the API** to minimize the number of requests
2. **Set appropriate stop conditions** to avoid unnecessary API calls
3. **Test with small page sizes first** to verify pagination works correctly
4. **Monitor API rate limits** when using large page sizes
5. **Use interpolated values** for configurable page sizes: `{{ config['page_size'] }}`

## Testing Pagination

When testing your pagination configuration:

1. **Start with small page sizes** (e.g., 2-5 records) to see multiple pages quickly
2. **Verify stop conditions** - Check that the connector stops paginating when there are no more records
3. **Check for completeness** - Verify that all records are retrieved without duplicates
4. **Test different page sizes** to ensure the configuration works correctly across different scenarios
5. **Validate first request behavior** - Ensure the first request works correctly with or without pagination parameters
6. **Test edge cases** - Try scenarios with empty responses, single records, or API errors

## Troubleshooting

### Infinite pagination

If your connector keeps paginating indefinitely:

- **Check stop condition**: Verify that your stop condition is correct and evaluates to true when there are no more pages
- **Verify cursor extraction**: Make sure the cursor value is being extracted correctly from the response
- **Validate API responses**: Ensure the API actually returns different data for each page
- **Check API limits**: Some APIs have maximum page limits that you might be exceeding
- **Review pagination logic**: For custom strategies, verify your pagination logic is sound

### Missing records

If some records are missing:

- **Verify parameter injection**: Check that pagination parameters are being injected correctly into the request
- **Check page size limits**: Ensure the page size is not too large for the API (some APIs have maximum limits)
- **Validate cursor extraction**: Make sure the cursor value is being extracted from the correct field in the response
- **Confirm pagination method**: Verify that the pagination method matches what the API expects
- **Review API documentation**: Double-check the API's pagination requirements

### Duplicate records

If you're seeing duplicate records:

- **Check pagination method**: Ensure the pagination method matches what the API expects (offset vs page vs cursor)
- **Verify cursor/offset calculation**: Make sure the cursor or offset is being calculated correctly
- **Avoid mixing methods**: Don't mix different pagination approaches in the same configuration
- **Validate cursor uniqueness**: For cursor pagination, ensure the cursor value uniquely identifies the position in the dataset

### First request issues

If the first request fails or behaves unexpectedly:

- **Check injection settings**: Verify if you need to enable "Inject Page Number on First Request" or "Inject Offset on First Request" for the first request
- **Validate start page**: Ensure the "Start From Page" value matches the API's expectations (0-based vs 1-based)
- **Review API requirements**: Some APIs don't accept pagination parameters on the first request - disable injection if needed
- **Test without pagination**: Try making a request without pagination parameters to understand the API's default behavior

### Stop condition not working

If pagination doesn't stop when expected:

- **Verify template syntax**: Check that the stop condition template syntax is correct
- **Validate field references**: Ensure you're referencing the right fields in the response
- **Test with sample data**: Test the stop condition logic with actual API responses
- **Check context availability**: Make sure the stop condition has access to the correct context (response, headers, etc.)
- **Debug with simple conditions**: Start with simple stop conditions and gradually add complexity

### Parameter injection issues

If pagination parameters aren't being sent correctly:

- **Verify injection method**: Ensure you're using the correct injection method (request_parameter, header, body_data, body_json)
- **Check parameter names**: Verify that parameter names match what the API expects
- **Test interpolation**: For interpolated values, ensure the template syntax is correct
- **Review API documentation**: Confirm the expected parameter format and location
