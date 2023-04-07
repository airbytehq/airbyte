package io.airbyte.integrations.destination.bigquery.materialization;

import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;

// super rough guess at what this interface looks like.
// maybe we don't actually want this thing to be shared
// but we definitely will want something for jdbc destinations at least
public interface MaterializationOperations<Schema> {

  Schema getTableSchema(ConfiguredAirbyteStream stream);
  void createOrAlterTable(String datasetId, String tableName, Schema schema);
  void mergeFromRawTable(String dataset, String rawTable, String finalTable, ConfiguredAirbyteStream stream, Schema schema) throws InterruptedException;
}
