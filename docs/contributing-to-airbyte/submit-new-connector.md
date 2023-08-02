# Submit a New Connector

:::info
Due to project priorities, we may not be able to accept all contributions at this time. 

:::

#### Find an Issue or Create it!
Before jumping into the code please first:
1. Verify if there is an existing [Issue](https://github.com/airbytehq/airbyte/issues?q=is%3Aopen+is%3Aissue+label%3Aarea%2Fconnectors+-label%3Aneeds-triage+label%3Acommunity) 
2. If you don't find an existing issue, [Request a New Connector](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=area%2Fconnectors%2Cnew-connector&projects=&template=5-feature-new-connector.yaml)

This will enable our team to make sure your contribution does not overlap with existing works and will comply with the design orientation we are currently heading the product toward. If you do not receive an update on the issue from our team, please ping us on [Slack](https://slack.airbyte.io)!


#### Code your contribution
1. To contribute to a connector, fork the [Connector repository](https://github.com/airbytehq/airbyte). 
2. Open a branch for your work
3. Code the change
4. Ensure all tests pass. For connectors, this includes acceptance tests as well.
5. Update documentation in `docs/integrations/<connector-name>.md` 


#### Open a pull request
1. Rebase master with your branch before submitting a pull request.
2. Open the pull request.
3. Follow the [title convention](./resources/pull-requests-handbook.md#pull-request-title-convention) for Pull Requests
4. Link to an existing Issue
5. Update the [description](./resources/pull-requests-handbook.md#descriptions)
6. Wait for a review from a community maintainer or our team.

#### 4. Review process
When we review, we look at:
* ‌Does the PR add all existing streams, pagination and incremental syncs?
* Is the proposed solution reasonable?
* Is it tested? \(unit tests or integation tests\)
‌Once your PR passes, we will merge it 🎉.

