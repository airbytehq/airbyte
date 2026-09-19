:::warning Airbyte versions before 2.3 require a MinIO image override
The `minio/minio` image that Airbyte versions before 2.3 use for internal storage is no longer available on Docker Hub. If you deploy or upgrade an Airbyte version earlier than 2.3 without overriding the MinIO image, MinIO fails to pull its image and the deployment stalls. Airbyte 2.3 and later use the `airbyte/minio` image and don't need this override.

Keep the image tag unchanged.

New installs:

Add the override to a `values.yaml` file and pass it to abctl:

```yaml
minio:
  image:
    repository: airbyte/minio
```

```bash
abctl local install --chart-version <chart-version> --values ./values.yaml
```

Here, `<chart-version>` is the pre-2.3 chart version you want to install.

Existing installs:

Run these steps in order. Don't run `abctl local install` first. It fails while MinIO is down.

1. Point the MinIO StatefulSet at the new image:

   ```bash
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig -n airbyte-abctl set image statefulset/airbyte-minio \
     airbyte-minio=airbyte/minio:RELEASE.2023-11-20T22-40-07Z
   ```

2. Delete the stuck pods (StatefulSet rollout stalls on a stuck pod):

   ```bash
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig -n airbyte-abctl delete pod airbyte-minio-0
   kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig -n airbyte-abctl delete pod airbyte-minio-create-bucket --ignore-not-found
   ```

3. Add the override to your `values.yaml` and re-run `abctl local install --chart-version <chart-version> --values ./values.yaml` with your current chart version so the override persists.

   ```yaml
   minio:
     image:
       repository: airbyte/minio
   ```

   ```bash
   abctl local install --chart-version <chart-version> --values ./values.yaml
   ```

   If this step fails on a `minio` hook, run it again.
:::
