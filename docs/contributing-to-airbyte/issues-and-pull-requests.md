# Issues & Pull Requests

## Titles

**Describe outputs, not implementation**: An issue or PR title should describe the desired end result, not the implementation. The exception is child issues/subissues of an epic. **Be specific about the domain**. Airbyte operates a monorepo, so being specific about what is being changed in the PR or issue title is important.

Some examples: _subpar issue title_: `Remove airbyteCdk.dependsOn("unrelatedPackage")`. This describes a solution not a problem.

_good issue title_: `Building the Airbyte Python CDK should not build unrelated packages`. Describes desired end state and the intent is understandable without reading the full issue.

_subpar PR title_: `Update tests`. Which tests? What was the update?

_good PR title_: `Source MySQL: update acceptance tests to connect to SSL-enabled database`. Specific about the domain and change that was made.

### Pull Request Title Convention

When creating a pull request follow the naming conventions depending on the change being made.
In general the pull request title starts with an emoji with the connector you're doing the changes, eg (✨ Source E-Commerce: add new stream `Users`).
Airbyte uses this pattern to automatically assign team reviews and build the product release notes.

| Pull Request Type | Emoji | Examples |
| ----------------- | ----- | ---------|
| New Connector (Source or Destination)  | 🎉 | 🎉 New Destination: Database                           |
| Add a feature to an existing connector | ✨ | ✨ Source E-Commerce: add new stream `Users`           |
| Fix a bug                              | 🐛 | 🐛 Source E-Commerce: fix start date parameter in spec |
| Documentation (updates or new entries) | 📝 | 📝 Fix Database connector changelog                    |
| It's a breaking change                 | 🚨 | 🚨🚨🐛 Source Kafka: fix a complex bug                  |

For more information about [breaking changes](README.md#breaking-changes-to-connectors). A maintainer will help and instruct about possible breaking changes.

Any refactors, cleanups, etc.. that are not visible improvements to the user should not have emojis.

If you're code change is doing more than one change type at once we strongly recommend to break into multiple pull requests. It helps us to review and merge your contribution.

## Descriptions

**Context**: Provide enough information \(or a link to enough information\) in the description so team members with no context can understand what the issue or PR is trying to accomplish. This usually means you should include two things:

1. Some background information motivating the problem
2. A description of the problem itself
3. Good places to start reading and file changes that can be skipped

   Some examples:

_insufficient context_: `Create an OpenAPI to JSON schema generator`. Unclear what the value or problem being solved here is.

_good context_:

```text
When creating or updating connectors, we spend a lot of time manually transcribing JSON Schema files based on OpenAPI docs. This is ncessary because OpenAPI and JSON schema are very similar but not perfectly compatible. This process is automatable. Therefore we should create a program which converts from OpenAPI to JSONSchema format.
```