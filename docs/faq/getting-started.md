# Getting Started

## **What do I need to get started using Airbyte?**

You can deploy Airbyte in several ways, as [documented here](../deploying-airbyte/). Airbyte will then help you replicate data between a source and a destination. Airbyte offers pre-built connectors for both, you can see their list [here](../changelog/connectors.md). If you don’t see the connector you need, you can [build your connector yourself](../contributing-to-airbyte/building-new-connector/) and benefit from Airbyte’s optional scheduling, orchestration and monitoring modules.

## **How long does it take to set up Airbyte?**

It depends on your source and destination. Check our setup guides to see the tasks for your source and destination. Each source and destination also has a list of prerequisites for setup. To make setup faster, get your prerequisites ready before you start to set up your connector. During the setup process, you may need to contact others \(like a database administrator or AWS account owner\) for help, which might slow you down. But if you have access to the connection information, it can take 2 minutes: see [demo video. ](https://www.youtube.com/watch?v=jWVYpUV9vEg)

## **What data sources does Airbyte offer connectors for?**

We already offer 50+ connectors, and will focus all our effort in ramping up the number of connectors and strengthening them. View the [full list here](../changelog/connectors.md). If you don’t see a source you need, you can file a [connector request here](https://github.com/airbytehq/airbyte/issues/new?assignees=&labels=area%2Fintegration%2C+new-integration&template=new-integration-request.md&title=).

## **Where can I see my data in Airbyte?**

You can’t see your data in Airbyte, because we don’t store it. The sync loads your data into your destination \(data warehouse, data lake, etc.\). While you can’t see your data directly in Airbyte, you can check your schema and sync status on the source detail page in Airbyte.

## **Can I add multiple destinations?**

Sure, you can. Just go to the "Destinations" section and click on the top right "+ new destination" button. You can have multiple destinations for the same source, and multiple sources for the same destination.

