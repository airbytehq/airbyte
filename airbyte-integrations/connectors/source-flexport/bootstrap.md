# Flexport

Flexport is a straightforward CRUD REST [API](https://developers.flexport.com/s/api). It consists of some REST resources like Company, Location, Product, etc., each of which is uniformly paginated. Each resource has a link to a related resource or resource collection. All relations might be optionally embedded within the resource instance. The `id` property identifies each resource.

API documentation is either outdated or incomplete. The issues are following:

1) Some resources that get embedded by default are not documented at all. However, since the schema of all resources follows the same pattern, their schema can be easily deduced too.
2) The documentation doesn't specify which properties are nullable - trial and error is the only way to learn that.
3) Some properties' type is ambiguous, i.e., `create` action specifies a property as required while `read` returns a nullable value.
4) The type of some properties is mislabeled, e.g., `integer` instead of an actual `string` type.

Authentication uses a pre-created API token which can be [created in the UI](https://apidocs.flexport.com/reference/authentication).

Paginations uses page number and items per page strategy.
