/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.JsonSchemaPrimitive;

public interface SourceOperations<QueryResult, SourceType> {

  JsonNode rowToJson(QueryResult queryResult) throws Exception;

  JsonSchemaPrimitive getType(SourceType sourceType);

}
