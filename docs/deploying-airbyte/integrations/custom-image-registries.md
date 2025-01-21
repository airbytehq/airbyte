---
products: oss-community, oss-enterprise
---

import ContainerProviders from '@site/static/_docker_image_registries.md';

# Custom image registry

You can optionally configure Airbyte to pull Docker images from a custom image registry rather than [Airbyte's public Docker repository](https://hub.docker.com/u/airbyte). In this case, Airbyte pulls both platform images (e.g. `server`, `webapp`, `workload-launcher`, etc.) and connector images (e.g. Postgres Source, S3 Destination, etc.) from the configured registry.

Implementing Airbyte this way has several advantages.

- **Security**: Private custom image registries keep images in your network, reducing the risk of external threats.
- **Access control**: You have more control over who can access and modify images.
- **Compliance**: By keeping images in a controlled environment, it's easier to prove compliance with regulatory requirements for data storage and handling.

## Before you start

Set up your custom image registry. The examples in this article use GitHub, but you have many options. Here are some popular ones:

<ContainerProviders/>

## Get a list of all Airbyte images

To get a list of Airbyte images for the latest version, use abctl.

```bash
abctl images manifest
```

You should see something like this:

```bash
airbyte/bootloader:1.3.1
airbyte/connector-builder-server:1.3.1
airbyte/connector-sidecar:1.3.1
airbyte/container-orchestrator:1.3.1
airbyte/cron:1.3.1
airbyte/db:1.3.1
airbyte/mc:latest
airbyte/server:1.3.1
airbyte/webapp:1.3.1
airbyte/worker:1.3.1
airbyte/workload-api-server:1.3.1
airbyte/workload-init-container:1.3.1
airbyte/workload-launcher:1.3.1
bitnami/kubectl:1.28.9
busybox:1.35
busybox:latest
curlimages/curl:8.1.1
minio/minio:RELEASE.2023-11-20T22-40-07Z
temporalio/auto-setup:1.23.0
```

## Step 1: Customize Airbyte to use your image registry

To pull all platform and connector images from a custom image registry, add the following customization to Airbyte's `values.yaml` file, replacing the `registry` value with your own registry location.

```yaml title="values.yaml"
global:
  image:
    registry: ghcr.io/NAMESPACE
```

If your registry requires authentication, you can create a Kubernetes secret and reference it in the Airbyte config:

1. Create a Kubernetes secret. In this example, you create a secret called `regcred` from a config file. That file contains authentication information for a private custom image registry. [Learn more about Kubernetes secrets](https://kubernetes.io/docs/tasks/configmap-secret/).

    ```bash
    kubectl create secret generic regcred \
    --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
    --type=kubernetes.io/dockerconfigjson
    ```

2. Add the secret you created to your `values.yaml` file. In this example, you use your `regcred` secret to authenticate.

    ```yaml title="values.yaml"
    global:
      image:
        registry: ghcr.io/NAMESPACE
      // highlight-start
      imagePullSecrets:
        - name: regcred
      // highlight-end
    ```

## Step 2: Tag and push Airbyte images

Tag and push Airbyte's images to your custom image registry. In this example, you tag all Airbyte images and push them all to GitHub.

```bash
abctl images manifest | xargs -L1 -I{} docker tag {} ghcr.io/NAMESPACE/{} && docker push ghcr.io/NAMESPACE/{}
```

Now, when you install Airbyte, images will come from the custom image registry you configured.