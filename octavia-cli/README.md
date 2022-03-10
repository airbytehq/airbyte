# 🐙 Octavia CLI

Octavia CLI is a tool to manage Airbyte configuration in YAML.
It has the following features:
* Scaffolding of a readable directory architecture that will host the YAML configs.
* Auto-generation of YAML config file that matches the resources' schemas.
* Manage Airbyte resources with YAML config files.
* Safe resources update through diff display and validation.
* Simple secret management to avoid versioning credentials.

The project is under development: readers can refer to our [tech spec deck](https://docs.google.com/presentation/d/10RjkCzBiVhCivnjSh63icYI7wG6S0N0ZIErEIsmXTqM/edit?usp=sharing) for an introduction to the tool.

# Install

## 1. Install and run Docker
We are packaging this CLI as a Docker image to avoid dependency hell, **[please install and run Docker if you are not](https://docs.docker.com/get-docker/)**. 

## 2.a If you are using ZSH / Bash:
```bash
curl -o- https://raw.githubusercontent.com/airbytehq/airbyte/master/octavia-cli/install.sh | bash
```

This script:
1. Pulls the [octavia-cli image](https://hub.docker.com/r/airbyte/octavia-cli/tags) from our Docker registry.
2. Creates an `octavia` alias in your profile.

## 2.b If you want to directly run the CLI without alias in your current directory:
```bash
docker run --rm -v ${PWD}:/home/octavia-project --network host -e AIRBYTE_URL="${AIRBYTE_URL}" -e AIRBYTE_WORKSPACE_ID="${AIRBYTE_WORKSPACE_ID}" airbyte/octavia-cli:dev
````

# Current development status
Octavia is currently under development. 
You can find a detailed and updated execution plan [here](https://docs.google.com/spreadsheets/d/1weB9nf0Zx3IR_QvpkxtjBAzyfGb7B0PWpsVt6iMB5Us/edit#gid=0).
We welcome community contributions!

# Secret management
Sources and destinations configurations have credential fields that you **do not want to store as plain text and version on Git**.
`octavia` offers secret management through environment variables expansion:
```yaml
configuration:
  password: ${MY_PASSWORD}
```
If you have set a  `MY_PASSWORD` environment variable, `octavia apply` will load its value into the `password` field. 

**Summary of achievements**:

| Date       | Milestone                           |
|------------|-------------------------------------|
| 2022-03-09 | Implement secret management through environment variable expansion |
| 2022-03-09 | Implement `octavia generate connection`|
| 2022-03-09 | Implement `octavia apply` for connections|
| 2022-03-02 | Implement `octavia apply` (sources and destination only)|
| 2022-02-06 | Implement `octavia generate` (sources and destination only)|
| 2022-01-25 | Implement `octavia init` + some context checks|
| 2022-01-19 | Implement `octavia list workspace sources`, `octavia list workspace destinations`, `octavia list workspace connections`|
| 2022-01-17 | Implement `octavia list connectors source` and `octavia list connectors destinations`|
| 2022-01-17 | Generate an API Python client from our Open API spec |
| 2021-12-22 | Bootstrapping the project's code base |

# Developing locally
1. Install Python 3.8.12. We suggest doing it through `pyenv`
2. Create a virtualenv: `python -m venv .venv`
3. Activate the virtualenv: `source .venv/bin/activate`
4. Install dev dependencies: `pip install -e .\[tests\]`
5. Install `pre-commit` hooks: `pre-commit install`
6. Run the unittest suite: `pytest --cov=octavia_cli`
7. Iterate: please check the [Contributing](#contributing) for instructions on contributing.

## Build
Build the project locally (from the root of the repo):
```bash
SUB_BUILD=OCTAVIA_CLI ./gradlew build # from the root directory of the repo
```
# Contributing
1. Please sign up to [Airbyte's Slack workspace](https://slack.airbyte.io/) and join the `#octavia-cli`. We'll sync up community efforts in this channel.
2. Read the [execution plan](https://docs.google.com/spreadsheets/d/1weB9nf0Zx3IR_QvpkxtjBAzyfGb7B0PWpsVt6iMB5Us/edit#gid=0) and find a task you'd like to work on.
3. Open a PR, make sure to test your code thoroughly. 