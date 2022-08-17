# Issues & Pull Requests

## Titles

**Describe outputs, not implementation**: An issue or PR title should describe the desired end result, not the implementation. The exception is child issues/subissues of an epic. **Be specific about the domain**. Airbyte operates a monorepo, so being specific about what is being changed in the PR or issue title is important.

Some examples: _subpar issue title_: `Remove airbyteCdk.dependsOn("unrelatedPackage")`. This describes a solution not a problem.

_good issue title_: `Building the Airbyte Python CDK should not build unrelated packages`. Describes desired end state and the intent is understandable without reading the full issue.

_subpar PR title_: `Update tests`. Which tests? What was the update?

_good PR title_: `Source MySQL: update acceptance tests to connect to SSL-enabled database`. Specific about the domain and change that was made.

**PR title conventions** When creating a PR, follow the naming conventions depending on the change being made:

* Notable updates to Airbyte Core: "🎉"
  * e.g: `🎉 enable configuring un-nesting in normalization`
* New connectors: “🎉 New source or destination: ” e.g: `🎉 New Source: Okta`
* New connector features: “🎉 :  E.g:
  * `🎉 Destination Redshift: write JSONs as SUPER type instead of VARCHAR`
  * `🎉 Source MySQL: enable logical replication`
* Bugfixes should start with the  🐛 emoji
  * `🐛 Source Facebook Marketing: fix incorrect parsing of lookback window`
* Documentation improvements should start with any of the book/paper emojis: 📚 📝 etc…
* Any refactors, cleanups, etc.. that are not visible improvements to the user should not have emojis

The emojis help us identify which commits should be included in the product release notes.

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