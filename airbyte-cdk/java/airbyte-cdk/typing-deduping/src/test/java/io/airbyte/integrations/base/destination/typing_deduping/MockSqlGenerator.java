/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.time.Instant;
import java.util.Optional;

/**
 * Basic SqlGenerator mock. See {@link DefaultTyperDeduperTest} for example usage.
 */
class MockSqlGenerator implements SqlGenerator<String> {

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    return null;
  }

  @Override
  public ColumnId buildColumnId(final String name, final String suffix) {
    return null;
  }

  @Override
  public String createTable(final StreamConfig stream, final String suffix, final boolean force) {
    return "CREATE TABLE " + stream.id().finalTableId("", suffix);
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final String existingTable) throws TableNotMigratedException {
    return false;
  }

  @Override
  public String updateTable(final StreamConfig stream,
                            final String finalSuffix,
                            final Optional<Instant> minRawTimestamp,
                            final boolean useExpensiveSaferCasting) {
    final String timestampFilter = minRawTimestamp
        .map(timestamp -> " WHERE extracted_at > " + timestamp)
        .orElse("");
    final String casting = useExpensiveSaferCasting ? " WITH" : " WITHOUT" + " SAFER CASTING";
    return "UPDATE TABLE " + stream.id().finalTableId("", finalSuffix) + casting + timestampFilter;
  }

  @Override
  public String overwriteFinalTable(final StreamId stream, final String finalSuffix) {
    return "OVERWRITE TABLE " + stream.finalTableId("") + " FROM " + stream.finalTableId("", finalSuffix);
  }

  @Override
  public String migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    return "MIGRATE TABLE " + String.join(".", namespace, tableName) + " TO " + streamId.rawTableId("");
  }

  @Override
  public String prepareTablesForSoftReset(final StreamConfig stream) {
    return "PREPARE " + String.join(".", stream.id().originalNamespace(), stream.id().originalName()) + " FOR SOFT RESET";
  }

}
