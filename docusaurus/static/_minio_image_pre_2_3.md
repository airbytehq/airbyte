:::warning Airbyte versions before 2.3 require a MinIO image override
The `minio/minio` image that Airbyte versions before 2.3 use for internal storage is no longer available on Docker Hub. If you deploy or upgrade an Airbyte version earlier than 2.3 without overriding the MinIO image, MinIO fails to pull its image and the deployment stalls. Airbyte 2.3 and later use the `airbyte/minio` image and don't need this override.

Set `minio.image.repository` to `airbyte/minio`. Keep the image tag unchanged.

New installs:

- Helm: add `--set minio.image.repository=airbyte/minio` to your install command. For example:

  ```bash
  helm install airbyte airbyte-v2/airbyte \
    --namespace airbyte --create-namespace --version 2.2.0 \
    --set minio.image.repository=airbyte/minio
  ```

- abctl: add the override to your `values.yaml` file and pass it with `abctl local install --chart-version <chart-version> --values ./values.yaml`, where `<chart-version>` is the pre-2.3 chart version you want to install.

  ```yaml
  minio:
    image:
      repository: airbyte/minio
  ```

Existing installs:

Run these steps in order. Don't run `helm upgrade` first. It fails while MinIO is down.

These commands assume your namespace and Helm release are both named `airbyte`. If yours differ, substitute your own names.

1. Point the MinIO StatefulSet at the new image.

   ```bash
   kubectl -n airbyte set image statefulset/airbyte-minio \
     airbyte-minio=airbyte/minio:RELEASE.2023-11-20T22-40-07Z
   ```

2. Delete the stuck pods. This is required because the StatefulSet rollout stalls on a stuck pod.

   ```bash
   kubectl -n airbyte delete pod airbyte-minio-0
   kubectl -n airbyte delete pod airbyte-minio-create-bucket --ignore-not-found
   ```

3. Upgrade the Helm release so the override persists. Replace `<repo>` with the name of your Helm repository, for example `airbyte-v2`. Replace `<chart-version>` with the chart version you currently run (`helm list -n airbyte` shows it) so the upgrade doesn't move you to a newer chart.

   ```bash
   helm upgrade airbyte <repo>/airbyte \
     --namespace airbyte --reuse-values \
     --version <chart-version> \
     --set minio.image.repository=airbyte/minio
   ```

   If this step fails on a `minio` hook, run it again.

If you use abctl, run steps 1 and 2 with `kubectl --kubeconfig ~/.airbyte/abctl/abctl.kubeconfig -n airbyte-abctl` instead of `kubectl -n airbyte`. Then, instead of `helm upgrade`, add the override to your `values.yaml` file and run `abctl local install --values ./values.yaml`.
:::
