/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.teradata.typing_deduping

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.commons.json.Jsons
import java.sql.ResultSet
import java.sql.SQLException
import java.util.*

/**
 * Teradata-specific implementation of {@link JdbcSourceOperations} to handle custom data types such
 * as JSON and time zones during result set processing.
 *
 * This class overrides the default behavior to ensure correct deserialization and mapping of
 * Teradata-specific column types into JSON format.
 */
class TeradataSourceOperations : JdbcSourceOperations() {
    /**
     * Overrides the default method to convert a specific SQL column value into a JSON field, with
     * custom logic for Teradata-specific types such as `JSON`, `TIMETZ`, and `TIMESTAMPTZ`.
     *
     * @param resultSet the {@link ResultSet} containing the data
     * @param colIndex the 1-based column index in the result set
     * @param json the {@link ObjectNode} to populate with the deserialized field
     * @throws SQLException if an SQL error occurs while accessing the result set
     */
    @Throws(SQLException::class)
    override fun copyToJsonField(resultSet: ResultSet, colIndex: Int, json: ObjectNode) {
        val columnName = resultSet.metaData.getColumnName(colIndex)
        val columnTypeName =
            resultSet.metaData.getColumnTypeName(colIndex).lowercase(Locale.getDefault())

        when (columnTypeName) {
            "json" ->
                json.set(
                    columnName,
                    Jsons.deserializeExact(resultSet.getString(colIndex)),
                )
            "timetz" -> putTimeWithTimezone(json, columnName, resultSet, colIndex)
            "timestamptz" -> putTimestampWithTimezone(json, columnName, resultSet, colIndex)
            else -> super.copyToJsonField(resultSet, colIndex, json)
        }
    }
}
