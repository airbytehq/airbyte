
## Base streams

Audience project is a REST based API. Connector is implemented with the [Airbyte Low-Code CDK](https://docs.airbyte.com/connector-development/config-based/low-code-cdk-overview/)

Connector has base streams that includes campaigns.
* [Campaigns](https://docs.audiencereport.com/audiencereport-api/?_gl=1*125uuoe*_ga*MTM3NTgzMDE0Ni4xNjkzMzE2MjE5*_ga_NC5YHF857R*MTY5MzMxNjIxOS4xLjAuMTY5MzMxNjIxOS4wLjAuMA..#api-Campaign-GetCampaigns)


## Report streams

Connector also has report streams including statistics about entities (e.g: how many spending on a campaign, how many clicks on a keyword, etc...).

* [Reports](https://docs.audiencereport.com/audiencereport-api/?_gl=1*125uuoe*_ga*MTM3NTgzMDE0Ni4xNjkzMzE2MjE5*_ga_NC5YHF857R*MTY5MzMxNjIxOS4xLjAuMTY5MzMxNjIxOS4wLjAuMA..#api-Report-GetReport)

## Reach streams

Connector also has reach streams, that retrieves reach data for a campaign report.

* [Reach](https://docs.audiencereport.com/audiencereport-api/?_gl=1*125uuoe*_ga*MTM3NTgzMDE0Ni4xNjkzMzE2MjE5*_ga_NC5YHF857R*MTY5MzMxNjIxOS4xLjAuMTY5MzMxNjIxOS4wLjAuMA..#api-Report-GetReach)

## Profiles streams

Connector also has profiles streams, that retrieves profile data for a campaign report.

* [Reach](https://docs.audiencereport.com/audiencereport-api/?_gl=1*125uuoe*_ga*MTM3NTgzMDE0Ni4xNjkzMzE2MjE5*_ga_NC5YHF857R*MTY5MzMxNjIxOS4xLjAuMTY5MzMxNjIxOS4wLjAuMA..#api-Report-GetProfile)

## Events streams

Connector also has profiles streams, that retrieves events data for a campaign report.

* [Reach](https://docs.audiencereport.com/audiencereport-api/?_gl=1*125uuoe*_ga*MTM3NTgzMDE0Ni4xNjkzMzE2MjE5*_ga_NC5YHF857R*MTY5MzMxNjIxOS4xLjAuMTY5MzMxNjIxOS4wLjAuMA..#api-Report-GetEventData)


Connector uses `start_date` config for initial reports sync and current date as an end date if this one is not explicitly set.

At the moment, Default `CAMPAIGN` status is (e.g: `deleted`, `,active`, `archived`, `dirty`).


See [this](https://docs.airbyte.io/integrations/sources/apple-audience-project) link for the nuances about the connector.
