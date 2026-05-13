# destination-pubsub: Contributor notes

## Test configuration

To run integration tests, you need a Google Cloud service account key file.

If you're a community contributor:

1. Create or choose a GCP project with Pub/Sub enabled.
2. Go to the Service Accounts page in the Google Cloud console.
3. Create a service account.
4. On the IAM page, add the `Pub/Sub Editor` role to the service account.
5. Create and download a JSON key for the service account.
6. Move the key to `secrets/credentials.json`.

If you're an Airbyte employee:

1. Access the `google pubsub test credentials.json` secret in LastPass under `shared-integration-test`.
2. Create `secrets/credentials.json` with the secret contents.
