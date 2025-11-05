---
products: oss-community
---

# Migrating from Docker Compose

<!-- This topic has been preserved from the original Quickstart guide, unchanged. It may be used later in rewritten deployment docs. -->

:::note

If you're using an external database or secret manager you don't need to run `--migrate` flag.
You must create the `secrets.yaml` and `values.yaml` and then run `abctl local install --values ./values.yaml --secret ./secrets.yaml`.
Please check [instructions](integrations/database.md) to setup the external database as example.

:::

If you have data that you would like to migrate from an existing docker compose instance follow the steps below:

1. Make sure that you have stopped the instance running in docker compose, this may require the following command:

```
docker compose stop
```

2. Make sure that you have the latest version of abctl by running the following command:

```
curl -LsfS https://get.airbyte.com | bash -
```

3. Run abctl with the migrate flag set with the following command:

```
abctl local install --migrate
```

:::note

If you're using a version of Airbyte that you've installed with `abctl`, you can find instructions on upgrading your Airbyte installation [here](../operator-guides/upgrading-airbyte.md#upgrading-with-abctl).

:::