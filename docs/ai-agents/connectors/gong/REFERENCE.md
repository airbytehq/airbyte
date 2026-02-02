# Gong full reference

This is the full reference documentation for the Gong agent connector.

## Supported entities and actions

The Gong connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Users | [List](#users-list), [Get](#users-get) |
| Calls | [List](#calls-list), [Get](#calls-get) |
| Calls Extensive | [List](#calls-extensive-list) |
| Call Audio | [Download](#call-audio-download) |
| Call Video | [Download](#call-video-download) |
| Workspaces | [List](#workspaces-list) |
| Call Transcripts | [List](#call-transcripts-list) |
| Stats Activity Aggregate | [List](#stats-activity-aggregate-list) |
| Stats Activity Day By Day | [List](#stats-activity-day-by-day-list) |
| Stats Interaction | [List](#stats-interaction-list) |
| Settings Scorecards | [List](#settings-scorecards-list) |
| Settings Trackers | [List](#settings-trackers-list) |
| Library Folders | [List](#library-folders-list) |
| Library Folder Content | [List](#library-folder-content-list) |
| Coaching | [List](#coaching-list) |
| Stats Activity Scorecards | [List](#stats-activity-scorecards-list) |

### Users

#### Users List

Returns a list of all users in the Gong account

**Python SDK**

```python
await gong.users.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `emailAddress` | `string` |  |
| `created` | `string` |  |
| `active` | `boolean` |  |
| `emailAliases` | `array<string>` |  |
| `trustedEmailAddress` | `string \| null` |  |
| `firstName` | `string` |  |
| `lastName` | `string` |  |
| `title` | `string \| null` |  |
| `phoneNumber` | `string \| null` |  |
| `extension` | `string \| null` |  |
| `personalMeetingUrls` | `array<string>` |  |
| `settings` | `object` |  |
| `managerId` | `string \| null` |  |
| `meetingConsentPageUrl` | `string \| null` |  |
| `spokenLanguages` | `array<object>` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.totalRecords` | `integer` |  |
| `pagination.currentPageSize` | `integer` |  |
| `pagination.currentPageNumber` | `integer` |  |
| `pagination.cursor` | `string` |  |

</details>

#### Users Get

Get a single user by ID

**Python SDK**

```python
await gong.users.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | User ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `emailAddress` | `string` |  |
| `created` | `string` |  |
| `active` | `boolean` |  |
| `emailAliases` | `array<string>` |  |
| `trustedEmailAddress` | `string \| null` |  |
| `firstName` | `string` |  |
| `lastName` | `string` |  |
| `title` | `string \| null` |  |
| `phoneNumber` | `string \| null` |  |
| `extension` | `string \| null` |  |
| `personalMeetingUrls` | `array<string>` |  |
| `settings` | `object` |  |
| `managerId` | `string \| null` |  |
| `meetingConsentPageUrl` | `string \| null` |  |
| `spokenLanguages` | `array<object>` |  |


</details>

### Calls

#### Calls List

Retrieve calls data by date range

**Python SDK**

```python
await gong.calls.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `fromDateTime` | `string` | No | Start date in ISO 8601 format |
| `toDateTime` | `string` | No | End date in ISO 8601 format |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `scheduled` | `string` |  |
| `started` | `string` |  |
| `duration` | `integer` |  |
| `primaryUserId` | `string` |  |
| `direction` | `string` |  |
| `system` | `string` |  |
| `scope` | `string` |  |
| `media` | `string` |  |
| `language` | `string` |  |
| `workspaceId` | `string` |  |
| `sdrDisposition` | `string \| null` |  |
| `clientUniqueId` | `string \| null` |  |
| `customData` | `string \| null` |  |
| `purpose` | `string \| null` |  |
| `meetingUrl` | `string` |  |
| `isPrivate` | `boolean` |  |
| `calendarEventId` | `string \| null` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.totalRecords` | `integer` |  |
| `pagination.currentPageSize` | `integer` |  |
| `pagination.currentPageNumber` | `integer` |  |
| `pagination.cursor` | `string` |  |

</details>

#### Calls Get

Get specific call data by ID

**Python SDK**

```python
await gong.calls.get(
    id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | Call ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `url` | `string` |  |
| `title` | `string` |  |
| `scheduled` | `string` |  |
| `started` | `string` |  |
| `duration` | `integer` |  |
| `primaryUserId` | `string` |  |
| `direction` | `string` |  |
| `system` | `string` |  |
| `scope` | `string` |  |
| `media` | `string` |  |
| `language` | `string` |  |
| `workspaceId` | `string` |  |
| `sdrDisposition` | `string \| null` |  |
| `clientUniqueId` | `string \| null` |  |
| `customData` | `string \| null` |  |
| `purpose` | `string \| null` |  |
| `meetingUrl` | `string` |  |
| `isPrivate` | `boolean` |  |
| `calendarEventId` | `string \| null` |  |


</details>

### Calls Extensive

#### Calls Extensive List

Retrieve detailed call data including participants, interaction stats, and content

**Python SDK**

```python
await gong.calls_extensive.list(
    filter={}
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "calls_extensive",
    "action": "list",
    "params": {
        "filter": {}
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `object` | Yes |  |
| `filter.fromDateTime` | `string` | No | Start date in ISO 8601 format |
| `filter.toDateTime` | `string` | No | End date in ISO 8601 format |
| `filter.callIds` | `array<string>` | No | List of specific call IDs to retrieve |
| `filter.workspaceId` | `string` | No | Filter by workspace ID |
| `contentSelector` | `object` | No | Select which content to include in the response |
| `contentSelector.context` | `"Extended"` | No | Context level for the data |
| `contentSelector.contextTiming` | `array<"Now" \| "TimeOfCall">` | No | Context timing options |
| `contentSelector.exposedFields` | `object` | No | Specify which fields to include in the response |
| `contentSelector.exposedFields.collaboration` | `object` | No |  |
| `contentSelector.exposedFields.collaboration.publicComments` | `boolean` | No | Include public comments |
| `contentSelector.exposedFields.content` | `object` | No |  |
| `contentSelector.exposedFields.content.pointsOfInterest` | `boolean` | No | Include points of interest (deprecated, use highlights) |
| `contentSelector.exposedFields.content.structure` | `boolean` | No | Include call structure |
| `contentSelector.exposedFields.content.topics` | `boolean` | No | Include topics discussed |
| `contentSelector.exposedFields.content.trackers` | `boolean` | No | Include trackers |
| `contentSelector.exposedFields.content.trackerOccurrences` | `boolean` | No | Include tracker occurrences |
| `contentSelector.exposedFields.content.brief` | `boolean` | No | Include call brief |
| `contentSelector.exposedFields.content.outline` | `boolean` | No | Include call outline |
| `contentSelector.exposedFields.content.highlights` | `boolean` | No | Include call highlights |
| `contentSelector.exposedFields.content.callOutcome` | `boolean` | No | Include call outcome |
| `contentSelector.exposedFields.content.keyPoints` | `boolean` | No | Include key points |
| `contentSelector.exposedFields.interaction` | `object` | No |  |
| `contentSelector.exposedFields.interaction.personInteractionStats` | `boolean` | No | Include person interaction statistics |
| `contentSelector.exposedFields.interaction.questions` | `boolean` | No | Include questions asked |
| `contentSelector.exposedFields.interaction.speakers` | `boolean` | No | Include speaker information |
| `contentSelector.exposedFields.interaction.video` | `boolean` | No | Include video interaction data |
| `contentSelector.exposedFields.media` | `boolean` | No | Include media URLs (audio/video) |
| `contentSelector.exposedFields.parties` | `boolean` | No | Include participant information |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `metaData` | `object` |  |
| `parties` | `array<object>` |  |
| `interaction` | `object` |  |
| `collaboration` | `object` |  |
| `content` | `object` |  |
| `media` | `object` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.totalRecords` | `integer` |  |
| `pagination.currentPageSize` | `integer` |  |
| `pagination.currentPageNumber` | `integer` |  |
| `pagination.cursor` | `string` |  |

</details>

### Call Audio

#### Call Audio Download

Downloads the audio media file for a call. Temporarily, the request body must be configured with:
\{"filter": \{"callIds": [CALL_ID]\}, "contentSelector": \{"exposedFields": \{"media": true\}\}\}


**Python SDK**

```python
async for chunk in gong.call_audio.download():# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_audio",
    "action": "download"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `object` | No |  |
| `filter.callIds` | `array<string>` | No | List containing the single call ID |
| `contentSelector` | `object` | No |  |
| `contentSelector.exposedFields` | `object` | No |  |
| `contentSelector.exposedFields.media` | `boolean` | No | Must be true to get media URLs |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


### Call Video

#### Call Video Download

Downloads the video media file for a call. Temporarily, the request body must be configured with:
\{"filter": \{"callIds": [CALL_ID]\}, "contentSelector": \{"exposedFields": \{"media": true\}\}\}


**Python SDK**

```python
async for chunk in gong.call_video.download():# Process each chunk (e.g., write to file)
    file.write(chunk)
```

> **Note**: Download operations return an async iterator of bytes chunks for memory-efficient streaming. Use `async for` to process chunks as they arrive.

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_video",
    "action": "download"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `object` | No |  |
| `filter.callIds` | `array<string>` | No | List containing the single call ID |
| `contentSelector` | `object` | No |  |
| `contentSelector.exposedFields` | `object` | No |  |
| `contentSelector.exposedFields.media` | `boolean` | No | Must be true to get media URLs |
| `range_header` | `string` | No | Optional Range header for partial downloads (e.g., 'bytes=0-99') |


### Workspaces

#### Workspaces List

List all company workspaces

**Python SDK**

```python
await gong.workspaces.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "workspaces",
    "action": "list"
}'
```



<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `workspaceId` | `string` |  |
| `name` | `string` |  |
| `description` | `string` |  |


</details>

### Call Transcripts

#### Call Transcripts List

Returns transcripts for calls in a specified date range or specific call IDs

**Python SDK**

```python
await gong.call_transcripts.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "call_transcripts",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `object` | No |  |
| `filter.fromDateTime` | `string` | No | Start date in ISO 8601 format (optional if callIds provided) |
| `filter.toDateTime` | `string` | No | End date in ISO 8601 format (optional if callIds provided) |
| `filter.callIds` | `array<string>` | No | List of specific call IDs to retrieve transcripts for |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `callId` | `string` |  |
| `transcript` | `array<object>` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.totalRecords` | `integer` |  |
| `pagination.currentPageSize` | `integer` |  |
| `pagination.currentPageNumber` | `integer` |  |
| `pagination.cursor` | `string` |  |

</details>

### Stats Activity Aggregate

#### Stats Activity Aggregate List

Provides aggregated user activity metrics across a specified period

**Python SDK**

```python
await gong.stats_activity_aggregate.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stats_activity_aggregate",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `object` | No |  |
| `filter.fromDate` | `string` | No | Start date (YYYY-MM-DD) |
| `filter.toDate` | `string` | No | End date (YYYY-MM-DD) |
| `filter.userIds` | `array<string>` | No | List of user IDs to retrieve stats for |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `userId` | `string` |  |
| `userEmailAddress` | `string` |  |
| `userAggregateActivityStats` | `object` |  |
| `userAggregateActivityStats.callsAsHost` | `integer` |  |
| `userAggregateActivityStats.callsGaveFeedback` | `integer` |  |
| `userAggregateActivityStats.callsRequestedFeedback` | `integer` |  |
| `userAggregateActivityStats.callsReceivedFeedback` | `integer` |  |
| `userAggregateActivityStats.ownCallsListenedTo` | `integer` |  |
| `userAggregateActivityStats.othersCallsListenedTo` | `integer` |  |
| `userAggregateActivityStats.callsSharedInternally` | `integer` |  |
| `userAggregateActivityStats.callsSharedExternally` | `integer` |  |
| `userAggregateActivityStats.callsScorecardsFilled` | `integer` |  |
| `userAggregateActivityStats.callsScorecardsReceived` | `integer` |  |
| `userAggregateActivityStats.callsAttended` | `integer` |  |
| `userAggregateActivityStats.callsCommentsGiven` | `integer` |  |
| `userAggregateActivityStats.callsCommentsReceived` | `integer` |  |
| `userAggregateActivityStats.callsMarkedAsFeedbackGiven` | `integer` |  |
| `userAggregateActivityStats.callsMarkedAsFeedbackReceived` | `integer` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.totalRecords` | `integer` |  |
| `pagination.currentPageSize` | `integer` |  |
| `pagination.currentPageNumber` | `integer` |  |
| `pagination.cursor` | `string` |  |

</details>

### Stats Activity Day By Day

#### Stats Activity Day By Day List

Delivers daily user activity metrics across a specified date range

**Python SDK**

```python
await gong.stats_activity_day_by_day.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stats_activity_day_by_day",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `object` | No |  |
| `filter.fromDate` | `string` | No | Start date (YYYY-MM-DD) |
| `filter.toDate` | `string` | No | End date (YYYY-MM-DD) |
| `filter.userIds` | `array<string>` | No | List of user IDs to retrieve stats for |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `userId` | `string` |  |
| `userEmailAddress` | `string` |  |
| `userDailyActivityStats` | `array<object>` |  |
| `userDailyActivityStats[].callsAsHost` | `array<string>` |  |
| `userDailyActivityStats[].callsGaveFeedback` | `array<string>` |  |
| `userDailyActivityStats[].callsRequestedFeedback` | `array<string>` |  |
| `userDailyActivityStats[].callsReceivedFeedback` | `array<string>` |  |
| `userDailyActivityStats[].ownCallsListenedTo` | `array<string>` |  |
| `userDailyActivityStats[].othersCallsListenedTo` | `array<string>` |  |
| `userDailyActivityStats[].callsSharedInternally` | `array<string>` |  |
| `userDailyActivityStats[].callsSharedExternally` | `array<string>` |  |
| `userDailyActivityStats[].callsAttended` | `array<string>` |  |
| `userDailyActivityStats[].callsCommentsGiven` | `array<string>` |  |
| `userDailyActivityStats[].callsCommentsReceived` | `array<string>` |  |
| `userDailyActivityStats[].callsMarkedAsFeedbackGiven` | `array<string>` |  |
| `userDailyActivityStats[].callsMarkedAsFeedbackReceived` | `array<string>` |  |
| `userDailyActivityStats[].callsScorecardsFilled` | `array<string>` |  |
| `userDailyActivityStats[].callsScorecardsReceived` | `array<string>` |  |
| `userDailyActivityStats[].fromDate` | `string` |  |
| `userDailyActivityStats[].toDate` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.totalRecords` | `integer` |  |
| `pagination.currentPageSize` | `integer` |  |
| `pagination.currentPageNumber` | `integer` |  |
| `pagination.cursor` | `string` |  |

</details>

### Stats Interaction

#### Stats Interaction List

Returns interaction stats for users based on calls that have Whisper turned on

**Python SDK**

```python
await gong.stats_interaction.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stats_interaction",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `object` | No |  |
| `filter.fromDate` | `string` | No | Start date (YYYY-MM-DD) |
| `filter.toDate` | `string` | No | End date (YYYY-MM-DD) |
| `filter.userIds` | `array<string>` | No | List of user IDs to retrieve stats for |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `userId` | `string` |  |
| `userEmailAddress` | `string` |  |
| `personInteractionStats` | `array<object>` |  |
| `personInteractionStats[].name` | `string` |  |
| `personInteractionStats[].value` | `number` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.totalRecords` | `integer` |  |
| `pagination.currentPageSize` | `integer` |  |
| `pagination.currentPageNumber` | `integer` |  |
| `pagination.cursor` | `string` |  |

</details>

### Settings Scorecards

#### Settings Scorecards List

Retrieve all scorecard configurations in the company

**Python SDK**

```python
await gong.settings_scorecards.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "settings_scorecards",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspaceId` | `string` | No | Filter scorecards by workspace ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `scorecardId` | `string` |  |
| `scorecardName` | `string` |  |
| `workspaceId` | `string \| null` |  |
| `enabled` | `boolean` |  |
| `updaterUserId` | `string` |  |
| `created` | `string` |  |
| `updated` | `string` |  |
| `reviewMethod` | `string` |  |
| `questions` | `array<object>` |  |
| `questions[].questionId` | `string` |  |
| `questions[].questionRevisionId` | `string` |  |
| `questions[].questionText` | `string` |  |
| `questions[].questionType` | `string` |  |
| `questions[].isRequired` | `boolean` |  |
| `questions[].isOverall` | `boolean` |  |
| `questions[].updaterUserId` | `string` |  |
| `questions[].answerGuide` | `string \| null` |  |
| `questions[].minRange` | `string \| null` |  |
| `questions[].maxRange` | `string \| null` |  |
| `questions[].created` | `string` |  |
| `questions[].updated` | `string` |  |
| `questions[].answerOptions` | `array<object>` |  |


</details>

### Settings Trackers

#### Settings Trackers List

Retrieve all keyword tracker configurations in the company

**Python SDK**

```python
await gong.settings_trackers.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "settings_trackers",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspaceId` | `string` | No | Filter trackers by workspace ID |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `trackerId` | `string` |  |
| `trackerName` | `string` |  |
| `workspaceId` | `string \| null` |  |
| `languageKeywords` | `array<object>` |  |
| `affiliation` | `string` |  |
| `partOfQuestion` | `boolean` |  |
| `saidAt` | `string` |  |
| `saidAtInterval` | `string \| null` |  |
| `saidAtUnit` | `string \| null` |  |
| `saidInTopics` | `array<string>` |  |
| `filterQuery` | `string` |  |
| `created` | `string` |  |
| `creatorUserId` | `string \| null` |  |
| `updated` | `string` |  |
| `updaterUserId` | `string \| null` |  |


</details>

### Library Folders

#### Library Folders List

Retrieve the folder structure of the call library

**Python SDK**

```python
await gong.library_folders.list(
    workspace_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "library_folders",
    "action": "list",
    "params": {
        "workspaceId": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspaceId` | `string` | Yes | Workspace ID to retrieve folders from |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `name` | `string` |  |
| `parentFolderId` | `string \| null` |  |
| `createdBy` | `string \| null` |  |
| `updated` | `string` |  |


</details>

### Library Folder Content

#### Library Folder Content List

Retrieve calls in a specific library folder

**Python SDK**

```python
await gong.library_folder_content.list(
    folder_id="<str>"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "library_folder_content",
    "action": "list",
    "params": {
        "folderId": "<str>"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `folderId` | `string` | Yes | Folder ID to retrieve content from |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `callId` | `string` |  |
| `title` | `string` |  |
| `started` | `string` |  |
| `duration` | `integer` |  |
| `primaryUserId` | `string` |  |
| `url` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.totalRecords` | `integer` |  |
| `pagination.currentPageSize` | `integer` |  |
| `pagination.currentPageNumber` | `integer` |  |
| `pagination.cursor` | `string` |  |

</details>

### Coaching

#### Coaching List

Retrieve coaching metrics for a manager and their direct reports

**Python SDK**

```python
await gong.coaching.list(
    workspace_id="<str>",
    manager_id="<str>",
    from_="2025-01-01T00:00:00Z",
    to="2025-01-01T00:00:00Z"
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "coaching",
    "action": "list",
    "params": {
        "workspace-id": "<str>",
        "manager-id": "<str>",
        "from": "2025-01-01T00:00:00Z",
        "to": "2025-01-01T00:00:00Z"
    }
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `workspace-id` | `string` | Yes | Workspace ID |
| `manager-id` | `string` | Yes | Manager user ID |
| `from` | `string` | Yes | Start date in ISO 8601 format |
| `to` | `string` | Yes | End date in ISO 8601 format |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `userId` | `string` |  |
| `userEmailAddress` | `string` |  |
| `userName` | `string` |  |
| `isManager` | `boolean` |  |
| `coachingMetrics` | `object` |  |
| `coachingMetrics.callsListened` | `integer` |  |
| `coachingMetrics.callsAttended` | `integer` |  |
| `coachingMetrics.callsWithFeedback` | `integer` |  |
| `coachingMetrics.callsWithComments` | `integer` |  |
| `coachingMetrics.scorecardsFilled` | `integer` |  |


</details>

### Stats Activity Scorecards

#### Stats Activity Scorecards List

Retrieve answered scorecards for applicable reviewed users or scorecards for a date range

**Python SDK**

```python
await gong.stats_activity_scorecards.list()
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances/{your_connector_instance_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "stats_activity_scorecards",
    "action": "list"
}'
```


**Parameters**

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `filter` | `object` | No |  |
| `filter.fromDateTime` | `string` | No | Start date in ISO 8601 format |
| `filter.toDateTime` | `string` | No | End date in ISO 8601 format |
| `filter.scorecardIds` | `array<string>` | No | List of scorecard IDs to filter by |
| `filter.reviewedUserIds` | `array<string>` | No | List of reviewed user IDs to filter by |
| `filter.reviewerUserIds` | `array<string>` | No | List of reviewer user IDs to filter by |
| `filter.callIds` | `array<string>` | No | List of call IDs to filter by |
| `cursor` | `string` | No | Cursor for pagination |


<details>
<summary><b>Response Schema</b></summary>

**Records**

| Field Name | Type | Description |
|------------|------|-------------|
| `answeredScorecardId` | `string` |  |
| `scorecardId` | `string` |  |
| `scorecardName` | `string` |  |
| `callId` | `string` |  |
| `callStartTime` | `string` |  |
| `reviewedUserId` | `string` |  |
| `reviewerUserId` | `string` |  |
| `reviewMethod` | `string` |  |
| `editorUserId` | `string \| null` |  |
| `answeredDateTime` | `string` |  |
| `reviewTime` | `string` |  |
| `visibilityType` | `string` |  |
| `answers` | `array<object>` |  |
| `answers[].questionId` | `string` |  |
| `answers[].questionRevisionId` | `string` |  |
| `answers[].isOverall` | `boolean` |  |
| `answers[].answer` | `string` |  |
| `answers[].answerText` | `string \| null` |  |
| `answers[].score` | `number` |  |
| `answers[].notApplicable` | `boolean` |  |
| `answers[].selectedOptions` | `array \| null` |  |
| `overallScore` | `number` |  |
| `visibility` | `string` |  |


**Meta**

| Field Name | Type | Description |
|------------|------|-------------|
| `pagination` | `object` |  |
| `pagination.totalRecords` | `integer` |  |
| `pagination.currentPageSize` | `integer` |  |
| `pagination.currentPageNumber` | `integer` |  |
| `pagination.cursor` | `string` |  |

</details>



## Authentication

The Gong connector supports the following authentication methods.


### OAuth 2.0 Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_token` | `str` | Yes | Your Gong OAuth2 Access Token. Token refresh is managed externally. |

#### Example

**Python SDK**

```python
GongConnector(
  auth_config=GongOauth20AuthenticationAuthConfig(
    access_token="<Your Gong OAuth2 Access Token. Token refresh is managed externally.>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "32382e40-3b49-4b99-9c5c-4076501914e7",
  "auth_config": {
    "access_token": "<Your Gong OAuth2 Access Token. Token refresh is managed externally.>"
  },
  "name": "My Gong Connector"
}'
```


### Access Key Authentication

| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| `access_key` | `str` | Yes | Your Gong API Access Key |
| `access_key_secret` | `str` | Yes | Your Gong API Access Key Secret |

#### Example

**Python SDK**

```python
GongConnector(
  auth_config=GongAccessKeyAuthenticationAuthConfig(
    access_key="<Your Gong API Access Key>",
    access_key_secret="<Your Gong API Access Key Secret>"
  )
)
```

**API**

```bash
curl --location 'https://api.airbyte.ai/api/v1/connectors/instances' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
  "connector_definition_id": "32382e40-3b49-4b99-9c5c-4076501914e7",
  "auth_config": {
    "access_key": "<Your Gong API Access Key>",
    "access_key_secret": "<Your Gong API Access Key Secret>"
  },
  "name": "My Gong Connector"
}'
```

