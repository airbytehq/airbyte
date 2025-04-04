/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.JsonSchemaType
import java.sql.SQLException

interface SourceOperations<QueryResult, SourceType> {
    /**
     * Converts a database row into it's JSON representation.
     *
     * @throws SQLException
     */
    @Throws(SQLException::class) fun rowToJson(queryResult: QueryResult): JsonNode

    /**
     * Converts a database source type into an Airbyte type, which is currently represented by a
     * [JsonSchemaType]
     */
    fun getAirbyteType(sourceType: SourceType): JsonSchemaType
}
