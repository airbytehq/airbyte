# Advanced topics

## Stream Slicers

`StreamSlicer`s define how to partition a stream into a subset of records.

It can be thought of as an iterator over the stream's data, where a `StreamSlice` is the retriever's unit of work.

When a stream is read incrementally, a state message will be output by the connector after reading every slice, which allows for [checkpointing](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/#state--checkpointing).

At the beginning of a `read` operation, the `StreamSlicer` will compute the slices to sync given the connection config and the stream's current state,
As the `Retriever` reads data from the `Source`, the `StreamSlicer` keeps track of the `Stream`'s state, which will be emitted after reading each stream slice.

More information of stream slicing can be found in the [stream-slices section](../cdk-python/stream-slices.md).

Schema:

```yaml
StreamSlicer:
  type: object
  oneOf:
    - "$ref": "#/definitions/DatetimeStreamSlicer"
    - "$ref": "#/definitions/ListStreamSlicer"
    - "$ref": "#/definitions/CartesianProductStreamSlicer"
    - "$ref": "#/definitions/SubstreamSlicer"
    - "$ref": "#/definitions/SingleSlice"
```

### Single slice

The single slice only produces one slice for the whole stream.

Schema:

```yaml
SingleSlice:
  type: object
  additionalProperties: false
```

### DatetimeStreamSlicer

The `DatetimeStreamSlicer` iterates over a datetime range by partitioning it into time windows.
This is done by slicing the stream on the records' cursor value, defined by the Stream's `cursor_field`.

Given a start time, an end time, and a step function, it will partition the interval [start, end] into small windows of the size described by the step.
For instance,

Schema:

```yaml
DatetimeStreamSlicer:
  type: object
  required:
    - start_datetime
    - end_datetime
    - step
    - cursor_field
    - datetime_format
  additional_properties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    start_datetime:
      "$ref": "#/definitions/MinMaxDatetime"
    end_datetime:
      "$ref": "#/definitions/MinMaxDatetime"
    step:
      type: string
    cursor_field:
      type: string
    datetime_format:
      type: string
    start_time_option:
      "$ref": "#/definitions/RequestOption"
    end_time_option:
      "$ref": "#/definitions/RequestOption"
    stream_state_field_start:
      type: string
    stream_state_field_end:
      type: string
    lookback_window:
      type: string
MinMaxDatetime:
  type: object
  required:
    - datetime
  additionalProperties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    datetime:
      type: string
    datetime_format:
      type: string
    min_datetime:
      type: string
    max_datetime:
      type: string
```

Example:

```yaml
stream_slicer:
  start_datetime: "2021-02-01T00:00:00.000000+0000",
  end_datetime: "2021-03-01T00:00:00.000000+0000",
  step: "1d"
```

will create one slice per day for the interval `2021-02-01` - `2021-03-01`.

The `DatetimeStreamSlicer` also supports an optional lookback window, specifying how many days before the start_datetime to read data for.

```yaml
stream_slicer:
  start_datetime: "2021-02-01T00:00:00.000000+0000",
  end_datetime: "2021-03-01T00:00:00.000000+0000",
  lookback_window: "31d"
  step: "1d"
```

will read data from `2021-01-01` to `2021-03-01`.

The stream slices will be of the form `{"start_date": "2021-02-01T00:00:00.000000+0000", "end_date": "2021-02-01T00:00:00.000000+0000"}`
The stream slices' field names can be customized through the `stream_state_field_start` and `stream_state_field_end` parameters.

The `datetime_format` can be used to specify the format of the start and end time. It is [RFC3339](https://datatracker.ietf.org/doc/html/rfc3339#section-5.6) by default.

The Stream's state will be derived by reading the record's `cursor_field`.
If the `cursor_field` is `created`, and the record is `{"id": 1234, "created": "2021-02-02T00:00:00.000000+0000"}`, then the state after reading that record is `"created": "2021-02-02T00:00:00.000000+0000"`. [^1]

#### Cursor update

When reading data from the source, the cursor value will be updated to the max datetime between

- The last record's cursor field
- The start of the stream slice
- The current cursor value. This ensures that the cursor will be updated even if a stream slice does not contain any data

#### Stream slicer on dates

If an API supports filtering data based on the cursor field, the `start_time_option` and `end_time_option` parameters can be used to configure this filtering.
For instance, if the API supports filtering using the request parameters `created[gte]` and `created[lte]`, then the stream slicer can specify the request parameters as

```yaml
stream_slicer:
  type: "DatetimeStreamSlicer"
  <...>
  start_time_option:
    field_name: "created[gte]"
    inject_into: "request_parameter"
  end_time_option:
    field_name: "created[lte]"
    inject_into: "request_parameter"
```

### List stream slicer

`ListStreamSlicer` iterates over values from a given list.
It is defined by

- The slice values, which are the valid values for the cursor field
- The cursor field on a record
- request_option: optional request option to set on outgoing request parameters

Schema:

```yaml
ListStreamSlicer:
  type: object
  required:
    - slice_values
    - cursor_field
  additionalProperties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    slice_values:
      type: array
      items:
        type: string
    cursor_field:
      type: string
    request_option:
      "$ref": "#/definitions/RequestOption"
```

As an example, this stream slicer will iterate over the 2 repositories ("airbyte" and "airbyte-secret") and will set a request_parameter on outgoing HTTP requests.

```yaml
stream_slicer:
  type: "ListStreamSlicer"
  slice_values:
    - "airbyte"
    - "airbyte-secret"
  cursor_field: "repository"
  request_option:
    field_name: "repository"
    inject_into: "request_parameter"
```

### Cartesian Product stream slicer

`CartesianProductStreamSlicer` iterates over the cartesian product of its underlying stream slicers.

Schema:

```yaml
CartesianProductStreamSlicer:
  type: object
  required:
    - stream_slicers
  additionalProperties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    stream_slicers:
      type: array
      items:
        "$ref": "#/definitions/StreamSlicer"
```

Given 2 stream slicers with the following slices:
A: `[{"start_date": "2021-01-01", "end_date": "2021-01-01"}, {"start_date": "2021-01-02", "end_date": "2021-01-02"}]`
B: `[{"s": "hello"}, {"s": "world"}]`
the resulting stream slices are

```
[
    {"start_date": "2021-01-01", "end_date": "2021-01-01", "s": "hello"},
    {"start_date": "2021-01-01", "end_date": "2021-01-01", "s": "world"},
    {"start_date": "2021-01-02", "end_date": "2021-01-02", "s": "hello"},
    {"start_date": "2021-02-01", "end_date": "2021-02-01", "s": "world"},
]
```

[^1] This is a slight oversimplification. See [update cursor section](#cursor-update) for more details on how the cursor is updated.

### SubstreamSlicers

Substreams are streams that depend on the records on another stream

We might for instance want to read all the commits for a given repository (parent stream).

Substreams are implemented by defining their stream slicer as a`SubstreamSlicer`.

`SubstreamSlicer` iterates over the parent's stream slices.
We might for instance want to read all the commits for a given repository (parent resource).

- what the parent stream is
- what is the key of the records in the parent stream
- what is the field defining the stream slice representing the parent record
- how to specify that information on an outgoing HTTP request

Schema:

```yaml
SubstreamSlicer:
  type: object
  required:
    - parent_stream_configs
  additionalProperties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    parent_stream_configs:
      type: array
      items:
        "$ref": "#/definitions/ParentStreamConfig"
ParentStreamConfig:
  type: object
  required:
    - stream
    - parent_key
    - stream_slice_field
  additionalProperties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    stream:
      "$ref": "#/definitions/Stream"
    parent_key:
      type: string
    stream_slice_field:
      type: string
    request_option:
      "$ref": "#/definitions/RequestOption"
```

Example:

```yaml
stream_slicer:
  type: "SubstreamSlicer"
  parent_streams_configs:
    - stream: "*ref(repositories_stream)"
      parent_key: "id"
      stream_slice_field: "repository"
      request_option:
        field_name: "repository"
        inject_into: "request_parameter"
```

REST APIs often nest sub-resources in the URL path.
If the URL to fetch commits was "/repositories/:id/commits", then the `Requester`'s path would need to refer to the stream slice's value and no `request_option` would be set:

Example:

```yaml
retriever:
  <...>
  requester:
    <...>
    path: "/respositories/{{ stream_slice.repository }}/commits"
  stream_slicer:
    type: "SubstreamSlicer"
parent_streams_configs:
  - stream: "*ref(repositories_stream)"
    parent_key: "id"
    stream_slice_field: "repository"
```

## Nested streams

Nested streams, subresources, or streams that depend on other streams can be implemented using a [`SubstreamSlicer`](#substreamslicers)

## Error handling

By default, only server errors (HTTP 5XX) and too many requests (HTTP 429) will be retried up to 5 times with exponential backoff.
Other HTTP errors will result in a failed read.

Other behaviors can be configured through the `Requester`'s `error_handler` field.

Schema:

```yaml
ErrorHandler:
  type: object
  description: "Error handler"
  oneOf:
    - "$ref": "#/definitions/DefaultErrorHandler"
    - "$ref": "#/definitions/CompositeErrorHandler"
BackoffStrategy:
  type: object
  oneOf:
    - "$ref": "#/definitions/ExponentialBackoff"
    - "$ref": "#/definitions/ConstantBackoff"
    - "$ref": "#/definitions/WaitTimeFromHeader"
    - "$ref": "#/definitions/WaitUntilTimeFromHeader"
```

### Default error handler

Schema:

```yaml
DefaultErrorHandler:
  type: object
  required:
    - max_retries
  additionalProperties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    response_filters:
      type: array
      items:
        "$ref": "#/definitions/HttpResponseFilter"
    max_retries:
      type: integer
      default: 5
    backoff_strategies:
      type: array
      items:
        "$ref": "#/definitions/BackoffStrategy"
      default: [ ]
```

### Defining errors

#### From status code

Response filters can be used to define how to handle requests resulting in responses with a specific HTTP status code.
For instance, this example will configure the handler to also retry responses with 404 error:

Schema:

```yaml
HttpResponseFilter:
  type: object
  required:
    - action
  additionalProperties: false
  properties:
    "$options":
      "$ref": "#/definitions/$options"
    action:
      "$ref": "#/definitions/ResponseAction"
    http_codes:
      type: array
      items:
        type: integer
      default: [ ]
    error_message_contains:
      type: string
    predicate:
      type: string
ResponseAction:
  type: string
  enum:
    - SUCCESS
    - FAIL
    - IGNORE
    - RETRY
```

Example:

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - http_codes: [ 404 ]
          action: RETRY
```

Response filters can be used to specify HTTP errors to ignore.
For instance, this example will configure the handler to ignore responses with 404 error:

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - http_codes: [ 404 ]
          action: IGNORE
```

#### From error message

Errors can also be defined by parsing the error message.
For instance, this error handler will ignore responses if the error message contains the string "ignorethisresponse"

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - error_message_contain: "ignorethisresponse"
          action: IGNORE
```

This can also be done through a more generic string interpolation strategy with the following parameters:

- response: the decoded response

This example ignores errors where the response contains a "code" field:

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - predicate: "{{ 'code' in response }}"
          action: IGNORE
```

The error handler can have multiple response filters.
The following example is configured to ignore 404 errors, and retry 429 errors:

```yaml
requester:
  <...>
  error_handler:
    response_filters:
        - http_codes: [ 404 ]
          action: IGNORE
                    - http_codes: [ 429 ]
                    action: RETRY
```

### Backoff Strategies

The error handler supports a few backoff strategies, which are described in the following sections.

#### Exponential backoff

This is the default backoff strategy. The requester will backoff with an exponential backoff interval

Schema:

```yaml
  ExponentialBackoff:
    type: object
    additionalProperties: false
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      factor:
        type: integer
        default: 5
```

#### Constant Backoff

When using the `ConstantBackoffStrategy`, the requester will backoff with a constant interval.

Schema:

```yaml
  ConstantBackoff:
    type: object
    additionalProperties: false
    required:
      - backoff_time_in_seconds
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      backoff_time_in_seconds:
        type: number
```

#### Wait time defined in header

When using the `WaitTimeFromHeaderBackoffStrategy`, the requester will backoff by an interval specified in the response header.
In this example, the requester will backoff by the response's "wait_time" header value:

Schema:

```yaml
  WaitTimeFromHeader:
    type: object
    additionalProperties: false
    required:
      - header
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      header:
        type: string
      regex:
        type: string
```

Example:

```yaml
requester:
  <...>
  error_handler:
    <...>
    backoff_strategies:
        - type: "WaitTimeFromHeaderBackoffStrategy"
          header: "wait_time"
```

Optionally, a regular expression can be configured to extract the wait time from the header value.

Example:

```yaml
requester:
  <...>
  error_handler:
    <...>
    backoff_strategies:
        - type: "WaitTimeFromHeaderBackoffStrategy"
          header: "wait_time"
          regex: "[-+]?\d+"
```

#### Wait until time defined in header

When using the `WaitUntilTimeFromHeaderBackoffStrategy`, the requester will backoff until the time specified in the response header.
In this example, the requester will wait until the time specified in the "wait_until" header value:

Schema:

```yaml
  WaitUntilTimeFromHeader:
    type: object
    additionalProperties: false
    required:
      - header
    properties:
      "$options":
        "$ref": "#/definitions/$options"
      header:
        type: string
      regex:
        type: string
      min_wait:
        type: float
```

Example:

```yaml
requester:
  <...>
  error_handler:
    <...>
    backoff_strategies:
        - type: "WaitUntilTimeFromHeaderBackoffStrategy"
          header: "wait_until"
          regex: "[-+]?\d+"
          min_wait: 5
```

The strategy accepts an optional regular expression to extract the time from the header value, and a minimum time to wait.

### Advanced error handling

The error handler can have multiple backoff strategies, allowing it to fallback if a strategy cannot be evaluated.
For instance, the following defines an error handler that will read the backoff time from a header, and default to a constant backoff if the wait time could not be extracted from the response:

Example:

```yaml
requester:
  <...>
  error_handler:
    <...>
    backoff_strategies:
        - type: "WaitTimeFromHeaderBackoffStrategy"
          header: "wait_time"
            - type: "ConstantBackoffStrategy"
              backoff_time_in_seconds: 5

```

The `requester` can be configured to use a `CompositeErrorHandler`, which sequentially iterates over a list of error handlers, enabling different retry mechanisms for different types of errors.

In this example, a constant backoff of 5 seconds, will be applied if the response contains a "code" field, and an exponential backoff will be applied if the error code is 403:

Schema:

```yaml
CompositeErrorHandler:
  type: object
  required:
    - error_handlers
  additionalProperties:
    "$options":
      "$ref": "#/definitions/$options"
    error_handlers:
      type: array
      items:
        "$ref": "#/definitions/ErrorHandler"
```

Example:

```yaml
requester:
  <...>
  error_handler:
    type: "CompositeErrorHandler"
    error_handlers:
      - response_filters:
          - predicate: "{{ 'code' in response }}"
            action: RETRY
        backoff_strategies:
          - type: "ConstantBackoffStrategy"
            backoff_time_in_seconds: 5
      - response_filters:
          - http_codes: [ 403 ]
            action: RETRY
        backoff_strategies:
          - type: "ExponentialBackoffStrategy"
```

## Transformations

Fields can be added or removed from records by adding `Transformation`s to a stream's definition.

### Adding fields

Fields can be added with the `AddFields` transformation.
This example adds a top-level field "field1" with a value "static_value"

```yaml
stream:
  <...>
  transformations:
      - type: AddFields
        fields:
          - path: [ "field1" ]
            value: "static_value"
```

This example adds a top-level field "start_date", whose value is evaluated from the stream slice:

```yaml
stream:
  <...>
  transformations:
      - type: AddFields
        fields:
          - path: [ "start_date" ]
            value: { { stream_slice[ 'start_date' ] } }
```

Fields can also be added in a nested object by writing the fields' path as a list.

Given a record of the following shape:

```
{
  "id": 0,
  "data":
  {
    "field0": "some_data"
  }
}
```

this definition will add a field in the "data" nested object:

```yaml
stream:
  <...>
  transformations:
      - type: AddFields
        fields:
          - path: [ "data", "field1" ]
            value: "static_value"
```

resulting in the following record:

```
{
  "id": 0,
  "data":
  {
    "field0": "some_data",
    "field1": "static_value"
  }
}
```

### Removing fields

Fields can be removed from records with the `RemoveFields` transformation.

Given a record of the following shape:

```
{
  "path": 
  {
    "to":
    {
      "field1": "data_to_remove",
      "field2": "data_to_keep"
    }
  },
  "path2": "data_to_remove",
  "path3": "data_to_keep"
}
```

this definition will remove the 2 instances of "data_to_remove" which are found in "path2" and "path.to.field1":

```yaml
the_stream:
  <...>
  transformations:
      - type: RemoveFields
        field_pointers:
          - [ "path", "to", "field1" ]
          - [ "path2" ]
```

resulting in the following record:

```
{
  "path": 
  {
    "to":
    {
      "field2": "data_to_keep"
    }
  },
  "path3": "data_to_keep"
}
```

## Custom components

Any builtin components can be overloaded by a custom Python class.
To create a custom component, define a new class in a new file in the connector's module.
The class must implement the interface of the component it is replacing. For instance, a pagination strategy must implement `airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy.PaginationStrategy`.
The class must also be a dataclass where each field represents an argument to configure from the yaml file, and an `InitVar` named options.

For example:

```
@dataclass
class MyPaginationStrategy(PaginationStrategy):
  my_field: Union[InterpolatedString, str]
  options: InitVar[Mapping[str, Any]]

  def __post_init__(self, options: Mapping[str, Any]):
    pass

  def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
    pass

  def reset(self):
    pass
```

This class can then be referred from the yaml file using its fully qualified class name:

```yaml
pagination_strategy:
  class_name: "my_connector_module.MyPaginationStrategy"
  my_field: "hello world"
```

## How the framework works

1. Given the connection config and the current stream state, the `StreamSlicer` computes the stream slices to read.
2. Iterate over all the stream slices defined by the stream slicer.
3. For each stream slice,
    1. Submit a request as defined by the requester
    2. Select the records from the response
    3. Repeat for as long as the paginator points to a next page

[connector-flow](./assets/connector-flow.png)

## Object instantiation

This section describes the object that are to be instantiated from the YAML definition.

If the component is a literal, then it is returned as is:

```
3
```

will result in

```
3
```

If the component is a mapping with a "class_name" field,
an object of type "class_name" will be instantiated by passing the mapping's other fields to the constructor

```yaml
my_component:
  class_name: "fully_qualified.class_name"
  a_parameter: 3
  another_parameter: "hello"
```

will result in

```
fully_qualified.class_name(a_parameter=3, another_parameter="hello")
```

If the component definition is a mapping with a "type" field,
the factory will lookup the [CLASS_TYPES_REGISTRY](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/declarative/parsers/class_types_registry.py) and replace the "type" field by "class_name" -> CLASS_TYPES_REGISTRY[type]
and instantiate the object from the resulting mapping

If the component definition is a mapping with neither a "class_name" nor a "type" field,
the factory will do a best-effort attempt at inferring the component type by looking up the parent object's constructor type hints.
If the type hint is an interface present in [DEFAULT_IMPLEMENTATIONS_REGISTRY](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/declarative/parsers/default_implementation_registry.py,
then the factory will create an object of its default implementation.

If the component definition is a list, then the factory will iterate over the elements of the list,
instantiate its subcomponents, and return a list of instantiated objects.

If the component has subcomponents, the factory will create the subcomponents before instantiating the top level object

```
{
  "type": TopLevel
  "param":
    {
      "type": "ParamType"
      "k": "v"
    }
}
```

will result in

```
TopLevel(param=ParamType(k="v"))
```

More details on object instantiation can be found [here](https://airbyte-cdk.readthedocs.io/en/latest/api/airbyte_cdk.sources.declarative.parsers.html?highlight=factory#airbyte_cdk.sources.declarative.parsers.factory.DeclarativeComponentFactory).

### $options

Parameters can be passed down from a parent component to its subcomponents using the $options key.
This can be used to avoid repetitions.

Schema:

```yaml
"$options":
  type: object
  additionalProperties: true
```

Example:

```yaml
outer:
  $options:
    MyKey: MyValue
  inner:
    k2: v2
```

This the example above, if both outer and inner are types with a "MyKey" field, both of them will evaluate to "MyValue".

These parameters can be overwritten by subcomponents as a form of specialization:

```yaml
outer:
  $options:
    MyKey: MyValue
  inner:
    $options:
      MyKey: YourValue
    k2: v2
```

In this example, "outer.MyKey" will evaluate to "MyValue", and "inner.MyKey" will evaluate to "YourValue".

The value can also be used for string interpolation:

```yaml
outer:
  $options:
    MyKey: MyValue
  inner:
    k2: "MyKey is {{ options['MyKey'] }}"
```

In this example, outer.inner.k2 will evaluate to "MyKey is MyValue"

## References

Strings can contain references to previously defined values.
The parser will dereference these values to produce a complete object definition.

References can be defined using a "*ref({arg})" string.

```yaml
key: 1234
reference: "*ref(key)"
```

will produce the following definition:

```yaml
key: 1234
reference: 1234
```

This also works with objects:

```yaml
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs: "*ref(key_value_pairs)"
```

will produce the following definition:

```yaml
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs:
  k1: v1
  k2: v2
```

The $ref keyword can be used to refer to an object and enhance it with addition key-value pairs

```yaml
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs:
  $ref: "*ref(key_value_pairs)"
  k3: v3
```

will produce the following definition:

```yaml
key_value_pairs:
  k1: v1
  k2: v2
same_key_value_pairs:
  k1: v1
  k2: v2
  k3: v3
```

References can also point to nested values.
Nested references are ambiguous because one could define a key containing with `.`
in this example, we want to refer to the limit key in the dict object:

```yaml
dict:
  limit: 50
limit_ref: "*ref(dict.limit)"
```

will produce the following definition:

```yaml
dict
limit: 50
limit-ref: 50
```

whereas here we want to access the `nested.path` value.

```yaml
nested:
  path: "first one"
nested.path: "uh oh"
value: "ref(nested.path)
```

will produce the following definition:

```yaml
nested:
  path: "first one"
nested.path: "uh oh"
value: "uh oh"
```

To resolve the ambiguity, we try looking for the reference key at the top-level, and then traverse the structs downward
until we find a key with the given path, or until there is nothing to traverse.

More details on referencing values can be found [here](https://airbyte-cdk.readthedocs.io/en/latest/api/airbyte_cdk.sources.declarative.parsers.html?highlight=yamlparser#airbyte_cdk.sources.declarative.parsers.yaml_parser.YamlParser).

## String interpolation

String values can be evaluated as Jinja2 templates.

If the input string is a raw string, the interpolated string will be the same.
`"hello world" -> "hello world"`

The engine will evaluate the content passed within `{{...}}`, interpolating the keys from context-specific arguments.
The "options" keyword [see ($options)](yaml-structure.md#object-instantiation) can be referenced.

For example, some_object.inner_object.key will evaluate to "Hello airbyte" at runtime.

```yaml
some_object:
  $options:
    name: "airbyte"
  inner_object:
    key: "Hello {{ options.name }}"
```

Some components also pass in additional arguments to the context.
This is the case for the [record selector](record-selector.md), which passes in an additional `response` argument.

Both dot notation and bracket notations (with single quotes ( `'`)) are interchangeable.
This means that both these string templates will evaluate to the same string:

1. `"{{ options.name }}"`
2. `"{{ options['name'] }}"`

In addition to passing additional values through the $options argument, macros can be called from within the string interpolation.
For example,
`"{{ max(2, 3) }}" -> 3`

The macros available can be found [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-cdk/python/airbyte_cdk/sources/declarative/interpolation/macros.py).

Additional information on jinja templating can be found at https://jinja.palletsprojects.com/en/3.1.x/templates/#
