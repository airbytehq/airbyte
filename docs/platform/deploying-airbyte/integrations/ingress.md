---
products: oss-community
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Ingress

Ingress controls access to your Airbyte deployment.

## How to manage ingress

Managing ingress with Airbyte works differently depending on whether you deploy with Helm or abctl.

- **If you are using abctl**, an NGINX ingress is automatically provided for you. You don't need to provision an additional ingress.

- **If you are using Helm**, you need to configure ingress for your deployment. You have two options.

  - **Use Airbyte's Helm chart ingress configuration** - Configure ingress through your `values.yaml` file.

  - **Bring your own ingress** - Manually create and manage your own Kubernetes ingress resource.

    Use the Helm chart ingress configuration if you want Airbyte to manage ingress creation and updates automatically. Use your own ingress if you need custom ingress configurations beyond what the Helm chart provides, or if you prefer to manage ingress independently.

## Request body size

The Airbyte server, workers, and workload API server each default to a maximum request body size of 50 MB (52,428,800 bytes). Larger requests, such as requests containing large discovered catalogs, can fail with HTTP `413` errors.

Airbyte's Helm chart ingress routes only to the Airbyte server. For requests from outside the cluster, configure your ingress controller and any reverse proxies to allow at least the server's request body limit. The worker and workload API server limits apply to requests inside the cluster, not traffic through this ingress.

