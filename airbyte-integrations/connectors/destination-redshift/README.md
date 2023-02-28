# Destination Redshift

This is the repository for the Redshift Destination Connector.

This connector can run in one of two mode:

- Direct Insert: using SQL to directly place data into tables.
- S3 Staging: Data files are uploaded to the customer's S3 and a load is done into the database from these files directly. This is a directly
  supported feature of Redshift. Consult Redshift documentation for more information and permissions.

This connector has a capability to query the database via an SSH Tunnel (bastion host). This can be useful for environments where Redshift has not
been exposed to the internet.

## Testing

Unit tests are run as usual.

Integration/Acceptance tests are run via the command line with secrets managed out of Google Cloud Secrets Manager.
Consult the integration test area for Redshift.

## Actual secrets

The actual secrets for integration tests can be found in Google Cloud Secrets Manager. Search on redshift for the labels:

- SECRET_DESTINATION-REDSHIFT__CREDS - used for Standard tests. (__config.json__)
- SECRET_DESTINATION-REDSHIFT_STAGING__CREDS - used for S3 Staging tests. (__config_staging.json__)
