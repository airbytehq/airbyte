## Installing DBT

1. Activate your venv and run `pip3 install dbt`
1. Copy `airbyte-normalization/sample_files/profiles.yml` over to `~/.dbt/profiles.yml`
1. Edit to configure your profiles accordingly

## Running DBT

1. `cd airbyte-normalization`
1. You can now run DBT commands, to check the setup is fine: `dbt debug`
1. To build the DBT tables in your warehouse: `dbt run`

Note that in order to work with the current models that i am testing, you should have:
 - `recipes` and `recipes_json` tables
 - in a `data` dataset in your bigquery project (referenced in your `profiles.yml`... 