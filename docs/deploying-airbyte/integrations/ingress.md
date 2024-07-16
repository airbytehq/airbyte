---
products: oss-community, oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Ingress

:::tip
If you are using `abctl` to manage your deployment, a nginx ingress is automatically provided for you. There is no need to provision an additional ingress.
:::

To access the Airbyte UI, you will need to manually attach an ingress configuration to your deployment.
The following is a simplified definition of an ingress resource you could use for your Airbyte instance:

<Tabs>
<TabItem value="NGINX" label="NGINX">

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: # ingress name, example: airbyte-production
  annotations:
    ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
    - host: # host, example: airbyte.company.example
      http:
        paths:
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-webapp-svc
                name: airbyte-airbyte-webapp-svc
                port:
                  number: 80 # service port, example: 8080
            path: /
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-keycloak-svc
                name: airbyte-airbyte-keycloak-svc
                port:
                  number: 8180
            path: /auth
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte--server-svc
                name: airbyte-airbyte-server-svc
                port:
                  number: 8001
            path: /api/public
            pathType: Prefix
```
</TabItem>
<TabItem value="Amazon ALB" label="Amazon ALB">

If you intend to use Amazon Application Load Balancer (ALB) for ingress, this ingress definition will be close to what's needed to get up and running:


```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: # ingress name, e.g. airbyte-production
  annotations:
    # Specifies that the Ingress should use an AWS ALB.
    kubernetes.io/ingress.class: "alb"
    # Redirects HTTP traffic to HTTPS.
    ingress.kubernetes.io/ssl-redirect: "true"
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
    - host: # e.g. airbyte.company.example
      http:
        paths:
          - backend:
              service:
                name: airbyte-airbyte-webapp-svc
                port:
                  number: 80
            path: /
            pathType: Prefix
          - backend:
              service:
                name: airbyte-airbyte-keycloak-svc
                port:
                  number: 8180
            path: /auth
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-server-svc
                name: airbyte-airbyte-server-svc
                port:
                  number: 8001
            path: /api/public
            pathType: Prefix
```

The ALB controller uses a `ServiceAccount` that requires the [following IAM policy](https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json) to be attached.

</TabItem>
</Tabs>
