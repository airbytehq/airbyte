# Pull request handbook

This topic explains how to title and describe your pull requests, and how to handle connector versioning.

## Pull request title conventions

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

In pull request descriptions, provide enough information (or a link to enough information) that team members with no context can understand what the PR is trying to accomplish. This means you should include three things:

1. Some background information motivating you to solve this problem

2. A description of the problem itself

3. Good places to start reading and file changes that reviewers can skip

### Insufficient context example

This description isn't clear about what problem you're solving or what value there is in this work.

```
Create an OpenAPI to JSON schema generator.
```

### Sufficient context example

This description equips reviewers to understand and make assessments about the decisions you've made in your PR.

```text
When creating or updating connectors, we spend a lot of time manually transcribing JSON Schema files based on OpenAPI docs. This is necessary because OpenAPI and JSON schema are very similar but not perfectly compatible. This process is automatable. Therefore we should create a program which converts from OpenAPI to JSONSchema format.
```

## Semantic versioning for connectors

Changes to connector behavior require a version bump and a changelog entry. Airbyte uses [semantic versioning](https://semver.org/). Since connectors are a bit different from APIs, Airbyte has its own take on semantic versioning, focusing on maintaining the best user experience of using a connector.

- **Major**: a version that requires manual intervention to update configurations to prevent an existing connection from failing, or one in which data the connector previously synced is no longer synced. This includes a schema change or different namespace in the final destination, because users must update downstream reports and tools.

- **Minor**: a version that introduces new user-facing capabilities in a backwards-compatible manner.

- **Patch**: a version that introduces backwards-compatible bug fixes or performance improvements.

### Examples

Here are some examples of code changes and their respective version changes.

If your situation isn't covered by any of these examples, note this in your pull request description. Your reviewing can help you pick the correct type of version change.

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
