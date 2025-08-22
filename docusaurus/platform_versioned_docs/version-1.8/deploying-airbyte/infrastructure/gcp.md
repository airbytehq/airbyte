---
products: oss-community, oss-enterprise
---

# Google Cloud Platform (GCP)

Installing Airbyte on GCP requires a service account. The service account must have the correct permissions to access 
Google Cloud Storage and Google Secrets Manager, if you those integrations are to be used in your installation. The
documentation for creating a GCP Service Account can be found [here](https://cloud.google.com/iam/docs/service-accounts-create)

## Google Cloud Storage Roles

```text
roles/storage.objectCreator
roles/storage.admin
```

## Google Secret Manager Roles

```text
roles/secretmanager.secretAccessor
roles/secretmanager.secretVersionAdder
roles/secretmanager.secretVersionManager
roles/secretmanager.viewer
```