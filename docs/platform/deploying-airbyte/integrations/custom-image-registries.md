---
products: oss-community
---

import ContainerProviders from '@site/static/_docker_image_registries.md';

# Custom image registry

You can optionally configure Airbyte to pull Docker images from a custom image registry rather than [Airbyte's public Docker repository](https://hub.docker.com/u/airbyte). In this case, Airbyte pulls both platform images (e.g. `server`, `workload-launcher`, etc.) and connector images (e.g. Postgres Source, S3 Destination, etc.) from the configured registry.

Implementing Airbyte this way has several advantages.

- **Security**: Private custom image registries keep images in your network, reducing the risk of external threats.
- **Access control**: You have more control over who can access and modify images.
- **Compliance**: By keeping images in a controlled environment, it's easier to prove compliance with regulatory requirements for data storage and handling.

## Before you start

Set up your custom image registry. The examples in this article use GitHub, but you have many options. Here are some popular ones:

<ContainerProviders/>

## Custom connectors using fully qualified domain names

[Custom Docker connectors](../../operator-guides/using-custom-connectors/) in your workspace that specify an image using a fully qualified domain name (for example, `example.com/airbyte/your-custom-source`) ignore your configured custom image registry and pull images from the domain specified by that connector.

## Get a list of all Airbyte images

Use abctl to generate the image list for the Helm chart version you plan to install. Replace `<version>` with your chart version, not the Airbyte platform version.

```bash
abctl images manifest --chart-version <version>
```

If you customize image settings, also pass `--values <your values file>` when generating the list. Generate the list before replacing the registry so you can pull images from their original locations.

The list includes images from containers, init containers, and keys ending in `_IMAGE` in the `airbyte-env` ConfigMap. Searching only for `image:` in Helm output misses images such as `CONNECTOR_SIDECAR_IMAGE`, `CONTAINER_ORCHESTRATOR_IMAGE`, and `WORKLOAD_INIT_IMAGE`.

For charts that use `temporalio/server` and `temporalio/admin-tools`, mirror both images with the same tag. The admin-tools image runs Temporal schema migrations, so its version must match the server version. By default, `temporal.adminTools.image.tag` uses `temporal.image.tag`.

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

Pull, tag, and push Airbyte's images to your custom image registry.

In this example, you pull all platform images, tag them, and push them to GitHub. Use the same chart version and any image overrides from the list-generation step.

```bash
abctl images manifest --chart-version <version> > images.txt
while IFS= read -r image; do
  docker pull "$image" &&
    docker tag "$image" "ghcr.io/NAMESPACE/$image" &&
    docker push "ghcr.io/NAMESPACE/$image" || exit 1
done < images.txt
```

You can also pull Airbyte's connector images from Docker, tag them, and push them to your custom image registry. You must do this prior to adding a source or destination.

In this example, you pull a connector from Docker, tag it, and push it to GitHub.

```bash
docker pull airbyte/destination-google-sheets:latest
docker tag airbyte/destination-google-sheets:latest ghcr.io/NAMESPACE/airbyte/destination-google-sheets:latest
docker push ghcr.io/NAMESPACE/airbyte/destination-google-sheets:latest
```

Now, when you install Airbyte, images will come from the custom image registry you configured.
