# Testing Connectors

The GitHub `master` and branch builds will build the core Airbyte infrastructure (scheduler, ui, etc) as well as the images for all connectors. Integration tests (tests that run a connector's image against an external resource) can be run one of three ways.

## 1. Local iteration

First, you can run the image locally. Connectors should have instructions in the connector's README on how to create or pull credentials necessary for the test. Also, during local development, there is usually a `main` entrypoint for Java integrations or `main_dev.py` for Python integrations that let you run your connector without containerization, which is fastest for iteration.

## 2. Requesting GitHub PR Integration Test Runs

If you don't want to handle secrets, you're making a relatively minor change, or you want to ensure the connector's integration test will run remotely, you should request builds on GitHub. You can request an integration test run by creating a comment with a slash command.

Here are some example commands:
1. `/test connector=all` - Runs integration tests for all connectors in a single GitHub workflow. Some of our integration tests interact with rate-limited resources, so please use this judiciously. 
2. `/test connector=source-sendgrid` - Runs integration tests for a single connector on the latest PR commit. 
3. `/test connector=source-sendgrid ref=master` - Runs integration tests for a single connector on a different branch.
4. `/test connector=source-sendgrid ref=d5c53102` - Runs integration tests for a single connector on a specific commit.

A command dispatcher GitHub workflow will launch on comment submission. This dispatcher will add an :eyes: reaction to the comment when it starts processing. If there is an error dispatching your request, an error will be appended to your comment. If it launches the test run successfully, a :rocket: reaction will appear on your comment.

Once the integration test workflow launches, it will append a link to the workflow at the end of the comment. A success or failure response will also be added upon workflow completion.

Integration tests can also be manually requested from https://github.com/airbytehq/airbyte/actions?query=workflow%3Aintegration-test by clicking "Run workflow" and specifying the connector and GitHub ref.

This option is not available to PRs from forks, so it is effectively limited to Airbyte employees. 

## 3. Automatically Run From `master`

Commits to `master` attempt to launch integration tests. Two workflows launch for each commit: one is a launcher for integration tests, the other is the core build (the same as the default for PR and branch builds).

Since some of our connectors use rate-limited external resources, we don't want to overload from multiple commits to master. If a certain threshold of `master` integration tests are running, the integration test launcher passes but does not launch any tests. This can manually be re-run if necessary. The `master` build also runs every few hours automatically, and will launch the integration tests at that time.

### Connector Health

The build status displayed on for https://github.com/airbytehq/airbyte/commits/master reflects the status of the core build but not integrations. For Airbyte employees to view the connector health, set up secrets and run `./tools/bin/build_status.py`, which will display the past runs for each integration. In modern terminals, you can `Cmd`+click on a status icon to open the workflow for debugging purposes.
