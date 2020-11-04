## Creating a new Integration

First, make sure you built the project by running `./gradlew build` from the project root directory. 

Then, from the `airbyte-integrations/connector-templates/generator` directory, run: 
```
npm run generate
```
and follow the interactive prompt. This will generate a new integration in the `airbyte-integrations/connectors/<your-integration>` directory. 
Follow the instructions generated in the checklist md file for bootstrapping the integration. The generated
README.md will also contain instructions on how to iterate. 

## Updating an integration's default version in Airbyte
Once you've finished iterating on the changes to a connector as specified in its `README.md`, follow these instructions
to tell Airbyte to use the latest version of your integration.   

1. Bump the version in the `Dockerfile` of the integration (`LABEL io.airbyte.version=X.X.X`)
1. Build the integration with the semantic version tag locally:
    ```
    ./tools/integrations/manage.sh build airbyte-integrations/connectors/<connector-name>
    ```
1. Publish the new version to Docker Hub. 
    ```
    ./tools/integrations/manage.sh publish airbyte-integrations/connectors/<connector-name>
    ```
1. Update the connector version inside the `STANDARD_SOURCE_DEFINITION` (or `STANDARD_DESTINATION_DEFINITION` directory) to the one you just published. 
This will update Airbyte to use this new version by default. 
1. Merge the PR containing the changes you made.

## Python Connector Development

Before working with integrations written in Python, we recommend running `./gradlew build` from the root project directory.
This will create a virtualenv for every integration and helper project and install dependencies locally. 

When iterating on a single connector, you will often iterate by running `./gradlew :airbyte-integrations:connectors:your-connector-dir:build`.
This command will:
1. Install a virtual environment at `airbyte-integrations/connectors/your-connector-dir/.venv`
1. Install local development dependencies specified in `airbyte-integrations/connectors/your-connector-dir/requirements.txt`
1. Runs the following pip modules:
    1. [Black](https://pypi.org/project/black/) to format the code
    1. [isort](https://pypi.org/project/isort/) to sort imports
    1. [Flake8](https://pypi.org/project/flake8/) to check formatting
    1. [MyPy](https://pypi.org/project/mypy/) to check type usage

At Airbyte, we use IntelliJ IDEA for development. Although it is possible to develop integrations with any IDE, 
we typically recommend IntelliJ IDEA or PyCharm, since we actively work towards compatibility. Our typical development flow is to have one Intellij project for Java development with Gradle and a separate Intellij project for Python.
The following setup steps are written for IntelliJ IDEA but should have similar equivalents for PyCharm:
1. Install the [Pydantic](https://plugins.jetbrains.com/plugin/12861-pydantic) plugin. This will help autocompletion with some of our internal types.
1. We recommend using one project for Java development with Gradle and a separate project for Python.
1. To create the Python project, go to `File -> New -> Project...`
1. Select Python.
1. Select a project name like `airbyte-python` and a directory *outside of the `airbyte` code root*.
1. Usually you will want to create this project in a new window and not replace the existing window.
1. Go to `Project Structure > Modules`. 
1. Click the + sign and `New Module`.
1. Set the content root and module file location to the location of your `airbyte-integrations` directory or a specific subdirectory.
1. Finish adding the module.

You should now have access to code completion and proper syntax highlighting for Python projects. 
You can use your default Python SDK, but if you want your dependency management to match what will be used in the build process, 
we recommend creating a Python SDK under `Project Structure > SDKs > + > Virtual Environment > Existing Environment` 
and setting the interpreter to the python script specified in a location such as `airbyte-integrations/connectors/source-exchangeratesapi-singer/.venv/bin/python`. 
Then, you can set the module interpreter to this venv-based interpreter to make sure imports are working as intended.
