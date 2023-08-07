package io.airbyte.integrations.destination.jdbc.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TableNotMigratedException;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;

public class JdbcSqlGenerator implements SqlGenerator<JdbcDatabase> {

  private final NamingConventionTransformer namingTransformer;

  private final SqlOperations sqlOperations;

  public JdbcSqlGenerator(final NamingConventionTransformer namingTransformer, final SqlOperations sqlOperations) {
    this.namingTransformer = namingTransformer;
    this.sqlOperations = sqlOperations;
  }

  @Override
  public StreamId buildStreamId(String namespace, String name, String rawNamespaceOverride) {
    return new StreamId(
        namingTransformer.getNamespace(namespace),
        namingTransformer.convertStreamName(name),
        namingTransformer.getNamespace(rawNamespaceOverride),
        namingTransformer.convertStreamName(StreamId.concatenateRawTableName(namespace, name)),
        namespace,
        name
    );
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
