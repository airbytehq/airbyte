# Monorepo Python Development

This guide contains instructions on how to setup Python with Gradle within the Airbyte Monorepo. If you are a contributor working on one or two connectors, 
this page is most likely not relevant to you. Instead, you should use your standard Python development flow.    

## Python Connector Development

Before working with connectors written in Python, we recommend running `./gradlew build` from the root project directory. This will create a `virtualenv` for every connector and helper project and install dependencies locally.

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

At Airbyte, we use IntelliJ IDEA for development. Although it is possible to develop connectors with any IDE, we typically recommend IntelliJ IDEA or PyCharm, since we actively work towards compatibility.

## Working on a Single Connector

When iterating on a single connector, the easiest approach is to open PyCharm with the desired connector directory.

You should then open the `Preferences > Project: <your connector> > Python Interpreter` to configure the Project Interpreter using the one that was installed with the requirements of the connector by the `gradle` command: `airbyte-integrations/connectors/your-connector-dir/.venv/bin/python`

## Multi Modules Setup

Our typical development flow is to have one Intellij project for `java` development with `gradle` and a separate Intellij project for python. The following setup steps are written for IntelliJ IDEA but should have similar equivalents for PyCharm:

1. Install the [Pydantic](https://plugins.jetbrains.com/plugin/12861-pydantic) plugin. This will help autocompletion with some of our internal types.
2. To create the python project, go to `File -> New -> Project...`
3. Select python.
4. Select a project name like `airbyte-python` and a directory **outside of** the `airbyte` code root.
5. Usually you will want to create this project in a new window and not replace the existing window.
6. Go to `Project Structure > Modules`.
7. Click the + sign and `New Module`.
8. Set the content root and module file location to the location of your `airbyte-integrations` directory or a specific subdirectory.
9. Finish adding the module.

You should now have access to code completion and proper syntax highlighting for python projects.

You can use your default python SDK, but if you want your dependency management to match what will be used in the build process, we recommend creating a Python SDK under `Project Structure > SDKs > + > Virtual Environment > Existing Environment` and setting the interpreter to the python script specified in a location such as `airbyte-integrations/connectors/your-connector-dir/.venv/bin/python`. Once this is done, you can set the module interpreter to this `venv`-based interpreter to make sure imports are working as intended.

