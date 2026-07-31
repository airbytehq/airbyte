# Contributing to source-twilio

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

## Incremental Stream Considerations

**Connector type:** Hybrid (manifest.yaml + Python custom components for datetime transformation and state migration)

**Analysis status:** Complete. 34 streams analyzed. 7 use incremental sync with date cursors. 27 are full-refresh. Most full-refresh streams are configuration/reference endpoints without date filtering support in the Twilio API.

### Incremental Streams

| Stream | Cursor Field | API Filter | Notes |
|--------|-------------|------------|-------|
| alerts | date_generated | `StartDate`/`EndDate` | Twilio Alerts API |
| calls | date_created (parameterized) | `StartTime`/`EndTime` | Twilio Calls API |
| conferences | date_created (parameterized) | `DateCreated` | Twilio Conferences API |
| message_media | date_created (parameterized) | `DateCreated` | Per-message media |
| messages | date_sent (parameterized) | `DateSent` | Twilio Messages API |
| recordings | date_created (parameterized) | `DateCreated` | Twilio Recordings API |
| usage_records | start_date (parameterized) | `StartDate`/`EndDate` | Twilio Usage Records API |

### Full-Refresh Streams (Not Actionable)

| Stream | Reason | Evidence |
|--------|--------|----------|
| accounts | Single record; no date filter | Returns account details |
| addresses | No date filter | Twilio Addresses API has no date param |
| applications | No date filter | Twilio Applications API has no date param |
| available_phone_number_countries | Reference data | Static list of countries |
| available_phone_numbers_local | Reference data | Available number search |
| available_phone_numbers_mobile | Reference data | Available number search |
| available_phone_numbers_toll_free | Reference data | Available number search |
| conference_participants | Substream; no date filter | Per-conference participants |
| conversations | No date filter | Twilio Conversations API has no date param |
| conversation_messages | No date filter | Per-conversation messages |
| conversation_participants | No date filter | Per-conversation participants |
| dependent_phone_numbers | Substream; no date filter | Per-address dependent numbers |
| executions | No date filter | Twilio Studio Executions API |
| flows | No date filter | Twilio Studio Flows API |
| incoming_phone_numbers | No date filter | Twilio Phone Numbers API |
| keys | Small dataset; no date filter | API keys list |
| outgoing_caller_ids | Small dataset; no date filter | Verified caller IDs |
| queues | Small dataset; no date filter | Call queues list |
| services | No date filter | Twilio Messaging Services |
| step | Substream of executions; no date filter | Per-execution steps |
| transcriptions | Deprecated endpoint | Twilio Transcriptions API (legacy) |
| trunks | Small dataset; no date filter | SIP trunks |
| usage_triggers | No date filter | Usage trigger configurations |
