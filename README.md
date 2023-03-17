<p align="center">
  <a href="https://airbyte.com"><img src="https://assets.website-files.com/605e01bc25f7e19a82e74788/624d9c4a375a55100be6b257_Airbyte_logo_color_dark.svg" alt="Airbyte"></a>
</p>
<p align="center">
    <em>Data integration platform for ELT pipelines from APIs, databases & files to databases, warehouses & lakes</em>
</p>
<p align="center">
<a href="https://github.com/airbytehq/airbyte/stargazers/" target="_blank">
    <img src="https://img.shields.io/github/stars/airbytehq/airbyte?style=social&label=Star&maxAge=2592000" alt="Test">
</a>
<a href="https://github.com/airbytehq/airbyte/releases" target="_blank">
    <img src="https://img.shields.io/github/v/release/airbytehq/airbyte?color=white" alt="Release">
</a>
<a href="https://airbytehq.slack.com/" target="_blank">
    <img src="https://img.shields.io/badge/slack-join-white.svg?logo=slack" alt="Slack">
</a>
<a href="https://www.youtube.com/c/AirbyteHQ/?sub_confirmation=1" target="_blank">
    <img alt="YouTube Channel Views" src="https://img.shields.io/youtube/channel/views/UCQ_JWEFzs1_INqdhIO3kmrw?style=social">
</a>
<a href="https://github.com/airbytehq/airbyte/actions/workflows/gradle.yml" target="_blank">
    <img src="https://img.shields.io/github/actions/workflow/status/airbytehq/airbyte/gradle.yml?branch=master" alt="Build">
</a>
<a href="https://github.com/airbytehq/airbyte/tree/master/docs/project-overview/licenses" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white" alt="License">
</a>
<a href="https://github.com/airbytehq/airbyte/tree/master/docs/project-overview/licenses" target="_blank">
    <img src="https://img.shields.io/static/v1?label=license&message=ELv2&color=white" alt="License">
</a>
</p>

We believe that only an **open-source** solution to data movement can cover the **long tail of data sources** while empowering data engineers to **customize existing connectors**. Our ultimate vision is to help you move data from any source to any destination. Airbyte already provides [300+ connectors](https://docs.airbyte.com/integrations/) for popular APIs, databases, data warehouses and data lakes.

Airbyte connectors can be implemented in any language and take the form of a Docker image that follows the [Airbyte specification](https://docs.airbyte.com/understanding-airbyte/airbyte-protocol/). You can create new connectors very fast with:
 - The [low-code Connector Development Kit](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview) (CDK) for API connectors ([demo](https://www.youtube.com/watch?v=i7VSL2bDvmw))
 - The [Python CDK](https://docs.airbyte.com/connector-development/cdk-python/) ([tutorial](https://docs.airbyte.com/connector-development/tutorials/cdk-speedrun))

Airbyte has a built-in scheduler and uses [Temporal](https://airbyte.com/blog/scale-workflow-orchestration-with-temporal) to orchestrate jobs and ensure reliability at scale. Airbyte leverages [dbt](https://www.youtube.com/watch?v=saXwh6SpeHA) to normalize extracted data and can trigger custom transformations in SQL and dbt. You can also orchestrate Airbyte syncs with [Airflow](https://docs.airbyte.com/operator-guides/using-the-airflow-airbyte-operator), [Prefect](https://docs.airbyte.com/operator-guides/using-prefect-task) or [Dagster](https://docs.airbyte.com/operator-guides/using-dagster-integration).

![Airbyte OSS Connections UI](https://user-images.githubusercontent.com/2302748/205949986-5207ca24-f1f0-41b1-97e1-a0745a0de55a.png)

Explore our [demo app](https://demo.airbyte.io/).

## Quick start

### Run Airbyte locally

You can run Airbyte locally with Docker.

```bash
git clone https://github.com/airbytehq/airbyte.git
cd airbyte
docker compose up
```

## Disaster Recovery:

### How to restart the Service:

If the Airbyte service is down and we need to start it up again. Follow the next steps

1. Destroy the current AirbyteStack and create another one from scrath:
    1. Go to the infrastructure repo and cd to `infrastructure/stacks/data_platform`
    2. Destroy the current stack: `cdk destroy --exclusively AirbyteStack --context config=datascience`
    3. Recreate the the stack: `cdk deploy --exclusively AirbyteStack --context config=datascience`
2. Go to the EC2 instance and copy the Public IPv4 DNS of the recently created EC2 instance.
3. Paste the IPv4 DNS in the SERVER variable in the Makefile in the root of this repo.
4. Make sure that you have the `airyte.pem` key in your ssh folder.
5. From the root of this repo run `make disaster_recovery`. It will take some minutes to run all the commands.
6. From the root of this repo run `make forward_ec2_port`. Now the Airbyte instance shoudl be accesible in `http://localhost:8000/`.
7. Now it is time deploy the Sources, Destinations and Connections. For that we will use Octavia.
    1. We need to store the passwords as secrets in the Octavia config file (~/.octavia)
        a. From the root of this repo run `make store_passwords`. You need to have the AWS credentials for the Data Science prod Account to run this command. As it gets the passwords from AWS Secret Manager.
    2. From the root of this repo run `make octavia_apply`. Once it is done, go to the Airbyte UI and enable all the connections.
8. Remember to go to `data-airflow` repo and change the connection Ids in the data_replication_airbyte_qogita_db_public_to_snowflake_raw and data_replication_airbyte_revenue_db_public_to_snowflake_raw DAGs
