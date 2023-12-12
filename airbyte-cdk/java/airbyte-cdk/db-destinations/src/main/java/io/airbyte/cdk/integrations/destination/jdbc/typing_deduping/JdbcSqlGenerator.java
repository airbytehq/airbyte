/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import org.jooq.DataType;
import org.jooq.SQLDialect;
import org.jooq.impl.SQLDataType;

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

  @Override
  public ColumnId buildColumnId(final String name, final String suffix) {
    final String nameWithSuffix = name + suffix;
    return new ColumnId(
        namingTransformer.getIdentifier(nameWithSuffix),
        name,
        namingTransformer.getIdentifier(nameWithSuffix));
  }

  protected DataType<?> toDialectType(final AirbyteType type) {
    if (type instanceof final AirbyteProtocolType airbyteProtocolType) {
      return toDialectType(airbyteProtocolType);
    }
    return switch (type.getTypeName()) {
      case Struct.TYPE, UnsupportedOneOf.TYPE -> getStructType();
      case Array.TYPE -> getArrayType();
      // No nested Unions supported so this will definitely not result in infinite recursion.
      case Union.TYPE -> toDialectType(((Union) type).chooseType());
      default -> throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
    };
  }

  protected DataType<?> toDialectType(final AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      // Many destinations default to a very short length (e.g. Redshift defaults to 256).
      // Explicitly set 64KiB here. Subclasses may want to override this value.
      case STRING -> SQLDataType.VARCHAR(65535);
      // We default to precision=38, scale=9 across destinations.
      // This is the default numeric parameters for both redshift and bigquery.
      case NUMBER -> SQLDataType.DECIMAL(38, 9);
      case INTEGER -> SQLDataType.BIGINT;
      case BOOLEAN -> SQLDataType.BOOLEAN;
      case TIMESTAMP_WITH_TIMEZONE -> SQLDataType.TIMESTAMPWITHTIMEZONE;
      case TIMESTAMP_WITHOUT_TIMEZONE -> SQLDataType.TIMESTAMP;
      case TIME_WITH_TIMEZONE -> SQLDataType.TIMEWITHTIMEZONE;
      case TIME_WITHOUT_TIMEZONE -> SQLDataType.TIME;
      case DATE -> SQLDataType.DATE;
      case UNKNOWN -> getWidestType();
    };
  }

  protected abstract DataType<?> getStructType();

  protected abstract DataType<?> getArrayType();

  protected abstract DataType<?> getWidestType();

  protected abstract SQLDialect getDialect();

}
