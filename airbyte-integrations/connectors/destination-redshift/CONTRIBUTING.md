# destination-redshift: Contributor notes

## Connector modes

This connector can write to Redshift in two modes:

- Direct insert: uses SQL to write directly into destination tables.
- S3 staging: uploads data files to the configured S3 bucket, then loads them into Redshift from S3.

The connector can also query Redshift through an SSH tunnel for environments where Redshift is not exposed to the internet.

## Integration test secrets

Integration test credentials are stored in Google Cloud Secret Manager. Search for Redshift secrets with these labels:

- `SECRET_DESTINATION-REDSHIFT__CREDS`: standard test credentials for `config.json`.
- `SECRET_DESTINATION-REDSHIFT_STAGING__CREDS`: S3 staging test credentials for `config_staging.json`.
