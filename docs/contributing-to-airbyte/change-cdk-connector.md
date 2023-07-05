# Changes to CDK or Low-Code Connector

#### Open an issue, or find a similar one.
Before jumping into the code please first:
1. Verify if an existing [connector](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Aarea%2Fconnectors+-label%3Aneeds-triage+label%3Acommunity) 
2. If you don't find an existing issue...
   1. [Report a Bug Connector](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fbug%2Carea%2Fconnectors%2Cneeds-triage&projects=&template=1-issue-connector.yaml)
   2. [Request a New Connector Feature](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=type%2Fenhancement%2Cneeds-triage&projects=&template=6-feature-request.yaml)

This will enable our team to make sure your contribution does not overlap with existing works and will comply with the design orientation we are currently heading the product toward. If you do not receive an update on the issue from our team, please ping us on [Slack](https://slack.airbyte.io)!

:::info
Make sure you're working on an issue had been already triaged to not have your contribution declined.
:::

#### Code your contribution
1. To contribute to a connector, fork the [Connector repository](https://github.com/airbytehq/airbyte). 
2. Open a branch for your work
3. Code the change
4. To each custom function you added or changed its a must to write unit **tests**.
5. Ensure all tests pass. For connectors, this includes acceptance tests as well.
6. Update the `metadata.yaml`, `Dockerfile` version following the [guidelines](./resources/pull-requests-handbook.md#semantic-versioning-for-connectors)
7. Update the changelog entry in documentation in `docs/integrations/<connector-name>.md` 

:::info
There is a README file inside each connector folder with instructions to run test locally
:::

:::warning
Pay attention to breaking changes to connectors. You can read more [here](#breaking-changes-to-connectors).
:::


#### Open a pull request
1. Rebase master with your branch before submitting a pull request.
2. Open the pull request.
3. Follow the [title convention](./resources/pull-requests-handbook.md#pull-request-title-convention) for Pull Requests
4. Link to an existing Issue
5. Update the [description](./resources/pull-requests-handbook.md#descriptions)
6. Wait for a review from a community maintainer or our team.

#### 4. Review process
When we review, we look at:
* ‌Does the PR solve the issue?
* Is the proposed solution reasonable?
* Is it tested? \(unit tests or integation tests\)
* Is it introducing security risks?
* Is it introducing a breaking change?
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