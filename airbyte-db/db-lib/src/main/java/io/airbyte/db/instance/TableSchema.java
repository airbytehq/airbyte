/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import com.fasterxml.jackson.databind.JsonNode;

public interface TableSchema {

  /**
   * @return table name in lower case
   */
  String getTableName();

  /**
   * @return the table definition in JsonSchema
   */
  JsonNode getTableDefinition();

}
