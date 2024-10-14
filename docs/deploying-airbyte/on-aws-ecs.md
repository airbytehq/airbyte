# On AWS ECS (Coming Soon)

:::warning
This page is deprecated as of October 2023. To deploy Airbyte, refer to our [Deployment Guide](./deploying-airbyte.md).
:::

:::info
We do not currently support deployment on ECS.
:::

The current iteration is not compatible with ECS.
Airbyte currently relies on docker containers being able to create other docker containers.
ECS does not permit containers to do this. We will be revising this strategy soon,
so that we can be compatible with ECS and other container services.
