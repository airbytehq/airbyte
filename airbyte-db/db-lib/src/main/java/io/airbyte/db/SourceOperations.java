/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.SQLException;

public interface SourceOperations<QueryResult, SourceType> {

  /**
   * Converts a database row into it's JSON representation.
   *
   * @throws SQLException
   */
  JsonNode rowToJson(QueryResult queryResult) throws SQLException;

  /**
   * Converts a database source type into an Airbyte type, which is currently represented by a
   * {@link JsonSchemaType}
   */
  JsonSchemaType getAirbyteType(SourceType sourceType);

}
