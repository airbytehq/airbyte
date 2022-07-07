# Getting Started

## **What do I need to get started using Airbyte?**

You can deploy Airbyte in several ways, as [documented here](../../deploying-airbyte/README.md). Airbyte will then help you replicate data between a source and a destination. Airbyte offers pre-built connectors for both, you can see their list [here](../../project-overview/changelog/connectors.md). If you don’t see the connector you need, you can [build your connector yourself](../../connector-development) and benefit from Airbyte’s optional scheduling, orchestration and monitoring modules.

## **How long does it take to set up Airbyte?**

It depends on your source and destination. Check our setup guides to see the tasks for your source and destination. Each source and destination also has a list of prerequisites for setup. To make setup faster, get your prerequisites ready before you start to set up your connector. During the setup process, you may need to contact others \(like a database administrator or AWS account owner\) for help, which might slow you down. But if you have access to the connection information, it can take 2 minutes: see [demo video. ](https://www.youtube.com/watch?v=jWVYpUV9vEg)

## **What data sources does Airbyte offer connectors for?**

We already offer 100+ connectors, and will focus all our effort in ramping up the number of connectors and strengthening them. View the [full list here](../../project-overview/changelog/connectors.md). If you don’t see a source you need, you can file a [connector request here](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=area%2Fintegration%2C+new-integration&template=new-integration-request.md&title=).

## **Where can I see my data in Airbyte?**

You can’t see your data in Airbyte, because we don’t store it. The sync loads your data into your destination \(data warehouse, data lake, etc.\). While you can’t see your data directly in Airbyte, you can check your schema and sync status on the source detail page in Airbyte.

## **Can I add multiple destinations?**

Sure, you can. Just go to the "Destinations" section and click on the top right "+ new destination" button. You can have multiple destinations for the same source, and multiple sources for the same destination.

## Am I limited to GUI interaction or is there a way to set up / run / interact with Airbyte programmatically?

You can use the API to do anything you do today from the UI. Though, word of notice, the API is in alpha and may change. You won’t lose any functionality, but you may need to update your code to catch up to any backwards incompatible changes in the API.

## How does Airbyte handle connecting to databases that are behind a firewall / NAT?

We don’t. Airbyte is to be self-hosted in your own private cloud.

## Can I set a start time for my integration?

[Here](../../understanding-airbyte/connections#sync-schedules) is the link to the docs on scheduling syncs.

## **Can I disable analytics in Airbyte?**

Yes, you can control what's sent outside of Airbyte for analytics purposes.

We added the following telemetry to Airbyte to ensure the best experience for users:

* Measure usage of features & connectors
* Measure failure rate of connectors to address bugs quickly
* Reach out to our users about Airbyte community updates if they opt-in
* ...

To disable telemetry, modify the `.env` file and define the two following environment variables:

```text
TRACKING_STRATEGY=logging
```
