# Title
Description

## Add bypass for connectors that fail the new CAT test

### Run tests on all connectors
Run CAT on all connectors.

```
python run_tests.py
```

### Collect output from connectors that fail due to `additionalProperties`
```
cd migrations/fail_on_extra_columns
sh get_failures.sh
```

### Migrate configs for failed connectors
For the connectors that failed due to `Additional properties are not allowed:`, we want to add the new 
`fail_on_extra_columns` input parameter to the basic read test. To do this, 

```
python config_migration.py --connectors $(ls migrations/fail_on_extra_columns/test_failure_logs)
```

Add these bypasses to the PR that adds the new CAT test!


## Create migration issue for failing connectors (`create_issues.py`)
Create one issue per GA connectors to migrate to `high` test strictness level.

Issues get created with the following labels:
* `area/connectors`
* `team/connectors-python`
* `type/enhancement`
* `column-selection-sources`

### How to run:
**Dry run**:
```
python create_issues.py --connectors $(ls migrations/fail_on_extra_columns/test_failure_logs)
```

**Real execution**:
```
python create_issues.py --connectors $(ls migrations/fail_on_extra_columns/test_failure_logs) --no-dry
```
