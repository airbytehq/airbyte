package io.airbyte.integrations.destination.snowflake;

import static java.util.stream.Collectors.joining;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.text.StringSubstitutor;

public class SnowflakeTestUtils {

  public static List<JsonNode> dumpRawTable(JdbcDatabase database, String tableIdentifier) throws SQLException {
    return dumpTable(JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES, database, tableIdentifier);
  }

  public static List<JsonNode> dumpFinalTable(JdbcDatabase database, String tableIdentifier, String databaseName, String schema, String table) throws SQLException {
    // We have to discover the column names, because if we just SELECT * then snowflake will upcase all column names.
    List<String> columns = database.queryJsons(
            """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_catalog = ?
                  AND table_schema = ?
                  AND table_name = ?
                ORDER BY ordinal_position;
                """,
            databaseName,
            schema,
            table
        ).stream()
        .map(column -> column.get("COLUMN_NAME").asText())
        .toList();
    return dumpTable(columns, database, tableIdentifier);
  }

  /**
   * This is mostly identical to SnowflakeInsertDestinationAcceptanceTest, except it doesn't verify table type.
   *
   * @param tableIdentifier Table identifier (e.g. "schema.table"), with quotes if necessary.
   */
  public static List<JsonNode> dumpTable(List<String> columns, JdbcDatabase database, String tableIdentifier) throws SQLException {
    return database.bufferedResultSetQuery(connection -> {
      connection.createStatement().execute("ALTER SESSION SET TIMEZONE = 'UTC';");
      return connection.createStatement().executeQuery(new StringSubstitutor(Map.of(
          "columns", columns.stream().map(column -> '"' + column + '"').collect(joining(",")),
          "table", tableIdentifier
      )).replace(
          """
              SELECT ${columns} FROM ${table} ORDER BY "_airbyte_extracted_at" ASC
              """
          ));
    }, new SnowflakeTestSourceOperations()::rowToJson);
  }
}
