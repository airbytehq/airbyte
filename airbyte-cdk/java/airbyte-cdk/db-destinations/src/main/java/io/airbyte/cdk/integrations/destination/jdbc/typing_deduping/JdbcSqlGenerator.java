/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.TypeInfoRecordSet;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import java.sql.JDBCType;
import java.sql.SQLException;
import java.sql.SQLType;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map.Entry;

public abstract class JdbcSqlGenerator implements SqlGenerator<TableDefinition> {

  private final NamingConventionTransformer namingTransformer;

  public JdbcSqlGenerator(final NamingConventionTransformer namingTransformer) {
    this.namingTransformer = namingTransformer;
  }

  @Override
  public StreamId buildStreamId(final String namespace, final String name, final String rawNamespaceOverride) {
    return new StreamId(
        namingTransformer.getNamespace(namespace),
        namingTransformer.convertStreamName(name),
        namingTransformer.getNamespace(rawNamespaceOverride),
        namingTransformer.convertStreamName(StreamId.concatenateRawTableName(namespace, name)),
        namespace,
        name);
  }

  public ColumnId buildColumnId(final String name, final String suffix) {
    final String nameWithSuffix = name + suffix;
    return new ColumnId(
        namingTransformer.getIdentifier(nameWithSuffix),
        name,
        namingTransformer.getIdentifier(nameWithSuffix));
  }

  protected String columnsAndTypes(final Statement statement, final StreamConfig stream, final SQLType structType) throws SQLException {
    final List<String> typeColumns = new ArrayList<>();
    for (final Entry<ColumnId, AirbyteType> entry : stream.columns().entrySet()) {
      typeColumns.add(
          String.join(" ", statement.enquoteIdentifier(entry.getKey().name(), false), toDialectType(entry.getValue(), structType).getName()));
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
    // TODO: Make this abstract, let vendor specific handle this logic.
    return preferredType(supportedTypes, List.of("VARIANT", "SUPER", "JSONB", "JSON"), widestType());
  }

  protected SQLType preferredType(final LinkedHashMap<String, TypeInfoRecordSet> supportedTypes,
                                  final List<String> orderedPreference,
                                  final SQLType fallback) {
    final var bestType = orderedPreference.stream()
        .filter(supportedTypes::containsKey)
        .map(preferredType -> new CustomSqlType(preferredType, vendorId(),
            supportedTypes.get(preferredType).dataType()))
        .findFirst();
    return bestType.isPresent() ? bestType.get() : fallback;
  }

  protected SQLType toDialectType(final AirbyteType type, final SQLType structType) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      return toDialectType(airbyteProtocolType, structType);
    }
    switch (type.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE:
        return structType;
      case Array.TYPE:
        return JDBCType.ARRAY;
      case Union.TYPE:
        return toDialectType(((Union) type).chooseType(), structType);
      default:
        throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    }
  }

  protected SQLType toDialectType(final AirbyteProtocolType airbyteProtocolType, final SQLType structType) {
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
      case UNKNOWN -> widestType();
    };
  }

}
