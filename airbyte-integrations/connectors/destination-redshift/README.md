# Destination Redshift

This is the repository for the Redshift Destination Connector.

## Testing
The `AirbyteCopier.java` class contains an ignored local test class. This is ignored as
the necessary components cannot be mocked locally. The class requires credentials in order
to run all its tests.

Users have the option of either filling in the variables defined at the top of the class,
or filling in a `config.properties` file in `src/test/resources` with the following property keys:
```aidl
s3.keyId=<key_id>
s3.accessKey=<access_key>

redshift.connString=<conn_string>
redshift.user=<user>
redshift.pass=<pass>
```
## Actual secrets
The actual secrets for integration tests could be found in Google Secrets Manager. It could be found by next labels:
- SECRET_DESTINATION-REDSHIFT__CREDS - used for Standard tests. (__config.json__)
- SECRET_DESTINATION-REDSHIFT_STAGING__CREDS - used for S3 Staging tests. (__config_staging.json__)

