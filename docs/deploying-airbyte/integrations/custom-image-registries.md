---
products: oss-community, oss-enterprise
---

import ContainerProviders from '@site/static/_docker_image_registries.md';

# Custom image registry

If your organization uses custom image registries, you can use them with Airbyte, too. Airbyte supports public image registries without secrets and private or public ones that use secrets.

Implementing Airbyte this way has several advantages.

- **Security**: Private custom image registries keep images in your network, reducing the risk of external threats.
- **Access control**: You have more control over who can access and modify images.
- **Compliance**: By keeping images in a controlled environment, it's easier to prove compliance with regulatory requirements for data storage and handling.

## Use a public custom image registry without secrets

1. Add images to your custom image registry. If you don't already use a custom image registry, see the docs for these common options.

    <ContainerProviders/>

2. Add the following customization to Airbyte's `values.yaml` file, replacing the `registry` value with your own registry location. This example demonstrates a custom image registry from GitHub.

    ```yaml
    global:
      image:
        registry: ghcr.io/NAMESPACE
    ```

## Use a private or public custom image registry with secrets

1. Add images to your custom image registry. If you don't already use a custom image registry, see the docs for these common options.

    <ContainerProviders/>

2. Create a Kubernetes secret. In this example, we create a secret called `regcred` from a config file. That file contains authentication information for a private custom image registry. [Learn more about Kubernetes secrets](https://kubernetes.io/docs/tasks/configmap-secret/).

    ```bash
    kubectl create secret generic regcred \
    --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
    --type=kubernetes.io/dockerconfigjson
    ```

3. Add the following customization to Airbyte's `values.yaml` file, replacing the `registry` value with your own registry location, and the secrets names with your own. This example demonstrates a custom image registry on GitHub and using the `regcred` secret, created earlier.

    ```yaml
    global:
      image:
        registry: ghcr.io/NAMESPACE
      imagePullSecrets:
        - name: regcred
      ```