# Changes to CDK or Low-Code Connector

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