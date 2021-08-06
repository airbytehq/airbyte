# Salesforce

## Overview

The Salesforce source supports both Full Refresh and Incremental syncs. You can choose if this connector will copy only the new or updated data, or all rows in the tables and columns you set up for replication, every time a sync is run.

This source wraps the Singer.io [tap-salesforce](https://github.com/singer-io/tap-salesforce).

### Output schema

Several output streams are available from this source. A list of these streams can be found below in the [Streams](salesforce.md#streams) section.

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | Yes |
| Replicate Incremental Deletes | Coming soon |
| SSL connection | Yes |
| Namespaces | No |

### Performance considerations

The connector is restricted by normal Salesforce rate limiting. For large transfers we recommend using the bulk API.

## Getting started

### Requirements

* Salesforce Account
* Salesforce OAuth credentials

### Setup guide

We recommend the following [walkthrough](https://medium.com/@bpmmendis94/obtain-access-refresh-tokens-from-salesforce-rest-api-a324fe4ccd9b) **while keeping in mind the edits we suggest below** for setting up a Salesforce app that can pull data from Salesforce and locating the credentials you need to provide to Airbyte.

Suggested edits:

1. If your salesforce URL does not take the form `X.salesforce.com`, use your actual Salesforce domain name. For example, if your Salesforce URL is `awesomecompany.force.com` then use that instead of `awesomecompany.salesforce.com`. 
2. When running a `curl` command, always run it with the `-L` option to follow any redirects.

#### is\_sandbox

If you log in using at [https://login.salesforce.com](https://login.salesforce.com), then the value is false. If you log in at [https://test.salesforce.com](https://test.salesforce.com) then the value should be true. If this is Greek to you, then this value should probably be false.

## Streams

List of available streams.

* ServiceAppointmentFeed
* ThirdPartyAccountLink
* DataAssessmentFieldMetric
* ServiceAppointmentHistory
* UserLogin
* CampaignFeed
* ApexTestRunResult
* BrandTemplate
* ListEmailRecipientSource
* Product2
* LoginHistory
* PricebookEntry
* SolutionFeed
* ServiceAppointment
* SiteFeed
* PermissionSetAssignment
* ServiceResourceFeed
* ApexTestResult
* AssetRelationshipHistory
* FieldPermissions
* OrgWideEmailAddress
* DuplicateRecordSet
* DashboardComponentFeed
* CollaborationGroupMember
* ExternalEventMappingShare
* UserProvisioningConfig
* MessagingSessionFeed
* ContactFeed
* MatchingRuleItem
* ContactShare
* AsyncApexJob
* ApexTrigger
* AuthConfigProviders
* CampaignHistory
* UserListViewCriterion
* ExternalEvent
* AppMenuItem
* ContentDocumentHistory
* LoginGeo
* SamlSsoConfig
* DatacloudDandBCompany
* ServiceTerritoryHistory
* OrderShare
* EmailDomainKey
* KnowledgeableUser
* PermissionSetGroup
* Report
* BackgroundOperation
* ProcessDefinition
* ListEmail
* LiveChatSensitiveDataRule
* PlatformCachePartition
* FileSearchActivity
* EmbeddedServiceDetail
* UserProvMockTarget
* ResourcePreferenceFeed
* QuickText
* SecureAgentPlugin
* ServiceAppointmentShare
* MessagingChannel
* ServiceResource
* Asset
* AuthConfig
* FiscalYearSettings
* SkillRequirement
* SkillRequirementHistory
* UserPackageLicense
* AssociatedLocation
* ApexEmailNotification
* ConnectedApplication
* Opportunity
* TaskFeed
* PermissionSet
* RecordType
* CaseTeamTemplate
* OauthToken
* CategoryNode
* UserProvAccount
* MacroShare
* CampaignMemberStatus
* ChatterExtension
* Group
* StaticResource
* MatchingInformation
* CollaborationGroup
* SetupAuditTrail
* ProcessNode
* CorsWhitelistEntry
* CaseContactRole
* TestSuiteMembership
* LeadShare
* CallCenter
* LoginEvent
* DataAssessmentMetric
* MobileApplicationDetail
* MessagingSession
* Domain
* Document
* ApexClass
* AssociatedLocationHistory
* DatacloudCompany
* ResourceAbsenceHistory
* ServiceResourceSkill
* OpportunityFeed
* DuplicateRule
* LeadFeed
* Idea
* Organization
* OpportunityShare
* BusinessProcess
* AssetRelationshipFeed
* FeedComment
* UserFeed
* ListViewChart
* UserAppMenuCustomizationShare
* BrandingSetProperty
* ServiceTerritoryMember
* Folder
* ContentWorkspacePermission
* LeadCleanInfo
* ListView
* CampaignMember
* ContentVersion
* UserListView
* ProcessInstanceWorkitem
* ChatterActivity
* LocationHistory
* ContentWorkspaceMember
* QuickTextHistory
* EventLogFile
* MessagingEndUserShare
* ContractContactRole
* WorkType
* LeadStatus
* QueueSobject
* BrandingSet
* TodayGoal
* CampaignShare
* ContractFeed
* AccountContactRole
* MessagingSessionShare
* AssetRelationship
* OpportunityPartner
* MacroHistory
* GrantedByLicense
* CaseTeamTemplateMember
* GroupMember
* UserProvisioningRequest
* ServiceResourceShare
* Skill
* CaseHistory
* OrderFeed
* WaveCompatibilityCheckItem
* Event
* LocationShare
* TopicAssignment
* TopicFeed
* ContentDocumentFeed
* ObjectPermissions
* SkillRequirementFeed
* FeedItem
* AccountHistory
* ApexComponent
* SetupEntityAccess
* StreamingChannel
* OperatingHours
* CaseSolution
* Publisher
* SiteHistory
* ApexPage
* AccountShare
* FlowInterviewShare
* Dashboard
* CaseTeamRole
* AccountPartner
* DatacloudAddress
* ChatterExtensionConfig
* OpportunityStage
* AuraDefinitionBundleInfo
* ResourcePreferenceHistory
* UserProvisioningLog
* ResourceAbsenceFeed
* IdpEventLog
* ContentDistributionView
* CollaborationGroupMemberRequest
* DomainSite
* EventFeed
* BusinessHours
* SecureAgentsCluster
* UserShare
* DataAssessmentValueMetric
* EntitySubscription
* VisualforceAccessMetrics
* CspTrustedSite
* Order
* InstalledMobileApp
* Location
* UserRole
* CaseFeed
* ContentDocument
* DuplicateRecordItem
* ServiceTerritoryMemberHistory
* Scontrol
* AssignedResourceFeed
* ApexLog
* CaseTeamMember
* DocumentAttachmentMap
* ServiceTerritoryMemberFeed
* OrderItemFeed
* UserAppMenuCustomization
* OpportunityCompetitor
* Product2History
* PushTopic
* ResourcePreference
* WorkTypeHistory
* StampAssignment
* LocationFeed
* EmailMessageRelation
* OrderHistory
* OpportunityLineItem
* WorkTypeShare
* AccountFeed
* ContentFolder
* LoginIp
* OpportunityHistory
* Macro
* MatchingRule
* SecureAgent
* AccountCleanInfo
* SecureAgentPluginProperty
* OrderItem
* MessagingEndUser
* ApexTestQueueItem
* QuickTextShare
* FeedPollChoice
* ProcessInstance
* CustomPermissionDependency
* SecurityCustomBaseline
* TenantUsageEntitlement
* ProcessInstanceStep
* ServiceTerritoryShare
* SearchPromotionRule
* Lead
* ClientBrowser
* CaseComment
* DatacloudOwnedEntity
* ContentWorkspaceDoc
* EmailServicesFunction
* Solution
* AssetHistory
* EmailServicesAddress
* CustomPermission
* PermissionSetGroupComponent
* AuraDefinitionInfo
* UserProvAccountStaging
* Note
* OpportunityFieldHistory
* DandBCompany
* MailmergeTemplate
* User
* AuthProvider
* FlowInterview
* VerificationHistory
* AssetFeed
* AuthSession
* EventRelation
* WorkTypeFeed
* UserPreference
* NamedCredential
* ServiceResourceSkillHistory
* UserProvisioningRequestShare
* EmailCapture
* CustomBrandAsset
* Campaign
* UserAppInfo
* UserPermissionAccess
* AdditionalNumber
* ContentAsset
* ConferenceNumber
* ServiceTerritory
* ActionLinkGroupTemplate
* CollaborationInvitation
* PermissionSetLicense
* ApexTestSuite
* ExternalEventMapping
* TimeSlot
* OrderItemHistory
* MessagingEndUserHistory
* ExternalDataUserAuth
* AuraDefinition
* LeadHistory
* ServiceAppointmentStatus
* EventBusSubscriber
* WebLink
* ApexTestResultLimits
* Profile
* CaseTeamTemplateRecord
* OpportunityContactRole
* CronTrigger
* DatacloudContact
* ContentWorkspace
* Period
* AssetShare
* MessagingLink
* Topic
* ServiceResourceHistory
* Case
* EntityDefinition
* ResourceAbsence
* Partner
* AssignmentRule
* ListEmailShare
* ContactHistory
* Site
* CustomBrand
* EmailMessage
* Pricebook2History
* FeedPollVote
* ServiceResourceSkillFeed
* Account
* SessionPermSetActivation
* ContractHistory
* Holiday
* EmailTemplate
* ActionLinkTemplate
* ReportFeed
* CollaborationGroupFeed
* CustomObjectUserLicenseMetrics
* FeedAttachment
* ContentDistribution
* ContentFolderLink
* FeedRevision
* UserAppMenuItem
* ProcessInstanceNode
* AuraDefinitionBundle
* TodayGoalShare
* Pricebook2
* CategoryData
* MacroInstruction
* StreamingChannelShare
* AssignedResource
* PackageLicense
* Product2Feed
* DashboardFeed
* Task
* UserLicense
* SolutionHistory
* ContentVersionHistory
* MessagingSessionHistory
* DashboardComponent
* CaseShare
* PermissionSetLicenseAssign
* ContactCleanInfo
* Contract
* Attachment
* DatacloudPurchaseUsage
* ServiceTerritoryFeed
* CronJobDetail
* ApexPageInfo
* PlatformCachePartitionType
* Contact
* Community
* Stamp
* OperatingHoursFeed
* ExternalDataSource


## Changelog

| Version | Date       | Pull Request | Subject |
| :------ | :--------  | :-----       | :------ |
| 0.2.5   | 2021-08-02 | [5100](https://github.com/airbytehq/airbyte/pull/5100) | Source salesforce: add configuration values for quota limit |
| 0.2.4   | 2021-07-06 | [4539](https://github.com/airbytehq/airbyte/pull/4539) | Add `AIRBYTE_ENTRYPOINT` for Kubernetes support |
| 0.2.3   | 2021-06-11 | [3708](https://github.com/airbytehq/airbyte/pull/3708) | Remove sensitive fields from logs |
| 0.2.2   | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add AIRBYTE_ENTRYPOINT for Kubernetes support |
| 0.2.1   | 2021-04-03 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix base connector versioning |
| 0.2.0   | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Protocol allows future/unknown properties |
| 0.1.6   | 2021-01-21 | [1654](https://github.com/airbytehq/airbyte/pull/1654) | Adopt connector best practices |
| 0.1.5   | 2021-01-06 | [1511](https://github.com/airbytehq/airbyte/pull/1511) | Support incremental sync |
| 0.1.4   | 2020-11-30 | [1046](https://github.com/airbytehq/airbyte/pull/1046) | Add connectors using an index YAML file |
