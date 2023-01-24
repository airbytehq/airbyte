# Insightly

This page guides you through the process of setting up the Insightly source connector.

## Set up the Insightly connector

1. Log into your [Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
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

* [Activity Sets](https://api.na1.insightly.com/v3.1/#!/ActivitySets/GetActivitySets) \(Full table\)
* [Contacts](https://api.na1.insightly.com/v3.1/#!/Contacts/GetEntities) \(Incremental\)
* [Countries](https://api.na1.insightly.com/v3.1/#!/Countries/GetCountries) \(Full table\)
* [Currencies](https://api.na1.insightly.com/v3.1/#!/Currencies/GetCurrencies) \(Full table\)
* [Emails](https://api.na1.insightly.com/v3.1/#!/Emails/GetEntities) \(Full table\)
* [Events](https://api.na1.insightly.com/v3.1/#!/Events/GetEntities) \(Incremental\)
* [Knowledge Article Categories](https://api.na1.insightly.com/v3.1/#!/KnowledgeArticleCategories/GetEntities) \(Incremental\)
* [Knowledge Article Folders](https://api.na1.insightly.com/v3.1/#!/KnowledgeArticleFolders/GetEntities) \(Incremental\)
* [Knowledge Articles](https://api.na1.insightly.com/v3.1/#!/KnowledgeArticles/GetEntities) \(Incremental\)
* [Leads](https://api.na1.insightly.com/v3.1/#!/Leads/GetEntities) \(Incremental\)
* [Lead Sources](https://api.na1.insightly.com/v3.1/#!/LeadSources/GetLeadSources) \(Full table\)
* [Lead Statuses](https://api.na1.insightly.com/v3.1/#!/LeadStatuses/GetLeadStatuses) \(Full table\)
* [Milestones](https://api.na1.insightly.com/v3.1/#!/Milestones/GetEntities) \(Incremental\)
* [Notes](https://api.na1.insightly.com/v3.1/#!/Notes/GetEntities) \(Incremental\)
* [Opportunities](https://api.na1.insightly.com/v3.1/#!/Opportunities/GetEntities) \(Incremental\)
* [Opportunity Categories](https://api.na1.insightly.com/v3.1/#!/OpportunityCategories/GetOpportunityCategories) \(Full table\)
* [Opportunity Products](https://api.na1.insightly.com/v3.1/#!/OpportunityProducts/GetEntities) \(Incremental\)
* [Opportunity State Reasons](https://api.na1.insightly.com/v3.1/#!/OpportunityStateReasons/GetOpportunityStateReasons) \(Full table\)
* [Organisations](https://api.na1.insightly.com/v3.1/#!/Organisations/GetEntities) \(Incremental\)
* [Pipelines](https://api.na1.insightly.com/v3.1/#!/Pipelines/GetPipelines) \(Full table\)
* [Pipeline Stages](https://api.na1.insightly.com/v3.1/#!/PipelineStages/GetPipelineStages) \(Full table\)
* [Price Book Entries](https://api.na1.insightly.com/v3.1/#!/PriceBookEntries/GetEntities) \(Incremental\)
* [Price Books](https://api.na1.insightly.com/v3.1/#!/PriceBooks/GetEntities) \(Incremental\)
* [Products](https://api.na1.insightly.com/v3.1/#!/Products/GetEntities) \(Incremental\)
* [Project Categories](https://api.na1.insightly.com/v3.1/#!/ProjectCategories/GetProjectCategories) \(Full table\)
* [Projects](https://api.na1.insightly.com/v3.1/#!/Projects/GetEntities) \(Incremental\)
* [Prospects](https://api.na1.insightly.com/v3.1/#!/Prospects/GetEntities) \(Incremental\)
* [Quote Products](https://api.na1.insightly.com/v3.1/#!/QuoteProducts/GetEntities) \(Incremental\)
* [Quotes](https://api.na1.insightly.com/v3.1/#!/Quotes/GetEntities) \(Incremental\)
* [Relationships](https://api.na1.insightly.com/v3.1/#!/Relationships/GetRelationships) \(Full table\)
* [Tags](https://api.na1.insightly.com/v3.1/#!/Tags/GetTags) \(Full table\)
* [Task Categories](https://api.na1.insightly.com/v3.1/#!/TaskCategories/GetTaskCategories) \(Full table\)
* [Tasks](https://api.na1.insightly.com/v3.1/#!/Tasks/GetEntities) \(Incremental\)
* [Team Members](https://api.na1.insightly.com/v3.1/#!/TeamMembers/GetTeamMembers) \(Full table\)
* [Teams](https://api.na1.insightly.com/v3.1/#!/Teams/GetTeams) \(Full table\)
* [Tickets](https://api.na1.insightly.com/v3.1/#!/Tickets/GetEntities) \(Incremental\)
* [Users](https://api.na1.insightly.com/v3.1/#!/Users/GetUsers) \(Incremental\)


## Performance considerations

The connector is restricted by Insightly [requests limitation](https://api.na1.insightly.com/v3.1/#!/Overview/Introduction).


## Changelog

| Version | Date       | Pull Request                                             | Subject                                                                           |
| :------ | :--------- | :------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| 0.1.1   | 2022-11-11 |    | Fix state date parse bug                            |
| 0.1.0   | 2022-10-19 |    | Release Insightly CDK Connector                     |
