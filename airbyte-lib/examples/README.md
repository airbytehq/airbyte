# Examples Readme

## Demo Workbook

To test this workbook, first clone the repo or open with GitHub Codespaces.

Note: You can execute the workbook within VS Code (including Codespaces), or you can spin up a Jupyter Server if you prefer. In the future, we may provide instructions to open this within Google Colab.

Create the airbyte-lib virtualenv.

```console
cd airbyte-lib
poetry install
```

Create the virtualenv for the airbyte-lib examples.

```console
cd airbyte-lib/examples
poetry install
```

The examples virtualenv can be used by the demo notebook.

### Resetting the demo

To reset the environment, delete directories like `airbyte-lib/examples/.venv*`, rerun `poetry install` and then restart the notebook kernel.
