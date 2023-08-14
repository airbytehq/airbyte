package io.airbyte.integrations.destination.jdbc.typing_deduping;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.TableNotMigratedException;
import io.airbyte.integrations.base.destination.typing_deduping.TypeAndDedupeQueryBuilder;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.TypeInfoRecordSet;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.SQLException;
import java.sql.SQLType;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import javax.sql.DataSource;
import lombok.SneakyThrows;
import org.apache.commons.text.StringSubstitutor;

public class JdbcSqlGenerator implements SqlGenerator<JdbcDatabase>, TypeAndDedupeQueryBuilder {

  private final NamingConventionTransformer namingTransformer;

  private final SqlOperations sqlOperations;

  private final DataSource dataSourceSupplier;

  public JdbcSqlGenerator(final NamingConventionTransformer namingTransformer, final SqlOperations sqlOperations,
                          final DataSource dataSourceSupplier) {
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

  private String columnsAndTypes(final Statement statement, StreamConfig stream, final SQLType structType) throws SQLException {
    List<String> typeColumns = new ArrayList<>();
    for (Entry<ColumnId, AirbyteType> entry : stream.columns().entrySet()) {
      typeColumns.add(
          String.join(" ", statement.enquoteIdentifier(entry.getKey().name(), false), toDialectType(entry.getValue(), structType).getName())
      );
    }
    return String.join(",\n", typeColumns);
  }

  protected String vendorId() {
    return "JDBC";
  }

  protected SQLType widestType() {
    return JDBCType.VARCHAR;
  }

  protected SQLType preferredStructType(final LinkedHashMap<String, TypeInfoRecordSet> supportedTypes) {
    return preferredType(supportedTypes, List.of("VARIANT", "SUPER", "JSONB", "JSON"), widestType());
  }

  protected SQLType preferredType(final LinkedHashMap<String, TypeInfoRecordSet> supportedTypes, final List<String> orderedPreference,
                                  final SQLType fallback) {
    final var bestType = orderedPreference.stream()
                                          .filter(supportedTypes::containsKey)
                                          .map(preferredType -> new CustomSqlType(preferredType, vendorId(),
                                                                                  supportedTypes.get(preferredType).dataType()
                                          ))
                                          .findFirst();
    return bestType.isPresent() ? bestType.get() : fallback;
  }

  protected SQLType toDialectType(final AirbyteType type, SQLType structType) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      return toDialectType(airbyteProtocolType, structType);
    }
    switch (type.getTypeName()) {
      case Struct.STRUCT, UnsupportedOneOf.UNSUPPORTED_ONE_OF:
        return structType;
      case Array.ARRAY:
        return JDBCType.ARRAY;
      case Union.UNION:
        return toDialectType(((Union) type).chooseType(), structType);
      default:
        throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    }
  }

  protected SQLType toDialectType(final AirbyteProtocolType airbyteProtocolType, SQLType structType) {
    return switch (airbyteProtocolType) {
      case STRING -> JDBCType.VARCHAR;
      case NUMBER -> JDBCType.NUMERIC;
      case INTEGER -> JDBCType.BIGINT;
      case BOOLEAN -> JDBCType.BOOLEAN;
      case TIMESTAMP_WITH_TIMEZONE -> JDBCType.TIMESTAMP_WITH_TIMEZONE;
      case TIMESTAMP_WITHOUT_TIMEZONE -> JDBCType.TIMESTAMP;
      case TIME_WITH_TIMEZONE -> JDBCType.TIME_WITH_TIMEZONE;
      case TIME_WITHOUT_TIMEZONE -> JDBCType.TIME;
      case DATE -> JDBCType.DATE;
      case UNKNOWN -> structType;
    };
  }


  @SneakyThrows
  @Override
  public String createTable(StreamConfig stream, String suffix) {
    Connection connection = dataSourceSupplier.getConnection();
    Statement statement = connection.createStatement();
    SQLType structType = preferredStructType(TypeInfoRecordSet.getTypeInfoList(connection.getMetaData()));

    final String columnDeclarations = columnsAndTypes(statement, stream, structType);
    return new StringSubstitutor(Map.of(
        "final_namespace", statement.enquoteIdentifier(stream.id().finalNamespace(), false),
        "final_table_id", statement.enquoteIdentifier(stream.id().finalTableId("", suffix), false),
        "column_declarations", columnDeclarations,
        "json_type", structType.getName()
    )).replace(
        """
            CREATE SCHEMA IF NOT EXISTS ${final_namespace};
              
            CREATE OR REPLACE TABLE ${final_table_id} (
              _airbyte_raw_id VARCHAR PRIMARY KEY NOT NULL,
              _airbyte_extracted_at TIMESTAMP NOT NULL,
              _airbyte_meta ${json_type} NOT NULL,
            ${column_declarations}
            );
            """);
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(StreamConfig stream, JdbcDatabase existingTable) throws TableNotMigratedException {
    existingTable.getMetaData().getColumns()
  }

  @SneakyThrows
  @Override
  public String clearLoadedAt(final StreamId streamId) {
    Connection connection = dataSourceSupplier.getConnection();
    Statement statement = connection.createStatement();
    return new StringSubstitutor(Map.of("raw_table_id", statement.enquoteIdentifier(streamId.rawTableId(""), false)))
        .replace("""
                     UPDATE ${raw_table_id} SET _airbyte_loaded_at = NULL WHERE 1=1;
                     """);
  }

  @Override
  public String updateTable(StreamConfig stream, String finalSuffix, final boolean verifyPrimaryKeys) {
    return updateTableQuery(stream, finalSuffix, verifyPrimaryKeys);
  }

  @Override
  public String overwriteFinalTable(StreamId stream, String finalSuffix) {
    return null;
  }

  @Override
  public String migrateFromV1toV2(final StreamId streamId, final String namespace, final String tableName) {
    return null;
  }

  @Override
  public String validatePrimaryKeys(final StreamId id, final List<ColumnId> primaryKeys, final LinkedHashMap<ColumnId, AirbyteType> streamColumns) {
    return null;
  }

  @Override
  public String insertNewRecords(final StreamConfig stream, final String finalSuffix, final LinkedHashMap<ColumnId, AirbyteType> streamColumns) {
    return null;
  }

  @Override
  public String dedupRawTable(final StreamId id, final String finalSuffix) {
    return null;
  }

  @Override
  public String dedupFinalTable(final StreamId id, final String finalSuffix, final List<ColumnId> primaryKey, final ColumnId cursor) {
    return null;
  }

  @Override
  public String commitRawTable(final StreamId id) {
    return null;
  }

  @Override
  public String cdcDeletes(final StreamConfig stream, final String finalSuffix, final LinkedHashMap<ColumnId, AirbyteType> streamColumns) {
    return null;
  }
}
