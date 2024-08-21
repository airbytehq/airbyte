---
products: oss-community, oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Ingress

:::tip
If you are using `abctl` to manage your deployment, a nginx ingress is automatically provided for you. There is no need to provision an additional ingress.
:::

To access the Airbyte UI, you will need to manually attach an ingress configuration to your deployment. These guides assume that you have already deployed an Ingress Controller.
The following is a simplified definition of an ingress resource you could use for your Airbyte instance:

<Tabs>
<TabItem value="NGINX" label="NGINX">

If you don't already have an NGINX controller installed, you can do it by running `helm install my-release oci://ghcr.io/nginxinc/charts/nginx-ingress --version 1.3.1` or following the [instructions](https://docs.nginx.com/nginx-ingress-controller/installation/installing-nic/installation-with-helm/) from NGINX.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airbyte-ingress # ingress name, example: airbyte-production-ingress
  annotations:
    ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
    - host: localhost # host, example: airbyte.company.example
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
```
</TabItem>
<TabItem value="Amazon ALB" label="Amazon ALB">

First you need to have an ALB deployed. You can read more about ALBs in the detail below. Reference AWS on how to set these up.

<details>
    <summary>AWS ALBs</summary>

The recommended method for Cluster Ingress is an AWS ALB. This configuration is outside the scope of this documentation. You can find more information on how to correctly configure an ALB Ingress Controller by reading the official [Route application and HTTP traffic with Application Load Balancers](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html) documentation provided by Amazon.

Once the AWS Load Balancer Controller has been correctly installed the Airbyte installation process will be able to automatically create an ALB for you. You can combine the ALB with AWS Certificate Manager (ACM) to secure your instance with TLS. The ACM documentation can be found here: [Getting Started with AWS Certificate Manager](https://aws.amazon.com/certificate-manager/getting-started/). To use the ACM certificate, you can specify the certificate-arn when creating the Kubernetes Ingress. For more information see the [Kubernetes Ingress Annotations documentation](https://kubernetes-sigs.github.io/aws-load-balancer-controller/v2.1/guide/ingress/annotations/#certificate-arn).
</details>

If you intend to use Amazon Application Load Balancer (ALB) for ingress, this ingress definition will be close to what's needed to get up and running:


```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: airbyte-ingress # ingress name, e.g. airbyte-production-ingress
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
    - host: localhost # e.g. airbyte.company.example
      http:
        paths:
          - backend:
              service:
                name: airbyte-airbyte-webapp-svc
                port:
                  number: 80
            path: /
            pathType: Prefix
```

The ALB controller uses a `ServiceAccount` that requires the [following IAM policy](https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json) to be attached.

</TabItem>
</Tabs>
