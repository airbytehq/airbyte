---
products: oss-enterprise
---

# Existing Instance Upgrades

This page supplements the [Self-Managed Enterprise implementation guide](./implementation-guide.md). It highlights the steps to take if you are currently using Airbyte Self-Managed Community, our free open source offering, and are ready to upgrade to [Airbyte Self-Managed Enterprise](./README.md).

A valid license key is required to get started with Airbyte Enterprise. [Talk to sales](https://airbyte.com/company/talk-to-sales) to receive your license key.

These instructions are for you if:

- You want your Self-Managed Enterprise instance to inherit state from your existing deployment.
- You are currently deploying Airbyte on Kubernetes.
- You are comfortable with an in-place upgrade. This guide does not dual-write to a new Airbyte deployment.

### Step 1: Update Airbyte Open Source

You must first update to the latest Open Source Community release. We assume you are running the following steps from the root of the `airbytehq/airbyte-platform` cloned repo.

1. Determine your current helm release name by running `helm list`. This will now be referred to as `[RELEASE_NAME]` for the rest of this guide.
2. Upgrade to the latest Open Source Community release. The output will now be refered to as `[RELEASE_VERSION]` for the rest of this guide:

```sh
helm upgrade [RELEASE_NAME] airbyte/airbyte
```

### Step 2: Configure Self-Managed Enterprise

Update your `values.yml` file as explained in the [Self-Managed Enterprise implementation guide](./implementation-guide.md). Avoid making any changes to your external database or log storage configuration at this time.

### Step 3: Deploy Self-Managed Enterprise

1. You can now run the following command to upgrade your instance to Self-Managed Enterprise. If you previously included additional `values` files on your existing deployment, be sure to add these here as well:

```sh
helm upgrade \
--namespace airbyte \
--values ./values.yaml \
--install [RELEASE_NAME] \
--version [RELEASE_VERSION] \
airbyte/airbyte
```

2. Once this is complete, you will need to upgrade your ingress to include the new `/auth` path. The following is a skimmed down definition of an ingress resource you could use for Self-Managed Enterprise:

<details>
<summary>Configuring your Airbyte ingress</summary>

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: # ingress name, example: enterprise-demo
  annotations:
    ingress.kubernetes.io/ssl-redirect: "false"
spec:
  ingressClassName: nginx
  rules:
    - host: # host, example: enterprise-demo.airbyte.com
      http:
        paths:
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-webapp-svc
                name: airbyte-enterprise-airbyte-webapp-svc
                port:
                  number: 80 # service port, example: 8080
            path: /
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-keycloak-svc
                name: airbyte-enterprise-airbyte-keycloak-svc
                port:
                  number: 8180
            path: /auth
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte--server-svc
                name: airbyte-enterprise-airbyte-server-svc
                port:
                  number: 8001
            path: /api/public
            pathType: Prefix
```

</details>

All set! When you log in, you should expect all connections, sources and destinations to be present, and configured as prior.
