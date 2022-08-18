# Request Options

There are a few ways to set request parameters, headers, and body on ongoing HTTP requests.

## Request Options Provider

The primary way to set request options is through the `Requester`'s `RequestOptionsProvider`.
The options can be configured as key value pairs:

```yaml
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.exchangeratesapi.io/v1/"
  http_method: "GET"
  request_options_provider:
    request_parameters:
      k1: v1
      k2: v2
    request_headers:
      header_key1: header_value1
      header_key2: header_value2
```

It is also possible to configure add a json-encoded body to outgoing requests.

```yaml
requester:
  type: HttpRequester
  name: "{{ options['name'] }}"
  url_base: "https://api.exchangeratesapi.io/v1/"
  http_method: "GET"
  request_options_provider:
    request_body_json:
      key: value
```

## Authenticators

It is also possible for authenticators to set request parameters or headers as needed.
For instance, the `BearerAuthenticator` will always set the `Authorization` header.

More details on the various authenticators can be found in the [authentication section](authentication.md).

## Paginators

The `LimitPaginator` can optionally set request options through the `limit_option` and the `page_token_option`.
The respective values can be set on the outgoing HTTP requests by specifying where it should be injected.

The following example will set the "page" request parameter value to the page to fetch, and the "page_size" request parameter to 5:

```yaml
paginator:
  type: "LimitPaginator"
  page_size: 5
  limit_option:
    option_type: request_parameter
    field_name: page_size
  pagination_strategy:
    type: "PageIncrement"
  page_token:
    option_type: "request_parameter"
    field_name: "page"
```

More details on paginators can be found in the [pagination section](pagination.md).

## Stream slicers

The `DatetimeStreamSlicer` can optionally set request options through the `start_time_option` and `end_time_option` fields.
The respective values can be set on the outgoing HTTP requests by specifying where it should be injected.

The following example will set the "created[gte]" request parameter value to the start of the time window, and "created[lte]" to the end of the time window.

```yaml
stream_slicer:
  start_datetime: "2021-02-01T00:00:00.000000+0000",
  end_datetime: "2021-03-01T00:00:00.000000+0000",
  step: "1d"
  start_time_option:
    field_name: "created[gte]"
    inject_into: "request_parameter"
  end_time_option:
    field_name: "created[lte]"
    inject_into: "request_parameter"
```

More details on the stream slicers can be found in the [stream-slicers section](stream-slicers.md).
