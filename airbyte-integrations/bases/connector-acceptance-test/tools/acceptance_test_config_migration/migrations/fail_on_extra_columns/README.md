# Bypassing column selection validation for sources which fail it
This migration adds `fail_on_extra_columns: false` to the `basic_read` test in the `acceptance-test-config.yml`
file for all Beta and GA connectors which fail the stricter validation added to the `basic_read` test. It creates
issues for each of the connectors whose configs were modified as a result.

Before following this README, please reference the `acceptance_test_config_migraton` README for general
usage information for the given scripts.

## Add bypass for connectors that fail the new CAT test

### Run tests on all connectors
Run CAT on all Beta and GA connectors.

```
python run_tests.py --allow_beta
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
python config_migration.py --connectors $(ls migrations/fail_on_extra_columns/test_failure_logs) --allow_beta
```

Add these bypasses to the PR that adds the new CAT test!


## Create issues for failing connectors (`create_issues.py`)
Create one issue per GA connectors to add the missing columns to the spec and remove the `fail_on_extra_columns` bypass.

Issues get created with the following labels:
* `area/connectors`
* `team/connectors-python`
* `type/enhancement`
* `column-selection-sources`

### How to run:
**Dry run**:
```
python create_issues.py --connectors $(ls migrations/fail_on_extra_columns/test_failure_logs) --allow_beta
```

**Real execution**:
```
python create_issues.py --connectors $(ls migrations/fail_on_extra_columns/test_failure_logs) --allow_beta --no-dry
```
