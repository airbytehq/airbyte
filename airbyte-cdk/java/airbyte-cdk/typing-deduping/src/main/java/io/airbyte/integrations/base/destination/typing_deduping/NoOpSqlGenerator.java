/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Optional;
import lombok.NoArgsConstructor;

@NoArgsConstructor
public class NoOpSqlGenerator implements SqlGenerator {

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    return null;
  }

  @Override
  public ColumnId buildColumnId(final String name) {
    return SqlGenerator.super.buildColumnId(name);
  }

  @Override
  public ColumnId buildColumnId(final String name, final String suffix) {
    return null;
  }

  @Override
  public Sql createTable(final StreamConfig stream, final String suffix, final boolean force) {
    return null;
  }

  @Override
  public Sql createSchema(final String schema) {
    return null;
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final Object existingTable) {
    return false;
  }

  @Override
  public Sql updateTable(final StreamConfig stream,
                         final String finalSuffix,
                         final Optional minRawTimestamp,
                         final boolean useExpensiveSaferCasting) {
    return null;
  }

  @Override
  public Sql overwriteFinalTable(final StreamId stream, final String finalSuffix) {
    return null;
  }

  @Override
  public Sql migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    return null;
  }

  @Override
  public Sql prepareTablesForSoftReset(final StreamConfig stream) {
    return SqlGenerator.super.prepareTablesForSoftReset(stream);
  }

  @Override
  public Sql clearLoadedAt(final StreamId streamId) {
    return null;
  }

  @Override
  public boolean shouldRetry(final Exception e) {
    return SqlGenerator.super.shouldRetry(e);
  }

}
