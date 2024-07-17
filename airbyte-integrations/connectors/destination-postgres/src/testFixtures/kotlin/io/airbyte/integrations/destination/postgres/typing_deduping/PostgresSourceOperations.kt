/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.commons.json.Jsons.deserializeExact
import java.sql.ResultSet
import java.sql.SQLException
import java.util.*

/**
 * See
 * [io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGeneratorIntegrationTest.RedshiftSourceOperations]
 * . Copied here to avoid weird dependencies.
 */
class PostgresSourceOperations : JdbcSourceOperations() {
    @Throws(SQLException::class)
    override fun copyToJsonField(resultSet: ResultSet, colIndex: Int, json: ObjectNode) {
        val columnName = resultSet.metaData.getColumnName(colIndex)
        val columnTypeName =
            resultSet.metaData.getColumnTypeName(colIndex).lowercase(Locale.getDefault())

        when (columnTypeName) {
            "jsonb" ->
                json.set<JsonNode>(columnName, deserializeExact(resultSet.getString(colIndex)))
            "timetz" -> putTimeWithTimezone(json, columnName, resultSet, colIndex)
            "timestamptz" -> putTimestampWithTimezone(json, columnName, resultSet, colIndex)
            else -> super.copyToJsonField(resultSet, colIndex, json)
        }
    }
}
