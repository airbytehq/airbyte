3PL Central source is modeled after their API, each stream representing an API resource. Then, four simple transformations are applied for each stream:

- Object keys are transformed from `TitleCase` to `snake_case`.
- [HAL](https://stateless.group/hal_specification.html) `_link` keys are removed from all objects.
- A `_cursor` field of date-time type is added for each incremental stream. The value of this field is a copy of an actual stream-specific and more or less deeply nested cursor field.
- An `_id` or `_{name}_id` field of integer type is added for each stream. The value of this field is a copy of an actual stream-specific and more or less deeply nested ID. `_id` is a primary key of a stream and is used when the actual ID of the resource is located in a nested object. `_{name}_id` is used when a resource itself doesn't have an ID, but the ID of a depending object is used as a part of a combined primary key where `{name}` is a name of depending object.

All schemas, field names, structure, and comments represent respective C# models described in the [API documentation (https://api.3plcentral.com/Rels/). Unfortunately, the documentation is somewhat outdated, and some endpoints return additional undocumented fields. These fields are added to the schemas to match actual data fields.

The API authentication endpoint requires either user login ID or name or both. API credentials can be obtained using the service UI.

Customer ID and Facility ID are used in URLs, be it path or query part.

API docs:

- https://api.3plcentral.com/Rels/
- https://developer.3plcentral.com
