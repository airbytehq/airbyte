# Tooling for automated migration of `acceptance-test-config.yml` files

This directory contains scripts that can help us manage the migration of connectors' `acceptance-test-config.yml` files.

## Setup
Before running these scripts you need to set up a local virtual environment in the **current directory**:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install gh
```

Then create a module to contain the information for your migration/issues etc.: 
```
mkdir migrations/<migration_name>
touch migrations/<migraton_name>/__init__.py
touch migrations/<migration_name>/config.py
```

Copy a config.py file from another migration and fill in the `MODULE_NAME` variable. The other variables
can be filled in when you use certain scripts. 
```python
#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional, List

# SET THESE BEFORE USING THE SCRIPT
MODULE_NAME: str = "<migration_name>"
# GITHUB_PROJECT_NAME: Optional[str] = None
# COMMON_ISSUE_LABELS: List[str] = ["area/connectors", "team/connectors-python", "type/enhancement", "column-selection-sources"]
# ISSUE_TITLE: str = "Add undeclared columns to spec"
```

## Scripts

The scripts perform operations on a set of connectors. 

### `run_tests.py`: Run CAT tests and save results by exit code

#### What it does

The script will run CAT on all connectors and report the results to `migrations/<migration_name>/output` and classify the
results by exit code.

TODO: Replace this process with Dagger

#### Before running

The tests will run on the `latest` version of CAT by default. To run the `dev` version of CAT, and select a specific 
test, commit the following hacky changes: (TODO: fill with changes to `acceptance-test-docker.sh` and CAT `Dockerfile`)

Note: you will need to give Docker a _lot_ of space to build all the connector images!

#### How to run 

Typical usage: 
```
python run_tests.py --connectors <connectors> 
```

Full options: 
```
usage: run_tests.py [-h] --connectors [CONNECTORS ...] [--allow_alpha | --no-allow_alpha] [--max_concurrency MAX_CONCURRENCY]

Run connector acceptance tests for a list of connectors.

options:
  -h, --help            show this help message and exit
  --connectors [CONNECTORS ...]
                        A list of connectors (separated by spaces) to run a script on.
  --allow_alpha, --no-allow_alpha
                        Whether to apply the change to alpha connectors, if they are included in the list of connectors. (default: False)
  --max_concurrency MAX_CONCURRENCY
                        The maximum number of acceptance tests that should happen at once. (default: 10)
```

### `create_issues.py`: Create issues in bulk
This script will create one issue per connector according to a template you provide. 

#### What it does:
For each connector:
1. Generate an issue content (title, body, labels, project), using an `issue.md.j2` template
2. Find an already existing issue with the same title, if one already exists
3. Create the issue and return its url if it does not exist.

Issues get created with the labels defined by `COMMON_ISSUE_LABELS`.

Issues are added to the `GITHUB_PROJECT_NAME` project, if one is provided.

#### Before running

1. Update your config file to define the following variables:

    ```python
    #
    # Copyright (c) 2023 Airbyte, Inc., all rights reserved.
    #
    
    from typing import Optional, List
    
    # SET THESE BEFORE USING THE SCRIPT
    MODULE_NAME: str = "<migration_name>"
    GITHUB_PROJECT_NAME: Optional[str] = "<project_name>"
    COMMON_ISSUE_LABELS: List[str] = ["<label_1>", "<label_2>", "..."]
    ISSUE_TITLE: str = "<issue_title>"
    ```
    Note that `ISSUE_TITLE` will be prepended with `Source <source name>:` in the actual created issue.

2. Create a template for your issue:

    ```bash
    touch migrations/<migration_name>/issue.md.j2
    ```
    
    If you need to fill more variables than are currently defined in the call to `template.render()`
    in `create_issues.py`, edit the script to allow filling of that variable and define how it should be
    filled. Please keep in mind the other migrations when you do this.

3. Update the following line in the script so that it points to the config file from your migration: 

    ```python
    ## Update this line before running the script
    from migrations.<migration_name> import config
    ```

#### How to run:

Typical usage (dry run):
```
python create_issues.py --connectors <connectors>
```

Typical usage (real execution):
```
python create_issues.py --connectors <connectors> --no-dry
```

Full options: 
```
usage: create_issues.py [-h] [-d | --dry | --no-dry] --connectors [CONNECTORS ...] [--allow_alpha | --no-allow_alpha]

Create issues for a list of connectors from a template.

options:
  -h, --help            show this help message and exit
  -d, --dry, --no-dry   Whether the action performed is a dry run. In the case of a dry run, no git actions will be pushed to the remote. (default: True)
  --connectors [CONNECTORS ...]
                        A list of connectors (separated by spaces) to run a script on.
  --allow_alpha, --no-allow_alpha
                        Whether to apply the change to alpha connectors, if they are included in the list of connectors. (default: False)
```


### `config_migration.py`: Perform migrations on `acceptance-test-config.yml` files 



### `create_prs.py`: Create a PR per connector that performs a config migration and pushes it


## Create migration PRs for GA connectors (`create_prs.py`)
This script will create one PR per GA connectors to migrate to `high` test strictness level.

#### What it does:
1. Iterate on all GA connectors in `../../../../../airbyte-config/init/src/main/resources/seed/source_definitions.yaml`
2. Create a branch for each GA connector
3. Locally migrate `acceptance_test_config.yml` to the latest format
4. Commit and push the changes on this branch
5. Open a PR for this branch
6. Run a connector acceptance test on this branch by posting a `/test` comment on the PR

An example of the PR it creates can be found [here](https://github.com/airbytehq/airbyte/pull/19136)

PR get created with the following labels:
* `area/connectors`
* `team/connectors-python`
* `type/enhancement`
* `test-strictness-level`

PR are added to the following project: `SAT-high-test-strictness-level`

#### How to run:
**Dry run**:
`python create_prs.py`

**Real execution**:
`python create_prs.py --dry False`

## Existing migrations
* `strictness_level_migration`: Migrates a connector from the old format to the new format, and adds enforcement of high strictness level.
* `fail_on_extra_columns`: Adds `fail_on_extra_columns: false` to connectors which fail the `Additional properties are not allowed` extra column validation.
  Supports adding this parameter to configs in the old and new config format.