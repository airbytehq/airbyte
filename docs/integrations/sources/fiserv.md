# Fiserv

This documentation provides details on setting up Fiserv source connector with Airbyte. 

## Set up the Fiserv connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Select **Sources** and then choose **+ New source**.
3. On the Set up the source page, click **Fiserv** from the dropdown list of source types.
4. Assign a unique name to your source
5. For **API token**, enter the API token for your Fiserv account. You can find your API token in your Fiserv Account > Click on your avatar > User Settings > API.
6. For **Start date**, enter the date in YYYY-MM-DD format. The data added on and after this date will be replicated.
7. Click **Set up source**.

## Supported sync modes

The Fiserv source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

 - Full Refresh | Overwrite
 - Incremental | Append 

## Supported Streams

The Fiserv source connector supports the following streams, some of them may need elevated permissions:

* [Chargeback](https://developer.fiserv.com/product/Reporting/api/?type=post&path=/v1/chargeback/search&branch=main&version=1.0.0) \(Incremental\)
* [Disbursement](https://developer.fiserv.com/product/Reporting/api/?type=post&path=/v1/disbursement/search&branch=main&version=1.0.0) \(Incremental\)
* [Funding](https://developer.fiserv.com/product/Reporting/api/?type=post&path=/v1/funding/search&branch=main&version=1.0.0) \(Incremental\)
* [Commercehub](https://developer.fiserv.com/product/Reporting/api/?type=post&path=/v1/commercehub/search&branch=main&version=1.0.0) \(Incremental\)
* [Bin](https://developer.fiserv.com/product/Reporting/api/?type=post&path=/v1/reference/bins/search&branch=main&version=1.0.0) \(Full table\)
* [Retrieval](https://developer.fiserv.com/product/Reporting/api/?type=post&path=/v1/retrieval/search&branch=main&version=1.0.0) \(Incremental\)
* [Sites](https://developer.fiserv.com/product/Reporting/api/?type=post&path=/v1/reference/sites/search&branch=main&version=1.0.0) \(Full table\)
* [Settlement](https://developer.fiserv.com/product/Reporting/api/?type=post&path=/v1/settlement/search&branch=main&version=1.0.0) \(Incremental\)
* [Transactions](https://developer.fiserv.com/product/Reporting/api/?type=post&path=/v1/prepaid/transactions/search&branch=main&version=1.0.0) \(Incremental\)

## Performance Considerations 

* To handle streams with large volumes of data, we implemented a hierarchical structure using stream inheritance. We designed the Bin stream to inherit from Chargeback, Settlement, and Retrieval streams which we were able to pull data in smaller, manageable batches rather than single large pull.