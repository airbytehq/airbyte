---
products: oss-*
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Update ingress for version 1.7 and later

Airbyte version 1.7 introduced a breaking change for ingress to the Connector Builder. If you're a Self-Managed Community user or Self-Managed Enterprise customer, and you're upgrading to version 1.7.0 or later, complete these steps when you upgrade. If you don't, the Connector Builder gives you 403 Forbidden errors and you can't test streams or use the Connector Builder UI.

## What changed

In version 1.7, Airbyte began merging the `webapp` service and its functions into `server`. As of version 1.8, Airbyte no longer publishes an `airbyte-webapp` image and it's no longer independently deployable. When you first deployed Airbyte, you probably set up ingress to expect that `webapp` would exist and function as a proxy.

If you're upgrading to version 1.7 or later, update your ingress rules to reflect that the webapp no longer exists. How you do this depends if you deploy Airbyte with Helm or abctl.

## Deploying with Helm

Update ingress rules on your deployment to handle `airbyte-server-svc` and `airbyte-connector-builder-server-svc`. Once you do this, the Connector Builder functions normally again.

Review the following examples and use them as a guide to update your own ingress settings.

<Tabs>
<TabItem value="banana" label="NGINX">

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
<TabItem value="orange" label="Amazon ALB">

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

</TabItem>
</Tabs>

## Deploying with abctl

If you deploy Airbyte with abctl, abctl handles ingress for you. abctl version 0.28 and later support the changes in Airbyte 1.7 and later.

1. Upgrade abctl to the latest version. For example, `brew upgrade abctl`.

2. Deploy the latest version of Airbyte. For example, `abctl local install`.
