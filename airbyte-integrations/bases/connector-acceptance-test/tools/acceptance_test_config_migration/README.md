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

## Scripts

The scripts perform operations on a set of connectors. 

### `run_tests.py`: Run CAT tests and save results by exit code

### `create_issues.py`: Create issues in bulk
This script will create one issue per GA connectors to migrate to `high` test strictness level.

#### What it does:
1. Find all GA connectors in `../../../../../airbyte-config/init/src/main/resources/seed/source_definitions.yaml`
2. Generate an issue content (title, body, labels, project), using `./templates/issue.md.j2`
3. Find an already existing issue with the same title.
4. Create the issue and return its url if it does not exist.

Issues get created with the following labels:
* `area/connectors`
* `team/connectors-python`
* `type/enhancement`
* `test-strictness-level`

Issues are added to the following project: `SAT-high-test-strictness-level`

#### How to run:
**Dry run**:
`python create_issues.py`

**Real execution**:
`python create_issues.py --dry False`


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