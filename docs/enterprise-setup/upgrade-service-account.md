---
products: oss-enterprise
---

# Update service account for 1.6

Airbyte version 1.6 introduced a breaking change for service account permissions. If you're a Self-Managed Enterprise customer upgrading from 1.5.1 or earlier to 1.6 or later, follow the directions in this article before you upgrade to 1.6. If you're a Self-Managed Community user, this information isn't relevant to you.

## Upgrading without updating service account permissions

If you try to upgrade from 1.5.1 or earlier to 1.6 or later without updating your service account permissions, you see the following error.

```bash
2025-04-08 21:40:25,960 [main]  INFO    i.a.b.Bootloader(load):73 - Initializing auth secrets...
2025-04-08 21:40:26,880 [main]  ERROR   i.a.b.ApplicationKt(main):28 - Unable to bootstrap Airbyte environment.
java.lang.IllegalStateException: Upgrade to version AirbyteVersion{version='1.6.0-alpha-35dc75a5941', major='1', minor='6', patch='0'} failed. As of version 1.6 of the Airbyte Platform, we require your Service Account permissions to include access to the "secrets" resource. To learn more, please visit our documentation page at https://docs.airbyte.com/enterprise-setup/upgrade-service-account.
        at io.airbyte.bootloader.AuthKubernetesSecretInitializer.checkAccessToSecrets(AuthKubernetesSecretInitializer.kt:57)
        at io.airbyte.bootloader.Bootloader.load(Bootloader.kt:74)
        at io.airbyte.bootloader.ApplicationKt.main(Application.kt:25)
```

Airbyte does not begin the upgrade process, and you can continue using your old version until you're ready to update permissions.

<!-- Do we need to undo anything locally, or does this fail gracefully? -->

## Update permissions and begin the upgrade

Follow the steps below to update your service account permissions.

<!-- Alex says it's not values.yaml change, we need to change the actual service acount. What happens if they're using the default Airbyte service worker? -->

1. Update your `values.yaml` file.

    ```yaml

    ```

2. Use the updated `values.yaml` file to upgrade Airbyte.

    ```bash
    helm upgrade \
    --namespace airbyte \
    --values ./values.yaml \
    --install airbyte-enterprise \
    airbyte/airbyte
    ```
