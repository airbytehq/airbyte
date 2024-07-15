## Event Sharing

Sharing the events is important to ensure that in case of issue, our team can investigate easily. The app will never share private or sensitive information, only errors and diagnostic metrics that allow our team to understand the problem.

In order to share the events, you can refer to the [Snowflake documentation](https://other-docs.snowflake.com/en/native-apps/consumer-enable-logging#label-nativeapps-consumer-logging-enabling). As of 2023-10-02, you have to:

1. Create the event table. This table is global to an account so all applications share the same event table. We recommend using:

```
CREATE DATABASE event_database;
CREATE SCHEMA event_schema;
CREATE EVENT TABLE event_database.event_schema.event_table;
```

2. Make the table active for your account,

```
ALTER ACCOUNT SET EVENT_TABLE=event_database.event_schema.event_table;
```

3. Allow the application to share the logs.

```
ALTER APPLICATION <application name> SET SHARE_EVENTS_WITH_PROVIDER = TRUE`;
```
