/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.db.DataTypeUtils
import io.airbyte.cdk.db.DataTypeUtils.toISO8601StringWithMicroseconds
import io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLDate
import io.airbyte.cdk.db.jdbc.DateTimeConverter.putJavaSQLTime
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.commons.json.Jsons.deserializeExact
import java.sql.ResultSet
import java.sql.SQLException
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.util.*

class SnowflakeSourceOperations : JdbcSourceOperations() {
    @Throws(SQLException::class)
    override fun copyToJsonField(resultSet: ResultSet, colIndex: Int, json: ObjectNode) {
        val columnName = resultSet.metaData.getColumnName(colIndex)
        val columnTypeName =
            resultSet.metaData.getColumnTypeName(colIndex).lowercase(Locale.getDefault())

        when (columnTypeName) {
            "variant",
            "array",
            "object" ->
                json.set<JsonNode>(columnName, deserializeExact(resultSet.getString(colIndex)))
            else -> super.copyToJsonField(resultSet, colIndex, json)
        }
    }

    @Throws(SQLException::class)
    override fun putDate(node: ObjectNode, columnName: String?, resultSet: ResultSet, index: Int) {
        putJavaSQLDate(node, columnName, resultSet, index)
    }

    @Throws(SQLException::class)
    override fun putTime(node: ObjectNode, columnName: String?, resultSet: ResultSet, index: Int) {
        putJavaSQLTime(node, columnName, resultSet, index)
    }

    @Throws(SQLException::class)
    override fun putTimestampWithTimezone(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        val timestampAsString = resultSet.getString(index)
        val timestampWithOffset =
            OffsetDateTime.parse(timestampAsString, SNOWFLAKE_TIMESTAMPTZ_FORMATTER)
        node.put(columnName, timestampWithOffset.format(DataTypeUtils.TIMESTAMPTZ_FORMATTER))
    }

    @Throws(SQLException::class)
    override fun putTimestamp(
        node: ObjectNode,
        columnName: String?,
        resultSet: ResultSet,
        index: Int
    ) {
        // for backward compatibility
        val instant = resultSet.getTimestamp(index).toInstant()
        node.put(columnName, toISO8601StringWithMicroseconds(instant))
    }

    companion object {
        private val SNOWFLAKE_TIMESTAMPTZ_FORMATTER: DateTimeFormatter =
            DateTimeFormatterBuilder()
                .parseCaseInsensitive()
                .append(DateTimeFormatter.ISO_LOCAL_DATE)
                .appendLiteral(' ')
                .append(DateTimeFormatter.ISO_LOCAL_TIME)
                .optionalStart()
                .appendLiteral(' ')
                .append(DateTimeFormatter.ofPattern("XX"))
                .toFormatter()
    }
}
