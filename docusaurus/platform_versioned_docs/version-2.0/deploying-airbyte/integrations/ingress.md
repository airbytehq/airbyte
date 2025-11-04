---
products: oss-community, oss-enterprise
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

## Before you begin: you must set up an ingress controller

Before enabling ingress in Airbyte, you must have an ingress controller deployed in your Kubernetes cluster. Airbyte doesn't install or manage the ingress controller. Without one, your configurations in Airbyte can't do anything. Refer to your ingress controller's documentation for installation instructions.

- [NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/deploy/)
- [AWS Load Balancer Controller](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html)
- Other ingress controllers: Refer to your controller's official documentation

For TLS certificate management, refer to tools like [cert-manager](https://cert-manager.io/docs/) or your cloud provider's certificate management service.

Set appropriate backend timeout values for the Airbyte server ingress. Timeout values that are too short can lead to 504 errors in the UI when creating new sources or destinations.

## Option 1: Use Airbyte's Helm chart

:::note
**Helm V2 users:** Follow the configuration examples below.

**Helm V1 users:** Ingress is available but uses a different configuration format. See the [values.yaml reference](/platform/deploying-airbyte/values) for the V1 ingress configuration structure.
:::

You can configure ingress directly in your `values.yaml` file. Airbyte will automatically create and manage the ingress resource for you.

### Basic configuration

Add the following to your `values.yaml` file. This example includes both required backend services for Airbyte to function properly:

```yaml
ingress:
  enabled: true
  className: "nginx"  # Specify your ingress class (e.g., "nginx", "alb", etc.)
  annotations: {}
    # Add any ingress-specific annotations here
    # Example for NGINX:
    # nginx.ingress.kubernetes.io/ssl-redirect: "false"
  hosts:
    - host: airbyte.example.com  # Replace with your domain
      paths:
        - path: /
          pathType: Prefix
          backend: server  # Routes to airbyte-server (UI and API)
        - path: /connector-builder
          pathType: Prefix
          backend: connector-builder-server  # Required for connector builder
  tls: []
    # Optionally configure TLS
    # - secretName: airbyte-tls
    #   hosts:
    #     - airbyte.example.com
```

The `backend` field specifies which Airbyte service to route to:

- `server` - Routes to the main Airbyte API server (handles UI and API requests)
- `connector-builder-server` - Routes to the connector builder service (required for Airbyte's connector builder to work)

### Switching from external ingress to Helm chart ingress

If you previously created a manual ingress resource and want to switch to using the Helm chart ingress configuration, follow the steps below. It isn't necessary to switch, and if you already have functioning ingress, it's likely easier to continue using it.

1. Delete your existing manual ingress resource:

   ```bash
   kubectl delete ingress <your-ingress-name> -n <namespace>
   ```

2. Add the ingress configuration to your `values.yaml` file as shown above

3. Upgrade your Helm deployment:

   ```bash
   helm upgrade airbyte airbyte-v2/airbyte \
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
   helm upgrade airbyte airbyte-v2/airbyte \
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
spec:
  ingressClassName: nginx
  rules:
    - host: airbyte.example.com # replace with your host
      http:
        paths:
          # BEGIN: Self-Managed Enterprise only - Do not include if you are an open source user
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-keycloak-svc 
                name: airbyte-airbyte-keycloak-svc 
                port: 
                  number: 8180 
            path: /auth
            pathType: Prefix
          # END: Self-Managed Enterprise only
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
          # BEGIN: Self-Managed Enterprise only - Do not include if you are an open source user
          - backend:
              service:
                name: airbyte-airbyte-keycloak-svc
                port:
                  number: 8180
            path: /auth
            pathType: Prefix
          # END: Self-Managed Enterprise only
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
