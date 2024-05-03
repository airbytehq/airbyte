/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static java.util.stream.Collectors.joining;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator;
import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import org.apache.commons.text.StringSubstitutor;

public class SnowflakeTestUtils {

  public static List<JsonNode> dumpRawTable(final JdbcDatabase database, final String tableIdentifier) throws SQLException {
    return dumpTable(
        List.of(
            quote(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID),
            timestampToString(quote(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)),
            timestampToString(quote(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)),
            quote(JavaBaseConstants.COLUMN_NAME_DATA)),
        database,
        tableIdentifier,
        // Raw tables still have lowercase names
        false);
  }

  public static List<JsonNode> dumpFinalTable(final JdbcDatabase database, final String databaseName, final String schema, final String table)
      throws SQLException {
    // We have to discover the column names, because if we just SELECT * then snowflake will upcase all
    // column names.
    final List<String> columns = database.queryJsons(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        ORDER BY ordinal_position;
        """,
        unescapeIdentifier(databaseName).toUpperCase(),
        unescapeIdentifier(schema).toUpperCase(),
        unescapeIdentifier(table).toUpperCase()).stream()
        .map(column -> {
          final String quotedName = quote(column.get("COLUMN_NAME").asText());
          final String type = column.get("DATA_TYPE").asText();
          return switch (type) {
            // something about JDBC is mangling date/time values
            // E.g. 2023-01-01T00:00:00Z becomes 2022-12-31T16:00:00Z
            // Explicitly convert to varchar to prevent jdbc from doing this.
            case "TIMESTAMP_TZ" -> timestampToString(quotedName);
            case "TIMESTAMP_NTZ", "TIMESTAMP_LTZ" -> "TO_VARCHAR(" + quotedName + ", 'YYYY-MM-DD\"T\"HH24:MI:SS.FF') as " + quotedName;
            case "TIME" -> "TO_VARCHAR(" + quotedName + ", 'HH24:MI:SS.FF') as " + quotedName;
            case "DATE" -> "TO_VARCHAR(" + quotedName + ", 'YYYY-MM-DD') as " + quotedName;
            default -> quotedName;
          };
        })
        .toList();
    return dumpTable(columns, database, quote(schema) + "." + quote(table), true);
  }

  /**
   * This is mostly identical to SnowflakeInsertDestinationAcceptanceTest, except it doesn't verify
   * table type.
   * <p>
   * The columns param is a list of column names/aliases. For example,
   * {@code "_airbyte_extracted_at :: varchar AS "_airbyte_extracted_at"}.
   *
   * @param tableIdentifier Table identifier (e.g. "schema.table"), with quotes if necessary.
   */
  public static List<JsonNode> dumpTable(final List<String> columns,
                                         final JdbcDatabase database,
                                         final String tableIdentifier,
                                         final boolean upcaseExtractedAt)
      throws SQLException {
    return database.bufferedResultSetQuery(connection -> connection.createStatement().executeQuery(new StringSubstitutor(Map.of(
        "columns", columns.stream().collect(joining(",")),
        "table", tableIdentifier,
        "extracted_at", upcaseExtractedAt ? "_AIRBYTE_EXTRACTED_AT" : "\"_airbyte_extracted_at\"")).replace(
            """
            SELECT ${columns} FROM ${table} ORDER BY ${extracted_at} ASC
            """)),
        new SnowflakeSourceOperations()::rowToJson);
  }

  private static String quote(final String name) {
    return '"' + SnowflakeSqlGenerator.escapeJsonIdentifier(name) + '"';
  }

  public static String timestampToString(final String quotedName) {
    return "TO_VARCHAR(" + quotedName + ", 'YYYY-MM-DD\"T\"HH24:MI:SS.FFTZH:TZM') as " + quotedName;
  }

  private static String unescapeIdentifier(final String escapedIdentifier) {
    return escapedIdentifier.replace("\"\"", "\"");
  }

}
