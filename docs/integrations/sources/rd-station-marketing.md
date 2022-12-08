# RD Station Marketing

RD Station Marketing is the leading Marketing Automation tool in Latin America. It is a software application that helps your company carry out better campaigns, nurture Leads, generate qualified business opportunities and achieve more results. From social media to email, Landing Pages, Pop-ups, even Automations and Analytics.

## Prerequisites
* An RD Station account
* A callback URL to receive the first account credential (can be done using localhost)
* `client_id` and `client_secret` credentials. Access [this link](https://appstore.rdstation.com/en/publisher) to register a new application and start the authentication flow. 

## Airbyte Open Source
* Start Date
* Client Id
* Client Secret
* Refresh token

## Supported sync modes

The RD Station Marketing source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):
 - Full Refresh
 - Incremental (for analytics endpoints)

## Supported Streams

* conversions (analytics endpoint)
* emails (analytics endpoint)
* funnel (analytics endpoint)
* workflow_emails_statistics (analytics endpoint)
* emails
* embeddables
* fields
* landing_pages
* popups
* segmentations
* workflows

## Performance considerations

Each endpoint has its own performance limitations, which also consider the account plan. For more informations, visit the page [API request limit](https://developers.rdstation.com/reference/limite-de-requisicoes-da-api?lng=en).

## Changelog

| Version | Date       | Pull Request                                             | Subject                                                         |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------------- |
| 0.1.1   | 2022-11-01 | [18826](https://github.com/airbytehq/airbyte/pull/18826) | Fix stream analytics_conversions                                |
| 0.1.0   | 2022-10-23 | [18348](https://github.com/airbytehq/airbyte/pull/18348) | Initial Release                                                 |
