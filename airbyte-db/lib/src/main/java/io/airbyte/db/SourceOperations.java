/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.sql.SQLException;

public interface SourceOperations<QueryResult, SourceType> {

  JsonNode rowToJson(QueryResult queryResult) throws SQLException;

  JsonSchemaPrimitive getType(SourceType sourceType);

}
