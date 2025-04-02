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

class TeradataSourceOperations : JdbcSourceOperations() {
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
