---
description: 'We love contributions to Airbyte, big or small.'
---

# Contributing to Airbyte

Thank you for your interest in contributing! We love community contributions. Contribution guidelines are listed below. If you're unsure about how to start contributing or have any questions even after reading them, feel free to ask us on [Slack](https://slack.airbyte.io) in the \#dev or \#general channel.

However, for those who want a bit more guidance on the best way to contribute to Airbyte, read on. This document will cover what we're looking for. By addressing the points below, the chances that we can quickly merge or address your contributions will increase.

## Code of conduct

Please follow our [Code of conduct](code-of-conduct.md) in the context of any contributions made to Airbyte.

## Airbyte specification

Before you can start contributing, you need to understand [Airbyte's data protocol specification](../understanding-airbyte/airbyte-protocol.md).

## First-time contributors, welcome!

We appreciate first time contributors and we are happy to assist you in getting started. In case of questions, just reach out to us via [email](mailto:hey@airbyte.io) or [Slack](https://slack.airbyte.io)!

Here is a list of easy [good first issues](https://github.com/airbytehq/airbyte/labels/good%20first%20issue) to do.

## Contributing to the codebase

We gladly welcome all improvements to the codebase.

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


### Airbyte CI workflows
* [Testing by SonarQube](sonar-qube-workflow.md)

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

## Contributing to documentation

Our goal is to keep our docs comprehensive and updated. If you would like to help us in doing so, we are grateful for any kind of contribution:

* Report missing content
* Fix errors in existing docs
* Help us in adding to the docs

The contributing guide for docs can be found [here](updating-documentation.md).

## Contributing community content

We welcome contributions as new tutorials / showcases / articles, or to any of the existing guides on our [tutorials page](https://airbyte.com/tutorials):

* Fix errors in existing tutorials
* Add new tutorials \(please reach out to us if you have ideas to avoid duplicate work\)
* Request tutorials

We have a repo dedicated to community content. Everything is documented [there](https://github.com/airbytehq/community-content/).

Feel free to submit a pull request in this repo, if you have something to add even if it's not related to anything mentioned above.

## Other ways to contribute

### Upvoting issues, feature and connector requests

You are welcome to add your own reactions to the existing issues. We will take them in consideration in our prioritization efforts, especially for connectors.

❤️ means that this task is CRITICAL to you.
👍 means it is important to you.

### Requesting new features

To request new features, please create an issue on this project.

If you would like to suggest a new feature, we ask that you please use our issue template. It contains a few essential questions that help us understand the problem you are looking to solve and how you think your recommendation will address it. We also tag incoming issues from this template with the "**community\_new**" label. This lets our teams quickly see what has been raised and better address the community recommendations.

To see what has already been proposed by the community, you can look [here](https://github.com/airbytehq/airbyte/labels/community).

Watch out for duplicates! If you are creating a new platform issue, please check [open](https://github.com/airbytehq/airbyte-platform/issues), or [recently closed](https://github.com/airbytehq/airbyte-platform/issues?utf8=%E2%9C%93&q=is%3Aissue%20is%3Aclosed%20).

### Requesting new connectors

This is very similar to requesting new features. The template will change a bit and all connector requests will be tagged with the “**community**” and “**area/connectors**” labels.

To see what has already been proposed by the community, you can look [here](https://github.com/airbytehq/airbyte/labels/area%2Fconnectors). Again, watch out for duplicates!

### Reporting bugs

**‌**Bug reports help us make Airbyte better for everyone. We provide a preconfigured template for bugs to make it very clear what information we need.

‌Please search within our [already reported bugs](https://github.com/airbytehq/airbyte/issues?q=is%3Aissue+is%3Aopen+label%3Atype%2Fbug) before raising a new one to make sure you're not raising a duplicate.

### Reporting security issues

Please do not create a public GitHub issue. If you've found a security issue, please email us directly at [security@airbyte.io](mailto:security@airbyte.io) instead of raising an issue.
