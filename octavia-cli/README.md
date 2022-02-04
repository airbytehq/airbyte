# 🐙 Octavia CLI

Octavia CLI is a tool to manage Airbyte configuration in YAML.
It has the following features:
* Scaffolding of a readable directory architecture that will host the YAML configs.
* Auto-generation of YAML config file that matches the resources' schemas.
* Manage Airbyte resources with YAML config files.
* Safe resources update through diff display and validation.
* Simple secret management to avoid versioning credentials.

The project is under development: readers can refer to our [tech spec deck](https://docs.google.com/presentation/d/10RjkCzBiVhCivnjSh63icYI7wG6S0N0ZIErEIsmXTqM/edit?usp=sharing) for an introduction to the tool.

# Usage
We encourage users to use the CLI with docker to avoid the hassle of setting up a Python installation. 
The project is under development: we have not yet published any docker image to our Docker registry.

1. Build the project locally (from the root of the repo):
```bash
SUB_BUILD=OCTAVIA_CLI ./gradlew build #from the root of the repo
```
2. Run the CLI from docker:
```bash
docker run airbyte/octavia-cli:dev 
````
3. Create an `octavia` alias in your `.bashrc` or `.zshrc`: 
````bash
echo 'alias octavia="docker run airbyte/octavia-cli:dev"'  >> ~/.zshrc
source ~/.zshrc
octavia
````

# Current development status
Octavia is currently under development. 
You can find a detailed and updated execution plan [here](https://docs.google.com/spreadsheets/d/1weB9nf0Zx3IR_QvpkxtjBAzyfGb7B0PWpsVt6iMB5Us/edit#gid=0).
We welcome community contributions!

**Summary of achievements**:

| Date       | Milestone                           |
|------------|-------------------------------------|
| 2022-01-25 | Implement `octavia init` + some context checks|
| 2022-01-19 | Implement `octavia list workspace sources`, `octavia list workspace destinations`, `octavia list workspace connections`|
| 2022-01-17 | Implement `octavia list connectors source` and `octavia list connectors destinations`|
| 2022-01-17 | Generate an API Python client from our Open API spec |
| 2021-12-22 | Bootstrapping the project's code base |

# Developing locally
1. Install Python 3.8.12. We suggest doing it through `pyenv`
2. Create a virtualenv: `python -m venv .venv`
3. Activate the virtualenv: `source .venv/bin/activate`
4. Install dev dependencies: `pip install -e .\[dev\]`
5. Install `pre-commit` hooks: `pre-commit install`
6. Run the test suite: `pytest --cov=octavia_cli unit_tests`
7. Iterate: please check the [Contributing](#contributing) for instructions on contributing.

# Contributing
1. Please sign up to [Airbyte's Slack workspace](https://slack.airbyte.io/) and join the `#octavia-cli`. We'll sync up community efforts in this channel.
2. Read the [execution plan](https://docs.google.com/spreadsheets/d/1weB9nf0Zx3IR_QvpkxtjBAzyfGb7B0PWpsVt6iMB5Us/edit#gid=0) and find a task you'd like to work on.
3. Open a PR, make sure to test your code thoroughly. 