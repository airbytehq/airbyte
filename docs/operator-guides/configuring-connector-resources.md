---
products: oss-*
---

# Configuring Connector Resources

There are four types of jobs in Airbyte.

- Sync
- Check
- Discover
- Spec

It is possible to configure resources for all four jobs, but this article focuses on Sync jobs as it's the most frequently run job and typically the one you want to configure.

There are four different ways to configure connector resource requirements for a sync. The narrower in scope the configuration, the higher the precedence.

| Configuration type   | Description                                                               | Precedence     | Overrides                           | Overridden by                           |
| -------------------- | ------------------------------------------------------------------------- | -------------- | ----------------------------------- | --------------------------------------- |
| Instance-wide        | Applies to all containers.                                                | Lowest         | Nothing                             | All others                              |
| Connector definition | Applies to all connectors of that type (for example, all Stripe sources). | Second-lowest  | Instance-wide                       | Connector-specific, connection-specific |
| Connector-specific   | Applies to one connector (for example, only _this_ Stripe source).          | Second-highest | Instance-wide, connector definition | Connection-specific                     |
| Connection-specific  | Applies to this connection only (i.e. only _this_ source/destination combination).                                          | Highest        | All others                          | Nothing                                 |

## Best Practices for Allocating Resources

Follow these best practices to minimize resource issues.

### Configuration Hierarchy

Start with the lowest-precedence configuration that's appropriate, then override that with more specific configurations as needed.

- Set instance-wide configurations if Airbyte's default is unsuitable for you
- Use connector definition configurations when possible
- Use connector-specific configurations only when necessary
- Apply connection-specific configurations for exceptional cases

We recommend that you start with the default resource allocations set by Airbyte. These should be sufficient for most use cases.

If you have an issue that you suspect is due to insufficient resources, you should be able to confirm it via observability tools (e.g. Airbyte-provided [logs](#debugging)). If these indicate that there's an issue with CPU or memory, start by upgrading resource profiles only for connectors that need it. Upgrade resource profiles for specific connections as a last resort.

## Configuring Instance-Wide Requirements

Instance-wide requirements affect all job containers that you don't override some other way. Set the following variables in your `values.yaml` file.

1. `JOB_MAIN_CONTAINER_CPU_REQUEST` - Define the job container's minimum CPU usage. Defaults to none.
2. `JOB_MAIN_CONTAINER_CPU_LIMIT` - Define the job container's maximum CPU usage. Defaults to none.
3. `JOB_MAIN_CONTAINER_MEMORY_REQUEST` - Define the job container's minimum RAM usage. Defaults to none.
4. `JOB_MAIN_CONTAINER_MEMORY_LIMIT` - Define the job container's maximum RAM usage. Defaults to none.

## Configuring Connector Definition Requirements

You can use SQL to configure connector definitions, affecting all connectors of that type.

1. Connect to the database and run the following query with the image name replaced to find the connector definition id.

   ```sql
   select * from actor_definition where actor_definition.docker_repository like '%<image-name>';
   ```

2. Run the following commend with the resource requirements and the connection definition id filled in.

   ```sql
   update actor_definition set resource_requirements = '{"jobSpecific": [{"jobType": "sync", "resourceRequirements": {"cpu_limit": "0.5", "cpu_request": "0.5", "memory_limit": "500Mi", "memory_request": "500Mi"}}]}' where id = '<id-from-step-1>';
   ```

## Configuring Connector-Specific Requirements

Self-Managed Enterprise customers can configure resource allocation through the "Connector resource allocation" dropdown in the Settings tab for each connector. You can also configure this with the API. This option isn't available for Self-Managed Community users.

The available profiles depend on the connector type. Specific resource requirements and options vary by connector. As a general rule, resource allocations look something like this.

API Connectors:

- Default: 1 CPU, 2 GB
- Large: 2 CPU, 3 GB
- Memory Intensive: 2 CPU, 6 GB
- Maximum: 4 CPU, 8 GB

Database Connectors:

- Default: 2 CPU, 2 GB
- Large: 3 CPU, 3 GB
- Memory Intensive: 3 CPU, 6 GB
- Maximum: 4 CPU, 8 GB

## Configuring Connection-Specific Requirements

1. Navigate to the connection in the Airbyte UI and extract the connection id from the url. 

   - The URL format is `<base_url>/workspaces/<workspace-id>/connections/<connection-id>/status`. So, if the url is `localhost:8000/workspaces/92ad8c0e-d204-4bb4-9c9e-30fe25614eee/connections/5432b428-b04a-4562-a12b-21c7b9e8b63a/status`,
      the connection id is `5432b428-b04a-4562-a12b-21c7b9e8b63a`.

2. Connect to the database and run the following command with the connection id and resource requirements filled in.

```sql
// SQL command with example
update connection set resource_requirements = '{"cpu_limit": "0.5", "cpu_request": "0.5", "memory_limit": "500Mi", "memory_request": "500Mi"}' where id = '<id-from-step-1>';
```

## Debugging Connection Resources {#debugging}

Airbyte logs the resource requirements as part of the job logs as containers are created. Both source and destination containers are logged.

If a job is running out-of-memory, simply navigate to the Job in the UI, and look for the log to confirm the right configuration is being detected. The log will look something like this:

```
2024-10-28 23:58:10 platform > Launching replication pod: replication-job-20154943-attempt-0 with containers:
2024-10-28 23:58:10 platform > [source] image: airbyte/source-sftp:1.2.0-dev.54744ff04b resources: ResourceRequirements(claims=[], limits={memory=2Gi, ephemeral-storage=5G, cpu=1}, requests={memory=1Gi, ephemeral-storage=5G, cpu=0.5}, additionalProperties={})
2024-10-28 23:58:10 platform > [destination] image: airbyte/destination-s3:1.4.0-dev.6b9d2e4595 resources: ResourceRequirements(claims=[], limits={memory=2Gi, cpu=1}, requests={memory=2Gi, cpu=0.5}, additionalProperties={})
2024-10-28 23:58:10 platform > [orchestrator] image: airbyte/container-orchestrator:build-256f73c6c2-20488-master resources: ResourceRequirements(claims=[], limits={memory=2Gi, cpu=1}, requests={memory=2Gi, cpu=1}, additionalProperties={})
```
