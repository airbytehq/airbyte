# S3 Test Configuration

In order to test the D3 destination, you need an AWS account (or alternative S3 account).

## Community Contributor

As a community contributor, you will need access to AWS to run the integration tests.

1. Create an S3 bucket for testing.
1. Get your `access_key_id` and `secret_access_key` that can read and write to the above bucket.
1. Paste the bucket and key information into the config files under [`./sample_secrets`](./sample_secrets).
1. Rename the directory from `sample_secrets` to `secrets`.
1. Feel free to modify the config files with different settings in the acceptance test file (e.g. `S3CsvDestinationAcceptanceTest.java`, method `getFormatConfig`), as long as they follow the schema defined in [spec.json](src/main/resources/spec.json).

## Airbyte Employee

1. Access the `destination s3 * creds` secrets on Last Pass. The `*` here represents the different file format.
1. Replace the `config.json` under `sample_secrets`.
1. Rename the directory from `sample_secrets` to `secrets`.
