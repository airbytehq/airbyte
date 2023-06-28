### Steps to contributing code

#### 1. Open an issue, or find a similar one.
Before jumping into the code please first:
1. Verify if an existing [connector](https://github.com/airbytehq/airbyte/issues) or [platform](https://github.com/airbytehq/airbyte-platform/issues) GitHub issue matches your contribution project.
2. If you don't find an existing issue, create a new [connector](https://github.com/airbytehq/airbyte/issues/new/choose) or [platform](https://github.com/airbytehq/airbyte-platform/issues/new/choose) issue to explain what you want to achieve.
3. Assign the issue to yourself and add a comment to tell that you want to work on this.

This will enable our team to make sure your contribution does not overlap with existing works and will comply with the design orientation we are currently heading the product toward.
If you do not receive an update on the issue from our team, please ping us on [Slack](https://slack.airbyte.io)!

#### 2. Code your contribution
1. To contribute to a connector, fork the [Connector repository](https://github.com/airbytehq/airbyte). To contribute to the Airbyte platform, fork our [Platform repository](https://github.com/airbytehq/airbyte-platform).
2. If contributing a new connector, check out our [new connectors guide](#new-connectors).
3. Open a branch for your work.
4. Code, and please write **tests**.
5. Ensure all tests pass. For connectors, this includes acceptance tests as well.
6. For connectors, make sure to increment the connector's version according to our [Semantic Versioning](#semantic-versioning-for-connectors) guidelines.

#### 3. Open a pull request
1. Rebase master with your branch before submitting a pull request.
2. Open the pull request.
3. Wait for a review from a community maintainer or our team.

#### 4. Review process
When we review, we look at:
* ‌Does the PR solve the issue?
* Is the proposed solution reasonable?
* Is it tested? \(unit tests or integration tests\)
* Is it introducing security risks?
‌Once your PR passes, we will merge it 🎉.


### Semantic versioning for connectors

Changes to connector behavior should always be accompanied by a version bump and a changelog entry. We use [semantic versioning](https://semver.org/) to version changes to connectors. Since connectors are a bit different from APIs, we have our own take on semantic versioning, focusing on maintaining the best user experience of using a connector.

- Major: a version in which a change is made which requires manual intervention (update to config or configured catalog) for an existing connection to continue to succeed, or one in which data that was previously being synced will no longer be synced
- Minor: a version that introduces user-facing functionality in a backwards compatible manner
- Patch: a version that introduces backwards compatible bug fixes or performance improvements

#### Examples

Here are some examples of code changes and their respective version changes:

| Change                                                                                        | Impact                                                                                                           | Version Change |
|-----------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|----------------|
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


### New connectors

It's easy to add your own connector to Airbyte! **Since Airbyte connectors are encapsulated within Docker containers, you can use any language you like.** Here are some links on how to add sources and destinations. We haven't built the documentation for all languages yet, so don't hesitate to reach out to us if you'd like help developing connectors in other languages.

For sources, simply head over to our [Python CDK](../connector-development/cdk-python/).

:::info
The CDK currently does not support creating destinations, but it will very soon.
:::

* See [Building new connectors](../connector-development/) to get started.
* Since we frequently build connectors in Python, on top of Singer or in Java, we've created generator libraries to get you started quickly: [Build Python Source Connectors](../connector-development/tutorials/building-a-python-source.md) and [Build Java Destination Connectors](../connector-development/tutorials/building-a-java-destination.md)
* Integration tests \(tests that run a connector's image against an external resource\) can be run one of three ways, as detailed [here](../connector-development/testing-connectors/connector-acceptance-tests-reference.md)

**Please note that, at no point in time, we will ask you to maintain your connector.** The goal is that the Airbyte team and the community helps maintain the connector.


## Breaking Changes to Connectors

Often times, changes to connectors can be made without impacting the user experience.  However, there are some changes that will require users to take action before they can continue to sync data.  These changes are considered **Breaking Changes** and require a

1. A **Major Version** increase 
2. An Airbyte Engineer to follow the  [Connector Breaking Change Release Playbook](https://docs.google.com/document/u/0/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit) before merging.


### Types of Breaking Change(s):
A breaking change is any change that will require users to take action before they can continue to sync data. The following are examples of breaking changes:

- **Spec Change** - The configuration required by users of this connector have been changed and syncs will fail until users reconfigure or re-authenticate.  This change is not possible via a Config Migration 
- **Schema Change** - The type of a property previously present within a record has changed
- **Stream or Property Removal** - Data that was previously being synced is no longer going to be synced.
- **Destination Format / Normalization Change** - The way the destination writes the final data or how normalization cleans that data is changing in a way that requires a full-refresh.**
- **State Changes** - The format of the source’s state has changed, and the full dataset will need to be re-synced


### Checklist for Contributors

First, ask yourself does your change correspond to any of the breaking changes above?

If so then follow this checklist below

- [ ] Apply the label breaking-change to your PR
- [ ] Apply a Major Version bump to your PR. See [Semantic Versioning for Connectors](#semantic-versioning-for-connectors) for more information.
- [ ] Prepend your PR title with the 🚨🚨 emoji.
- [ ] Add a section to the PR description titled Breaking Change that describes why this is a breaking change, and if possible how you can migrate users and/or rollback
- [ ] Assign an Airbyte Engineer through the `airbytehq/connector-operations` group and have them start the [Connector Breaking Change Playbook](https://docs.google.com/document/d/1VYQggHbL_PN0dDDu7rCyzBLGRtX-R3cpwXaY8QxEgzw/edit#)
