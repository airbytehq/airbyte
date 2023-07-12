# Planhat Analytics

This page guides you through the process of setting up the Planhat destination connector for analytics.

Get started with Planhat at the [Planhat website](https://www.planhat.com/).

See your data on the [Planhat dashboard](https://app.planhat.com/developer).

## Overview

The Planhat destination connector supports the Append Sync. The connector uses the bulk upsert endpoints. 

## Prerequisites

This Planhat Analytics destination connector has two endpoints:

1. **Metrics**: Dimension Data is a set of model level metrics (Company by default) to understand how well your customers are doing, and the value they get out of your service.Requires an API Token.
2. **User Activities**: Keeping track of your endusers activity

Airbyte automatically picks an approach depending on the given configuration.

Parameters: 
* **Token UUID**
  * To get your Tenant UUID please visit the [Developer](https://app.planhat.com/developer) section in Planhat App.
* **Batch size** (optional)
  * The number of records you want to send at the same time. Minimum: 1, Maximum: 100 000 , Default: 10 000

For Metrics endpoint:
* **Api Token**
  * See [this](https://docs.planhat.com/#authentication) to create an api token



## Connector-specific features & highlights

### Input schema 

Planhat supports to endpoint which need specific schema: 

* **[Metrics endpoint](https://docs.planhat.com/#metrics)** :
  * **dimensionId (required)**: name of the event (Any string without spaces or special characters)
  * **value (required)**: the value of the event
  * **externalId (required)**: the model external id in your systems, which the event will be associated
  * **model**: the model in Planhat, which the event will be associated. Default: Company
  * **date**: the date of the event in a valid ISO format date string. Default: Use the time the request was received

* **[User activities](https://docs.planhat.com/#activity_bulk)**
  * **email (required)**: the email of the user
  * **euExtId (required if email not specified )**: the user external id in your systems
  * **action**: name of the event
  * **count**: the value of the event


### Output schema

Each steam will be output in the platform [here](https://app.planhat.com/data/metrics), in :
* custom metrics section for Metrics endpoint
* user activities section for User Activities endpoint

The Planhat API enables all records to be sent, even if some fields are incorrect. 
In the logs, you'll be able to see how many records have been sent correctly and how many have been sent with errors. Likewise, on Planhat, you can find incorrect records by going to *Data > Metrics > Review > Failed Metrics*.

Logs example : 

```bash 
{"processed":1,"errors":[{"item":{"value":1,"externalId":"my_id","model":"Company"},"error":"dimensionId must be specified"}]} 
```

## Changelog

| Version | Date       | Pull Request                                           | Subject                    |
| :------ | :--------- | :----------------------------------------------------- | :------------------------- |
| 0.1.0   | 2023-07-11 | [XXXX](https://github.com/airbytehq/airbyte/pull/XXXX) | 🎉 New Destination: Planhat |
