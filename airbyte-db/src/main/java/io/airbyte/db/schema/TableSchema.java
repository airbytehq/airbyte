package io.airbyte.db.schema;

import com.fasterxml.jackson.databind.JsonNode;

public interface TableSchema {

  /**
   * @return table name in lower case
   */
  String getTableName();

  JsonNode getTableDefinition();

}
