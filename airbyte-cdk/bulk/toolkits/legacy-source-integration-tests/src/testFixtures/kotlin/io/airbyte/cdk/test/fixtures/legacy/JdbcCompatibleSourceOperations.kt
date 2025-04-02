/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import java.sql.*

interface JdbcCompatibleSourceOperations<SourceType> : SourceOperations<ResultSet, SourceType> {
    /**
     * Read from a result set, and copy the value of the column at colIndex to the Json object.
     *
     * @param colIndex 1-based column index.
     */
    @Throws(SQLException::class)
    fun copyToJsonField(resultSet: ResultSet, colIndex: Int, json: ObjectNode)

    /** Set the cursor field in incremental table query. */
    @Throws(SQLException::class)
    fun setCursorField(
        preparedStatement: PreparedStatement,
        parameterIndex: Int,
        cursorFieldType: SourceType?,
        value: String?
    )

    /** Determine the database specific type of the input field based on its column metadata. */
    fun getDatabaseFieldType(field: JsonNode): SourceType

    /**
     * This method will verify that filed could be used as cursor for incremental sync
     *
     * @param type
     * - table field type that should be checked
     * @return true is field type can be used as cursor field for incremental sync
     */
    fun isCursorType(type: SourceType?): Boolean

    @Throws(SQLException::class)
    fun convertDatabaseRowToAirbyteRecordData(queryContext: ResultSet): AirbyteRecordData
}
