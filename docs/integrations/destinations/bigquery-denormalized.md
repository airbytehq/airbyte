# BigQuery Denormalized

See [destinations/bigquery](https://docs.airbyte.com/integrations/destinations/bigquery)

## Changelog

### bigquery-denormalized

| Version | Date       | Pull Request                                               | Subject                                                                                                                  |
| :------ | :--------- | :--------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| 1.5.0   | 2023-06-27 | [\#27781](https://github.com/airbytehq/airbyte/pull/27781) | License Update: Elv2                                                                                                     |
| 1.4.1   | 2023-05-17 | [\#26213](https://github.com/airbytehq/airbyte/pull/26213) | Fix bug in parsing file buffer config count                                                                              |
| 1.4.0   | 2023-04-28 | [\#25570](https://github.com/airbytehq/airbyte/pull/25570) | Fix: all integer schemas should be converted to Avro longs                                                               |
| 1.3.3   | 2023-04-27 | [\#25346](https://github.com/airbytehq/airbyte/pull/25346) | Internal code cleanup                                                                                                    |
| 1.3.0   | 2023-04-19 | [\#25287](https://github.com/airbytehq/airbyte/pull/25287) | Add parameter to configure the number of file buffers when GCS is used as the loading method                             |
| 1.2.20  | 2023-04-12 | [\#25122](https://github.com/airbytehq/airbyte/pull/25122) | Add additional data centers                                                                                              |
| 1.2.19  | 2023-03-29 | [\#24671](https://github.com/airbytehq/airbyte/pull/24671) | Fail faster in certain error cases                                                                                       |
| 1.2.18  | 2023-03-23 | [\#24447](https://github.com/airbytehq/airbyte/pull/24447) | Set the Service Account Key JSON field to always_show: true so that it isn't collapsed into an optional fields section   |
| 1.2.17  | 2023-03-17 | [\#23788](https://github.com/airbytehq/airbyte/pull/23788) | S3-Parquet: added handler to process null values in arrays                                                               |
| 1.2.16  | 2023-03-10 | [\#23931](https://github.com/airbytehq/airbyte/pull/23931) | Added support for periodic buffer flush                                                                                  |
| 1.2.15  | 2023-03-10 | [\#23466](https://github.com/airbytehq/airbyte/pull/23466) | Changed S3 Avro type from Int to Long                                                                                    |
| 1.2.14  | 2023-02-08 | [\#22497](https://github.com/airbytehq/airbyte/pull/22497) | Fixed table already exists error                                                                                         |
| 1.2.13  | 2023-01-26 | [\#20631](https://github.com/airbytehq/airbyte/pull/20631) | Added support for destination checkpointing with staging                                                                 |
| 1.2.12  | 2023-01-18 | [\#21087](https://github.com/airbytehq/airbyte/pull/21087) | Wrap Authentication Errors as Config Exceptions                                                                          |
| 1.2.11  | 2023-01-18 | [\#21144](https://github.com/airbytehq/airbyte/pull/21144) | Added explicit error message if sync fails due to a config issue                                                         |
| 1.2.10  | 2023-01-04 | [\#20730](https://github.com/airbytehq/airbyte/pull/20730) | An incoming source Number type will create a big query integer rather than a float.                                      |
| 1.2.9   | 2022-12-14 | [\#20501](https://github.com/airbytehq/airbyte/pull/20501) | Report GCS staging failures that occur during connection check                                                           |
| 1.2.8   | 2022-11-22 | [\#19489](https://github.com/airbytehq/airbyte/pull/19489) | Added non-billable projects handle to check connection stage                                                             |
| 1.2.7   | 2022-11-11 | [\#19358](https://github.com/airbytehq/airbyte/pull/19358) | Fixed check method to capture mismatch dataset location                                                                  |
| 1.2.6   | 2022-11-10 | [\#18554](https://github.com/airbytehq/airbyte/pull/18554) | Improve check connection method to handle more errors                                                                    |
| 1.2.5   | 2022-10-19 | [\#18162](https://github.com/airbytehq/airbyte/pull/18162) | Improve error logs                                                                                                       |
| 1.2.4   | 2022-09-26 | [\#16890](https://github.com/airbytehq/airbyte/pull/16890) | Add user-agent header                                                                                                    |
| 1.2.3   | 2022-09-22 | [\#17054](https://github.com/airbytehq/airbyte/pull/17054) | Respect stream namespace                                                                                                 |
| 1.2.2   | 2022-09-14 | [\#15668](https://github.com/airbytehq/airbyte/pull/15668) | (bugged, do not use) Wrap logs in AirbyteLogMessage                                                                      |
| 1.2.1   | 2022-09-10 | [\#16401](https://github.com/airbytehq/airbyte/pull/16401) | (bugged, do not use) Wrapping string objects with TextNode                                                               |
| 1.2.0   | 2022-09-09 | [\#14023](https://github.com/airbytehq/airbyte/pull/14023) | (bugged, do not use) Cover arrays only if they are nested                                                                |
| 1.1.16  | 2022-09-01 | [\#16243](https://github.com/airbytehq/airbyte/pull/16243) | Fix Json to Avro conversion when there is field name clash from combined restrictions (`anyOf`, `oneOf`, `allOf` fields) |
| 1.1.15  | 2022-08-03 | [\#14784](https://github.com/airbytehq/airbyte/pull/14784) | Enabling Application Default Credentials                                                                                 |
| 1.1.14  | 2022-08-02 | [\#14801](https://github.com/airbytehq/airbyte/pull/14801) | Fix multiple log bindings                                                                                                |
| 1.1.13  | 2022-08-02 | [\#15180](https://github.com/airbytehq/airbyte/pull/15180) | Fix standard loading mode                                                                                                |
| 1.1.12  | 2022-06-29 | [\#14079](https://github.com/airbytehq/airbyte/pull/14079) | Map "airbyte_type": "big_integer" to INT64                                                                               |
| 1.1.11  | 2022-06-24 | [\#14114](https://github.com/airbytehq/airbyte/pull/14114) | Remove "additionalProperties": false from specs for connectors with staging                                              |
| 1.1.10  | 2022-06-16 | [\#13852](https://github.com/airbytehq/airbyte/pull/13852) | Updated stacktrace format for any trace message errors                                                                   |
| 1.1.9   | 2022-06-17 | [\#13753](https://github.com/airbytehq/airbyte/pull/13753) | Deprecate and remove PART_SIZE_MB fields from connectors based on StreamTransferManager                                  |
| 1.1.8   | 2022-06-07 | [\#13579](https://github.com/airbytehq/airbyte/pull/13579) | Always check GCS bucket for GCS loading method to catch invalid HMAC keys.                                               |
| 1.1.7   | 2022-06-07 | [\#13424](https://github.com/airbytehq/airbyte/pull/13424) | Reordered fields for specification.                                                                                      |
| 1.1.6   | 2022-05-15 | [\#12768](https://github.com/airbytehq/airbyte/pull/12768) | Clarify that the service account key json field is required on cloud.                                                    |
| 0.3.5   | 2022-05-12 | [\#12805](https://github.com/airbytehq/airbyte/pull/12805) | Updated to latest base-java to emit AirbyteTraceMessage on error.                                                        |
| 0.3.4   | 2022-05-04 | [\#12578](https://github.com/airbytehq/airbyte/pull/12578) | In JSON to Avro conversion, log JSON field values that do not follow Avro schema for debugging.                          |
| 0.3.3   | 2022-05-02 | [\#12528](https://github.com/airbytehq/airbyte/pull/12528) | Update Dataset location field description                                                                                |
| 0.3.2   | 2022-04-29 | [\#12477](https://github.com/airbytehq/airbyte/pull/12477) | Dataset location is a required field                                                                                     |
| 0.3.1   | 2022-04-15 | [\#11978](https://github.com/airbytehq/airbyte/pull/11978) | Fixed emittedAt timestamp.                                                                                               |
| 0.3.0   | 2022-04-06 | [\#11776](https://github.com/airbytehq/airbyte/pull/11776) | Use serialized buffering strategy to reduce memory consumption.                                                          |
| 0.2.15  | 2022-04-05 | [\#11166](https://github.com/airbytehq/airbyte/pull/11166) | Fixed handling of anyOf and allOf fields                                                                                 |
| 0.2.14  | 2022-04-02 | [\#11620](https://github.com/airbytehq/airbyte/pull/11620) | Updated spec                                                                                                             |
| 0.2.13  | 2022-04-01 | [\#11636](https://github.com/airbytehq/airbyte/pull/11636) | Added new unit tests                                                                                                     |
| 0.2.12  | 2022-03-28 | [\#11454](https://github.com/airbytehq/airbyte/pull/11454) | Integration test enhancement for picking test-data and schemas                                                           |
| 0.2.11  | 2022-03-18 | [\#10793](https://github.com/airbytehq/airbyte/pull/10793) | Fix namespace with invalid characters                                                                                    |
| 0.2.10  | 2022-03-03 | [\#10755](https://github.com/airbytehq/airbyte/pull/10755) | Make sure to kill children threads and stop JVM                                                                          |
| 0.2.8   | 2022-02-14 | [\#10256](https://github.com/airbytehq/airbyte/pull/10256) | Add `-XX:+ExitOnOutOfMemoryError` JVM option                                                                             |
| 0.2.7   | 2022-02-01 | [\#9959](https://github.com/airbytehq/airbyte/pull/9959)   | Fix null pointer exception from buffered stream consumer.                                                                |
| 0.2.6   | 2022-01-29 | [\#9745](https://github.com/airbytehq/airbyte/pull/9745)   | Integrate with Sentry.                                                                                                   |
| 0.2.5   | 2022-01-18 | [\#9573](https://github.com/airbytehq/airbyte/pull/9573)   | BigQuery Destination : update description for some input fields                                                          |
| 0.2.4   | 2022-01-17 | [\#8383](https://github.com/airbytehq/airbyte/issues/8383) | BigQuery/BiqQuery denorm Destinations : Support dataset-id prefixed by project-id                                        |
| 0.2.3   | 2022-01-12 | [\#9415](https://github.com/airbytehq/airbyte/pull/9415)   | BigQuery Destination : Fix GCS processing of Facebook data                                                               |
| 0.2.2   | 2021-12-22 | [\#9039](https://github.com/airbytehq/airbyte/pull/9039)   | Added part_size configuration to UI for GCS staging                                                                      |
| 0.2.1   | 2021-12-21 | [\#8574](https://github.com/airbytehq/airbyte/pull/8574)   | Added namespace to Avro and Parquet record types                                                                         |
| 0.2.0   | 2021-12-17 | [\#8788](https://github.com/airbytehq/airbyte/pull/8788)   | BigQuery/BiqQuery denorm Destinations : Add possibility to use different types of GCS files                              |
| 0.1.11  | 2021-12-16 | [\#8816](https://github.com/airbytehq/airbyte/issues/8816) | Update dataset locations                                                                                                 |
| 0.1.10  | 2021-11-09 | [\#7804](https://github.com/airbytehq/airbyte/pull/7804)   | handle null values in fields described by a $ref definition                                                              |
| 0.1.9   | 2021-11-08 | [\#7736](https://github.com/airbytehq/airbyte/issues/7736) | Fixed the handling of ObjectNodes with $ref definition key                                                               |
| 0.1.8   | 2021-10-27 | [\#7413](https://github.com/airbytehq/airbyte/issues/7413) | Fixed DATETIME conversion for BigQuery                                                                                   |
| 0.1.7   | 2021-10-26 | [\#7240](https://github.com/airbytehq/airbyte/issues/7240) | Output partitioned/clustered tables                                                                                      |
| 0.1.6   | 2021-09-16 | [\#6145](https://github.com/airbytehq/airbyte/pull/6145)   | BigQuery Denormalized support for date, datetime & timestamp types through the json "format" key                         |
| 0.1.5   | 2021-09-07 | [\#5881](https://github.com/airbytehq/airbyte/pull/5881)   | BigQuery Denormalized NPE fix                                                                                            |
| 0.1.4   | 2021-09-04 | [\#5813](https://github.com/airbytehq/airbyte/pull/5813)   | fix Stackoverflow error when receive a schema from source where "Array" type doesn't contain a required "items" element  |
| 0.1.3   | 2021-08-07 | [\#5261](https://github.com/airbytehq/airbyte/pull/5261)   | 🐛 Destination BigQuery\(Denormalized\): Fix processing arrays of records                                                |
| 0.1.2   | 2021-07-30 | [\#5125](https://github.com/airbytehq/airbyte/pull/5125)   | Enable `additionalPropertities` in spec.json                                                                             |
| 0.1.1   | 2021-06-21 | [\#3555](https://github.com/airbytehq/airbyte/pull/3555)   | Partial Success in BufferedStreamConsumer                                                                                |
| 0.1.0   | 2021-06-21 | [\#4176](https://github.com/airbytehq/airbyte/pull/4176)   | Destination using Typed Struct and Repeated fields                                                                       |
