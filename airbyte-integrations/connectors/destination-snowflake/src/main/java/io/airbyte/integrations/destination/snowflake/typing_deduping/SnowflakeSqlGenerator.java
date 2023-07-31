package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static java.util.stream.Collectors.joining;

import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.TableNotMigratedException;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import java.util.Map;
import org.apache.commons.text.StringSubstitutor;

public class SnowflakeSqlGenerator implements SqlGenerator<SnowflakeTableDefinition> {

  public static final String QUOTE = "\"";

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

  public String toDialectType(final AirbyteType type) {
    if (type instanceof final AirbyteProtocolType p) {
      return toDialectType(p);
    } else if (type instanceof Struct) {
      // TODO should this+array just be VARIANT?
      return "OBJECT";
    } else if (type instanceof Array) {
      return "ARRAY";
    } else if (type instanceof UnsupportedOneOf) {
      return "VARIANT";
    } else if (type instanceof final Union u) {
      final AirbyteType typeWithPrecedence = u.chooseType();
      // typeWithPrecedence is never a Union, so this recursion is safe.
      return toDialectType(typeWithPrecedence);
    }

    // Literally impossible; AirbyteType is a sealed interface.
    throw new IllegalArgumentException("Unsupported AirbyteType: " + type);
  }

  public String toDialectType(final AirbyteProtocolType airbyteProtocolType) {
    // TODO verify these types against normalization
    return switch (airbyteProtocolType) {
      case STRING -> "TEXT";
      case NUMBER -> "NUMBER";
      case INTEGER -> "INTEGER";
      case BOOLEAN -> "BOOLEAN";
      case TIMESTAMP_WITH_TIMEZONE -> "TIMESTAMP_TZ";
      case TIMESTAMP_WITHOUT_TIMEZONE -> "TIMESTAMP_NTZ";
      case TIME_WITH_TIMEZONE -> "STRING";
      case TIME_WITHOUT_TIMEZONE -> "TIME";
      case DATE -> "DATE";
      case UNKNOWN -> "VARIANT";
    };
  }

  @Override
  public String createTable(StreamConfig stream, String suffix) {
    final String columnDeclarations = stream.columns().entrySet().stream()
        .map(column -> column.getKey().name(QUOTE) + " " + toDialectType(column.getValue()))
        .collect(joining(",\n"));
    // TODO indexes and stuff
    return new StringSubstitutor(Map.of(
        "final_namespace", stream.id().finalNamespace(QUOTE),
        "final_table_id", stream.id().finalTableId(suffix, QUOTE),
        "column_declarations", columnDeclarations)).replace(
        """
        CREATE SCHEMA IF NOT EXISTS ${final_namespace};

        CREATE TABLE ${final_table_id} (
          _airbyte_raw_id STRING NOT NULL,
          _airbyte_extracted_at TIMESTAMP NOT NULL,
          _airbyte_meta VARIANT NOT NULL,
          ${column_declarations}
        );
        """);
  }

  @Override
  public boolean existingSchemaMatchesStreamConfig(StreamConfig stream, SnowflakeTableDefinition existingTable) throws TableNotMigratedException {
    return false;
  }

  @Override
  public String updateTable(StreamConfig stream, String finalSuffix) {
    return updateTable(stream, finalSuffix, true);
  }

  private String updateTable(StreamConfig stream, String finalSuffix, boolean verifyPrimaryKeys) {
    return "";
  }

  @Override
  public String overwriteFinalTable(StreamId stream, String finalSuffix) {
    return "";
  }

  @Override
  public String softReset(StreamConfig stream) {
    String createTempTable = createTable(stream, SOFT_RESET_SUFFIX);
    String clearLoadedAt = clearLoadedAt(stream.id());
    final String rebuildInTempTable = updateTable(stream, SOFT_RESET_SUFFIX, false);
    final String overwriteFinalTable = overwriteFinalTable(stream.id(), SOFT_RESET_SUFFIX);
    return String.join("\n", createTempTable, clearLoadedAt, rebuildInTempTable, overwriteFinalTable);
  }

  private String clearLoadedAt(final StreamId streamId) {
    return new StringSubstitutor(Map.of("raw_table_id", streamId.rawTableId(QUOTE)))
        .replace("""
            UPDATE ${raw_table_id} SET _airbyte_loaded_at = NULL;
            """);
  }

}
