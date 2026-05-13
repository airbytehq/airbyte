# destination-bigquery: Contributor notes

## Managing BigQuery permissions

Before testing the connector, create or reuse a Google Cloud service account with the permissions needed to create datasets, create jobs, and write table data.

1. In the Google Cloud console, go to IAM & Admin > Service Accounts.
2. Create a service account, or choose an existing one.
3. In IAM & Admin > Roles, create a custom role with these permissions:
   - `bigquery.datasets.create`
   - `bigquery.datasets.get`
   - `bigquery.jobs.create`
   - `bigquery.tables.create`
   - `bigquery.tables.delete`
   - `bigquery.tables.get`
   - `bigquery.tables.updateData`
4. Assign the custom role to the service account.
