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

You must first update to the latest Open Source community release. We assume you are running the following steps from the root of the `airbytehq/airbyte-platform` cloned repo.

1. Determine your current helm release name by running `helm list`. This will now be referred to as `[RELEASE_NAME]` for the rest of this guide.
2. Upgrade to the latest Open Source community release. The output will now be refered to as `[RELEASE_VERSION]` for the rest of this guide:

```sh
helm upgrade [RELEASE_NAME] airbyte/airbyte
```

### Step 2: Configure Self-Managed Enterprise

At this step, please create and fill out the `airbyte.yml` as explained in the [Self-Managed Enterprise implementation guide](./implementation-guide.md#clone--configure-airbyte) in the `configs` directory. You should avoid making any changes to your Airbyte database or log storage at this time. When complete, you should have a completed file matching the following skeleton:

<details>
<summary>Configuring your airbyte.yml file</summary>

```yml
webapp-url: # example: localhost:8080

initial-user:
  email:
  first-name:
  last-name:
  username: # your existing Airbyte instance username
  password: # your existing Airbyte instance password

license-key:

auth:
  identity-providers:
    - type: okta
      domain:
      app-name:
      client-id:
      client-secret:
```

</details>

### Step 3: Deploy Self-Managed Enterprise

1. You can now run the following command to upgrade your instance to Self-Managed Enterprise. If you previously included additional `values` files on your existing deployment, be sure to add these here as well:

```sh
helm upgrade [RELEASE_NAME] airbyte/airbyte \
--version [RELEASE_VERSION] \
--set-file airbyteYml=./configs/airbyte.yml \
--values ./charts/airbyte/airbyte-pro-values.yaml [... additional --values]
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
  rules:
    - host: # host, example: enterprise-demo.airbyte.com
      http:
        paths:
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-webapp-svc
                name: airbyte-pro-airbyte-webapp-svc
                port:
                  number: # service port, example: 8080
            path: /
            pathType: Prefix
          - backend:
              service:
                # format is ${RELEASE_NAME}-airbyte-keycloak-svc
                name: airbyte-pro-airbyte-keycloak-svc
                port:
                  number: # service port, example: 8180
            path: /auth
            pathType: Prefix
```

</details>

All set! When you log in, you should expect all connections, sources and destinations to be present, and configured as prior.
