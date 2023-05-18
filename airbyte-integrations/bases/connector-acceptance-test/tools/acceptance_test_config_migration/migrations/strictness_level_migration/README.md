# Migrating connectors' acceptance test configs to high strictness
This migration sets connectors' `acceptance-test-config.yml` to `high` test strictness level.
In doing so, it migrates the config files from a previous format into our new format.

Before following this README, please reference the `acceptance_test_config_migraton` README for general
usage information for the given scripts.

## Create migration issue for GA connectors (`create_issues.py`)
Create one issue per GA connectors to migrate to `high` test strictness level.

Issues get created with the following labels:
* `area/connectors`
* `team/connectors-python`
* `type/enhancement`
* `test-strictness-level`

Issues are added to the following project: `SAT-high-test-strictness-level`

### How to run:
**Dry run**:
```
python create_issues.py
```

**Real execution**:
```
python create_issues.py --no-dry
```

## Create migration PRs for GA connectors (`create_prs.py`)
Create one PR per GA connector to perform the migration to `high` test strictness level.

An example of the PR it creates can be found [here](https://github.com/airbytehq/airbyte/pull/19136)

PR get created with the following labels:
* `area/connectors`
* `team/connectors-python`
* `type/enhancement`
* `test-strictness-level`

PR are added to the following project: `SAT-high-test-strictness-level`

### How to run:
**Dry run**:
`python create_prs.py`

**Real execution**:
`python create_prs.py --no-dry`