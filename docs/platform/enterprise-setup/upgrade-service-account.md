---
products: oss-enterprise
---

# Update service account for 1.6

Airbyte version 1.6 introduced a breaking change for service account permissions. If you're a Self-Managed Enterprise customer upgrading from 1.5.1 or earlier to 1.6 or later, follow the directions in this article before you upgrade to 1.6. If you're a Self-Managed Community user, this information isn't relevant to you. [Learn more about service accounts](https://kubernetes.io/docs/concepts/security/service-accounts/).

## Upgrading without updating service account permissions

If you try to upgrade from 1.5.1 or earlier to 1.6 or later without updating your service account permissions, the Bootloader pod fails and you see the following error in the logs.

```bash
2025-04-08 21:40:25,960 [main]  INFO    i.a.b.Bootloader(load):73 - Initializing auth secrets...
2025-04-08 21:40:26,880 [main]  ERROR   i.a.b.ApplicationKt(main):28 - Unable to bootstrap Airbyte environment.
java.lang.IllegalStateException: Upgrade to version AirbyteVersion{version='1.6.0-alpha-35dc75a5941', major='1', minor='6', patch='0'} failed. As of version 1.6 of the Airbyte Platform, we require your Service Account permissions to include access to the "secrets" resource. To learn more, please visit our documentation page at https://docs.airbyte.com/enterprise-setup/upgrade-service-account.
        at io.airbyte.bootloader.AuthKubernetesSecretInitializer.checkAccessToSecrets(AuthKubernetesSecretInitializer.kt:57)
        at io.airbyte.bootloader.Bootloader.load(Bootloader.kt:74)
        at io.airbyte.bootloader.ApplicationKt.main(Application.kt:25)
```

Airbyte doesn't begin the upgrade process, and you can continue using your old version until you're ready to update permissions. Until you do, the Bootloader pod shows that it's in a failed state, but this doesn't prevent Airbyte from working.

## Update permissions and begin the upgrade

The process you follow depends on whether you're using Airbyte's default service account or your own.

### Which one you're using

If you've defined a service account in the `values.yaml` file you use to deploy Airbyte, you're using your own.

```yaml title="values.yaml"
serviceAccount:
  name:
```

If you haven't, you're using Airbyte's default service account, `airbyte-sa`.

### Using Airbyte's default service account

1. Run the following kubectl command.

    ```bash
    kubectl -n <namespace> patch role airbyte-admin-role --type='json' -p='[{"op": "replace", "path": "/rules/0/resources", "value": ["jobs", "pods", "pods/log", "pods/exec", "pods/attach", "secrets"]}]'
    ```

2. Upgrade Airbyte as you normally would.

### Using your own service account

1. Upgrade your service account/role to grant it **secrets** access. The role should look approximately like this:

    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      name: roleName    app.kubernetes.io/managed-by: Helm
      annotations:
        helm.sh/hook: pre-install
        helm.sh/hook-weight: "-5"
    rules:
      - apiGroups: ["*"]
      //highlight-next-line
        resources: ["jobs", "pods", "pods/log", "pods/exec", "pods/attach", "secrets"]
        verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
    ```

2. Upgrade Airbyte as your normally would.
