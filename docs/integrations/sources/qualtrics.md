# Qualtrics Source Connector for Airbyte

This page contains the setup guide and reference information for the Qualtrics source connector.

## Prerequisites

Before setting up the Qualtrics connector, ensure you have the following:

- A Qualtrics account
- An API key for your Qualtrics account

## Supported Sync Modes

The Qualtrics source connector supports the following sync modes:

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental - Append Sync | Yes (only for responses) |

## Supported Streams

This connector outputs the following streams:

- **Groups:** Retrieves information about the groups in your Qualtrics account.
- **Surveys:** Retrieves information about the surveys in your Qualtrics account.
- **Survey Questions:** Retrieves the questions for each survey.
- **Survey Responses:** Retrieves the responses for each survey.

### Stream Details:

1. **Groups:**
   - **Endpoint:** `/groups`
   - **Primary Key:** `id`

2. **Surveys:**
   - **Endpoint:** `/surveys`
   - **Primary Key:** `id`

3. **Surveys Questions:**
   - **Endpoint:** `/survey-definitions/{{ stream_partition.id }}/questions`
   - **Primary Key:** `id`
   - **Partitioned by:** `survey_id`

4. **Surveys Responses:**
   - **Endpoint:** `/surveys/{{ stream_partition.id }}/responses`
   - **Primary Key:** `responseId`
   - **Partitioned by:** `survey_id`
   - **Incremental Sync:** Supported using the `_lastModifiedDate` cursor field.

## Changelog

| Version | Date       | Pull Request                                      | Subject                                    |
|---------|------------|--------------------------------------------------|--------------------------------------------|
| 0.1.0  | 2024-06-05 | [38751](https://github.com/airbytehq/airbyte/pull/38751) | Initial release of Qualtrics connector    |


### Troubleshooting

For troubleshooting common issues, visit the [Airbyte Forum](https://github.com/airbytehq/airbyte/discussions).

## Additional Information

For more detailed documentation, visit the [Qualtrics API Documentation](https://api.qualtrics.com).
