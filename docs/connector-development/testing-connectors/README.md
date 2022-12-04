# Testing Connectors

## Running Integration tests

The GitHub `master` and branch builds will build the core Airbyte infrastructure \(scheduler, ui, etc\) as well as the images for all connectors. Integration tests \(tests that run a connector's image against an external resource\) can be run one of three ways.

### 1. Local iteration

First, you can run the image locally. Connectors should have instructions in the connector's README on how to create or pull credentials necessary for the test. Also, during local development, there is usually a `main` entrypoint for Java integrations or `main_dev.py` for Python integrations that let you run your connector without containerization, which is fastest for iteration.

### 2. Code Static Checkers

#### Python Code
Using the following tools:
1. flake8
2. black
3. isort
4. mypy

Airbyte CI/CD workflows use them during "test/publish" commands obligatorily. 
All their settings are aggregated into the single file `pyproject.toml` into Airbyte project root.
Locally all these tools can be launched by the following gradle command:
```
 ./gradlew --no-daemon  :airbyte-integrations:connectors:<connector_name>:airbytePythonFormat
```
For instance:
```
./gradlew --no-daemon  :airbyte-integrations:connectors:source-s3:airbytePythonFormat
./gradlew --no-daemon  :airbyte-integrations:connectors:source-salesforce:airbytePythonFormat
```
### 3. Requesting GitHub PR Integration Test Runs

:::caution

This option is not available to PRs from forks, so it is effectively limited to Airbyte employees.

:::

If you don't want to handle secrets, you're making a relatively minor change, or you want to ensure the connector's integration test will run remotely, you should request builds on GitHub. You can request an integration test run by creating a comment with a slash command.

Here are some example commands:

1. `/test connector=all` - Runs integration tests for all connectors in a single GitHub workflow. Some of our integration tests interact with rate-limited resources, so please use this judiciously.
2. `/test connector=source-sendgrid` - Runs integration tests for a single connector on the latest PR commit.
3. `/test connector=connectors/source-sendgrid` - Runs integration tests for a single connector on the latest PR commit.
4. `/test connector=source-sendgrid ref=master` - Runs integration tests for a single connector on a different branch.
5. `/test connector=source-sendgrid ref=d5c53102` - Runs integration tests for a single connector on a specific commit.

A command dispatcher GitHub workflow will launch on comment submission. This dispatcher will add an :eyes: reaction to the comment when it starts processing. If there is an error dispatching your request, an error will be appended to your comment. If it launches the test run successfully, a :rocket: reaction will appear on your comment.

Once the integration test workflow launches, it will append a link to the workflow at the end of the comment. A success or failure response will also be added upon workflow completion.

Integration tests can also be manually requested by clicking "[Run workflow](https://github.com/airbytehq/airbyte/actions?query=workflow%3Aintegration-test)" and specifying the connector and GitHub ref.

### 4. Requesting GitHub PR publishing Docker Images

In order for users to reference the new versions of a connector, it needs to be published and available in the [dockerhub](https://hub.docker.com/r/airbyte/source-sendgrid/tags?page=1&ordering=last_updated) with the latest tag updated.

As seen previously, GitHub workflow can be triggered by comment submission. Publishing docker images to the dockerhub repository can also be submitted likewise:

Note that integration tests can be triggered with a slightly different syntax for arguments. This second set is required to distinguish between `connectors` and `bases` folders. Thus, it is also easier to switch between the `/test` and `/publish` commands:

* `/test connector=connectors/source-sendgrid` - Runs integration tests for a single connector on the latest PR commit.
* `/publish connector=connectors/source-sendgrid` - Publish the docker image if it doesn't exist for a single connector on the latest PR commit.

### 5. Automatically Run From `master`

Commits to `master` attempt to launch integration tests. Two workflows launch for each commit: one is a launcher for integration tests, the other is the core build \(the same as the default for PR and branch builds\).

Since some of our connectors use rate-limited external resources, we don't want to overload from multiple commits to master. If a certain threshold of `master` integration tests are running, the integration test launcher passes but does not launch any tests. This can manually be re-run if necessary. The `master` build also runs every few hours automatically, and will launch the integration tests at that time.

