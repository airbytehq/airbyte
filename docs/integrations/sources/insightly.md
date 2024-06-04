# Insightly

This page guides you through the process of setting up the Insightly source connector.

## Set up the Insightly connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.com/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the Set up the source page, select **Insightly** from the Source type dropdown.
4. Enter a name for your source.
5. For **API token**, enter the API token for your Insightly account. You can find your API token in your Insightly Account > Click on your avatar > User Settings > API.
6. For **Start date**, enter the date in YYYY-MM-DDTHH:mm:ssZ format. The data added on and after this date will be replicated.
7. Click **Set up source**.

## Supported sync modes

The Insightly source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full Refresh
- Incremental

## Supported Streams

The Insightly source connector supports the following streams, some of them may need elevated permissions:

- [Activity Sets](https://api.na1.insightly.com/v3.1/#!/ActivitySets/GetActivitySets) \(Full table\)
- [Contacts](https://api.na1.insightly.com/v3.1/#!/Contacts/GetEntities) \(Incremental\)
- [Countries](https://api.na1.insightly.com/v3.1/#!/Countries/GetCountries) \(Full table\)
- [Currencies](https://api.na1.insightly.com/v3.1/#!/Currencies/GetCurrencies) \(Full table\)
- [Emails](https://api.na1.insightly.com/v3.1/#!/Emails/GetEntities) \(Full table\)
- [Events](https://api.na1.insightly.com/v3.1/#!/Events/GetEntities) \(Incremental\)
- [Knowledge Article Categories](https://api.na1.insightly.com/v3.1/#!/KnowledgeArticleCategories/GetEntities) \(Incremental\)
- [Knowledge Article Folders](https://api.na1.insightly.com/v3.1/#!/KnowledgeArticleFolders/GetEntities) \(Incremental\)
- [Knowledge Articles](https://api.na1.insightly.com/v3.1/#!/KnowledgeArticles/GetEntities) \(Incremental\)
- [Leads](https://api.na1.insightly.com/v3.1/#!/Leads/GetEntities) \(Incremental\)
- [Lead Sources](https://api.na1.insightly.com/v3.1/#!/LeadSources/GetLeadSources) \(Full table\)
- [Lead Statuses](https://api.na1.insightly.com/v3.1/#!/LeadStatuses/GetLeadStatuses) \(Full table\)
- [Milestones](https://api.na1.insightly.com/v3.1/#!/Milestones/GetEntities) \(Incremental\)
- [Notes](https://api.na1.insightly.com/v3.1/#!/Notes/GetEntities) \(Incremental\)
- [Opportunities](https://api.na1.insightly.com/v3.1/#!/Opportunities/GetEntities) \(Incremental\)
- [Opportunity Categories](https://api.na1.insightly.com/v3.1/#!/OpportunityCategories/GetOpportunityCategories) \(Full table\)
- [Opportunity Products](https://api.na1.insightly.com/v3.1/#!/OpportunityProducts/GetEntities) \(Incremental\)
- [Opportunity State Reasons](https://api.na1.insightly.com/v3.1/#!/OpportunityStateReasons/GetOpportunityStateReasons) \(Full table\)
- [Organisations](https://api.na1.insightly.com/v3.1/#!/Organisations/GetEntities) \(Incremental\)
- [Pipelines](https://api.na1.insightly.com/v3.1/#!/Pipelines/GetPipelines) \(Full table\)
- [Pipeline Stages](https://api.na1.insightly.com/v3.1/#!/PipelineStages/GetPipelineStages) \(Full table\)
- [Price Book Entries](https://api.na1.insightly.com/v3.1/#!/PriceBookEntries/GetEntities) \(Incremental\)
- [Price Books](https://api.na1.insightly.com/v3.1/#!/PriceBooks/GetEntities) \(Incremental\)
- [Products](https://api.na1.insightly.com/v3.1/#!/Products/GetEntities) \(Incremental\)
- [Project Categories](https://api.na1.insightly.com/v3.1/#!/ProjectCategories/GetProjectCategories) \(Full table\)
- [Projects](https://api.na1.insightly.com/v3.1/#!/Projects/GetEntities) \(Incremental\)
- [Prospects](https://api.na1.insightly.com/v3.1/#!/Prospects/GetEntities) \(Incremental\)
- [Quote Products](https://api.na1.insightly.com/v3.1/#!/QuoteProducts/GetEntities) \(Incremental\)
- [Quotes](https://api.na1.insightly.com/v3.1/#!/Quotes/GetEntities) \(Incremental\)
- [Relationships](https://api.na1.insightly.com/v3.1/#!/Relationships/GetRelationships) \(Full table\)
- [Tags](https://api.na1.insightly.com/v3.1/#!/Tags/GetTags) \(Full table\)
- [Task Categories](https://api.na1.insightly.com/v3.1/#!/TaskCategories/GetTaskCategories) \(Full table\)
- [Tasks](https://api.na1.insightly.com/v3.1/#!/Tasks/GetEntities) \(Incremental\)
- [Team Members](https://api.na1.insightly.com/v3.1/#!/TeamMembers/GetTeamMembers) \(Full table\)
- [Teams](https://api.na1.insightly.com/v3.1/#!/Teams/GetTeams) \(Full table\)
- [Tickets](https://api.na1.insightly.com/v3.1/#!/Tickets/GetEntities) \(Incremental\)
- [Users](https://api.na1.insightly.com/v3.1/#!/Users/GetUsers) \(Incremental\)

## Performance considerations

The connector is restricted by Insightly [requests limitation](https://api.na1.insightly.com/v3.1/#!/Overview/Introduction).

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                                         |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------------------------------ |
| 0.2.5   | 2024-05-14 | [38140](https://github.com/airbytehq/airbyte/pull/38140) | Make compatible with builder                                                    |
| 0.2.4   | 2024-04-19 | [37177](https://github.com/airbytehq/airbyte/pull/37177) | Updating to 0.80.0 CDK                                                          |
| 0.2.3   | 2024-04-18 | [37177](https://github.com/airbytehq/airbyte/pull/37177) | Manage dependencies with Poetry.                                                |
| 0.2.2   | 2024-04-15 | [37177](https://github.com/airbytehq/airbyte/pull/37177) | Base image migration: remove Dockerfile and use the python-connector-base image |
| 0.2.1   | 2024-04-12 | [37177](https://github.com/airbytehq/airbyte/pull/37177) | schema descriptions                                                             |
| 0.2.0   | 2023-10-23 | [31162](https://github.com/airbytehq/airbyte/pull/31162) | Migrate to low-code framework                                                   |
| 0.1.3   | 2023-05-15 | [26079](https://github.com/airbytehq/airbyte/pull/26079) | Make incremental syncs timestamp inclusive                                      |
| 0.1.2   | 2023-03-23 | [24422](https://github.com/airbytehq/airbyte/pull/24422) | Fix incremental timedelta causing missing records                               |
| 0.1.1   | 2022-11-11 | [19356](https://github.com/airbytehq/airbyte/pull/19356) | Fix state date parse bug                                                        |
| 0.1.0   | 2022-10-19 | [18164](https://github.com/airbytehq/airbyte/pull/18164) | Release Insightly CDK Connector                                                 |

</details>