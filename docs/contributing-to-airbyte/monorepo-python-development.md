# Monorepo Python Development

This guide contains instructions on how to setup Python with Gradle within the Airbyte Monorepo. If you are a contributor working on one or two connectors, this page is most likely not relevant to you. Instead, you should use your standard Python development flow.

## Python Connector Development

Before working with connectors written in Python, we recommend running the following command from the airbyte root directory

```bash
python3 tools/bin/update_intellij_venv.py -modules <connector directory name> --install-venv
```

e.g

```bash
python tools/bin/update_intellij_venv.py -modules source-stripe --install-venv
```

If using Pycharm or IntelliJ, you'll also want to add the interpreter to the IDE's list of known interpreters. You can do this by adding the `--update-intellij` flag. More details can be found [here](#ide)

```bash
python tools/bin/update_intellij_venv.py -modules <connector directory name> --install-venv --update-intellij
```

If working with many connectors, you can use the `--all-modules` flag to install the virtual environments for all connectors

```bash
python tools/bin/update_intellij_venv.py --all-modules --install-venv
```

This will create a `virtualenv` and install dependencies for the connector you want to work on as well as any internal Airbyte python packages it depends on.

When iterating on a single connector, you will often iterate by running

```text
./gradlew :airbyte-integrations:connectors:your-connector-dir:build
```

This command will:

1. Install a virtual environment at `airbyte-integrations/connectors/<your-connector-dir>/.venv`
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

1.`python tools/bin/update_intellij_venv.py -modules <your-connector-dir> --update-intellij`

2. Restart PyCharm
3. Go to `File -> New -> Project...`
4. Select `Pure Python`.
5. Select a project name like `airbyte` and a directory **outside of** the `airbyte` code root.
6. Go to `Preferences -> Project -> Python Interpreter`
7. Find a gear ⚙️ button next to `Python interpreter` dropdown list, click and select `Add`
8. Select `Virtual Environment -> Existing`
9. Set the interpreter path to the one that was created by Python command, i.e. `airbyte-integrations/connectors/<your-connector-dir>/.venv/bin/python`.
10. Wait for PyCharm to finish indexing and loading skeletons from selected virtual environment.

You should now have access to code completion and proper syntax highlighting for python projects.

If you need to work on another connector you can quickly change the current virtual environment in the bottom toolbar.

## Intra Repo Python Dependencies

Sometimes, you may want to use other python module(s) within the Airbyte monorepo as dependencies for your connector. This can be achieved as follows:

1. To enable the dependency for local development, add a line referencing the dependency module in the requirements.txt of your connector, in the format:
   
    ```text
    -e {relative path to dependency}
    ```
   
    
In the case of the `source-file-secure` connector, it has the `source-file` connector as a dependency. Initially the requirements file looks like:

```text
-e ../../bases/source-acceptance-test
-e .
```

and after we add the dependency line:

```text
-e ../../bases/source-acceptance-test
-e ../source-file
-e .
```

When you `pip install -r requirements.txt`, a symlink to the dependency module will be added in your local venv’s site-packages. This is sufficient for local development, but we also need to add the dependency to the Dockerfile so that it's picked up during build.

2.  There are 3 lines (for each dependency) that we need to add in the Dockerfile:
    1. At the top of the file, before the other , we 