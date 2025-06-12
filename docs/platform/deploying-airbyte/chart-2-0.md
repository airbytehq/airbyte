---
products: oss-community, oss-enterprise
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Upgrade to Helm chart 2.0

Airbyte has upgraded its Helm chart to a new version called "2.0." Using Helm chart 2.0 is currently optional. In the future, at a date not yet announced, these new Helm chart will become mandatory. However, you should upgrade your existing Airbyte deployment to use these new Helm charts before they're mandatory. If you're a new Airbyte customer, you can use Helm chart 2.0 from the beginning and avoid the upgrade entirely.

## What's a Helm chart?

Airbyte runs on [Kubernetes](https://kubernetes.io/). [Helm](https://helm.sh/) is a package manager for Kubernetes. A [Helm chart](https://helm.sh/docs/topics/charts/) is a collection of files that describe a related set of Kubernetes resources. Think of Helm charts as the method Airbyte uses to define, install, and manage its Kubernetes application. When you install or upgrade Airbyte, you pull in a specific set of Helm charts representing that version.

## Why you should upgrade

Upgrading to the new Helm charts now has several benefits.

1. By upgrading in advance, you can schedule this upgrade for a convenient time, and avoid blocking yourself from upgrading to a future version of Airbyte that requires the new Helm charts when you're too busy to convert.

2. The new Helm charts don't require [Keycloak](https://www.keycloak.org/). If you don't want to use Keycloak for authentication, or want to use generic OIDC, you must run the new Helm charts.

3. The new Helm charts are compliant with Helm's best practices for chart design.

4. The new Helm charts have broader and more detailed options to customize your deployment. In most cases, it's no longer necessary to specify environment variables in your `values.yaml` file because the chart offers a more detailed interface for customizaton. If you do need to use environment variables, you probably don't need many.

## Which versions can upgrade to Helm chart 2.0

Airbyte version 1.6.0 and later can use the new Helm charts.

## How to upgrade

In most cases, upgrading is straightforward. To upgrade to Helm charts V2, you'll complete the following steps.

1. Before upgrading, ensure you have configured and deployed Airbyte with an external database, external bucket storage, and external secrets manager. This is absolutely critical to avoid the possibility of losing data, logs, and connection secrets.

2. Prepare to deploy a fresh installation of Airbyte.

3. Update your `values.yaml` file.

4. Deploy a new version of Airbyte using your new `values.yaml` file, and using your existing external database, external bucket storage, and external secrets manager.

### Configure external database, bucket storage, and secrets manager

:::danger
Don't skip this step. This is critical to avoid the possibility of losing data, logs, and connection secrets.
:::

Although Airbyte provides its own basic database, storage, and secrets management, most people opt to use their own. If you don't already do this, you must enable these before migrating.

- [Configure an external database](integrations/database)
- [Configure external storage](integrations/storage)
- [Configure external secrets](integrations/secrets)

<!-- Is a deployment necessary here to activate? Anything specific that needs to be done. -->

### Prepare a fresh deployment of Airbyte

<!-- Need to research more and elaborate what exactly we mean when we say this -->

### Add the Helm chart 2.0 repo

While Helm chart 2.0 is optional, it uses a different repo while it's usage is optional. For now, add it separately.

```bash
helm repo add airbyte-v2 https://airbytehq.github.io/charts
```

### Update your values.yaml file

The majority of the work when you migrate to the 2.0 chart involves making adjustments to your existing `values.yaml` file. In most cases, the adjustments are small and involve changing keys and moving sections.

This section walks you through the main updates you need to make. If you already know what to do, see [Values.yaml reference](values) to compare the interfaces in full.

#### Main differences

- **Global configuration**: Helm chart 2.0 has a more feature-rich `global` section, so you define common settings like database, storage, and auth once and can reference them later. Helm chart 2.0 renames or restructures some components to support this design.

- **Multiple cluster support**: Helm chart 2.0 adds support for different cluster types: hybrid, control plane, and data planes.

- **Authentication and security**: Configurable generic OIDC integration, and security settings for cookies and JWT

- **Secrets management**: Comprehensive secrets management with support for multiple backends: Valut, AWS< GCP, and Azure.

- **Storage backend flexibility**: Multiple storage backend support (S3, GCS, Azure, Minio), separate bucket configuration for different data types, and component changes

- **New components**: `workloadLauncher` to manage Kubernetes pod lifecycle, `connectorRolloutWorker` to handle connector version updates, `workloadApiServer` for API workload management, `featureflagServer` for feature flag management, and `keycloak` and `keycloakSetup` for identity management.

#### Migration tips

Airbyte recommends approaching this project in this way:

1. Document the customizations in your v1 `values.yaml` file so you don't forget anything.

2. Start with a basic v2 `values.yaml` and verify that it works, and expand it later.

3. Map your v1 settings to v2, transferring one set of configurations at a time.

4. Use Helm template validation before applying changes. For example, `helm template -f your-v2-values.yaml airbyte/airbyte`.

5. Test in a non-production environment before deploying to production.

#### How to approach this project

Everyone has a slightly different configuration, so it's impossible to prescribe an exact migration path. However, for most people, upgrading your `values.yaml` generally follows this pattern:

1. Move shared settings to the global section

2. If you're using authentication, configure the new auth system

3. Update storage configuration to use the new structure

4. Update database settings to use the global configuration

5. Update component configurations to match the new structure

6. If you're using audit logging, configure the new audit logging system

Depending on your configuration and priorities, you may need or want to adjust the following.

1. Consider using the new secrets management system

2. Configure workload resources and scheduling

3. Set up enhanced metrics collection

#### Create a `global` configuration

Create your basic global configuration.

<Tabs groupId="product">
<TabItem value="enterprise" label="Self-Managed Enterprise">

```yaml
global:
  edition: enterprise

  enterprise:
    secretName: "" # Secret name where an Airbyte license key is stored
    licenseKeySecretKey: "" # The key within `licenseKeySecretName` where the Airbyte license key is stored

  airbyteUrl: "" # The URL where Airbyte will be reached; This should match your Ingress host
```

</TabItem>
<TabItem value="community" label="Self-Managed Community">

```yaml
global:
  edition: community

  airbyteUrl: "" # The URL where Airbyte will be reached; This should match your Ingress host
```

</TabItem>
</Tabs>

#### Add `auth` and single sign on

Self-Managed Enterprise customers can implement single sign on (SSO) with OIDC or new generic OIDC.

<Tabs groupId="product">
<TabItem value="enterprise" label="Self-Managed Enterprise">

```yaml
global:

  auth:

    enabled: true # Set to false if you're not ready to turn this on yet

    # -- Admin user configuration
    instanceAdmin:
      firstName: ""
      lastName:  ""
      emailSecretKey: "" # The key within `emailSecretName` where the initial user's email is stored
      passwordSecretKey: "" # The key within `passwordSecretName` where the initial user's password is stored

        # -- SSO Identify Provider configuration; (requires Enterprise)
        identityProvider:
            secretName: "" # Secret name where the OIDC configuration is stored
            type: "" # The identity provider type, must be one of: "oidc" or "generic-oidc"

            # Implement EITHER oidc or genericOidc but not both

            ## OPTION 1
            # -- OIDC configuration (required if `auth.identityProvider.type` is "oidc")
            oidc:
              # -- OIDC application domain
              domain: ""
              # -- OIDC application name
              appName: ""
              # -- The key within `clientIdSecretName` where the OIDC client id is stored
              clientIdSecretKey: ""
              # -- The key within `clientSecretSecretName` where the OIDC client secret is stored
              clientSecretSecretKey: ""

            ## OPTION 2
            # -- Generic OIDC configuration (required if `auth.identityProvider.type` is "generic-oidc")
            genericOidc:
              clientId: ""
              audience: ""
              issuer: ""
              endpoints:
                authorizationServerEndpoint: ""
                jwksEndpoint: ""
              fields:
                subject: sub
                email: email
                name: name
                issuer: iss
```

For more help implementing generic OIDC, see [TODO](#).

</TabItem>
<TabItem value="community" label="Self-Managed Community">

```yaml
# Not applicable
```

</TabItem>
</Tabs>

### Redeploy Airbyte

Here is an example of how to deploy version 1.6.2 of Airbyte using the latest Helm chart 2.0 values. Normally the Helm chart version is identical to the Airbyte version. Since using this chart version is optional, the Helm chart and Airbyte have different, but compatible, versions.

```bash
helm upgrade -i \
--namespace airbyte \
--values ./values.yaml \
airbyte \
airbyte-v2/airbyte \
--version 2.0.3 \
--set global.image.tag=1.6.2
```
