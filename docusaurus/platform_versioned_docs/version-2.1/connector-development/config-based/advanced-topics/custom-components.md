# Custom Components

:::info
Please help us improve the low code CDK! If you find yourself needing to build a custom component,please [create a feature request issue](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fenhancement%2C+%2Cneeds-triage%2C+area%2Flow-code%2Fcomponents&template=feature-request.md&title=Low%20Code%20Feature:). If appropriate, we'll add it directly to the framework (or you can submit a PR)!

If an issue already exist for the missing feature you need, please upvote or comment on it so we can prioritize the issue accordingly.
:::

Any built-in components can be overloaded by a custom Python class.
To create a custom component, define a new class in a new file in the connector's module.
The class must implement the interface of the component it is replacing. For instance, a pagination strategy must implement `airbyte_cdk.sources.declarative.requesters.paginators.strategies.pagination_strategy.PaginationStrategy`.
The class must also be a dataclass where each field represents an argument to configure from the yaml file, and an `InitVar` named parameters.

For example:

```
@dataclass
class MyPaginationStrategy(PaginationStrategy):
  my_field: Union[InterpolatedString, str]
  parameters: InitVar[Mapping[str, Any]]

  def __post_init__(self, parameters: Mapping[str, Any]):
    pass

  def next_page_token(self, response: requests.Response, last_records: List[Mapping[str, Any]]) -> Optional[Any]:
    pass

  def reset(self):
    pass
```

This class can then be referred from the yaml file by specifying the type of custom component and using its fully qualified class name:

```yaml
pagination_strategy:
  type: "CustomPaginationStrategy"
  class_name: "my_connector_module.MyPaginationStrategy"
  my_field: "hello world"
```

### Custom Components that pass fields to child components

There are certain scenarios where a child subcomponent might rely on a field defined on a parent component. For regular components, we perform this propagation of fields from the parent component to the child automatically.
However, custom components do not support this behavior. If you have a child subcomponent of your custom component that falls under this use case, you will see an error message like:

```
Error creating component 'DefaultPaginator' with parent custom component source_example.components.CustomRetriever: Please provide DefaultPaginator.$parameters.url_base
```

When you receive this error, you can address this by defining the missing field within the `$parameters` block of the child component.

```yaml
  paginator:
    type: "DefaultPaginator"
    <...>
    $parameters:
      url_base: "https://example.com"
```