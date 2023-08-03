package io.airbyte.integrations.destination.jdbc.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TableNotMigratedException;

public class JdbcSqlGenerator implements SqlGenerator<JdbcDatabase> {

  @Override
  public StreamId buildStreamId(String namespace, String name, String rawNamespaceOverride) {
    return null;
  }

  @Override
  public ColumnId buildColumnId(String name) {
    return null;
  }

  @Override
  public String createTable(StreamConfig stream, String suffix) {
    return null;
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(StreamConfig stream, JdbcDatabase existingTable) throws TableNotMigratedException {
    return false;
  }

  @Override
  public String softReset(StreamConfig stream) {
    return null;
  }

  @Override
  public String updateTable(StreamConfig stream, String finalSuffix) {
    return null;
  }

  @Override
  public String overwriteFinalTable(StreamId stream, String finalSuffix) {
    return null;
  }
}
