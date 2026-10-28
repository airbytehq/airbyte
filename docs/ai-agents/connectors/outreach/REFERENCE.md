# Outreach full reference

This is the full reference documentation for the Outreach agent connector.

## Supported entities and actions

The Outreach connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Prospects | [List](#prospects-list), [Get](#prospects-get), [Context Store Search](#prospects-context-store-search), [Context Store SQL Query](#prospects-context-store-sql-query) |
| Accounts | [List](#accounts-list), [Get](#accounts-get), [Context Store Search](#accounts-context-store-search), [Context Store SQL Query](#accounts-context-store-sql-query) |
| Sequences | [List](#sequences-list), [Get](#sequences-get), [Context Store Search](#sequences-context-store-search), [Context Store SQL Query](#sequences-context-store-sql-query) |
| Sequence States | [List](#sequence-states-list), [Get](#sequence-states-get), [Context Store Search](#sequence-states-context-store-search), [Context Store SQL Query](#sequence-states-context-store-sql-query) |
| Sequence Steps | [List](#sequence-steps-list), [Get](#sequence-steps-get), [Context Store Search](#sequence-steps-context-store-search), [Context Store SQL Query](#sequence-steps-context-store-sql-query) |
| Opportunities | [List](#opportunities-list), [Get](#opportunities-get), [Context Store Search](#opportunities-context-store-search), [Context Store SQL Query](#opportunities-context-store-sql-query) |
| Calls | [List](#calls-list), [Get](#calls-get), [Context Store Search](#calls-context-store-search), [Context Store SQL Query](#calls-context-store-sql-query) |
| Call Dispositions | [List](#call-dispositions-list), [Get](#call-dispositions-get), [Context Store Search](#call-dispositions-context-store-search), [Context Store SQL Query](#call-dispositions-context-store-sql-query) |
| Call Purposes | [List](#call-purposes-list), [Get](#call-purposes-get), [Context Store Search](#call-purposes-context-store-search), [Context Store SQL Query](#call-purposes-context-store-sql-query) |
| Mailings | [List](#mailings-list), [Get](#mailings-get), [Context Store Search](#mailings-context-store-search), [Context Store SQL Query](#mailings-context-store-sql-query) |
| Mailboxes | [List](#mailboxes-list), [Get](#mailboxes-get), [Context Store Search](#mailboxes-context-store-search), [Context Store SQL Query](#mailboxes-context-store-sql-query) |
| Tasks | [List](#tasks-list), [Get](#tasks-get), [Context Store Search](#tasks-context-store-search), [Context Store SQL Query](#tasks-context-store-sql-query) |
| Users | [List](#users-list), [Get](#users-get), [Context Store Search](#users-context-store-search), [Context Store SQL Query](#users-context-store-sql-query) |
| Stages | [List](#stages-list), [Get](#stages-get), [Context Store Search](#stages-context-store-search), [Context Store SQL Query](#stages-context-store-sql-query) |
| Personas | [List](#personas-list), [Get](#personas-get), [Context Store Search](#personas-context-store-search), [Context Store SQL Query](#personas-context-store-sql-query) |
| Templates | [List](#templates-list), [Get](#templates-get), [Context Store Search](#templates-context-store-search), [Context Store SQL Query](#templates-context-store-sql-query) |
| Snippets | [List](#snippets-list), [Get](#snippets-get), [Context Store Search](#snippets-context-store-search), [Context Store SQL Query](#snippets-context-store-sql-query) |

## Prospects

### Prospects List

Returns a paginated list of prospects (contacts) in Outreach

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "prospects",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.prospects.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "prospects",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Prospects Get

Get a single prospect by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "prospects",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.prospects.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "prospects",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Prospect ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Prospects Context Store Search

Search and filter prospects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "prospects",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "account": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.prospects.context_store_search(
    query={"filter": {"eq": {"account": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "prospects",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"account": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `account` | `array` | Account |
| `accountName` | `string` | Account name |
| `activeSequenceStates` | `array` | Active sequence states |
| `addedAt` | `string` | Added at |
| `addressCity` | `string` | Address city |
| `addressCountry` | `string` | Address country |
| `addressState` | `string` | Address state |
| `addressStreet` | `string` | Address street |
| `addressStreet2` | `string` | Address street2 |
| `addressZip` | `string` | Address zip |
| `angelListUrl` | `string` | Angel list url |
| `assignedTeams` | `array` | Assigned teams |
| `assignedUsers` | `array` | Assigned users |
| `availableAt` | `string` | Available at |
| `batches` | `array` | Batches |
| `callOptedOut` | `boolean` | Call opted out |
| `calls` | `array` | Calls |
| `callsOptStatus` | `string` | Calls opt status |
| `callsOptedAt` | `string` | Calls opted at |
| `campaignName` | `string` | Campaign name |
| `clickCount` | `integer` | Click count |
| `company` | `string` | Company |
| `companyFollowers` | `integer` | Company followers |
| `companyFoundedAt` | `string` | Company founded at |
| `companyIndustry` | `string` | Company industry |
| `companyLinkedIn` | `string` | Company linked in |
| `companyLinkedInEmployees` | `string` | Company linked in employees |
| `companyLocality` | `string` | Company locality |
| `companyNatural` | `string` | Company natural |
| `companySize` | `integer` | Company size |
| `companyStartDate` | `string` | Company start date |
| `companyType` | `string` | Company type |
| `contactHistogram` | `array` | Contact histogram |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `custom1` | `string` | Custom field 1 |
| `custom10` | `string` | Custom field 10 |
| `custom100` | `string` | Custom field 100 |
| `custom101` | `string` | Custom field 101 |
| `custom102` | `string` | Custom field 102 |
| `custom103` | `string` | Custom field 103 |
| `custom104` | `string` | Custom field 104 |
| `custom105` | `string` | Custom field 105 |
| `custom106` | `string` | Custom field 106 |
| `custom107` | `string` | Custom field 107 |
| `custom108` | `string` | Custom field 108 |
| `custom109` | `string` | Custom field 109 |
| `custom11` | `string` | Custom field 11 |
| `custom110` | `string` | Custom field 110 |
| `custom111` | `string` | Custom field 111 |
| `custom112` | `string` | Custom field 112 |
| `custom113` | `string` | Custom field 113 |
| `custom114` | `string` | Custom field 114 |
| `custom115` | `string` | Custom field 115 |
| `custom116` | `string` | Custom field 116 |
| `custom117` | `string` | Custom field 117 |
| `custom118` | `string` | Custom field 118 |
| `custom119` | `string` | Custom field 119 |
| `custom12` | `string` | Custom field 12 |
| `custom120` | `string` | Custom field 120 |
| `custom121` | `string` | Custom field 121 |
| `custom122` | `string` | Custom field 122 |
| `custom123` | `string` | Custom field 123 |
| `custom124` | `string` | Custom field 124 |
| `custom125` | `string` | Custom field 125 |
| `custom126` | `string` | Custom field 126 |
| `custom127` | `string` | Custom field 127 |
| `custom128` | `string` | Custom field 128 |
| `custom129` | `string` | Custom field 129 |
| `custom13` | `string` | Custom field 13 |
| `custom130` | `string` | Custom field 130 |
| `custom131` | `string` | Custom field 131 |
| `custom132` | `string` | Custom field 132 |
| `custom133` | `string` | Custom field 133 |
| `custom134` | `string` | Custom field 134 |
| `custom135` | `string` | Custom field 135 |
| `custom136` | `string` | Custom field 136 |
| `custom137` | `string` | Custom field 137 |
| `custom138` | `string` | Custom field 138 |
| `custom139` | `string` | Custom field 139 |
| `custom14` | `string` | Custom field 14 |
| `custom140` | `string` | Custom field 140 |
| `custom141` | `string` | Custom field 141 |
| `custom142` | `string` | Custom field 142 |
| `custom143` | `string` | Custom field 143 |
| `custom144` | `string` | Custom field 144 |
| `custom145` | `string` | Custom field 145 |
| `custom146` | `string` | Custom field 146 |
| `custom147` | `string` | Custom field 147 |
| `custom148` | `string` | Custom field 148 |
| `custom149` | `string` | Custom field 149 |
| `custom15` | `string` | Custom field 15 |
| `custom150` | `string` | Custom field 150 |
| `custom16` | `string` | Custom field 16 |
| `custom17` | `string` | Custom field 17 |
| `custom18` | `string` | Custom field 18 |
| `custom19` | `string` | Custom field 19 |
| `custom2` | `string` | Custom field 2 |
| `custom20` | `string` | Custom field 20 |
| `custom21` | `string` | Custom field 21 |
| `custom22` | `string` | Custom field 22 |
| `custom23` | `string` | Custom field 23 |
| `custom24` | `string` | Custom field 24 |
| `custom25` | `string` | Custom field 25 |
| `custom26` | `string` | Custom field 26 |
| `custom27` | `string` | Custom field 27 |
| `custom28` | `string` | Custom field 28 |
| `custom29` | `string` | Custom field 29 |
| `custom3` | `string` | Custom field 3 |
| `custom30` | `string` | Custom field 30 |
| `custom31` | `string` | Custom field 31 |
| `custom32` | `string` | Custom field 32 |
| `custom33` | `string` | Custom field 33 |
| `custom34` | `string` | Custom field 34 |
| `custom35` | `string` | Custom field 35 |
| `custom36` | `string` | Custom field 36 |
| `custom37` | `string` | Custom field 37 |
| `custom38` | `string` | Custom field 38 |
| `custom39` | `string` | Custom field 39 |
| `custom4` | `string` | Custom field 4 |
| `custom40` | `string` | Custom field 40 |
| `custom41` | `string` | Custom field 41 |
| `custom42` | `string` | Custom field 42 |
| `custom43` | `string` | Custom field 43 |
| `custom44` | `string` | Custom field 44 |
| `custom45` | `string` | Custom field 45 |
| `custom46` | `string` | Custom field 46 |
| `custom47` | `string` | Custom field 47 |
| `custom48` | `string` | Custom field 48 |
| `custom49` | `string` | Custom field 49 |
| `custom5` | `string` | Custom field 5 |
| `custom50` | `string` | Custom field 50 |
| `custom51` | `string` | Custom field 51 |
| `custom52` | `string` | Custom field 52 |
| `custom53` | `string` | Custom field 53 |
| `custom54` | `string` | Custom field 54 |
| `custom55` | `string` | Custom field 55 |
| `custom56` | `string` | Custom field 56 |
| `custom57` | `string` | Custom field 57 |
| `custom58` | `string` | Custom field 58 |
| `custom59` | `string` | Custom field 59 |
| `custom6` | `string` | Custom field 6 |
| `custom60` | `string` | Custom field 60 |
| `custom61` | `string` | Custom field 61 |
| `custom62` | `string` | Custom field 62 |
| `custom63` | `string` | Custom field 63 |
| `custom64` | `string` | Custom field 64 |
| `custom65` | `string` | Custom field 65 |
| `custom66` | `string` | Custom field 66 |
| `custom67` | `string` | Custom field 67 |
| `custom68` | `string` | Custom field 68 |
| `custom69` | `string` | Custom field 69 |
| `custom7` | `string` | Custom field 7 |
| `custom70` | `string` | Custom field 70 |
| `custom71` | `string` | Custom field 71 |
| `custom72` | `string` | Custom field 72 |
| `custom73` | `string` | Custom field 73 |
| `custom74` | `string` | Custom field 74 |
| `custom75` | `string` | Custom field 75 |
| `custom76` | `string` | Custom field 76 |
| `custom77` | `string` | Custom field 77 |
| `custom78` | `string` | Custom field 78 |
| `custom79` | `string` | Custom field 79 |
| `custom8` | `string` | Custom field 8 |
| `custom80` | `string` | Custom field 80 |
| `custom81` | `string` | Custom field 81 |
| `custom82` | `string` | Custom field 82 |
| `custom83` | `string` | Custom field 83 |
| `custom84` | `string` | Custom field 84 |
| `custom85` | `string` | Custom field 85 |
| `custom86` | `string` | Custom field 86 |
| `custom87` | `string` | Custom field 87 |
| `custom88` | `string` | Custom field 88 |
| `custom89` | `string` | Custom field 89 |
| `custom9` | `string` | Custom field 9 |
| `custom90` | `string` | Custom field 90 |
| `custom91` | `string` | Custom field 91 |
| `custom92` | `string` | Custom field 92 |
| `custom93` | `string` | Custom field 93 |
| `custom94` | `string` | Custom field 94 |
| `custom95` | `string` | Custom field 95 |
| `custom96` | `string` | Custom field 96 |
| `custom97` | `string` | Custom field 97 |
| `custom98` | `string` | Custom field 98 |
| `custom99` | `string` | Custom field 99 |
| `dateOfBirth` | `string` | Date of birth |
| `defaultPluginMapping` | `array` | Default plugin mapping |
| `degree` | `string` | Degree |
| `emailAddresses` | `array` | Email addresses |
| `emailContacts` | `array` | Email contacts |
| `emailOptedOut` | `boolean` | Email opted out |
| `emails` | `array` | Emails |
| `emailsOptStatus` | `string` | Emails opt status |
| `emailsOptedAt` | `string` | Emails opted at |
| `engagedAt` | `string` | Engaged at |
| `engagedScore` | `number` | Engaged score |
| `eventName` | `string` | Event name |
| `externalId` | `string` | External id |
| `externalOwner` | `string` | External owner |
| `externalSource` | `string` | External source |
| `facebookUrl` | `string` | Facebook url |
| `favorites` | `array` | Favorites |
| `firstName` | `string` | First name |
| `gender` | `string` | Gender |
| `githubUrl` | `string` | Github url |
| `githubUsername` | `string` | Github username |
| `googlePlusUrl` | `string` | Google plus url |
| `graduationDate` | `string` | Graduation date |
| `homePhones` | `array` | Home phones |
| `id` | `integer` | Unique prospect identifier |
| `jobStartDate` | `string` | Job start date |
| `lastName` | `string` | Last name |
| `linkedInConnections` | `integer` | Linked in connections |
| `linkedInId` | `string` | Linked in id |
| `linkedInSlug` | `string` | Linked in slug |
| `linkedInUrl` | `string` | Linked in url |
| `mailings` | `array` | Mailings |
| `middleName` | `string` | Middle name |
| `mobilePhones` | `array` | Mobile phones |
| `name` | `string` | Name |
| `nickname` | `string` | Nickname |
| `occupation` | `string` | Occupation |
| `openCount` | `integer` | Open count |
| `opportunities` | `array` | Opportunities |
| `opportunityProspectRoles` | `array` | Opportunity prospect roles |
| `optedOut` | `boolean` | Opted out |
| `optedOutAt` | `string` | Opted out at |
| `otherPhones` | `array` | Other phones |
| `owner` | `array` | Owner |
| `persona` | `array` | Persona |
| `personaName` | `string` | Persona name |
| `personalNote1` | `string` | Personal note1 |
| `personalNote2` | `string` | Personal note2 |
| `phoneNumbers` | `array` | Phone numbers |
| `preferredContact` | `string` | Preferred contact |
| `quoraUrl` | `string` | Quora url |
| `region` | `string` | Region |
| `replyCount` | `integer` | Reply count |
| `school` | `string` | School |
| `score` | `number` | Score |
| `sequenceStates` | `array` | Sequence states |
| `sharingTeamId` | `string` | Sharing team id |
| `smsOptStatus` | `string` | Sms opt status |
| `smsOptedAt` | `string` | Sms opted at |
| `smsOptedOut` | `boolean` | Sms opted out |
| `source` | `string` | Source |
| `specialties` | `string` | Specialties |
| `stackOverflowId` | `string` | Stack overflow id |
| `stackOverflowUrl` | `string` | Stack overflow url |
| `stage` | `array` | Stage |
| `stageName` | `string` | Stage name |
| `tags` | `array` | Tags |
| `tasks` | `array` | Tasks |
| `timeZone` | `string` | Time zone |
| `timeZoneIana` | `string` | Time zone iana |
| `timeZoneInferred` | `string` | Time zone inferred |
| `title` | `string` | Title |
| `touchedAt` | `string` | Touched at |
| `trashedAt` | `string` | Trashed at |
| `trashedByAccount` | `array` | Trashed by account |
| `twitterUrl` | `string` | Twitter url |
| `twitterUsername` | `string` | Twitter username |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |
| `updaterId` | `integer` | Updater id |
| `updaterType` | `string` | Updater type |
| `voipPhones` | `array` | Voip phones |
| `websiteUrl1` | `string` | Website url1 |
| `websiteUrl2` | `string` | Website url2 |
| `websiteUrl3` | `string` | Website url3 |
| `workPhones` | `array` | Work phones |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account` | `array` | Account |
| `data[].accountName` | `string` | Account name |
| `data[].activeSequenceStates` | `array` | Active sequence states |
| `data[].addedAt` | `string` | Added at |
| `data[].addressCity` | `string` | Address city |
| `data[].addressCountry` | `string` | Address country |
| `data[].addressState` | `string` | Address state |
| `data[].addressStreet` | `string` | Address street |
| `data[].addressStreet2` | `string` | Address street2 |
| `data[].addressZip` | `string` | Address zip |
| `data[].angelListUrl` | `string` | Angel list url |
| `data[].assignedTeams` | `array` | Assigned teams |
| `data[].assignedUsers` | `array` | Assigned users |
| `data[].availableAt` | `string` | Available at |
| `data[].batches` | `array` | Batches |
| `data[].callOptedOut` | `boolean` | Call opted out |
| `data[].calls` | `array` | Calls |
| `data[].callsOptStatus` | `string` | Calls opt status |
| `data[].callsOptedAt` | `string` | Calls opted at |
| `data[].campaignName` | `string` | Campaign name |
| `data[].clickCount` | `integer` | Click count |
| `data[].company` | `string` | Company |
| `data[].companyFollowers` | `integer` | Company followers |
| `data[].companyFoundedAt` | `string` | Company founded at |
| `data[].companyIndustry` | `string` | Company industry |
| `data[].companyLinkedIn` | `string` | Company linked in |
| `data[].companyLinkedInEmployees` | `string` | Company linked in employees |
| `data[].companyLocality` | `string` | Company locality |
| `data[].companyNatural` | `string` | Company natural |
| `data[].companySize` | `integer` | Company size |
| `data[].companyStartDate` | `string` | Company start date |
| `data[].companyType` | `string` | Company type |
| `data[].contactHistogram` | `array` | Contact histogram |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].custom1` | `string` | Custom field 1 |
| `data[].custom10` | `string` | Custom field 10 |
| `data[].custom100` | `string` | Custom field 100 |
| `data[].custom101` | `string` | Custom field 101 |
| `data[].custom102` | `string` | Custom field 102 |
| `data[].custom103` | `string` | Custom field 103 |
| `data[].custom104` | `string` | Custom field 104 |
| `data[].custom105` | `string` | Custom field 105 |
| `data[].custom106` | `string` | Custom field 106 |
| `data[].custom107` | `string` | Custom field 107 |
| `data[].custom108` | `string` | Custom field 108 |
| `data[].custom109` | `string` | Custom field 109 |
| `data[].custom11` | `string` | Custom field 11 |
| `data[].custom110` | `string` | Custom field 110 |
| `data[].custom111` | `string` | Custom field 111 |
| `data[].custom112` | `string` | Custom field 112 |
| `data[].custom113` | `string` | Custom field 113 |
| `data[].custom114` | `string` | Custom field 114 |
| `data[].custom115` | `string` | Custom field 115 |
| `data[].custom116` | `string` | Custom field 116 |
| `data[].custom117` | `string` | Custom field 117 |
| `data[].custom118` | `string` | Custom field 118 |
| `data[].custom119` | `string` | Custom field 119 |
| `data[].custom12` | `string` | Custom field 12 |
| `data[].custom120` | `string` | Custom field 120 |
| `data[].custom121` | `string` | Custom field 121 |
| `data[].custom122` | `string` | Custom field 122 |
| `data[].custom123` | `string` | Custom field 123 |
| `data[].custom124` | `string` | Custom field 124 |
| `data[].custom125` | `string` | Custom field 125 |
| `data[].custom126` | `string` | Custom field 126 |
| `data[].custom127` | `string` | Custom field 127 |
| `data[].custom128` | `string` | Custom field 128 |
| `data[].custom129` | `string` | Custom field 129 |
| `data[].custom13` | `string` | Custom field 13 |
| `data[].custom130` | `string` | Custom field 130 |
| `data[].custom131` | `string` | Custom field 131 |
| `data[].custom132` | `string` | Custom field 132 |
| `data[].custom133` | `string` | Custom field 133 |
| `data[].custom134` | `string` | Custom field 134 |
| `data[].custom135` | `string` | Custom field 135 |
| `data[].custom136` | `string` | Custom field 136 |
| `data[].custom137` | `string` | Custom field 137 |
| `data[].custom138` | `string` | Custom field 138 |
| `data[].custom139` | `string` | Custom field 139 |
| `data[].custom14` | `string` | Custom field 14 |
| `data[].custom140` | `string` | Custom field 140 |
| `data[].custom141` | `string` | Custom field 141 |
| `data[].custom142` | `string` | Custom field 142 |
| `data[].custom143` | `string` | Custom field 143 |
| `data[].custom144` | `string` | Custom field 144 |
| `data[].custom145` | `string` | Custom field 145 |
| `data[].custom146` | `string` | Custom field 146 |
| `data[].custom147` | `string` | Custom field 147 |
| `data[].custom148` | `string` | Custom field 148 |
| `data[].custom149` | `string` | Custom field 149 |
| `data[].custom15` | `string` | Custom field 15 |
| `data[].custom150` | `string` | Custom field 150 |
| `data[].custom16` | `string` | Custom field 16 |
| `data[].custom17` | `string` | Custom field 17 |
| `data[].custom18` | `string` | Custom field 18 |
| `data[].custom19` | `string` | Custom field 19 |
| `data[].custom2` | `string` | Custom field 2 |
| `data[].custom20` | `string` | Custom field 20 |
| `data[].custom21` | `string` | Custom field 21 |
| `data[].custom22` | `string` | Custom field 22 |
| `data[].custom23` | `string` | Custom field 23 |
| `data[].custom24` | `string` | Custom field 24 |
| `data[].custom25` | `string` | Custom field 25 |
| `data[].custom26` | `string` | Custom field 26 |
| `data[].custom27` | `string` | Custom field 27 |
| `data[].custom28` | `string` | Custom field 28 |
| `data[].custom29` | `string` | Custom field 29 |
| `data[].custom3` | `string` | Custom field 3 |
| `data[].custom30` | `string` | Custom field 30 |
| `data[].custom31` | `string` | Custom field 31 |
| `data[].custom32` | `string` | Custom field 32 |
| `data[].custom33` | `string` | Custom field 33 |
| `data[].custom34` | `string` | Custom field 34 |
| `data[].custom35` | `string` | Custom field 35 |
| `data[].custom36` | `string` | Custom field 36 |
| `data[].custom37` | `string` | Custom field 37 |
| `data[].custom38` | `string` | Custom field 38 |
| `data[].custom39` | `string` | Custom field 39 |
| `data[].custom4` | `string` | Custom field 4 |
| `data[].custom40` | `string` | Custom field 40 |
| `data[].custom41` | `string` | Custom field 41 |
| `data[].custom42` | `string` | Custom field 42 |
| `data[].custom43` | `string` | Custom field 43 |
| `data[].custom44` | `string` | Custom field 44 |
| `data[].custom45` | `string` | Custom field 45 |
| `data[].custom46` | `string` | Custom field 46 |
| `data[].custom47` | `string` | Custom field 47 |
| `data[].custom48` | `string` | Custom field 48 |
| `data[].custom49` | `string` | Custom field 49 |
| `data[].custom5` | `string` | Custom field 5 |
| `data[].custom50` | `string` | Custom field 50 |
| `data[].custom51` | `string` | Custom field 51 |
| `data[].custom52` | `string` | Custom field 52 |
| `data[].custom53` | `string` | Custom field 53 |
| `data[].custom54` | `string` | Custom field 54 |
| `data[].custom55` | `string` | Custom field 55 |
| `data[].custom56` | `string` | Custom field 56 |
| `data[].custom57` | `string` | Custom field 57 |
| `data[].custom58` | `string` | Custom field 58 |
| `data[].custom59` | `string` | Custom field 59 |
| `data[].custom6` | `string` | Custom field 6 |
| `data[].custom60` | `string` | Custom field 60 |
| `data[].custom61` | `string` | Custom field 61 |
| `data[].custom62` | `string` | Custom field 62 |
| `data[].custom63` | `string` | Custom field 63 |
| `data[].custom64` | `string` | Custom field 64 |
| `data[].custom65` | `string` | Custom field 65 |
| `data[].custom66` | `string` | Custom field 66 |
| `data[].custom67` | `string` | Custom field 67 |
| `data[].custom68` | `string` | Custom field 68 |
| `data[].custom69` | `string` | Custom field 69 |
| `data[].custom7` | `string` | Custom field 7 |
| `data[].custom70` | `string` | Custom field 70 |
| `data[].custom71` | `string` | Custom field 71 |
| `data[].custom72` | `string` | Custom field 72 |
| `data[].custom73` | `string` | Custom field 73 |
| `data[].custom74` | `string` | Custom field 74 |
| `data[].custom75` | `string` | Custom field 75 |
| `data[].custom76` | `string` | Custom field 76 |
| `data[].custom77` | `string` | Custom field 77 |
| `data[].custom78` | `string` | Custom field 78 |
| `data[].custom79` | `string` | Custom field 79 |
| `data[].custom8` | `string` | Custom field 8 |
| `data[].custom80` | `string` | Custom field 80 |
| `data[].custom81` | `string` | Custom field 81 |
| `data[].custom82` | `string` | Custom field 82 |
| `data[].custom83` | `string` | Custom field 83 |
| `data[].custom84` | `string` | Custom field 84 |
| `data[].custom85` | `string` | Custom field 85 |
| `data[].custom86` | `string` | Custom field 86 |
| `data[].custom87` | `string` | Custom field 87 |
| `data[].custom88` | `string` | Custom field 88 |
| `data[].custom89` | `string` | Custom field 89 |
| `data[].custom9` | `string` | Custom field 9 |
| `data[].custom90` | `string` | Custom field 90 |
| `data[].custom91` | `string` | Custom field 91 |
| `data[].custom92` | `string` | Custom field 92 |
| `data[].custom93` | `string` | Custom field 93 |
| `data[].custom94` | `string` | Custom field 94 |
| `data[].custom95` | `string` | Custom field 95 |
| `data[].custom96` | `string` | Custom field 96 |
| `data[].custom97` | `string` | Custom field 97 |
| `data[].custom98` | `string` | Custom field 98 |
| `data[].custom99` | `string` | Custom field 99 |
| `data[].dateOfBirth` | `string` | Date of birth |
| `data[].defaultPluginMapping` | `array` | Default plugin mapping |
| `data[].degree` | `string` | Degree |
| `data[].emailAddresses` | `array` | Email addresses |
| `data[].emailContacts` | `array` | Email contacts |
| `data[].emailOptedOut` | `boolean` | Email opted out |
| `data[].emails` | `array` | Emails |
| `data[].emailsOptStatus` | `string` | Emails opt status |
| `data[].emailsOptedAt` | `string` | Emails opted at |
| `data[].engagedAt` | `string` | Engaged at |
| `data[].engagedScore` | `number` | Engaged score |
| `data[].eventName` | `string` | Event name |
| `data[].externalId` | `string` | External id |
| `data[].externalOwner` | `string` | External owner |
| `data[].externalSource` | `string` | External source |
| `data[].facebookUrl` | `string` | Facebook url |
| `data[].favorites` | `array` | Favorites |
| `data[].firstName` | `string` | First name |
| `data[].gender` | `string` | Gender |
| `data[].githubUrl` | `string` | Github url |
| `data[].githubUsername` | `string` | Github username |
| `data[].googlePlusUrl` | `string` | Google plus url |
| `data[].graduationDate` | `string` | Graduation date |
| `data[].homePhones` | `array` | Home phones |
| `data[].id` | `integer` | Unique prospect identifier |
| `data[].jobStartDate` | `string` | Job start date |
| `data[].lastName` | `string` | Last name |
| `data[].linkedInConnections` | `integer` | Linked in connections |
| `data[].linkedInId` | `string` | Linked in id |
| `data[].linkedInSlug` | `string` | Linked in slug |
| `data[].linkedInUrl` | `string` | Linked in url |
| `data[].mailings` | `array` | Mailings |
| `data[].middleName` | `string` | Middle name |
| `data[].mobilePhones` | `array` | Mobile phones |
| `data[].name` | `string` | Name |
| `data[].nickname` | `string` | Nickname |
| `data[].occupation` | `string` | Occupation |
| `data[].openCount` | `integer` | Open count |
| `data[].opportunities` | `array` | Opportunities |
| `data[].opportunityProspectRoles` | `array` | Opportunity prospect roles |
| `data[].optedOut` | `boolean` | Opted out |
| `data[].optedOutAt` | `string` | Opted out at |
| `data[].otherPhones` | `array` | Other phones |
| `data[].owner` | `array` | Owner |
| `data[].persona` | `array` | Persona |
| `data[].personaName` | `string` | Persona name |
| `data[].personalNote1` | `string` | Personal note1 |
| `data[].personalNote2` | `string` | Personal note2 |
| `data[].phoneNumbers` | `array` | Phone numbers |
| `data[].preferredContact` | `string` | Preferred contact |
| `data[].quoraUrl` | `string` | Quora url |
| `data[].region` | `string` | Region |
| `data[].replyCount` | `integer` | Reply count |
| `data[].school` | `string` | School |
| `data[].score` | `number` | Score |
| `data[].sequenceStates` | `array` | Sequence states |
| `data[].sharingTeamId` | `string` | Sharing team id |
| `data[].smsOptStatus` | `string` | Sms opt status |
| `data[].smsOptedAt` | `string` | Sms opted at |
| `data[].smsOptedOut` | `boolean` | Sms opted out |
| `data[].source` | `string` | Source |
| `data[].specialties` | `string` | Specialties |
| `data[].stackOverflowId` | `string` | Stack overflow id |
| `data[].stackOverflowUrl` | `string` | Stack overflow url |
| `data[].stage` | `array` | Stage |
| `data[].stageName` | `string` | Stage name |
| `data[].tags` | `array` | Tags |
| `data[].tasks` | `array` | Tasks |
| `data[].timeZone` | `string` | Time zone |
| `data[].timeZoneIana` | `string` | Time zone iana |
| `data[].timeZoneInferred` | `string` | Time zone inferred |
| `data[].title` | `string` | Title |
| `data[].touchedAt` | `string` | Touched at |
| `data[].trashedAt` | `string` | Trashed at |
| `data[].trashedByAccount` | `array` | Trashed by account |
| `data[].twitterUrl` | `string` | Twitter url |
| `data[].twitterUsername` | `string` | Twitter username |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |
| `data[].updaterId` | `integer` | Updater id |
| `data[].updaterType` | `string` | Updater type |
| `data[].voipPhones` | `array` | Voip phones |
| `data[].websiteUrl1` | `string` | Website url1 |
| `data[].websiteUrl2` | `string` | Website url2 |
| `data[].websiteUrl3` | `string` | Website url3 |
| `data[].workPhones` | `array` | Work phones |

</details>

### Prospects Context Store SQL Query

Run a SQL query against prospects records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "prospects",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.prospects.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "prospects",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Accounts

### Accounts List

Returns a paginated list of accounts

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "accounts",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.accounts.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Accounts Get

Get a single account by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "accounts",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.accounts.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Account ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Accounts Context Store Search

Search and filter accounts records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "accounts",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "assignedTeams": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.accounts.context_store_search(
    query={"filter": {"eq": {"assignedTeams": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"assignedTeams": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `assignedTeams` | `array` | Assigned teams |
| `assignedUsers` | `array` | Assigned users |
| `batches` | `array` | Batches |
| `buyerIntentScore` | `number` | Buyer intent score |
| `companyType` | `string` | Company type |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `custom1` | `string` | Custom field 1 |
| `custom10` | `string` | Custom field 10 |
| `custom100` | `string` | Custom field 100 |
| `custom101` | `string` | Custom field 101 |
| `custom102` | `string` | Custom field 102 |
| `custom103` | `string` | Custom field 103 |
| `custom104` | `string` | Custom field 104 |
| `custom105` | `string` | Custom field 105 |
| `custom106` | `string` | Custom field 106 |
| `custom107` | `string` | Custom field 107 |
| `custom108` | `string` | Custom field 108 |
| `custom109` | `string` | Custom field 109 |
| `custom11` | `string` | Custom field 11 |
| `custom110` | `string` | Custom field 110 |
| `custom111` | `string` | Custom field 111 |
| `custom112` | `string` | Custom field 112 |
| `custom113` | `string` | Custom field 113 |
| `custom114` | `string` | Custom field 114 |
| `custom115` | `string` | Custom field 115 |
| `custom116` | `string` | Custom field 116 |
| `custom117` | `string` | Custom field 117 |
| `custom118` | `string` | Custom field 118 |
| `custom119` | `string` | Custom field 119 |
| `custom12` | `string` | Custom field 12 |
| `custom120` | `string` | Custom field 120 |
| `custom121` | `string` | Custom field 121 |
| `custom122` | `string` | Custom field 122 |
| `custom123` | `string` | Custom field 123 |
| `custom124` | `string` | Custom field 124 |
| `custom125` | `string` | Custom field 125 |
| `custom126` | `string` | Custom field 126 |
| `custom127` | `string` | Custom field 127 |
| `custom128` | `string` | Custom field 128 |
| `custom129` | `string` | Custom field 129 |
| `custom13` | `string` | Custom field 13 |
| `custom130` | `string` | Custom field 130 |
| `custom131` | `string` | Custom field 131 |
| `custom132` | `string` | Custom field 132 |
| `custom133` | `string` | Custom field 133 |
| `custom134` | `string` | Custom field 134 |
| `custom135` | `string` | Custom field 135 |
| `custom136` | `string` | Custom field 136 |
| `custom137` | `string` | Custom field 137 |
| `custom138` | `string` | Custom field 138 |
| `custom139` | `string` | Custom field 139 |
| `custom14` | `string` | Custom field 14 |
| `custom140` | `string` | Custom field 140 |
| `custom141` | `string` | Custom field 141 |
| `custom142` | `string` | Custom field 142 |
| `custom143` | `string` | Custom field 143 |
| `custom144` | `string` | Custom field 144 |
| `custom145` | `string` | Custom field 145 |
| `custom146` | `string` | Custom field 146 |
| `custom147` | `string` | Custom field 147 |
| `custom148` | `string` | Custom field 148 |
| `custom149` | `string` | Custom field 149 |
| `custom15` | `string` | Custom field 15 |
| `custom150` | `string` | Custom field 150 |
| `custom16` | `string` | Custom field 16 |
| `custom17` | `string` | Custom field 17 |
| `custom18` | `string` | Custom field 18 |
| `custom19` | `string` | Custom field 19 |
| `custom2` | `string` | Custom field 2 |
| `custom20` | `string` | Custom field 20 |
| `custom21` | `string` | Custom field 21 |
| `custom22` | `string` | Custom field 22 |
| `custom23` | `string` | Custom field 23 |
| `custom24` | `string` | Custom field 24 |
| `custom25` | `string` | Custom field 25 |
| `custom26` | `string` | Custom field 26 |
| `custom27` | `string` | Custom field 27 |
| `custom28` | `string` | Custom field 28 |
| `custom29` | `string` | Custom field 29 |
| `custom3` | `string` | Custom field 3 |
| `custom30` | `string` | Custom field 30 |
| `custom31` | `string` | Custom field 31 |
| `custom32` | `string` | Custom field 32 |
| `custom33` | `string` | Custom field 33 |
| `custom34` | `string` | Custom field 34 |
| `custom35` | `string` | Custom field 35 |
| `custom36` | `string` | Custom field 36 |
| `custom37` | `string` | Custom field 37 |
| `custom38` | `string` | Custom field 38 |
| `custom39` | `string` | Custom field 39 |
| `custom4` | `string` | Custom field 4 |
| `custom40` | `string` | Custom field 40 |
| `custom41` | `string` | Custom field 41 |
| `custom42` | `string` | Custom field 42 |
| `custom43` | `string` | Custom field 43 |
| `custom44` | `string` | Custom field 44 |
| `custom45` | `string` | Custom field 45 |
| `custom46` | `string` | Custom field 46 |
| `custom47` | `string` | Custom field 47 |
| `custom48` | `string` | Custom field 48 |
| `custom49` | `string` | Custom field 49 |
| `custom5` | `string` | Custom field 5 |
| `custom50` | `string` | Custom field 50 |
| `custom51` | `string` | Custom field 51 |
| `custom52` | `string` | Custom field 52 |
| `custom53` | `string` | Custom field 53 |
| `custom54` | `string` | Custom field 54 |
| `custom55` | `string` | Custom field 55 |
| `custom56` | `string` | Custom field 56 |
| `custom57` | `string` | Custom field 57 |
| `custom58` | `string` | Custom field 58 |
| `custom59` | `string` | Custom field 59 |
| `custom6` | `string` | Custom field 6 |
| `custom60` | `string` | Custom field 60 |
| `custom61` | `string` | Custom field 61 |
| `custom62` | `string` | Custom field 62 |
| `custom63` | `string` | Custom field 63 |
| `custom64` | `string` | Custom field 64 |
| `custom65` | `string` | Custom field 65 |
| `custom66` | `string` | Custom field 66 |
| `custom67` | `string` | Custom field 67 |
| `custom68` | `string` | Custom field 68 |
| `custom69` | `string` | Custom field 69 |
| `custom7` | `string` | Custom field 7 |
| `custom70` | `string` | Custom field 70 |
| `custom71` | `string` | Custom field 71 |
| `custom72` | `string` | Custom field 72 |
| `custom73` | `string` | Custom field 73 |
| `custom74` | `string` | Custom field 74 |
| `custom75` | `string` | Custom field 75 |
| `custom76` | `string` | Custom field 76 |
| `custom77` | `string` | Custom field 77 |
| `custom78` | `string` | Custom field 78 |
| `custom79` | `string` | Custom field 79 |
| `custom8` | `string` | Custom field 8 |
| `custom80` | `string` | Custom field 80 |
| `custom81` | `string` | Custom field 81 |
| `custom82` | `string` | Custom field 82 |
| `custom83` | `string` | Custom field 83 |
| `custom84` | `string` | Custom field 84 |
| `custom85` | `string` | Custom field 85 |
| `custom86` | `string` | Custom field 86 |
| `custom87` | `string` | Custom field 87 |
| `custom88` | `string` | Custom field 88 |
| `custom89` | `string` | Custom field 89 |
| `custom9` | `string` | Custom field 9 |
| `custom90` | `string` | Custom field 90 |
| `custom91` | `string` | Custom field 91 |
| `custom92` | `string` | Custom field 92 |
| `custom93` | `string` | Custom field 93 |
| `custom94` | `string` | Custom field 94 |
| `custom95` | `string` | Custom field 95 |
| `custom96` | `string` | Custom field 96 |
| `custom97` | `string` | Custom field 97 |
| `custom98` | `string` | Custom field 98 |
| `custom99` | `string` | Custom field 99 |
| `customId` | `string` | Custom id |
| `defaultPluginMapping` | `array` | Default plugin mapping |
| `description` | `string` | Description |
| `domain` | `string` | Domain |
| `externalSource` | `string` | External source |
| `favorites` | `array` | Favorites |
| `followers` | `integer` | Followers |
| `foundedAt` | `string` | Founded at |
| `id` | `integer` | Unique account identifier |
| `industry` | `string` | Industry |
| `linkedInEmployees` | `integer` | Linked in employees |
| `linkedInUrl` | `string` | Linked in url |
| `locality` | `string` | Locality |
| `name` | `string` | Name |
| `named` | `boolean` | Named |
| `naturalName` | `string` | Natural name |
| `numberOfEmployees` | `integer` | Number of employees |
| `owner` | `array` | Owner |
| `prospects` | `array` | Prospects |
| `sharingTeamId` | `string` | Sharing team id |
| `tags` | `array` | Tags |
| `tasks` | `array` | Tasks |
| `touchedAt` | `string` | Touched at |
| `trashedAt` | `string` | Trashed at |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |
| `websiteUrl` | `string` | Website url |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].assignedTeams` | `array` | Assigned teams |
| `data[].assignedUsers` | `array` | Assigned users |
| `data[].batches` | `array` | Batches |
| `data[].buyerIntentScore` | `number` | Buyer intent score |
| `data[].companyType` | `string` | Company type |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].custom1` | `string` | Custom field 1 |
| `data[].custom10` | `string` | Custom field 10 |
| `data[].custom100` | `string` | Custom field 100 |
| `data[].custom101` | `string` | Custom field 101 |
| `data[].custom102` | `string` | Custom field 102 |
| `data[].custom103` | `string` | Custom field 103 |
| `data[].custom104` | `string` | Custom field 104 |
| `data[].custom105` | `string` | Custom field 105 |
| `data[].custom106` | `string` | Custom field 106 |
| `data[].custom107` | `string` | Custom field 107 |
| `data[].custom108` | `string` | Custom field 108 |
| `data[].custom109` | `string` | Custom field 109 |
| `data[].custom11` | `string` | Custom field 11 |
| `data[].custom110` | `string` | Custom field 110 |
| `data[].custom111` | `string` | Custom field 111 |
| `data[].custom112` | `string` | Custom field 112 |
| `data[].custom113` | `string` | Custom field 113 |
| `data[].custom114` | `string` | Custom field 114 |
| `data[].custom115` | `string` | Custom field 115 |
| `data[].custom116` | `string` | Custom field 116 |
| `data[].custom117` | `string` | Custom field 117 |
| `data[].custom118` | `string` | Custom field 118 |
| `data[].custom119` | `string` | Custom field 119 |
| `data[].custom12` | `string` | Custom field 12 |
| `data[].custom120` | `string` | Custom field 120 |
| `data[].custom121` | `string` | Custom field 121 |
| `data[].custom122` | `string` | Custom field 122 |
| `data[].custom123` | `string` | Custom field 123 |
| `data[].custom124` | `string` | Custom field 124 |
| `data[].custom125` | `string` | Custom field 125 |
| `data[].custom126` | `string` | Custom field 126 |
| `data[].custom127` | `string` | Custom field 127 |
| `data[].custom128` | `string` | Custom field 128 |
| `data[].custom129` | `string` | Custom field 129 |
| `data[].custom13` | `string` | Custom field 13 |
| `data[].custom130` | `string` | Custom field 130 |
| `data[].custom131` | `string` | Custom field 131 |
| `data[].custom132` | `string` | Custom field 132 |
| `data[].custom133` | `string` | Custom field 133 |
| `data[].custom134` | `string` | Custom field 134 |
| `data[].custom135` | `string` | Custom field 135 |
| `data[].custom136` | `string` | Custom field 136 |
| `data[].custom137` | `string` | Custom field 137 |
| `data[].custom138` | `string` | Custom field 138 |
| `data[].custom139` | `string` | Custom field 139 |
| `data[].custom14` | `string` | Custom field 14 |
| `data[].custom140` | `string` | Custom field 140 |
| `data[].custom141` | `string` | Custom field 141 |
| `data[].custom142` | `string` | Custom field 142 |
| `data[].custom143` | `string` | Custom field 143 |
| `data[].custom144` | `string` | Custom field 144 |
| `data[].custom145` | `string` | Custom field 145 |
| `data[].custom146` | `string` | Custom field 146 |
| `data[].custom147` | `string` | Custom field 147 |
| `data[].custom148` | `string` | Custom field 148 |
| `data[].custom149` | `string` | Custom field 149 |
| `data[].custom15` | `string` | Custom field 15 |
| `data[].custom150` | `string` | Custom field 150 |
| `data[].custom16` | `string` | Custom field 16 |
| `data[].custom17` | `string` | Custom field 17 |
| `data[].custom18` | `string` | Custom field 18 |
| `data[].custom19` | `string` | Custom field 19 |
| `data[].custom2` | `string` | Custom field 2 |
| `data[].custom20` | `string` | Custom field 20 |
| `data[].custom21` | `string` | Custom field 21 |
| `data[].custom22` | `string` | Custom field 22 |
| `data[].custom23` | `string` | Custom field 23 |
| `data[].custom24` | `string` | Custom field 24 |
| `data[].custom25` | `string` | Custom field 25 |
| `data[].custom26` | `string` | Custom field 26 |
| `data[].custom27` | `string` | Custom field 27 |
| `data[].custom28` | `string` | Custom field 28 |
| `data[].custom29` | `string` | Custom field 29 |
| `data[].custom3` | `string` | Custom field 3 |
| `data[].custom30` | `string` | Custom field 30 |
| `data[].custom31` | `string` | Custom field 31 |
| `data[].custom32` | `string` | Custom field 32 |
| `data[].custom33` | `string` | Custom field 33 |
| `data[].custom34` | `string` | Custom field 34 |
| `data[].custom35` | `string` | Custom field 35 |
| `data[].custom36` | `string` | Custom field 36 |
| `data[].custom37` | `string` | Custom field 37 |
| `data[].custom38` | `string` | Custom field 38 |
| `data[].custom39` | `string` | Custom field 39 |
| `data[].custom4` | `string` | Custom field 4 |
| `data[].custom40` | `string` | Custom field 40 |
| `data[].custom41` | `string` | Custom field 41 |
| `data[].custom42` | `string` | Custom field 42 |
| `data[].custom43` | `string` | Custom field 43 |
| `data[].custom44` | `string` | Custom field 44 |
| `data[].custom45` | `string` | Custom field 45 |
| `data[].custom46` | `string` | Custom field 46 |
| `data[].custom47` | `string` | Custom field 47 |
| `data[].custom48` | `string` | Custom field 48 |
| `data[].custom49` | `string` | Custom field 49 |
| `data[].custom5` | `string` | Custom field 5 |
| `data[].custom50` | `string` | Custom field 50 |
| `data[].custom51` | `string` | Custom field 51 |
| `data[].custom52` | `string` | Custom field 52 |
| `data[].custom53` | `string` | Custom field 53 |
| `data[].custom54` | `string` | Custom field 54 |
| `data[].custom55` | `string` | Custom field 55 |
| `data[].custom56` | `string` | Custom field 56 |
| `data[].custom57` | `string` | Custom field 57 |
| `data[].custom58` | `string` | Custom field 58 |
| `data[].custom59` | `string` | Custom field 59 |
| `data[].custom6` | `string` | Custom field 6 |
| `data[].custom60` | `string` | Custom field 60 |
| `data[].custom61` | `string` | Custom field 61 |
| `data[].custom62` | `string` | Custom field 62 |
| `data[].custom63` | `string` | Custom field 63 |
| `data[].custom64` | `string` | Custom field 64 |
| `data[].custom65` | `string` | Custom field 65 |
| `data[].custom66` | `string` | Custom field 66 |
| `data[].custom67` | `string` | Custom field 67 |
| `data[].custom68` | `string` | Custom field 68 |
| `data[].custom69` | `string` | Custom field 69 |
| `data[].custom7` | `string` | Custom field 7 |
| `data[].custom70` | `string` | Custom field 70 |
| `data[].custom71` | `string` | Custom field 71 |
| `data[].custom72` | `string` | Custom field 72 |
| `data[].custom73` | `string` | Custom field 73 |
| `data[].custom74` | `string` | Custom field 74 |
| `data[].custom75` | `string` | Custom field 75 |
| `data[].custom76` | `string` | Custom field 76 |
| `data[].custom77` | `string` | Custom field 77 |
| `data[].custom78` | `string` | Custom field 78 |
| `data[].custom79` | `string` | Custom field 79 |
| `data[].custom8` | `string` | Custom field 8 |
| `data[].custom80` | `string` | Custom field 80 |
| `data[].custom81` | `string` | Custom field 81 |
| `data[].custom82` | `string` | Custom field 82 |
| `data[].custom83` | `string` | Custom field 83 |
| `data[].custom84` | `string` | Custom field 84 |
| `data[].custom85` | `string` | Custom field 85 |
| `data[].custom86` | `string` | Custom field 86 |
| `data[].custom87` | `string` | Custom field 87 |
| `data[].custom88` | `string` | Custom field 88 |
| `data[].custom89` | `string` | Custom field 89 |
| `data[].custom9` | `string` | Custom field 9 |
| `data[].custom90` | `string` | Custom field 90 |
| `data[].custom91` | `string` | Custom field 91 |
| `data[].custom92` | `string` | Custom field 92 |
| `data[].custom93` | `string` | Custom field 93 |
| `data[].custom94` | `string` | Custom field 94 |
| `data[].custom95` | `string` | Custom field 95 |
| `data[].custom96` | `string` | Custom field 96 |
| `data[].custom97` | `string` | Custom field 97 |
| `data[].custom98` | `string` | Custom field 98 |
| `data[].custom99` | `string` | Custom field 99 |
| `data[].customId` | `string` | Custom id |
| `data[].defaultPluginMapping` | `array` | Default plugin mapping |
| `data[].description` | `string` | Description |
| `data[].domain` | `string` | Domain |
| `data[].externalSource` | `string` | External source |
| `data[].favorites` | `array` | Favorites |
| `data[].followers` | `integer` | Followers |
| `data[].foundedAt` | `string` | Founded at |
| `data[].id` | `integer` | Unique account identifier |
| `data[].industry` | `string` | Industry |
| `data[].linkedInEmployees` | `integer` | Linked in employees |
| `data[].linkedInUrl` | `string` | Linked in url |
| `data[].locality` | `string` | Locality |
| `data[].name` | `string` | Name |
| `data[].named` | `boolean` | Named |
| `data[].naturalName` | `string` | Natural name |
| `data[].numberOfEmployees` | `integer` | Number of employees |
| `data[].owner` | `array` | Owner |
| `data[].prospects` | `array` | Prospects |
| `data[].sharingTeamId` | `string` | Sharing team id |
| `data[].tags` | `array` | Tags |
| `data[].tasks` | `array` | Tasks |
| `data[].touchedAt` | `string` | Touched at |
| `data[].trashedAt` | `string` | Trashed at |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |
| `data[].websiteUrl` | `string` | Website url |

</details>

### Accounts Context Store SQL Query

Run a SQL query against accounts records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "accounts",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.accounts.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "accounts",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Sequences

### Sequences List

Returns a paginated list of sequences

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequences",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.sequences.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequences",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Sequences Get

Get a single sequence by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequences",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.sequences.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequences",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Sequence ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Sequences Context Store Search

Search and filter sequences records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequences",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "automationPercentage": 0.0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.sequences.context_store_search(
    query={"filter": {"eq": {"automationPercentage": 0.0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequences",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"automationPercentage": 0.0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `automationPercentage` | `number` | Automation percentage |
| `bounceCount` | `integer` | Bounce count |
| `calls` | `array` | Calls |
| `clickCount` | `integer` | Click count |
| `contentCategoryMemberships` | `array` | Content category memberships |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `deliverCount` | `integer` | Deliver count |
| `description` | `string` | Description |
| `durationInDays` | `integer` | Duration in days |
| `enabled` | `boolean` | Enabled |
| `enabledAt` | `string` | Enabled at |
| `failureCount` | `integer` | Failure count |
| `finishOnReply` | `boolean` | Finish on reply |
| `id` | `integer` | Unique sequence identifier |
| `lastUsedAt` | `string` | Last used at |
| `locked` | `boolean` | Locked |
| `lockedAt` | `string` | Locked at |
| `mailings` | `array` | Mailings |
| `maxActivations` | `integer` | Max activations |
| `name` | `string` | Name |
| `negativeReplyCount` | `integer` | Negative reply count |
| `neutralReplyCount` | `integer` | Neutral reply count |
| `numContactedProspects` | `integer` | Num contacted prospects |
| `numRepliedProspects` | `integer` | Num replied prospects |
| `openCount` | `integer` | Open count |
| `optOutCount` | `integer` | Opt out count |
| `owner` | `array` | Owner |
| `positiveReplyCount` | `integer` | Positive reply count |
| `primaryReplyAction` | `string` | Primary reply action |
| `primaryReplyPauseDuration` | `integer` | Primary reply pause duration |
| `replyCount` | `integer` | Reply count |
| `ruleset` | `array` | Ruleset |
| `schedule` | `array` | Schedule |
| `scheduleCount` | `integer` | Schedule count |
| `scheduleIntervalType` | `string` | Schedule interval type |
| `secondaryReplyAction` | `string` | Secondary reply action |
| `secondaryReplyPauseDuration` | `integer` | Secondary reply pause duration |
| `sequenceStates` | `array` | Sequence states |
| `sequenceStepCount` | `integer` | Sequence step count |
| `sequenceSteps` | `array` | Sequence steps |
| `sequenceType` | `string` | Sequence type |
| `shareType` | `string` | Share type |
| `tags` | `array` | Tags |
| `tasks` | `array` | Tasks |
| `throttleCapacity` | `integer` | Throttle capacity |
| `throttleMaxAddsPerDay` | `integer` | Throttle max adds per day |
| `throttlePaused` | `boolean` | Throttle paused |
| `throttlePausedAt` | `string` | Throttle paused at |
| `transactional` | `boolean` | Transactional |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].automationPercentage` | `number` | Automation percentage |
| `data[].bounceCount` | `integer` | Bounce count |
| `data[].calls` | `array` | Calls |
| `data[].clickCount` | `integer` | Click count |
| `data[].contentCategoryMemberships` | `array` | Content category memberships |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].deliverCount` | `integer` | Deliver count |
| `data[].description` | `string` | Description |
| `data[].durationInDays` | `integer` | Duration in days |
| `data[].enabled` | `boolean` | Enabled |
| `data[].enabledAt` | `string` | Enabled at |
| `data[].failureCount` | `integer` | Failure count |
| `data[].finishOnReply` | `boolean` | Finish on reply |
| `data[].id` | `integer` | Unique sequence identifier |
| `data[].lastUsedAt` | `string` | Last used at |
| `data[].locked` | `boolean` | Locked |
| `data[].lockedAt` | `string` | Locked at |
| `data[].mailings` | `array` | Mailings |
| `data[].maxActivations` | `integer` | Max activations |
| `data[].name` | `string` | Name |
| `data[].negativeReplyCount` | `integer` | Negative reply count |
| `data[].neutralReplyCount` | `integer` | Neutral reply count |
| `data[].numContactedProspects` | `integer` | Num contacted prospects |
| `data[].numRepliedProspects` | `integer` | Num replied prospects |
| `data[].openCount` | `integer` | Open count |
| `data[].optOutCount` | `integer` | Opt out count |
| `data[].owner` | `array` | Owner |
| `data[].positiveReplyCount` | `integer` | Positive reply count |
| `data[].primaryReplyAction` | `string` | Primary reply action |
| `data[].primaryReplyPauseDuration` | `integer` | Primary reply pause duration |
| `data[].replyCount` | `integer` | Reply count |
| `data[].ruleset` | `array` | Ruleset |
| `data[].schedule` | `array` | Schedule |
| `data[].scheduleCount` | `integer` | Schedule count |
| `data[].scheduleIntervalType` | `string` | Schedule interval type |
| `data[].secondaryReplyAction` | `string` | Secondary reply action |
| `data[].secondaryReplyPauseDuration` | `integer` | Secondary reply pause duration |
| `data[].sequenceStates` | `array` | Sequence states |
| `data[].sequenceStepCount` | `integer` | Sequence step count |
| `data[].sequenceSteps` | `array` | Sequence steps |
| `data[].sequenceType` | `string` | Sequence type |
| `data[].shareType` | `string` | Share type |
| `data[].tags` | `array` | Tags |
| `data[].tasks` | `array` | Tasks |
| `data[].throttleCapacity` | `integer` | Throttle capacity |
| `data[].throttleMaxAddsPerDay` | `integer` | Throttle max adds per day |
| `data[].throttlePaused` | `boolean` | Throttle paused |
| `data[].throttlePausedAt` | `string` | Throttle paused at |
| `data[].transactional` | `boolean` | Transactional |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |

</details>

### Sequences Context Store SQL Query

Run a SQL query against sequences records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequences",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.sequences.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequences",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Sequence States

### Sequence States List

Returns a paginated list of sequence states (prospect-in-sequence associations)

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequence_states",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.sequence_states.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequence_states",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Sequence States Get

Get a single sequence state by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequence_states",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.sequence_states.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequence_states",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Sequence State ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |


</details>

### Sequence States Context Store Search

Search and filter sequence states records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequence_states",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "account": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.sequence_states.context_store_search(
    query={"filter": {"eq": {"account": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequence_states",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"account": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `account` | `array` | Account |
| `activeAt` | `string` | Active at |
| `activeStepMailings` | `array` | Active step mailings |
| `activeStepTasks` | `array` | Active step tasks |
| `bounceCount` | `integer` | Bounce count |
| `callCompletedAt` | `string` | Call completed at |
| `calls` | `array` | Calls |
| `clickCount` | `integer` | Click count |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `deliverCount` | `integer` | Deliver count |
| `errorReason` | `string` | Error reason |
| `failureCount` | `integer` | Failure count |
| `id` | `integer` | Unique sequence state identifier |
| `mailbox` | `array` | Mailbox |
| `mailings` | `array` | Mailings |
| `negativeReplyCount` | `integer` | Negative reply count |
| `neutralReplyCount` | `integer` | Neutral reply count |
| `openCount` | `integer` | Open count |
| `opportunity` | `array` | Opportunity |
| `optOutCount` | `integer` | Opt out count |
| `pauseReason` | `string` | Pause reason |
| `positiveReplyCount` | `integer` | Positive reply count |
| `prospect` | `array` | Prospect |
| `repliedAt` | `string` | Replied at |
| `replyCount` | `integer` | Reply count |
| `scheduleCount` | `integer` | Schedule count |
| `sequence` | `array` | Sequence |
| `sequenceStep` | `array` | Sequence step |
| `state` | `string` | State |
| `stateChangedAt` | `string` | State changed at |
| `tasks` | `array` | Tasks |
| `updatedAt` | `string` | Updated at |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account` | `array` | Account |
| `data[].activeAt` | `string` | Active at |
| `data[].activeStepMailings` | `array` | Active step mailings |
| `data[].activeStepTasks` | `array` | Active step tasks |
| `data[].bounceCount` | `integer` | Bounce count |
| `data[].callCompletedAt` | `string` | Call completed at |
| `data[].calls` | `array` | Calls |
| `data[].clickCount` | `integer` | Click count |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].deliverCount` | `integer` | Deliver count |
| `data[].errorReason` | `string` | Error reason |
| `data[].failureCount` | `integer` | Failure count |
| `data[].id` | `integer` | Unique sequence state identifier |
| `data[].mailbox` | `array` | Mailbox |
| `data[].mailings` | `array` | Mailings |
| `data[].negativeReplyCount` | `integer` | Negative reply count |
| `data[].neutralReplyCount` | `integer` | Neutral reply count |
| `data[].openCount` | `integer` | Open count |
| `data[].opportunity` | `array` | Opportunity |
| `data[].optOutCount` | `integer` | Opt out count |
| `data[].pauseReason` | `string` | Pause reason |
| `data[].positiveReplyCount` | `integer` | Positive reply count |
| `data[].prospect` | `array` | Prospect |
| `data[].repliedAt` | `string` | Replied at |
| `data[].replyCount` | `integer` | Reply count |
| `data[].scheduleCount` | `integer` | Schedule count |
| `data[].sequence` | `array` | Sequence |
| `data[].sequenceStep` | `array` | Sequence step |
| `data[].state` | `string` | State |
| `data[].stateChangedAt` | `string` | State changed at |
| `data[].tasks` | `array` | Tasks |
| `data[].updatedAt` | `string` | Updated at |

</details>

### Sequence States Context Store SQL Query

Run a SQL query against sequence states records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequence_states",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.sequence_states.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequence_states",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Sequence Steps

### Sequence Steps List

Returns a paginated list of sequence steps

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequence_steps",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.sequence_steps.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequence_steps",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Sequence Steps Get

Get a single sequence step by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequence_steps",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.sequence_steps.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequence_steps",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Sequence Step ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Sequence Steps Context Store Search

Search and filter sequence steps records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequence_steps",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "bounceCount": 0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.sequence_steps.context_store_search(
    query={"filter": {"eq": {"bounceCount": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequence_steps",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"bounceCount": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `bounceCount` | `integer` | Bounce count |
| `callPurpose` | `array` | Call purpose |
| `calls` | `array` | Calls |
| `clickCount` | `integer` | Click count |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `date` | `string` | Date |
| `deliverCount` | `integer` | Deliver count |
| `displayName` | `string` | Display name |
| `failureCount` | `integer` | Failure count |
| `id` | `integer` | Unique sequence step identifier |
| `interval` | `integer` | Interval |
| `mailings` | `array` | Mailings |
| `negativeReplyCount` | `integer` | Negative reply count |
| `neutralReplyCount` | `integer` | Neutral reply count |
| `openCount` | `integer` | Open count |
| `optOutCount` | `integer` | Opt out count |
| `order` | `integer` | Order |
| `positiveReplyCount` | `integer` | Positive reply count |
| `replyCount` | `integer` | Reply count |
| `scheduleCount` | `integer` | Schedule count |
| `sequence` | `array` | Sequence |
| `sequenceTemplates` | `array` | Sequence templates |
| `stepType` | `string` | Step type |
| `taskAutoDisplay` | `string` | Task auto display |
| `taskPriority` | `array` | Task priority |
| `tasks` | `array` | Tasks |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].bounceCount` | `integer` | Bounce count |
| `data[].callPurpose` | `array` | Call purpose |
| `data[].calls` | `array` | Calls |
| `data[].clickCount` | `integer` | Click count |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].date` | `string` | Date |
| `data[].deliverCount` | `integer` | Deliver count |
| `data[].displayName` | `string` | Display name |
| `data[].failureCount` | `integer` | Failure count |
| `data[].id` | `integer` | Unique sequence step identifier |
| `data[].interval` | `integer` | Interval |
| `data[].mailings` | `array` | Mailings |
| `data[].negativeReplyCount` | `integer` | Negative reply count |
| `data[].neutralReplyCount` | `integer` | Neutral reply count |
| `data[].openCount` | `integer` | Open count |
| `data[].optOutCount` | `integer` | Opt out count |
| `data[].order` | `integer` | Order |
| `data[].positiveReplyCount` | `integer` | Positive reply count |
| `data[].replyCount` | `integer` | Reply count |
| `data[].scheduleCount` | `integer` | Schedule count |
| `data[].sequence` | `array` | Sequence |
| `data[].sequenceTemplates` | `array` | Sequence templates |
| `data[].stepType` | `string` | Step type |
| `data[].taskAutoDisplay` | `string` | Task auto display |
| `data[].taskPriority` | `array` | Task priority |
| `data[].tasks` | `array` | Tasks |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |

</details>

### Sequence Steps Context Store SQL Query

Run a SQL query against sequence steps records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "sequence_steps",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.sequence_steps.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "sequence_steps",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Opportunities

### Opportunities List

Returns a paginated list of opportunities

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "opportunities",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.opportunities.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Opportunities Get

Get a single opportunity by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "opportunities",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.opportunities.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Opportunity ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Opportunities Context Store Search

Search and filter opportunities records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "opportunities",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "account": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.opportunities.context_store_search(
    query={"filter": {"eq": {"account": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"account": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `account` | `array` | Account |
| `amount` | `integer` | Amount |
| `assignedTeams` | `array` | Assigned teams |
| `assignedUsers` | `array` | Assigned users |
| `closeDate` | `string` | Close date |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `currencyType` | `string` | Currency type |
| `custom1` | `string` | Custom field 1 |
| `custom10` | `string` | Custom field 10 |
| `custom100` | `string` | Custom field 100 |
| `custom101` | `string` | Custom field 101 |
| `custom102` | `string` | Custom field 102 |
| `custom103` | `string` | Custom field 103 |
| `custom104` | `string` | Custom field 104 |
| `custom105` | `string` | Custom field 105 |
| `custom106` | `string` | Custom field 106 |
| `custom107` | `string` | Custom field 107 |
| `custom108` | `string` | Custom field 108 |
| `custom109` | `string` | Custom field 109 |
| `custom11` | `string` | Custom field 11 |
| `custom110` | `string` | Custom field 110 |
| `custom111` | `string` | Custom field 111 |
| `custom112` | `string` | Custom field 112 |
| `custom113` | `string` | Custom field 113 |
| `custom114` | `string` | Custom field 114 |
| `custom115` | `string` | Custom field 115 |
| `custom116` | `string` | Custom field 116 |
| `custom117` | `string` | Custom field 117 |
| `custom118` | `string` | Custom field 118 |
| `custom119` | `string` | Custom field 119 |
| `custom12` | `string` | Custom field 12 |
| `custom120` | `string` | Custom field 120 |
| `custom121` | `string` | Custom field 121 |
| `custom122` | `string` | Custom field 122 |
| `custom123` | `string` | Custom field 123 |
| `custom124` | `string` | Custom field 124 |
| `custom125` | `string` | Custom field 125 |
| `custom126` | `string` | Custom field 126 |
| `custom127` | `string` | Custom field 127 |
| `custom128` | `string` | Custom field 128 |
| `custom129` | `string` | Custom field 129 |
| `custom13` | `string` | Custom field 13 |
| `custom130` | `string` | Custom field 130 |
| `custom131` | `string` | Custom field 131 |
| `custom132` | `string` | Custom field 132 |
| `custom133` | `string` | Custom field 133 |
| `custom134` | `string` | Custom field 134 |
| `custom135` | `string` | Custom field 135 |
| `custom136` | `string` | Custom field 136 |
| `custom137` | `string` | Custom field 137 |
| `custom138` | `string` | Custom field 138 |
| `custom139` | `string` | Custom field 139 |
| `custom14` | `string` | Custom field 14 |
| `custom140` | `string` | Custom field 140 |
| `custom141` | `string` | Custom field 141 |
| `custom142` | `string` | Custom field 142 |
| `custom143` | `string` | Custom field 143 |
| `custom144` | `string` | Custom field 144 |
| `custom145` | `string` | Custom field 145 |
| `custom146` | `string` | Custom field 146 |
| `custom147` | `string` | Custom field 147 |
| `custom148` | `string` | Custom field 148 |
| `custom149` | `string` | Custom field 149 |
| `custom15` | `string` | Custom field 15 |
| `custom150` | `string` | Custom field 150 |
| `custom16` | `string` | Custom field 16 |
| `custom17` | `string` | Custom field 17 |
| `custom18` | `string` | Custom field 18 |
| `custom19` | `string` | Custom field 19 |
| `custom2` | `string` | Custom field 2 |
| `custom20` | `string` | Custom field 20 |
| `custom21` | `string` | Custom field 21 |
| `custom22` | `string` | Custom field 22 |
| `custom23` | `string` | Custom field 23 |
| `custom24` | `string` | Custom field 24 |
| `custom25` | `string` | Custom field 25 |
| `custom26` | `string` | Custom field 26 |
| `custom27` | `string` | Custom field 27 |
| `custom28` | `string` | Custom field 28 |
| `custom29` | `string` | Custom field 29 |
| `custom3` | `string` | Custom field 3 |
| `custom30` | `string` | Custom field 30 |
| `custom31` | `string` | Custom field 31 |
| `custom32` | `string` | Custom field 32 |
| `custom33` | `string` | Custom field 33 |
| `custom34` | `string` | Custom field 34 |
| `custom35` | `string` | Custom field 35 |
| `custom36` | `string` | Custom field 36 |
| `custom37` | `string` | Custom field 37 |
| `custom38` | `string` | Custom field 38 |
| `custom39` | `string` | Custom field 39 |
| `custom4` | `string` | Custom field 4 |
| `custom40` | `string` | Custom field 40 |
| `custom41` | `string` | Custom field 41 |
| `custom42` | `string` | Custom field 42 |
| `custom43` | `string` | Custom field 43 |
| `custom44` | `string` | Custom field 44 |
| `custom45` | `string` | Custom field 45 |
| `custom46` | `string` | Custom field 46 |
| `custom47` | `string` | Custom field 47 |
| `custom48` | `string` | Custom field 48 |
| `custom49` | `string` | Custom field 49 |
| `custom5` | `string` | Custom field 5 |
| `custom50` | `string` | Custom field 50 |
| `custom51` | `string` | Custom field 51 |
| `custom52` | `string` | Custom field 52 |
| `custom53` | `string` | Custom field 53 |
| `custom54` | `string` | Custom field 54 |
| `custom55` | `string` | Custom field 55 |
| `custom56` | `string` | Custom field 56 |
| `custom57` | `string` | Custom field 57 |
| `custom58` | `string` | Custom field 58 |
| `custom59` | `string` | Custom field 59 |
| `custom6` | `string` | Custom field 6 |
| `custom60` | `string` | Custom field 60 |
| `custom61` | `string` | Custom field 61 |
| `custom62` | `string` | Custom field 62 |
| `custom63` | `string` | Custom field 63 |
| `custom64` | `string` | Custom field 64 |
| `custom65` | `string` | Custom field 65 |
| `custom66` | `string` | Custom field 66 |
| `custom67` | `string` | Custom field 67 |
| `custom68` | `string` | Custom field 68 |
| `custom69` | `string` | Custom field 69 |
| `custom7` | `string` | Custom field 7 |
| `custom70` | `string` | Custom field 70 |
| `custom71` | `string` | Custom field 71 |
| `custom72` | `string` | Custom field 72 |
| `custom73` | `string` | Custom field 73 |
| `custom74` | `string` | Custom field 74 |
| `custom75` | `string` | Custom field 75 |
| `custom76` | `string` | Custom field 76 |
| `custom77` | `string` | Custom field 77 |
| `custom78` | `string` | Custom field 78 |
| `custom79` | `string` | Custom field 79 |
| `custom8` | `string` | Custom field 8 |
| `custom80` | `string` | Custom field 80 |
| `custom81` | `string` | Custom field 81 |
| `custom82` | `string` | Custom field 82 |
| `custom83` | `string` | Custom field 83 |
| `custom84` | `string` | Custom field 84 |
| `custom85` | `string` | Custom field 85 |
| `custom86` | `string` | Custom field 86 |
| `custom87` | `string` | Custom field 87 |
| `custom88` | `string` | Custom field 88 |
| `custom89` | `string` | Custom field 89 |
| `custom9` | `string` | Custom field 9 |
| `custom90` | `string` | Custom field 90 |
| `custom91` | `string` | Custom field 91 |
| `custom92` | `string` | Custom field 92 |
| `custom93` | `string` | Custom field 93 |
| `custom94` | `string` | Custom field 94 |
| `custom95` | `string` | Custom field 95 |
| `custom96` | `string` | Custom field 96 |
| `custom97` | `string` | Custom field 97 |
| `custom98` | `string` | Custom field 98 |
| `custom99` | `string` | Custom field 99 |
| `defaultPluginMapping` | `array` | Default plugin mapping |
| `description` | `string` | Description |
| `externalCreatedAt` | `string` | External created at |
| `externalCreator` | `array` | External creator |
| `favorites` | `array` | Favorites |
| `healthCategory` | `string` | Health category |
| `healthScore` | `integer` | Health score |
| `id` | `integer` | Unique opportunity identifier |
| `mapLink` | `string` | Map link |
| `mapNextSteps` | `string` | Map next steps |
| `mapNumberOfOverdueTasks` | `integer` | Map number of overdue tasks |
| `mapStatus` | `string` | Map status |
| `name` | `string` | Name |
| `nextStep` | `string` | Next step |
| `opportunityHealthFactors` | `array` | Opportunity health factors |
| `opportunityStage` | `array` | Opportunity stage |
| `opportunityType` | `string` | Opportunity type |
| `owner` | `array` | Owner |
| `primaryProspect` | `array` | Primary prospect |
| `probability` | `integer` | Probability |
| `prospectingRepId` | `string` | Prospecting rep id |
| `prospects` | `array` | Prospects |
| `sharingTeamId` | `string` | Sharing team id |
| `stage` | `array` | Stage |
| `tags` | `array` | Tags |
| `touchedAt` | `string` | Touched at |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account` | `array` | Account |
| `data[].amount` | `integer` | Amount |
| `data[].assignedTeams` | `array` | Assigned teams |
| `data[].assignedUsers` | `array` | Assigned users |
| `data[].closeDate` | `string` | Close date |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].currencyType` | `string` | Currency type |
| `data[].custom1` | `string` | Custom field 1 |
| `data[].custom10` | `string` | Custom field 10 |
| `data[].custom100` | `string` | Custom field 100 |
| `data[].custom101` | `string` | Custom field 101 |
| `data[].custom102` | `string` | Custom field 102 |
| `data[].custom103` | `string` | Custom field 103 |
| `data[].custom104` | `string` | Custom field 104 |
| `data[].custom105` | `string` | Custom field 105 |
| `data[].custom106` | `string` | Custom field 106 |
| `data[].custom107` | `string` | Custom field 107 |
| `data[].custom108` | `string` | Custom field 108 |
| `data[].custom109` | `string` | Custom field 109 |
| `data[].custom11` | `string` | Custom field 11 |
| `data[].custom110` | `string` | Custom field 110 |
| `data[].custom111` | `string` | Custom field 111 |
| `data[].custom112` | `string` | Custom field 112 |
| `data[].custom113` | `string` | Custom field 113 |
| `data[].custom114` | `string` | Custom field 114 |
| `data[].custom115` | `string` | Custom field 115 |
| `data[].custom116` | `string` | Custom field 116 |
| `data[].custom117` | `string` | Custom field 117 |
| `data[].custom118` | `string` | Custom field 118 |
| `data[].custom119` | `string` | Custom field 119 |
| `data[].custom12` | `string` | Custom field 12 |
| `data[].custom120` | `string` | Custom field 120 |
| `data[].custom121` | `string` | Custom field 121 |
| `data[].custom122` | `string` | Custom field 122 |
| `data[].custom123` | `string` | Custom field 123 |
| `data[].custom124` | `string` | Custom field 124 |
| `data[].custom125` | `string` | Custom field 125 |
| `data[].custom126` | `string` | Custom field 126 |
| `data[].custom127` | `string` | Custom field 127 |
| `data[].custom128` | `string` | Custom field 128 |
| `data[].custom129` | `string` | Custom field 129 |
| `data[].custom13` | `string` | Custom field 13 |
| `data[].custom130` | `string` | Custom field 130 |
| `data[].custom131` | `string` | Custom field 131 |
| `data[].custom132` | `string` | Custom field 132 |
| `data[].custom133` | `string` | Custom field 133 |
| `data[].custom134` | `string` | Custom field 134 |
| `data[].custom135` | `string` | Custom field 135 |
| `data[].custom136` | `string` | Custom field 136 |
| `data[].custom137` | `string` | Custom field 137 |
| `data[].custom138` | `string` | Custom field 138 |
| `data[].custom139` | `string` | Custom field 139 |
| `data[].custom14` | `string` | Custom field 14 |
| `data[].custom140` | `string` | Custom field 140 |
| `data[].custom141` | `string` | Custom field 141 |
| `data[].custom142` | `string` | Custom field 142 |
| `data[].custom143` | `string` | Custom field 143 |
| `data[].custom144` | `string` | Custom field 144 |
| `data[].custom145` | `string` | Custom field 145 |
| `data[].custom146` | `string` | Custom field 146 |
| `data[].custom147` | `string` | Custom field 147 |
| `data[].custom148` | `string` | Custom field 148 |
| `data[].custom149` | `string` | Custom field 149 |
| `data[].custom15` | `string` | Custom field 15 |
| `data[].custom150` | `string` | Custom field 150 |
| `data[].custom16` | `string` | Custom field 16 |
| `data[].custom17` | `string` | Custom field 17 |
| `data[].custom18` | `string` | Custom field 18 |
| `data[].custom19` | `string` | Custom field 19 |
| `data[].custom2` | `string` | Custom field 2 |
| `data[].custom20` | `string` | Custom field 20 |
| `data[].custom21` | `string` | Custom field 21 |
| `data[].custom22` | `string` | Custom field 22 |
| `data[].custom23` | `string` | Custom field 23 |
| `data[].custom24` | `string` | Custom field 24 |
| `data[].custom25` | `string` | Custom field 25 |
| `data[].custom26` | `string` | Custom field 26 |
| `data[].custom27` | `string` | Custom field 27 |
| `data[].custom28` | `string` | Custom field 28 |
| `data[].custom29` | `string` | Custom field 29 |
| `data[].custom3` | `string` | Custom field 3 |
| `data[].custom30` | `string` | Custom field 30 |
| `data[].custom31` | `string` | Custom field 31 |
| `data[].custom32` | `string` | Custom field 32 |
| `data[].custom33` | `string` | Custom field 33 |
| `data[].custom34` | `string` | Custom field 34 |
| `data[].custom35` | `string` | Custom field 35 |
| `data[].custom36` | `string` | Custom field 36 |
| `data[].custom37` | `string` | Custom field 37 |
| `data[].custom38` | `string` | Custom field 38 |
| `data[].custom39` | `string` | Custom field 39 |
| `data[].custom4` | `string` | Custom field 4 |
| `data[].custom40` | `string` | Custom field 40 |
| `data[].custom41` | `string` | Custom field 41 |
| `data[].custom42` | `string` | Custom field 42 |
| `data[].custom43` | `string` | Custom field 43 |
| `data[].custom44` | `string` | Custom field 44 |
| `data[].custom45` | `string` | Custom field 45 |
| `data[].custom46` | `string` | Custom field 46 |
| `data[].custom47` | `string` | Custom field 47 |
| `data[].custom48` | `string` | Custom field 48 |
| `data[].custom49` | `string` | Custom field 49 |
| `data[].custom5` | `string` | Custom field 5 |
| `data[].custom50` | `string` | Custom field 50 |
| `data[].custom51` | `string` | Custom field 51 |
| `data[].custom52` | `string` | Custom field 52 |
| `data[].custom53` | `string` | Custom field 53 |
| `data[].custom54` | `string` | Custom field 54 |
| `data[].custom55` | `string` | Custom field 55 |
| `data[].custom56` | `string` | Custom field 56 |
| `data[].custom57` | `string` | Custom field 57 |
| `data[].custom58` | `string` | Custom field 58 |
| `data[].custom59` | `string` | Custom field 59 |
| `data[].custom6` | `string` | Custom field 6 |
| `data[].custom60` | `string` | Custom field 60 |
| `data[].custom61` | `string` | Custom field 61 |
| `data[].custom62` | `string` | Custom field 62 |
| `data[].custom63` | `string` | Custom field 63 |
| `data[].custom64` | `string` | Custom field 64 |
| `data[].custom65` | `string` | Custom field 65 |
| `data[].custom66` | `string` | Custom field 66 |
| `data[].custom67` | `string` | Custom field 67 |
| `data[].custom68` | `string` | Custom field 68 |
| `data[].custom69` | `string` | Custom field 69 |
| `data[].custom7` | `string` | Custom field 7 |
| `data[].custom70` | `string` | Custom field 70 |
| `data[].custom71` | `string` | Custom field 71 |
| `data[].custom72` | `string` | Custom field 72 |
| `data[].custom73` | `string` | Custom field 73 |
| `data[].custom74` | `string` | Custom field 74 |
| `data[].custom75` | `string` | Custom field 75 |
| `data[].custom76` | `string` | Custom field 76 |
| `data[].custom77` | `string` | Custom field 77 |
| `data[].custom78` | `string` | Custom field 78 |
| `data[].custom79` | `string` | Custom field 79 |
| `data[].custom8` | `string` | Custom field 8 |
| `data[].custom80` | `string` | Custom field 80 |
| `data[].custom81` | `string` | Custom field 81 |
| `data[].custom82` | `string` | Custom field 82 |
| `data[].custom83` | `string` | Custom field 83 |
| `data[].custom84` | `string` | Custom field 84 |
| `data[].custom85` | `string` | Custom field 85 |
| `data[].custom86` | `string` | Custom field 86 |
| `data[].custom87` | `string` | Custom field 87 |
| `data[].custom88` | `string` | Custom field 88 |
| `data[].custom89` | `string` | Custom field 89 |
| `data[].custom9` | `string` | Custom field 9 |
| `data[].custom90` | `string` | Custom field 90 |
| `data[].custom91` | `string` | Custom field 91 |
| `data[].custom92` | `string` | Custom field 92 |
| `data[].custom93` | `string` | Custom field 93 |
| `data[].custom94` | `string` | Custom field 94 |
| `data[].custom95` | `string` | Custom field 95 |
| `data[].custom96` | `string` | Custom field 96 |
| `data[].custom97` | `string` | Custom field 97 |
| `data[].custom98` | `string` | Custom field 98 |
| `data[].custom99` | `string` | Custom field 99 |
| `data[].defaultPluginMapping` | `array` | Default plugin mapping |
| `data[].description` | `string` | Description |
| `data[].externalCreatedAt` | `string` | External created at |
| `data[].externalCreator` | `array` | External creator |
| `data[].favorites` | `array` | Favorites |
| `data[].healthCategory` | `string` | Health category |
| `data[].healthScore` | `integer` | Health score |
| `data[].id` | `integer` | Unique opportunity identifier |
| `data[].mapLink` | `string` | Map link |
| `data[].mapNextSteps` | `string` | Map next steps |
| `data[].mapNumberOfOverdueTasks` | `integer` | Map number of overdue tasks |
| `data[].mapStatus` | `string` | Map status |
| `data[].name` | `string` | Name |
| `data[].nextStep` | `string` | Next step |
| `data[].opportunityHealthFactors` | `array` | Opportunity health factors |
| `data[].opportunityStage` | `array` | Opportunity stage |
| `data[].opportunityType` | `string` | Opportunity type |
| `data[].owner` | `array` | Owner |
| `data[].primaryProspect` | `array` | Primary prospect |
| `data[].probability` | `integer` | Probability |
| `data[].prospectingRepId` | `string` | Prospecting rep id |
| `data[].prospects` | `array` | Prospects |
| `data[].sharingTeamId` | `string` | Sharing team id |
| `data[].stage` | `array` | Stage |
| `data[].tags` | `array` | Tags |
| `data[].touchedAt` | `string` | Touched at |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |

</details>

### Opportunities Context Store SQL Query

Run a SQL query against opportunities records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "opportunities",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.opportunities.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "opportunities",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Calls

### Calls List

Returns a paginated list of calls

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "calls",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.calls.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Calls Get

Get a single call by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "calls",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.calls.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Call ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Calls Context Store Search

Search and filter calls records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "calls",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "answeredAt": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.calls.context_store_search(
    query={"filter": {"eq": {"answeredAt": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"answeredAt": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `answeredAt` | `string` | Answered at |
| `batches` | `array` | Batches |
| `callDisposition` | `array` | Call disposition |
| `callPurpose` | `array` | Call purpose |
| `completedAt` | `string` | Completed at |
| `createdAt` | `string` | Created at |
| `dialedAt` | `string` | Dialed at |
| `direction` | `string` | Direction |
| `externalVendor` | `string` | External vendor |
| `from` | `string` | From |
| `id` | `integer` | Unique call identifier |
| `note` | `string` | Note |
| `opportunity` | `array` | Opportunity |
| `outboundVoicemail` | `array` | Outbound voicemail |
| `outcome` | `string` | Outcome |
| `phone` | `array` | Phone |
| `phoneNumber` | `array` | Phone number |
| `prospect` | `array` | Prospect |
| `recordingDeletionReason` | `string` | Recording deletion reason |
| `recordingUrl` | `string` | Recording url |
| `returnedAt` | `string` | Returned at |
| `sequence` | `array` | Sequence |
| `sequenceAction` | `string` | Sequence action |
| `sequenceState` | `array` | Sequence state |
| `sequenceStep` | `array` | Sequence step |
| `shouldRecordCall` | `boolean` | Should record call |
| `state` | `string` | State |
| `stateChangedAt` | `string` | State changed at |
| `tags` | `array` | Tags |
| `task` | `array` | Task |
| `to` | `string` | To |
| `uid` | `string` | Uid |
| `updatedAt` | `string` | Updated at |
| `user` | `array` | User |
| `userCallType` | `string` | User call type |
| `vendorCallId` | `string` | Vendor call id |
| `voicemailRecordingUrl` | `string` | Voicemail recording url |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].answeredAt` | `string` | Answered at |
| `data[].batches` | `array` | Batches |
| `data[].callDisposition` | `array` | Call disposition |
| `data[].callPurpose` | `array` | Call purpose |
| `data[].completedAt` | `string` | Completed at |
| `data[].createdAt` | `string` | Created at |
| `data[].dialedAt` | `string` | Dialed at |
| `data[].direction` | `string` | Direction |
| `data[].externalVendor` | `string` | External vendor |
| `data[].from` | `string` | From |
| `data[].id` | `integer` | Unique call identifier |
| `data[].note` | `string` | Note |
| `data[].opportunity` | `array` | Opportunity |
| `data[].outboundVoicemail` | `array` | Outbound voicemail |
| `data[].outcome` | `string` | Outcome |
| `data[].phone` | `array` | Phone |
| `data[].phoneNumber` | `array` | Phone number |
| `data[].prospect` | `array` | Prospect |
| `data[].recordingDeletionReason` | `string` | Recording deletion reason |
| `data[].recordingUrl` | `string` | Recording url |
| `data[].returnedAt` | `string` | Returned at |
| `data[].sequence` | `array` | Sequence |
| `data[].sequenceAction` | `string` | Sequence action |
| `data[].sequenceState` | `array` | Sequence state |
| `data[].sequenceStep` | `array` | Sequence step |
| `data[].shouldRecordCall` | `boolean` | Should record call |
| `data[].state` | `string` | State |
| `data[].stateChangedAt` | `string` | State changed at |
| `data[].tags` | `array` | Tags |
| `data[].task` | `array` | Task |
| `data[].to` | `string` | To |
| `data[].uid` | `string` | Uid |
| `data[].updatedAt` | `string` | Updated at |
| `data[].user` | `array` | User |
| `data[].userCallType` | `string` | User call type |
| `data[].vendorCallId` | `string` | Vendor call id |
| `data[].voicemailRecordingUrl` | `string` | Voicemail recording url |

</details>

### Calls Context Store SQL Query

Run a SQL query against calls records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "calls",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.calls.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Call Dispositions

### Call Dispositions List

Returns a paginated list of call dispositions

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "call_dispositions",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.call_dispositions.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_dispositions",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Call Dispositions Get

Get a single call disposition by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "call_dispositions",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.call_dispositions.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_dispositions",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Call Disposition ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Call Dispositions Context Store Search

Search and filter call dispositions records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "call_dispositions",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "calls": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.call_dispositions.context_store_search(
    query={"filter": {"eq": {"calls": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_dispositions",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"calls": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `calls` | `array` | Calls |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `defaultForOutboundVoicemail` | `boolean` | Default for outbound voicemail |
| `id` | `integer` | Unique call disposition identifier |
| `name` | `string` | Name |
| `order` | `integer` | Order |
| `outcome` | `string` | Outcome |
| `updatedAt` | `string` | Updated at |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].calls` | `array` | Calls |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].defaultForOutboundVoicemail` | `boolean` | Default for outbound voicemail |
| `data[].id` | `integer` | Unique call disposition identifier |
| `data[].name` | `string` | Name |
| `data[].order` | `integer` | Order |
| `data[].outcome` | `string` | Outcome |
| `data[].updatedAt` | `string` | Updated at |

</details>

### Call Dispositions Context Store SQL Query

Run a SQL query against call dispositions records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "call_dispositions",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.call_dispositions.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_dispositions",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Call Purposes

### Call Purposes List

Returns a paginated list of call purposes

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "call_purposes",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.call_purposes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_purposes",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Call Purposes Get

Get a single call purpose by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "call_purposes",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.call_purposes.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_purposes",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Call Purpose ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Call Purposes Context Store Search

Search and filter call purposes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "call_purposes",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "calls": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.call_purposes.context_store_search(
    query={"filter": {"eq": {"calls": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_purposes",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"calls": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `calls` | `array` | Calls |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `id` | `integer` | Unique call purpose identifier |
| `name` | `string` | Name |
| `order` | `integer` | Order |
| `updatedAt` | `string` | Updated at |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].calls` | `array` | Calls |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].id` | `integer` | Unique call purpose identifier |
| `data[].name` | `string` | Name |
| `data[].order` | `integer` | Order |
| `data[].updatedAt` | `string` | Updated at |

</details>

### Call Purposes Context Store SQL Query

Run a SQL query against call purposes records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "call_purposes",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.call_purposes.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_purposes",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Mailings

### Mailings List

Returns a paginated list of mailings

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "mailings",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.mailings.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "mailings",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Mailings Get

Get a single mailing by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "mailings",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.mailings.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "mailings",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Mailing ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Mailings Context Store Search

Search and filter mailings records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "mailings",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "attachments": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.mailings.context_store_search(
    query={"filter": {"eq": {"attachments": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "mailings",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"attachments": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `attachments` | `array` | Attachments |
| `attributableSequenceId` | `integer` | Attributable sequence id |
| `attributableSequenceName` | `string` | Attributable sequence name |
| `bodyHtml` | `string` | Body html |
| `bodyText` | `string` | Body text |
| `bouncedAt` | `string` | Bounced at |
| `calendar` | `array` | Calendar |
| `clickCount` | `integer` | Click count |
| `clickedAt` | `string` | Clicked at |
| `createdAt` | `string` | Created at |
| `deliveredAt` | `string` | Delivered at |
| `desiredAt` | `string` | Desired at |
| `errorBacktrace` | `string` | Error backtrace |
| `errorReason` | `string` | Error reason |
| `followUpSequence` | `array` | Follow up sequence |
| `followUpSequenceId` | `integer` | Follow up sequence id |
| `followUpSequenceName` | `string` | Follow up sequence name |
| `followUpSequenceStartingDate` | `string` | Follow up sequence starting date |
| `followUpTaskScheduledAt` | `string` | Follow up task scheduled at |
| `followUpTaskType` | `string` | Follow up task type |
| `id` | `integer` | Unique mailing identifier |
| `mailbox` | `array` | Mailbox |
| `mailboxAddress` | `string` | Mailbox address |
| `mailingType` | `string` | Mailing type |
| `markedAsSpamAt` | `string` | Marked as spam at |
| `meetingDescription` | `string` | Meeting description |
| `meetingDuration` | `integer` | Meeting duration |
| `meetingLocation` | `string` | Meeting location |
| `meetingTitle` | `string` | Meeting title |
| `messageId` | `string` | Message id |
| `notifyThreadCondition` | `string` | Notify thread condition |
| `notifyThreadScheduledAt` | `string` | Notify thread scheduled at |
| `notifyThreadStatus` | `string` | Notify thread status |
| `openCount` | `integer` | Open count |
| `openedAt` | `string` | Opened at |
| `opportunity` | `array` | Opportunity |
| `optimizedScheduledAt` | `string` | Optimized scheduled at |
| `overrideSafetySettings` | `boolean` | Override safety settings |
| `prospect` | `array` | Prospect |
| `recipients` | `array` | Recipients |
| `references` | `array` | References |
| `repliedAt` | `string` | Replied at |
| `replySentiment` | `string` | Reply sentiment |
| `retryAt` | `string` | Retry at |
| `retryCount` | `integer` | Retry count |
| `retryInterval` | `integer` | Retry interval |
| `schedule` | `array` | Schedule |
| `scheduleId` | `integer` | Schedule id |
| `scheduledAt` | `string` | Scheduled at |
| `sequence` | `array` | Sequence |
| `sequenceState` | `array` | Sequence state |
| `sequenceStep` | `array` | Sequence step |
| `state` | `string` | State |
| `stateChangedAt` | `string` | State changed at |
| `subject` | `string` | Subject |
| `task` | `array` | Task |
| `tasks` | `array` | Tasks |
| `template` | `array` | Template |
| `trackLinks` | `boolean` | Track links |
| `trackOpens` | `boolean` | Track opens |
| `unsubscribedAt` | `string` | Unsubscribed at |
| `updatedAt` | `string` | Updated at |
| `user` | `array` | User |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].attachments` | `array` | Attachments |
| `data[].attributableSequenceId` | `integer` | Attributable sequence id |
| `data[].attributableSequenceName` | `string` | Attributable sequence name |
| `data[].bodyHtml` | `string` | Body html |
| `data[].bodyText` | `string` | Body text |
| `data[].bouncedAt` | `string` | Bounced at |
| `data[].calendar` | `array` | Calendar |
| `data[].clickCount` | `integer` | Click count |
| `data[].clickedAt` | `string` | Clicked at |
| `data[].createdAt` | `string` | Created at |
| `data[].deliveredAt` | `string` | Delivered at |
| `data[].desiredAt` | `string` | Desired at |
| `data[].errorBacktrace` | `string` | Error backtrace |
| `data[].errorReason` | `string` | Error reason |
| `data[].followUpSequence` | `array` | Follow up sequence |
| `data[].followUpSequenceId` | `integer` | Follow up sequence id |
| `data[].followUpSequenceName` | `string` | Follow up sequence name |
| `data[].followUpSequenceStartingDate` | `string` | Follow up sequence starting date |
| `data[].followUpTaskScheduledAt` | `string` | Follow up task scheduled at |
| `data[].followUpTaskType` | `string` | Follow up task type |
| `data[].id` | `integer` | Unique mailing identifier |
| `data[].mailbox` | `array` | Mailbox |
| `data[].mailboxAddress` | `string` | Mailbox address |
| `data[].mailingType` | `string` | Mailing type |
| `data[].markedAsSpamAt` | `string` | Marked as spam at |
| `data[].meetingDescription` | `string` | Meeting description |
| `data[].meetingDuration` | `integer` | Meeting duration |
| `data[].meetingLocation` | `string` | Meeting location |
| `data[].meetingTitle` | `string` | Meeting title |
| `data[].messageId` | `string` | Message id |
| `data[].notifyThreadCondition` | `string` | Notify thread condition |
| `data[].notifyThreadScheduledAt` | `string` | Notify thread scheduled at |
| `data[].notifyThreadStatus` | `string` | Notify thread status |
| `data[].openCount` | `integer` | Open count |
| `data[].openedAt` | `string` | Opened at |
| `data[].opportunity` | `array` | Opportunity |
| `data[].optimizedScheduledAt` | `string` | Optimized scheduled at |
| `data[].overrideSafetySettings` | `boolean` | Override safety settings |
| `data[].prospect` | `array` | Prospect |
| `data[].recipients` | `array` | Recipients |
| `data[].references` | `array` | References |
| `data[].repliedAt` | `string` | Replied at |
| `data[].replySentiment` | `string` | Reply sentiment |
| `data[].retryAt` | `string` | Retry at |
| `data[].retryCount` | `integer` | Retry count |
| `data[].retryInterval` | `integer` | Retry interval |
| `data[].schedule` | `array` | Schedule |
| `data[].scheduleId` | `integer` | Schedule id |
| `data[].scheduledAt` | `string` | Scheduled at |
| `data[].sequence` | `array` | Sequence |
| `data[].sequenceState` | `array` | Sequence state |
| `data[].sequenceStep` | `array` | Sequence step |
| `data[].state` | `string` | State |
| `data[].stateChangedAt` | `string` | State changed at |
| `data[].subject` | `string` | Subject |
| `data[].task` | `array` | Task |
| `data[].tasks` | `array` | Tasks |
| `data[].template` | `array` | Template |
| `data[].trackLinks` | `boolean` | Track links |
| `data[].trackOpens` | `boolean` | Track opens |
| `data[].unsubscribedAt` | `string` | Unsubscribed at |
| `data[].updatedAt` | `string` | Updated at |
| `data[].user` | `array` | User |

</details>

### Mailings Context Store SQL Query

Run a SQL query against mailings records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "mailings",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.mailings.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "mailings",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Mailboxes

### Mailboxes List

Returns a paginated list of mailboxes

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "mailboxes",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.mailboxes.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "mailboxes",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Mailboxes Get

Get a single mailbox by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "mailboxes",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.mailboxes.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "mailboxes",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Mailbox ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Mailboxes Context Store Search

Search and filter mailboxes records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "mailboxes",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "authId": 0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.mailboxes.context_store_search(
    query={"filter": {"eq": {"authId": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "mailboxes",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"authId": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `authId` | `integer` | Auth id |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `editable` | `boolean` | Editable |
| `email` | `string` | Email |
| `emailHash` | `string` | Email hash |
| `emailProvider` | `string` | Email provider |
| `emailSignature` | `string` | Email signature |
| `ewsCustomSearchFolder` | `boolean` | Ews custom search folder |
| `ewsDelegateSync` | `boolean` | Ews delegate sync |
| `ewsEndpoint` | `string` | Ews endpoint |
| `ewsImpersonation` | `boolean` | Ews impersonation |
| `ewsSslVerifyMode` | `integer` | Ews ssl verify mode |
| `exchangeVersion` | `string` | Exchange version |
| `id` | `integer` | Unique mailbox identifier |
| `imapHost` | `string` | Imap host |
| `imapPort` | `integer` | Imap port |
| `imapSsl` | `boolean` | Imap ssl |
| `mailAliases` | `array` | Mail aliases |
| `mailings` | `array` | Mailings |
| `maxEmailsPerDay` | `integer` | Max emails per day |
| `maxMailingsPerDay` | `integer` | Max mailings per day |
| `maxMailingsPerWeek` | `integer` | Max mailings per week |
| `optOutMessage` | `string` | Opt out message |
| `optOutSignature` | `string` | Opt out signature |
| `prospectEmailExclusions` | `array` | Prospect email exclusions |
| `providerId` | `integer` | Provider id |
| `providerType` | `string` | Provider type |
| `sendDisabled` | `boolean` | Send disabled |
| `sendErroredAt` | `string` | Send errored at |
| `sendMaxRetries` | `integer` | Send max retries |
| `sendMethod` | `string` | Send method |
| `sendPeriod` | `integer` | Send period |
| `sendPermanentErrorAt` | `string` | Send permanent error at |
| `sendRequiresSync` | `boolean` | Send requires sync |
| `sendSuccessAt` | `string` | Send success at |
| `sendThreshold` | `integer` | Send threshold |
| `sendgridWebhookUrl` | `string` | Sendgrid webhook url |
| `smtpHost` | `string` | Smtp host |
| `smtpPort` | `integer` | Smtp port |
| `smtpSsl` | `boolean` | Smtp ssl |
| `smtpUsername` | `string` | Smtp username |
| `syncActiveFrequency` | `integer` | Sync active frequency |
| `syncDisabled` | `boolean` | Sync disabled |
| `syncErroredAt` | `string` | Sync errored at |
| `syncFinishedAt` | `string` | Sync finished at |
| `syncMethod` | `string` | Sync method |
| `syncOutreachFolder` | `boolean` | Sync outreach folder |
| `syncPassiveFrequency` | `integer` | Sync passive frequency |
| `syncPermanentErrorAt` | `string` | Sync permanent error at |
| `syncSuccessAt` | `string` | Sync success at |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |
| `user` | `array` | User |
| `userId` | `integer` | User id |
| `username` | `string` | Username |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].authId` | `integer` | Auth id |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].editable` | `boolean` | Editable |
| `data[].email` | `string` | Email |
| `data[].emailHash` | `string` | Email hash |
| `data[].emailProvider` | `string` | Email provider |
| `data[].emailSignature` | `string` | Email signature |
| `data[].ewsCustomSearchFolder` | `boolean` | Ews custom search folder |
| `data[].ewsDelegateSync` | `boolean` | Ews delegate sync |
| `data[].ewsEndpoint` | `string` | Ews endpoint |
| `data[].ewsImpersonation` | `boolean` | Ews impersonation |
| `data[].ewsSslVerifyMode` | `integer` | Ews ssl verify mode |
| `data[].exchangeVersion` | `string` | Exchange version |
| `data[].id` | `integer` | Unique mailbox identifier |
| `data[].imapHost` | `string` | Imap host |
| `data[].imapPort` | `integer` | Imap port |
| `data[].imapSsl` | `boolean` | Imap ssl |
| `data[].mailAliases` | `array` | Mail aliases |
| `data[].mailings` | `array` | Mailings |
| `data[].maxEmailsPerDay` | `integer` | Max emails per day |
| `data[].maxMailingsPerDay` | `integer` | Max mailings per day |
| `data[].maxMailingsPerWeek` | `integer` | Max mailings per week |
| `data[].optOutMessage` | `string` | Opt out message |
| `data[].optOutSignature` | `string` | Opt out signature |
| `data[].prospectEmailExclusions` | `array` | Prospect email exclusions |
| `data[].providerId` | `integer` | Provider id |
| `data[].providerType` | `string` | Provider type |
| `data[].sendDisabled` | `boolean` | Send disabled |
| `data[].sendErroredAt` | `string` | Send errored at |
| `data[].sendMaxRetries` | `integer` | Send max retries |
| `data[].sendMethod` | `string` | Send method |
| `data[].sendPeriod` | `integer` | Send period |
| `data[].sendPermanentErrorAt` | `string` | Send permanent error at |
| `data[].sendRequiresSync` | `boolean` | Send requires sync |
| `data[].sendSuccessAt` | `string` | Send success at |
| `data[].sendThreshold` | `integer` | Send threshold |
| `data[].sendgridWebhookUrl` | `string` | Sendgrid webhook url |
| `data[].smtpHost` | `string` | Smtp host |
| `data[].smtpPort` | `integer` | Smtp port |
| `data[].smtpSsl` | `boolean` | Smtp ssl |
| `data[].smtpUsername` | `string` | Smtp username |
| `data[].syncActiveFrequency` | `integer` | Sync active frequency |
| `data[].syncDisabled` | `boolean` | Sync disabled |
| `data[].syncErroredAt` | `string` | Sync errored at |
| `data[].syncFinishedAt` | `string` | Sync finished at |
| `data[].syncMethod` | `string` | Sync method |
| `data[].syncOutreachFolder` | `boolean` | Sync outreach folder |
| `data[].syncPassiveFrequency` | `integer` | Sync passive frequency |
| `data[].syncPermanentErrorAt` | `string` | Sync permanent error at |
| `data[].syncSuccessAt` | `string` | Sync success at |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |
| `data[].user` | `array` | User |
| `data[].userId` | `integer` | User id |
| `data[].username` | `string` | Username |

</details>

### Mailboxes Context Store SQL Query

Run a SQL query against mailboxes records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "mailboxes",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.mailboxes.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "mailboxes",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Tasks

### Tasks List

Returns a paginated list of tasks

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "tasks",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.tasks.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Tasks Get

Get a single task by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "tasks",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.tasks.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Task ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Tasks Context Store Search

Search and filter tasks records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "tasks",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "account": []
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.tasks.context_store_search(
    query={"filter": {"eq": {"account": []}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"account": []}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `account` | `array` | Account |
| `action` | `string` | Action |
| `autoskipAt` | `string` | Autoskip at |
| `call` | `array` | Call |
| `calls` | `array` | Calls |
| `compiledSequenceTemplateHtml` | `string` | Compiled sequence template html |
| `completed` | `boolean` | Completed |
| `completedAt` | `string` | Completed at |
| `completer` | `array` | Completer |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `defaultPluginMapping` | `array` | Default plugin mapping |
| `dueAt` | `string` | Due at |
| `id` | `integer` | Unique task identifier |
| `mailing` | `array` | Mailing |
| `mailings` | `array` | Mailings |
| `note` | `string` | Note |
| `opportunity` | `array` | Opportunity |
| `opportunityAssociation` | `string` | Opportunity association |
| `owner` | `array` | Owner |
| `prospect` | `array` | Prospect |
| `prospectAccount` | `array` | Prospect account |
| `prospectContacts` | `array` | Prospect contacts |
| `prospectOwner` | `array` | Prospect owner |
| `prospectPhoneNumbers` | `array` | Prospect phone numbers |
| `prospectStage` | `array` | Prospect stage |
| `scheduledAt` | `string` | Scheduled at |
| `sequence` | `array` | Sequence |
| `sequenceSequenceSteps` | `array` | Sequence sequence steps |
| `sequenceState` | `array` | Sequence state |
| `sequenceStateSequenceStep` | `array` | Sequence state sequence step |
| `sequenceStateSequenceStepOverrides` | `array` | Sequence state sequence step overrides |
| `sequenceStateStartingTemplate` | `array` | Sequence state starting template |
| `sequenceStep` | `array` | Sequence step |
| `sequenceStepOverrideTemplates` | `array` | Sequence step override templates |
| `sequenceTemplate` | `array` | Sequence template |
| `sequenceTemplateTemplate` | `array` | Sequence template template |
| `state` | `string` | State |
| `stateChangedAt` | `string` | State changed at |
| `subject` | `array` | Subject |
| `taskPriority` | `array` | Task priority |
| `taskTheme` | `array` | Task theme |
| `taskType` | `string` | Task type |
| `template` | `array` | Template |
| `updatedAt` | `string` | Updated at |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].account` | `array` | Account |
| `data[].action` | `string` | Action |
| `data[].autoskipAt` | `string` | Autoskip at |
| `data[].call` | `array` | Call |
| `data[].calls` | `array` | Calls |
| `data[].compiledSequenceTemplateHtml` | `string` | Compiled sequence template html |
| `data[].completed` | `boolean` | Completed |
| `data[].completedAt` | `string` | Completed at |
| `data[].completer` | `array` | Completer |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].defaultPluginMapping` | `array` | Default plugin mapping |
| `data[].dueAt` | `string` | Due at |
| `data[].id` | `integer` | Unique task identifier |
| `data[].mailing` | `array` | Mailing |
| `data[].mailings` | `array` | Mailings |
| `data[].note` | `string` | Note |
| `data[].opportunity` | `array` | Opportunity |
| `data[].opportunityAssociation` | `string` | Opportunity association |
| `data[].owner` | `array` | Owner |
| `data[].prospect` | `array` | Prospect |
| `data[].prospectAccount` | `array` | Prospect account |
| `data[].prospectContacts` | `array` | Prospect contacts |
| `data[].prospectOwner` | `array` | Prospect owner |
| `data[].prospectPhoneNumbers` | `array` | Prospect phone numbers |
| `data[].prospectStage` | `array` | Prospect stage |
| `data[].scheduledAt` | `string` | Scheduled at |
| `data[].sequence` | `array` | Sequence |
| `data[].sequenceSequenceSteps` | `array` | Sequence sequence steps |
| `data[].sequenceState` | `array` | Sequence state |
| `data[].sequenceStateSequenceStep` | `array` | Sequence state sequence step |
| `data[].sequenceStateSequenceStepOverrides` | `array` | Sequence state sequence step overrides |
| `data[].sequenceStateStartingTemplate` | `array` | Sequence state starting template |
| `data[].sequenceStep` | `array` | Sequence step |
| `data[].sequenceStepOverrideTemplates` | `array` | Sequence step override templates |
| `data[].sequenceTemplate` | `array` | Sequence template |
| `data[].sequenceTemplateTemplate` | `array` | Sequence template template |
| `data[].state` | `string` | State |
| `data[].stateChangedAt` | `string` | State changed at |
| `data[].subject` | `array` | Subject |
| `data[].taskPriority` | `array` | Task priority |
| `data[].taskTheme` | `array` | Task theme |
| `data[].taskType` | `string` | Task type |
| `data[].template` | `array` | Template |
| `data[].updatedAt` | `string` | Updated at |

</details>

### Tasks Context Store SQL Query

Run a SQL query against tasks records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "tasks",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.tasks.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tasks",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Users

### Users List

Returns a paginated list of users

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "users",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.users.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Users Get

Get a single user by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "users",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.users.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | User ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Users Context Store Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "users",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "accountsViewId": 0
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.users.context_store_search(
    query={"filter": {"eq": {"accountsViewId": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"accountsViewId": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `accountsViewId` | `integer` | Accounts view id |
| `activeProspectsCount` | `integer` | Active prospects count |
| `activityNotificationsDisabled` | `boolean` | Activity notifications disabled |
| `batches` | `array` | Batches |
| `batchesViewId` | `integer` | Batches view id |
| `bounceWarningEmailEnabled` | `boolean` | Bounce warning email enabled |
| `bridgePhone` | `string` | Bridge phone |
| `bridgePhoneExtension` | `string` | Bridge phone extension |
| `buyerLanguagePreference` | `string` | Buyer language preference |
| `calendar` | `array` | Calendar |
| `calendarEventsViewId` | `integer` | Calendar events view id |
| `callsViewId` | `integer` | Calls view id |
| `contentCategories` | `array` | Content categories |
| `contentCategoryOwnerships` | `array` | Content category ownerships |
| `controlledTabDefault` | `string` | Controlled tab default |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `currentSignInAt` | `string` | Current sign in at |
| `custom1` | `string` | Custom field 1 |
| `custom2` | `string` | Custom field 2 |
| `custom3` | `string` | Custom field 3 |
| `custom4` | `string` | Custom field 4 |
| `custom5` | `string` | Custom field 5 |
| `dailyDigestEmailEnabled` | `boolean` | Daily digest email enabled |
| `defaultRulesetId` | `integer` | Default ruleset id |
| `defaultScheduleId` | `integer` | Default schedule id |
| `duties` | `array` | Duties |
| `dutiesSetAt` | `string` | Duties set at |
| `email` | `string` | Email |
| `enableVoiceRecordings` | `boolean` | Enable voice recordings |
| `engagementEmailsEnabled` | `boolean` | Engagement emails enabled |
| `favorites` | `array` | Favorites |
| `firstName` | `string` | First name |
| `globalId` | `string` | Global id |
| `id` | `integer` | Unique user identifier |
| `importsViewId` | `integer` | Imports view id |
| `inboundBridgePhone` | `string` | Inbound bridge phone |
| `inboundBridgePhoneExtension` | `string` | Inbound bridge phone extension |
| `inboundCallBehavior` | `string` | Inbound call behavior |
| `inboundPhoneType` | `string` | Inbound phone type |
| `inboundVoicemailCustomMessageText` | `string` | Inbound voicemail custom message text |
| `inboundVoicemailMessageTextVoice` | `string` | Inbound voicemail message text voice |
| `inboundVoicemailPromptType` | `string` | Inbound voicemail prompt type |
| `jobRole` | `array` | Job role |
| `kaiaRecordingsViewId` | `integer` | Kaia recordings view id |
| `keepBridgePhoneConnected` | `boolean` | Keep bridge phone connected |
| `languagePreference` | `string` | Language preference |
| `lastName` | `string` | Last name |
| `lastSignInAt` | `string` | Last sign in at |
| `linkToSequenceStateInTaskFlow` | `boolean` | Link to sequence state in task flow |
| `liveListenViewId` | `integer` | Live listen view id |
| `locked` | `boolean` | Locked |
| `mailbox` | `array` | Mailbox |
| `mailboxErrorEmailEnabled` | `boolean` | Mailbox error email enabled |
| `mailboxes` | `array` | Mailboxes |
| `mailingsDeliveredCount` | `integer` | Mailings delivered count |
| `mailingsRepliedCount` | `integer` | Mailings replied count |
| `mailingsViewId` | `integer` | Mailings view id |
| `meetingEngagementNotificationEnabled` | `boolean` | Meeting engagement notification enabled |
| `meetingTypesViewId` | `integer` | Meeting types view id |
| `name` | `string` | Name |
| `notificationsEnabled` | `boolean` | Notifications enabled |
| `oceClickToDialEverywhere` | `boolean` | Oce click to dial everywhere |
| `oceGmailToolbar` | `boolean` | Oce gmail toolbar |
| `oceGmailTrackingState` | `string` | Oce gmail tracking state |
| `oceSalesforceEmailDecorating` | `boolean` | Oce salesforce email decorating |
| `oceSalesforcePhoneDecorating` | `boolean` | Oce salesforce phone decorating |
| `oceUniversalTaskFlow` | `boolean` | Oce universal task flow |
| `oceWindowMode` | `boolean` | Oce window mode |
| `onboardedAt` | `string` | Onboarded at |
| `opportunitiesViewId` | `integer` | Opportunities view id |
| `orcaStandaloneEnabled` | `boolean` | Orca standalone enabled |
| `outboundVoicemails` | `array` | Outbound voicemails |
| `passwordExpiresAt` | `string` | Password expires at |
| `phone` | `array` | Phone |
| `phoneCountryCode` | `string` | Phone country code |
| `phoneNumber` | `string` | Phone number |
| `phoneType` | `string` | Phone type |
| `phones` | `array` | Phones |
| `phonesViewId` | `integer` | Phones view id |
| `pluginAlertNotificationEnabled` | `boolean` | Plugin alert notification enabled |
| `preferredVoiceRegion` | `string` | Preferred voice region |
| `prefersLocalPresence` | `boolean` | Prefers local presence |
| `primaryTimezone` | `string` | Primary timezone |
| `profile` | `array` | Profile |
| `prospectDetailDefault` | `string` | Prospect detail default |
| `prospectsViewId` | `integer` | Prospects view id |
| `recipients` | `array` | Recipients |
| `reportsSequencePerformanceViewId` | `integer` | Reports sequence performance view id |
| `reportsTeamPerfViewId` | `integer` | Reports team perf view id |
| `reportsTeamPerformanceIntradayViewId` | `integer` | Reports team performance intraday view id |
| `reportsTeamPerformanceViewId` | `integer` | Reports team performance view id |
| `reportsViewId` | `integer` | Reports view id |
| `role` | `array` | Role |
| `scimExternalId` | `string` | Scim external id |
| `scimSource` | `string` | Scim source |
| `secondaryTimezone` | `string` | Secondary timezone |
| `sendInviteFallback` | `boolean` | Send invite fallback |
| `senderNotificationsExcluded` | `boolean` | Sender notifications excluded |
| `sequenceStatesViewId` | `integer` | Sequence states view id |
| `sequencesViewId` | `integer` | Sequences view id |
| `smsPhone` | `array` | Sms phone |
| `snippetsViewId` | `integer` | Snippets view id |
| `tasksDueCount` | `integer` | Tasks due count |
| `tasksViewId` | `integer` | Tasks view id |
| `teams` | `array` | Teams |
| `teamsViewId` | `integer` | Teams view id |
| `templatesViewId` | `integer` | Templates view id |
| `tertiaryTimezone` | `string` | Tertiary timezone |
| `textingEmailNotifications` | `boolean` | Texting email notifications |
| `title` | `string` | Title |
| `unknownReplyEmailEnabled` | `boolean` | Unknown reply email enabled |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |
| `useSalesNavigatorForLinkedInTasks` | `boolean` | Use sales navigator for linked in tasks |
| `userGuid` | `string` | User guid |
| `username` | `string` | Username |
| `usersViewId` | `integer` | Users view id |
| `voicemailNotificationEnabled` | `boolean` | Voicemail notification enabled |
| `voicemailPrompts` | `array` | Voicemail prompts |
| `weeklyDigestEmailEnabled` | `boolean` | Weekly digest email enabled |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].accountsViewId` | `integer` | Accounts view id |
| `data[].activeProspectsCount` | `integer` | Active prospects count |
| `data[].activityNotificationsDisabled` | `boolean` | Activity notifications disabled |
| `data[].batches` | `array` | Batches |
| `data[].batchesViewId` | `integer` | Batches view id |
| `data[].bounceWarningEmailEnabled` | `boolean` | Bounce warning email enabled |
| `data[].bridgePhone` | `string` | Bridge phone |
| `data[].bridgePhoneExtension` | `string` | Bridge phone extension |
| `data[].buyerLanguagePreference` | `string` | Buyer language preference |
| `data[].calendar` | `array` | Calendar |
| `data[].calendarEventsViewId` | `integer` | Calendar events view id |
| `data[].callsViewId` | `integer` | Calls view id |
| `data[].contentCategories` | `array` | Content categories |
| `data[].contentCategoryOwnerships` | `array` | Content category ownerships |
| `data[].controlledTabDefault` | `string` | Controlled tab default |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].currentSignInAt` | `string` | Current sign in at |
| `data[].custom1` | `string` | Custom field 1 |
| `data[].custom2` | `string` | Custom field 2 |
| `data[].custom3` | `string` | Custom field 3 |
| `data[].custom4` | `string` | Custom field 4 |
| `data[].custom5` | `string` | Custom field 5 |
| `data[].dailyDigestEmailEnabled` | `boolean` | Daily digest email enabled |
| `data[].defaultRulesetId` | `integer` | Default ruleset id |
| `data[].defaultScheduleId` | `integer` | Default schedule id |
| `data[].duties` | `array` | Duties |
| `data[].dutiesSetAt` | `string` | Duties set at |
| `data[].email` | `string` | Email |
| `data[].enableVoiceRecordings` | `boolean` | Enable voice recordings |
| `data[].engagementEmailsEnabled` | `boolean` | Engagement emails enabled |
| `data[].favorites` | `array` | Favorites |
| `data[].firstName` | `string` | First name |
| `data[].globalId` | `string` | Global id |
| `data[].id` | `integer` | Unique user identifier |
| `data[].importsViewId` | `integer` | Imports view id |
| `data[].inboundBridgePhone` | `string` | Inbound bridge phone |
| `data[].inboundBridgePhoneExtension` | `string` | Inbound bridge phone extension |
| `data[].inboundCallBehavior` | `string` | Inbound call behavior |
| `data[].inboundPhoneType` | `string` | Inbound phone type |
| `data[].inboundVoicemailCustomMessageText` | `string` | Inbound voicemail custom message text |
| `data[].inboundVoicemailMessageTextVoice` | `string` | Inbound voicemail message text voice |
| `data[].inboundVoicemailPromptType` | `string` | Inbound voicemail prompt type |
| `data[].jobRole` | `array` | Job role |
| `data[].kaiaRecordingsViewId` | `integer` | Kaia recordings view id |
| `data[].keepBridgePhoneConnected` | `boolean` | Keep bridge phone connected |
| `data[].languagePreference` | `string` | Language preference |
| `data[].lastName` | `string` | Last name |
| `data[].lastSignInAt` | `string` | Last sign in at |
| `data[].linkToSequenceStateInTaskFlow` | `boolean` | Link to sequence state in task flow |
| `data[].liveListenViewId` | `integer` | Live listen view id |
| `data[].locked` | `boolean` | Locked |
| `data[].mailbox` | `array` | Mailbox |
| `data[].mailboxErrorEmailEnabled` | `boolean` | Mailbox error email enabled |
| `data[].mailboxes` | `array` | Mailboxes |
| `data[].mailingsDeliveredCount` | `integer` | Mailings delivered count |
| `data[].mailingsRepliedCount` | `integer` | Mailings replied count |
| `data[].mailingsViewId` | `integer` | Mailings view id |
| `data[].meetingEngagementNotificationEnabled` | `boolean` | Meeting engagement notification enabled |
| `data[].meetingTypesViewId` | `integer` | Meeting types view id |
| `data[].name` | `string` | Name |
| `data[].notificationsEnabled` | `boolean` | Notifications enabled |
| `data[].oceClickToDialEverywhere` | `boolean` | Oce click to dial everywhere |
| `data[].oceGmailToolbar` | `boolean` | Oce gmail toolbar |
| `data[].oceGmailTrackingState` | `string` | Oce gmail tracking state |
| `data[].oceSalesforceEmailDecorating` | `boolean` | Oce salesforce email decorating |
| `data[].oceSalesforcePhoneDecorating` | `boolean` | Oce salesforce phone decorating |
| `data[].oceUniversalTaskFlow` | `boolean` | Oce universal task flow |
| `data[].oceWindowMode` | `boolean` | Oce window mode |
| `data[].onboardedAt` | `string` | Onboarded at |
| `data[].opportunitiesViewId` | `integer` | Opportunities view id |
| `data[].orcaStandaloneEnabled` | `boolean` | Orca standalone enabled |
| `data[].outboundVoicemails` | `array` | Outbound voicemails |
| `data[].passwordExpiresAt` | `string` | Password expires at |
| `data[].phone` | `array` | Phone |
| `data[].phoneCountryCode` | `string` | Phone country code |
| `data[].phoneNumber` | `string` | Phone number |
| `data[].phoneType` | `string` | Phone type |
| `data[].phones` | `array` | Phones |
| `data[].phonesViewId` | `integer` | Phones view id |
| `data[].pluginAlertNotificationEnabled` | `boolean` | Plugin alert notification enabled |
| `data[].preferredVoiceRegion` | `string` | Preferred voice region |
| `data[].prefersLocalPresence` | `boolean` | Prefers local presence |
| `data[].primaryTimezone` | `string` | Primary timezone |
| `data[].profile` | `array` | Profile |
| `data[].prospectDetailDefault` | `string` | Prospect detail default |
| `data[].prospectsViewId` | `integer` | Prospects view id |
| `data[].recipients` | `array` | Recipients |
| `data[].reportsSequencePerformanceViewId` | `integer` | Reports sequence performance view id |
| `data[].reportsTeamPerfViewId` | `integer` | Reports team perf view id |
| `data[].reportsTeamPerformanceIntradayViewId` | `integer` | Reports team performance intraday view id |
| `data[].reportsTeamPerformanceViewId` | `integer` | Reports team performance view id |
| `data[].reportsViewId` | `integer` | Reports view id |
| `data[].role` | `array` | Role |
| `data[].scimExternalId` | `string` | Scim external id |
| `data[].scimSource` | `string` | Scim source |
| `data[].secondaryTimezone` | `string` | Secondary timezone |
| `data[].sendInviteFallback` | `boolean` | Send invite fallback |
| `data[].senderNotificationsExcluded` | `boolean` | Sender notifications excluded |
| `data[].sequenceStatesViewId` | `integer` | Sequence states view id |
| `data[].sequencesViewId` | `integer` | Sequences view id |
| `data[].smsPhone` | `array` | Sms phone |
| `data[].snippetsViewId` | `integer` | Snippets view id |
| `data[].tasksDueCount` | `integer` | Tasks due count |
| `data[].tasksViewId` | `integer` | Tasks view id |
| `data[].teams` | `array` | Teams |
| `data[].teamsViewId` | `integer` | Teams view id |
| `data[].templatesViewId` | `integer` | Templates view id |
| `data[].tertiaryTimezone` | `string` | Tertiary timezone |
| `data[].textingEmailNotifications` | `boolean` | Texting email notifications |
| `data[].title` | `string` | Title |
| `data[].unknownReplyEmailEnabled` | `boolean` | Unknown reply email enabled |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |
| `data[].useSalesNavigatorForLinkedInTasks` | `boolean` | Use sales navigator for linked in tasks |
| `data[].userGuid` | `string` | User guid |
| `data[].username` | `string` | Username |
| `data[].usersViewId` | `integer` | Users view id |
| `data[].voicemailNotificationEnabled` | `boolean` | Voicemail notification enabled |
| `data[].voicemailPrompts` | `array` | Voicemail prompts |
| `data[].weeklyDigestEmailEnabled` | `boolean` | Weekly digest email enabled |

</details>

### Users Context Store SQL Query

Run a SQL query against users records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "users",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.users.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Stages

### Stages List

Returns a paginated list of opportunity stages

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "stages",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.stages.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stages",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Stages Get

Get a single stage by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "stages",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.stages.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stages",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Stage ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Stages Context Store Search

Search and filter stages records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "stages",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "color": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.stages.context_store_search(
    query={"filter": {"eq": {"color": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stages",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"color": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `color` | `string` | Color |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `id` | `integer` | Unique stage identifier |
| `name` | `string` | Name |
| `order` | `integer` | Order |
| `prospects` | `array` | Prospects |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].color` | `string` | Color |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].id` | `integer` | Unique stage identifier |
| `data[].name` | `string` | Name |
| `data[].order` | `integer` | Order |
| `data[].prospects` | `array` | Prospects |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |

</details>

### Stages Context Store SQL Query

Run a SQL query against stages records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "stages",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.stages.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stages",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Personas

### Personas List

Returns a paginated list of personas

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "personas",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.personas.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "personas",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Personas Get

Get a single persona by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "personas",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.personas.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "personas",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Persona ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Personas Context Store Search

Search and filter personas records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "personas",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "createdAt": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.personas.context_store_search(
    query={"filter": {"eq": {"createdAt": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "personas",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"createdAt": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `createdAt` | `string` | Created at |
| `description` | `string` | Description |
| `id` | `integer` | Unique persona identifier |
| `name` | `string` | Name |
| `prospects` | `array` | Prospects |
| `updatedAt` | `string` | Updated at |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].createdAt` | `string` | Created at |
| `data[].description` | `string` | Description |
| `data[].id` | `integer` | Unique persona identifier |
| `data[].name` | `string` | Name |
| `data[].prospects` | `array` | Prospects |
| `data[].updatedAt` | `string` | Updated at |

</details>

### Personas Context Store SQL Query

Run a SQL query against personas records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "personas",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.personas.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "personas",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Templates

### Templates List

Returns a paginated list of email templates

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "templates",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.templates.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "templates",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Templates Get

Get a single template by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "templates",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.templates.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "templates",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Template ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Templates Context Store Search

Search and filter templates records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "templates",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "archived": true
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.templates.context_store_search(
    query={"filter": {"eq": {"archived": True}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "templates",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"archived": True}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `archived` | `boolean` | Archived |
| `archivedAt` | `string` | Archived at |
| `bccRecipients` | `string` | Bcc recipients |
| `bodyHtml` | `string` | Body html |
| `bodyText` | `string` | Body text |
| `bounceCount` | `integer` | Bounce count |
| `ccRecipients` | `string` | Cc recipients |
| `clickCount` | `integer` | Click count |
| `contentCategoryMemberships` | `array` | Content category memberships |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `deliverCount` | `integer` | Deliver count |
| `failureCount` | `integer` | Failure count |
| `id` | `integer` | Unique template identifier |
| `lastUsedAt` | `string` | Last used at |
| `name` | `string` | Name |
| `negativeReplyCount` | `integer` | Negative reply count |
| `neutralReplyCount` | `integer` | Neutral reply count |
| `openCount` | `integer` | Open count |
| `optOutCount` | `integer` | Opt out count |
| `owner` | `array` | Owner |
| `positiveReplyCount` | `integer` | Positive reply count |
| `recipients` | `array` | Recipients |
| `replyCount` | `integer` | Reply count |
| `scheduleCount` | `integer` | Schedule count |
| `sequenceTemplates` | `array` | Sequence templates |
| `shareType` | `string` | Share type |
| `subject` | `string` | Subject |
| `tags` | `string` | Tags |
| `toRecipients` | `string` | To recipients |
| `trackLinks` | `boolean` | Track links |
| `trackOpens` | `boolean` | Track opens |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].archived` | `boolean` | Archived |
| `data[].archivedAt` | `string` | Archived at |
| `data[].bccRecipients` | `string` | Bcc recipients |
| `data[].bodyHtml` | `string` | Body html |
| `data[].bodyText` | `string` | Body text |
| `data[].bounceCount` | `integer` | Bounce count |
| `data[].ccRecipients` | `string` | Cc recipients |
| `data[].clickCount` | `integer` | Click count |
| `data[].contentCategoryMemberships` | `array` | Content category memberships |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].deliverCount` | `integer` | Deliver count |
| `data[].failureCount` | `integer` | Failure count |
| `data[].id` | `integer` | Unique template identifier |
| `data[].lastUsedAt` | `string` | Last used at |
| `data[].name` | `string` | Name |
| `data[].negativeReplyCount` | `integer` | Negative reply count |
| `data[].neutralReplyCount` | `integer` | Neutral reply count |
| `data[].openCount` | `integer` | Open count |
| `data[].optOutCount` | `integer` | Opt out count |
| `data[].owner` | `array` | Owner |
| `data[].positiveReplyCount` | `integer` | Positive reply count |
| `data[].recipients` | `array` | Recipients |
| `data[].replyCount` | `integer` | Reply count |
| `data[].scheduleCount` | `integer` | Schedule count |
| `data[].sequenceTemplates` | `array` | Sequence templates |
| `data[].shareType` | `string` | Share type |
| `data[].subject` | `string` | Subject |
| `data[].tags` | `string` | Tags |
| `data[].toRecipients` | `string` | To recipients |
| `data[].trackLinks` | `boolean` | Track links |
| `data[].trackOpens` | `boolean` | Track opens |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |

</details>

### Templates Context Store SQL Query

Run a SQL query against templates records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "templates",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.templates.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "templates",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

## Snippets

### Snippets List

Returns a paginated list of snippets

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "snippets",
  "action": "list"
}'
```

#### Python SDK

```python
await outreach.snippets.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "snippets",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page[size]` | `integer` | No | Number of items per page |
| `sort` | `string` | No | Sort field |
| `count` | `string` | No | Include count |
| `page[after]` | `string` | No | Cursor for the next page; use the page[after] value from meta.next_link |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


#### Meta

| Field Name | Type | Description |
|------------|------|-------------|
| `next_link` | `null \| string` |  |

</details>

### Snippets Get

Get a single snippet by ID

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "snippets",
  "action": "get",
  "params": {
    "id": 0
  }
}'
```

#### Python SDK

```python
await outreach.snippets.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "snippets",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | Snippet ID |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `type` | `null \| string` |  |
| `attributes` | `object` |  |
| `relationships` | `null \| object` |  |
| `links` | `object` |  |


</details>

### Snippets Context Store Search

Search and filter snippets records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "snippets",
  "action": "context_store_search",
  "params": {
    "query": {
      "filter": {
        "eq": {
          "bodyHtml": "<str>"
        }
      }
    }
  }
}'
```

#### Python SDK

```python
await outreach.snippets.context_store_search(
    query={"filter": {"eq": {"bodyHtml": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "snippets",
    "action": "context_store_search",
    "params": {
        "query": {"filter": {"eq": {"bodyHtml": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, startswith, endswith, contains, array_contains, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `bodyHtml` | `string` | Body html |
| `bodyText` | `string` | Body text |
| `contentCategoryMemberships` | `array` | Content category memberships |
| `createdAt` | `string` | Created at |
| `creator` | `array` | Creator |
| `id` | `integer` | Unique snippet identifier |
| `name` | `string` | Name |
| `owner` | `array` | Owner |
| `shareType` | `string` | Share type |
| `tags` | `string` | Tags |
| `updatedAt` | `string` | Updated at |
| `updater` | `array` | Updater |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].bodyHtml` | `string` | Body html |
| `data[].bodyText` | `string` | Body text |
| `data[].contentCategoryMemberships` | `array` | Content category memberships |
| `data[].createdAt` | `string` | Created at |
| `data[].creator` | `array` | Creator |
| `data[].id` | `integer` | Unique snippet identifier |
| `data[].name` | `string` | Name |
| `data[].owner` | `array` | Owner |
| `data[].shareType` | `string` | Share type |
| `data[].tags` | `string` | Tags |
| `data[].updatedAt` | `string` | Updated at |
| `data[].updater` | `array` | Updater |

</details>

### Snippets Context Store SQL Query

Run a SQL query against snippets records in the Airbyte Context Store. SQL projections may return any set of columns, so each result row is a dictionary matching the query's selected fields. Only available in hosted mode.

Use the hosted server documentation to find the qualified Context Store table name and SQL guidance.

#### CLI

```bash
airbyte-agent connectors execute --json '{
  "workspace": "<your_workspace_name>",
  "name": "outreach",
  "entity": "snippets",
  "action": "context_store_sql_query",
  "params": {
    "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
  }
}'
```

#### Python SDK

```python
await outreach.snippets.context_store_sql_query(
    sql="SELECT * FROM <qualified_context_store_table> LIMIT 100"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "snippets",
    "action": "context_store_sql_query",
    "params": {
        "sql": "SELECT * FROM <qualified_context_store_table> LIMIT 100"
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `sql` | `string` | Yes | SQL query to execute against this entity's Context Store data |
| `limit` | `integer` | No | Maximum results to return |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | Projected rows, with dictionary keys matching the selected columns |
| `meta` | `object` | Query metadata |
| `meta.has_more` | `boolean` | Whether the result was limited and more rows are available |
| `meta.cursor` | `null` | SQL query results do not use cursor pagination |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |

</details>

