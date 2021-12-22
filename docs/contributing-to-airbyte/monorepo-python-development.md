# Monorepo Python Development

This guide contains instructions on how to setup Python with Gradle within the Airbyte Monorepo. If you are a contributor working on one or two connectors, this page is most likely not relevant to you. Instead, you should use your standard Python development flow.

## Python Connector Development

Before working with connectors written in Python, we recommend running

```bash
./gradlew :airbyte-integrations:connectors:<connector directory name>:build
```

e.g

```bash
./gradlew :airbyte-integrations:connectors:source-postgres:build
```

from the root project directory. This will create a `virtualenv` and install dependencies for the connector you want to work on as well as any internal Airbyte python packages it depends on.

When iterating on a single connector, you will often iterate by running

```text
./gradlew :airbyte-integrations:connectors:your-connector-dir:build
```

This command will:

1. Install a virtual environment at `airbyte-integrations/connectors/your-connector-dir/.venv`
2. Install local development dependencies specified in `airbyte-integrations/connectors/your-connector-dir/requirements.txt`
3. Runs the following pip modules:
   1. [Black](https://pypi.org/project/black/) to lint the code
   2. [isort](https://pypi.org/project/isort/) to sort imports
   3. [Flake8](https://pypi.org/project/flake8/) to check formatting
   4. [MyPy](https://pypi.org/project/mypy/) to check type usage

## Formatting/linting

To format and lint your code before commit you can use the Gradle command above, but for convenience we support [pre-commit](https://pre-commit.com/) tool. To use it you need to install it first:

```bash
pip install pre-commit
```

then, to install `pre-commit` as a git hook, run

```text
pre-commit install
```

That's it, `pre-commit` will format/lint the code every time you commit something. You find more information about pre-commit [here](https://pre-commit.com/).

## IDE

At Airbyte, we use IntelliJ IDEA for development. Although it is possible to develop connectors with any IDE, we typically recommend IntelliJ IDEA or PyCharm, since we actively work towards compatibility.

### Autocompletion

Install the [Pydantic](https://plugins.jetbrains.com/plugin/12861-pydantic) plugin. This will help autocompletion with some of our internal types.

### PyCharm \(ItelliJ IDEA\)

The following setup steps are written for PyCharm but should have similar equivalents for IntelliJ IDEA:

1. Go to `File -> New -> Project...`
2. Select `Pure Python`.
3. Select a project name like `airbyte` and a directory **outside of** the `airbyte` code root.
4. Go to `Prefferences -> Project -> Python Interpreter`
5. Find a gear ⚙️ button next to `Python interpreter` dropdown list, click and select `Add`
6. Select `Virtual Environment -> Existing`
7. Set the interpreter path to the one that was created by Gradle command, i.e. `airbyte-integrations/connectors/your-connector-dir/.venv/bin/python`.
8. Wait for PyCharm to finish indexing and loading skeletons from selected virtual environment.

You should now have access to code completion and proper syntax highlighting for python projects.

If you need to work on another connector you can quickly change the current virtual environment in the bottom toolbar.

