package io.airbyte.integrations.debezium.internals.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.JdbcDatabase;

/**
 * This class is inspired by Debezium's MySQL connector internal implementation on how it parses
 * the state
 */
public class MySqlDebeziumStateUtil {

  /**
   * Method to construct initial Debezium state which can be passed onto Debezium engine to make it
   * process binlogs from a specific offset and skip snapshot phase.
   */
  public JsonNode constructInitialDebeziumState(final JdbcDatabase database, final String dbName) {
    // TODO : Implement this.
    return null;
  }
}
