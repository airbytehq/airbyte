# Google PubSub Test Configuration

In order to test the PubSub destination, you need a service account key file.

## Community Contributor

As a community contributor, you will need access to a GCP project and PubSub to run tests.

1. Go to the `Service Accounts` page on the GCP console
1. Click on `+ Create Service Account" button
1. Fill out a descriptive name/id/description
1. Click the edit icon next to the service account you created on the `IAM` page
1. Add the `Pub/Sub Editor` role
1. Go back to the `Service Accounts` page and use the actions modal to `Create Key`
1. Download this key as a JSON file
1. Move and rename this file to `secrets/credentials.json`

## Airbyte Employee

1. Access the `google pubsub test credentials.json` secret on Lastpass under the `shared-integration-test` folder
1. Create a file with the contents at `secrets/credentials.json`
