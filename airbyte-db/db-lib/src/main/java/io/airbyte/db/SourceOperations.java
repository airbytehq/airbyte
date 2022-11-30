/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.SQLException;

public interface SourceOperations<QueryResult, SourceType> {

  JsonNode rowToJson(QueryResult queryResult) throws SQLException;

  JsonSchemaType getJsonType(SourceType sourceType);

  //
  // JsonSchemaType getJsonSchemaType(SourceType columnType);
}
