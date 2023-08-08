package io.airbyte.integrations.destination.jdbc.typing_deduping;

import com.google.protobuf.MapEntry;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.TableNotMigratedException;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.function.Supplier;
import javax.sql.DataSource;
import org.apache.commons.text.StringSubstitutor;

public class JdbcSqlGenerator implements SqlGenerator<JdbcDatabase> {

  private final NamingConventionTransformer namingTransformer;

  private final SqlOperations sqlOperations;

  private final Supplier<DataSource> dataSourceSupplier;

  public JdbcSqlGenerator(final NamingConventionTransformer namingTransformer, final SqlOperations sqlOperations,
                          final Supplier<DataSource> dataSourceSupplier) {
    this.namingTransformer = namingTransformer;
    this.sqlOperations = sqlOperations;
    this.dataSourceSupplier = dataSourceSupplier;
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

  private String columnsAndTypes(final Statement statement, StreamConfig stream) throws SQLException {
    List<String> typeColumns = new ArrayList<>();
    for (Entry<ColumnId, AirbyteType> entry : stream.columns().entrySet()) {
      String.join(" ", statement.enquoteIdentifier(entry.getKey().name(), false), )
    }


  }


  @Override
  public String createTable(StreamConfig stream, String suffix) {
    try {
      Statement statement = dataSourceSupplier.get().getConnection().createStatement();

      final String columnDeclarations = columnsAndTypes(statement, stream);
      return new StringSubstitutor(Map.of(
          "final_namespace",  statement.enquoteIdentifier(stream.id().finalNamespace(), false),
          "final_table_id", statement.enquoteIdentifier(stream.id().finalTableId("", suffix), false),
          "column_declarations", columnDeclarations,
      )).replace(
          """
              CREATE SCHEMA IF NOT EXISTS ${final_namespace};
  
              CREATE OR REPLACE TABLE ${final_table_id} (
                _airbyte_raw_id STRING NOT NULL,
                _airbyte_extracted_at TIMESTAMP NOT NULL,
                _airbyte_meta JSON NOT NULL,
              ${column_declarations}
              );
              """);
    } catch (Exception e) {
      // TODO something
    }

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
