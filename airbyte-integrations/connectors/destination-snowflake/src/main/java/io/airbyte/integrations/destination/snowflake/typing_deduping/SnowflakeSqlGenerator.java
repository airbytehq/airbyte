package io.airbyte.integrations.destination.snowflake.typing_deduping;

import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TableNotMigratedException;

public class SnowflakeSqlGenerator implements SqlGenerator<SnowflakeTableDefinition> {
  @Override
  public StreamId buildStreamId(String namespace, String name, String rawNamespaceOverride) {
    // TODO
    return new StreamId(namespace, name, rawNamespaceOverride, StreamId.concatenateRawTableName(namespace, name), namespace, name);
  }

  @Override
  public ColumnId buildColumnId(String name) {
    // TODO
    return new ColumnId(name, name, name);
  }

  @Override
  public String createTable(StreamConfig stream, String suffix) {
    return null;
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(StreamConfig stream, SnowflakeTableDefinition existingTable) throws TableNotMigratedException {
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
