/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TableNotMigratedException;

public class JdbcSqlGenerator implements SqlGenerator<JdbcDatabase> {

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    return null;
  }

  @Override
  public ColumnId buildColumnId(final String name) {
    return null;
  }

  @Override
  public String createTable(final StreamConfig stream, final String suffix) {
    return null;
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final JdbcDatabase existingTable) throws TableNotMigratedException {
    return false;
  }

  @Override
  public String softReset(final StreamConfig stream) {
    return null;
  }

  @Override
  public String updateTable(final StreamConfig stream, final String finalSuffix) {
    return null;
  }

  @Override
  public String overwriteFinalTable(final StreamId stream, final String finalSuffix) {
    return null;
  }

}