For ingress-nginx, the default [`proxy-body-size`](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/#proxy-body-size) is `1m`. Use the [`nginx.ingress.kubernetes.io/proxy-body-size` annotation](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/#custom-max-body-size) to set the limit for your ingress. The NGINX examples below set it to `"50m"` to match Airbyte's default.

:::warning abctl request limit

abctl v0.30.4 limits incoming requests to 10 MB through its NGINX ingress, even when the Airbyte server allows larger requests. Increasing the limit on a reverse proxy in front of abctl doesn't raise this ingress limit.

:::

### Increase the limit for a Helm deployment

To allow larger requests, set all three [request size variables](../../operator-guides/configuring-airbyte.md#airbyte-services) to the same byte value on `server`, `worker`, and `workloadApiServer` in your `values.yaml` file. Raising only one limit can still result in HTTP `413` errors. For requests through the server ingress, also increase the ingress and any reverse proxy limits to match.

For example, this configuration sets the service limits to 100 MB (104,857,600 bytes) and the ingress-nginx limit to `100m`:

```yaml
server:
  env_vars:
    MICRONAUT_SERVER_MAX_REQUEST_SIZE: "104857600"
    MICRONAUT_SERVER_MAX_REQUEST_BUFFER_SIZE: "104857600"
    NETTY_AGGREGATOR_MAX_CONTENT_LENGTH: "104857600"
worker:
  env_vars:
    MICRONAUT_SERVER_MAX_REQUEST_SIZE: "104857600"
    MICRONAUT_SERVER_MAX_REQUEST_BUFFER_SIZE: "104857600"
    NETTY_AGGREGATOR_MAX_CONTENT_LENGTH: "104857600"
workloadApiServer:
  env_vars:
    MICRONAUT_SERVER_MAX_REQUEST_SIZE: "104857600"
    MICRONAUT_SERVER_MAX_REQUEST_BUFFER_SIZE: "104857600"
    NETTY_AGGREGATOR_MAX_CONTENT_LENGTH: "104857600"
ingress:
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
```

Apply the updated values with `helm upgrade`.

## Before you begin: you must set up an ingress controller

Before enabling ingress in Airbyte, you must have an ingress controller deployed in your Kubernetes cluster. Airbyte doesn't install or manage the ingress controller. Without one, your configurations in Airbyte can't do anything. Refer to your ingress controller's documentation for installation instructions.

- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/)
- [AWS Load Balancer Controller](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html)
- Other ingress controllers: Refer to your controller's official documentation

For TLS certificate management, refer to tools like [cert-manager](https://cert-manager.io/docs/) or your cloud provider's certificate management service.

Set appropriate backend timeout values for the Airbyte server ingress. Timeout values that are too short can lead to 504 errors in the UI when creating new sources or destinations.

## Option 1: Use Airbyte's Helm chart

:::note
Follow the configuration examples below.
:::

You can configure ingress directly in your `values.yaml` file. Airbyte will automatically create and manage the ingress resource for you.

### Basic configuration

Add the following to your `values.yaml` file. This example routes requests to the Airbyte server:

```yaml
ingress:
  enabled: true
  className: "nginx"  # Specify your ingress class (e.g., "nginx", "alb", etc.)
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
    # nginx.ingress.kubernetes.io/ssl-redirect: "false"
  hosts:
    - host: airbyte.example.com  # Replace with your domain
      paths:
        - path: /
          pathType: Prefix
          backend: server  # Routes to airbyte-server (UI and API)
  tls: []
    # Optionally configure TLS
    # - secretName: airbyte-tls
    #   hosts:
    #     - airbyte.example.com
```

The `backend` field must be `server`. The Helm chart rejects other backend values.

### Switching from external ingress to Helm chart ingress

If you previously created a manual ingress resource and want to switch to using the Helm chart ingress configuration, follow the steps below. It isn't necessary to switch, and if you already have functioning ingress, it's likely easier to continue using it.

1. Delete your existing manual ingress resource:

   ```bash
   kubectl delete ingress <your-ingress-name> -n <namespace>
   ```

2. Add the ingress configuration to your `values.yaml` file as shown above

3. Upgrade your Helm deployment:

   ```bash
   helm upgrade airbyte airbyte/airbyte \
     --namespace <namespace> \
     --values ./values.yaml
   ```

## Option 2: Bring your own ingress

If you prefer to manage your own ingress resource, you can manually create a Kubernetes ingress resource. This approach gives you complete control over the ingress configuration.

### Switching from Helm Chart Ingress to Manual Ingress

If you previously used the Helm chart ingress configuration and want to switch to manual ingress management:

1. Disable ingress in your `values.yaml`:

   ```yaml
   ingress:
     enabled: false
   ```

2. Upgrade your Helm deployment to remove the ingress resource:

   ```bash
   helm upgrade airbyte airbyte/airbyte \
     --namespace <namespace> \
     --values ./values.yaml
   ```

3. Create your manual ingress resource using one of the examples below.

### Manual ingress examples

<Tabs>
<TabItem value="NGINX" label="NGINX">

Refer to the [NGINX Ingress Controller installation documentation](https://kubernetes.github.io/ingress-nginx/deploy/) for setup instructions.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airbyte-ingress # ingress name, example: airbyte-production-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "false"
    nginx.ingress.kubernetes.io/proxy-body-size: "50m"
spec:
  ingressClassName: nginx
  rules:
    - host: airbyte.example.com # replace with your host
      http:
        paths:
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-connector-builder-server-svc
                name: airbyte-airbyte-connector-builder-server-svc
                port:
                  number: 80 # service port, example: 8080
            path: /api/v1/connector_builder/
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-server-svc
                name: airbyte-airbyte-server-svc
                port:
                  number: 8001 # service port, example: 8080
            path: /
            pathType: Prefix
```

</TabItem>
<TabItem value="Amazon ALB" label="Amazon ALB">

If you intend to use Amazon Application Load Balancer (ALB) for ingress, this ingress definition is close to what's needed to get up and running. Refer to the AWS documentation for [installing the AWS Load Balancer Controller](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html). For TLS configuration, see [AWS Certificate Manager](https://aws.amazon.com/certificate-manager/getting-started/).

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airbyte-ingress # ingress name, e.g. airbyte-production-ingress
  annotations:
    # Specifies that the Ingress should use an AWS ALB.
    kubernetes.io/ingress.class: "alb"
    # Redirects HTTP traffic to HTTPS.
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    # Creates an internal ALB, which is only accessible within your VPC or through a VPN.
    alb.ingress.kubernetes.io/scheme: internal
    # Specifies the ARN of the SSL certificate managed by AWS ACM, essential for HTTPS.
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-x:xxxxxxxxx:certificate/xxxxxxxxx-xxxxx-xxxx-xxxx-xxxxxxxxxxx
    # Sets the idle timeout value for the ALB.
    alb.ingress.kubernetes.io/load-balancer-attributes: idle_timeout.timeout_seconds=30
    # [If Applicable] Specifies the VPC subnets and security groups for the ALB
    # alb.ingress.kubernetes.io/subnets: '' e.g. 'subnet-12345, subnet-67890'
    # alb.ingress.kubernetes.io/security-groups: <SECURITY_GROUP>
spec:
  rules:
    - host: airbyte.example.com # replace with your host
      http:
        paths:
          - backend:
              service:
                name: airbyte-airbyte-connector-builder-server-svc
                port:
                  number: 80
            path: /api/v1/connector_builder/
            pathType: Prefix
          - backend:
              service:
                name: airbyte-airbyte-server-svc
                port:
                  number: 8001
            path: /
            pathType: Prefix
```

The ALB controller uses a `ServiceAccount` that requires the [following IAM policy](https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json) to be attached.

</TabItem>
</Tabs>

## Ensure your airbyte URL matches your ingress host

Once you configure ingress, ensure that the value of `global.airbyteUrl` in your values.yaml matches the ingress URL.

```yaml
global:
  airbyteUrl: # e.g. https://airbyte.example.com
```
