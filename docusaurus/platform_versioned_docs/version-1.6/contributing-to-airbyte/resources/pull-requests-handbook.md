# Pull Request Handbook

### Pull Request Title Convention

Pull request titles must follow [Conventional Commits](https://www.conventionalcommits.org/) format. CI enforces this automatically, and Airbyte uses these titles to generate release notes and changelogs.

The format is:

```text
type(optional-scope): description
```

For breaking changes, add `!` after the type or scope:

```text
type!: description
type(scope)!: description
```

The following table lists the valid types and examples of each:

| Type       | Description                                      | Example                                                  |
| ---------- | ------------------------------------------------ | -------------------------------------------------------- |
| `feat`     | Add a new feature or connector                   | `feat(source-postgres): add new stream Users`            |
| `fix`      | Fix a bug                                        | `fix(source-shopify): fix start date parameter in spec`  |
| `docs`     | Documentation changes                            | `docs: update connector setup guide`                     |
| `refactor` | Code restructuring without behavior changes      | `refactor(destination-bigquery): simplify error handler` |
| `perf`     | Performance improvements                         | `perf(source-mysql): optimize large table reads`         |
| `test`     | Add or update tests                              | `test(source-github): add unit tests for rate limiting`  |
| `ci`       | CI/CD workflow changes                           | `ci: update workflow-actions pinned SHA`                 |
| `build`    | Build system or external dependency changes      | `build: upgrade CDK to v6`                               |
| `chore`    | Maintenance tasks                                | `chore(source-github): update dependencies`              |
| `deps`     | Dependency updates                               | `deps: bump airbyte-cdk version`                         |
| `style`    | Code style changes without logic changes         | `style: fix formatting in manifest`                      |
| `revert`   | Revert a previous commit                         | `revert: undo stream removal`                            |
| `release`  | Release-related changes                          | `release(source-stripe): promote 5.15.18`                |

The scope is optional but recommended for connector changes. Use the connector's name as the scope, for example `source-postgres` or `destination-bigquery`.

For [more information about breaking changes](#semantic-versioning-for-connectors), contact a maintainer who can help identify possible breaking changes.

If your code change involves more than one change type, break it into multiple pull requests. This helps maintainers review and merge your contribution.

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

## Semantic Versioning for Connectors

Changes to connector behavior should always be accompanied by a version bump and a changelog entry. We use [semantic versioning](https://semver.org/) to version changes to connectors. Since connectors are a bit different from APIs, we have our own take on semantic versioning, focusing on maintaining the best user experience of using a connector.

- Major: a version in which a change is made which requires manual intervention (update to config or configured catalog) for an existing connection to continue to succeed, or one in which data that was previously being synced will no longer be synced
  - Note that a category of "user intervention" is a schema change in the destination, as users will be required to update downstream reports and tools. A change that leads to a different final table in the destination is a breaking change
- Minor: a version that introduces user-facing functionality in a backwards compatible manner
- Patch: a version that introduces backwards compatible bug fixes or performance improvements

### Examples

Here are some examples of code changes and their respective version changes:

| Change                                                                                        | Impact                                                                                                           | Version Change |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------- |
| Adding a required parameter to a connector's `spec`                                           | Users will have to add the new parameter to their `config`                                                       | Major          |
| Changing a format of a parameter in a connector's `spec` from a single parameter to a `oneOf` | Users will have to edit their `config` to define their old parameter value in the `oneOf` format                 | Major          |
| Removing a stream from a connector's `catalog`                                                | Data that was being synced will no longer be synced                                                              | Major          |
| Renaming a stream in a connector's `catalog`                                                  | Users will have to update the name of the stream in their `catalog`                                              | Major          |
| Removing a column from a stream in a connector's `catalog`                                    | Users will have to remove that column from their `catalog`, data that was being synced will no longer be synced  | Major          |
| Renaming a column from a stream in a connector's `catalog`                                    | Users will have to update the name of the column in their `catalog`                                              | Major          |
| Changing the datatype for a column of a stream in a connector's `catalog`                     | Users will have to update that data type in their `catalog`, data that was being synced will have changed format | Major          |
| Adding a non-required parameter to a connector's `spec`                                       | Users will have the option to use the required parameter in the future                                           | Minor          |
| Adding a stream in a connector's `catalog`                                                    | Additional data will be synced                                                                                   | Minor          |
| Adding a column to a stream's schema in a connector's `catalog`                               | Additional data will be synced                                                                                   | Minor          |
| Updating the format of the connector's `STATE`                                                | Incremental streams will automatically run a full refresh only for the next sync                                 | Patch          |
| Optimizing a connector's performance                                                          | Syncs will be faster                                                                                             | Patch          |
| Fixing a bug in a connector                                                                   | Some syncs that would have failed will now succeed                                                               | Patch          |

Trying to contribute, and don't see the change you want to make in this list? Call it out in your PR and your reviewer will help you pick the correct type of version change. Feel free to contribute the results back to this list!
