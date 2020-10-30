# Google Analytics Source

## Documentation
* [User Documentation](https://docs.airbyte.io/integrations/sources/googleanalytics)

## Community Contributor

1. Look at the integration documentation to see how to create a credentials json file and get a view id.
1. Create a file at `secrets/config.json` with the following format:
```
{
  "credentials_json": "{\"type\": \"service_account\",\n  \"project_id\": \"REDACTED\",\n  \"private_key_id\": \"REDACTED\",\n  \"private_key\": \"-----BEGIN PRIVATE KEY-----\\REDACTED\\n-----END PRIVATE KEY-----\\n\",\n  \"client_email\": \"REDACTED\",\n  \"client_id\": \"103293192021796062643\",\n  \"auth_uri\": \"https://accounts.google.com/o/oauth2/auth\",\n  \"token_uri\": \"https://oauth2.googleapis.com/token\",\n  \"auth_provider_x509_cert_url\": \"https://www.googleapis.com/oauth2/v1/certs\",\n  \"client_x509_cert_url\": \"REDACTED\"\n}",
  "view_id": "123456789",
  "start_date": "2020-05-01T00:00:00Z"
}
```
1. Run the tests with the `GOOGLE_ANALYTICS_TEST_TRACKING_ID` environment variable set to the tracking ID for your instance (example: `UA-1234567-1`).

## For Airbyte employees
Put the contents of the `google-analytics-test-config` secret on Rippling under the `Engineering` folder into `secrets/config.json` and `google-analytics-test-tracker` to `secrets/tracker.txt` to be able to run integration tests locally.
