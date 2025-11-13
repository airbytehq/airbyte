/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql_v2.component

import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.util.serializeToString
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.math.BigDecimal
import java.sql.Timestamp
import java.time.format.DateTimeFormatter
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Requires(env = ["component"])
@Singleton
class MysqlTestTableOperationsClient(
    private val dataSource: DataSource,
) : TestTableOperationsClient {

    override suspend fun ping() {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.executeQuery("SELECT 1").use { resultSet ->
                    resultSet.next()
                }
            }
        }
    }

    override suspend fun dropNamespace(namespace: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.execute("DROP DATABASE IF EXISTS `$namespace`")
            }
        }
    }

    override suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) {
        if (records.isEmpty()) return

        dataSource.connection.use { connection ->
            connection.autoCommit = false
            try {
                val columns = records.first().keys.toList()
                val columnList = columns.joinToString(", ") { "`$it`" }
                val placeholders = columns.joinToString(", ") { "?" }

                val sql = """
                    INSERT INTO `${table.namespace}`.`${table.name}` ($columnList)
                    VALUES ($placeholders)
                """.trimIndent()

                connection.prepareStatement(sql).use { statement ->
                    records.forEach { record ->
                        columns.forEachIndexed { index, column ->
                            val value = record[column] ?: NullValue
                            setParameter(statement, index + 1, value)
                        }
                        statement.addBatch()
                    }
                    statement.executeBatch()
                }
                connection.commit()
            } catch (e: Exception) {
                connection.rollback()
                throw e
            }
        }
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.executeQuery(
                    """SELECT * FROM `${table.namespace}`.`${table.name}`"""
                ).use { resultSet ->
                    val metaData = resultSet.metaData
                    val columnCount = metaData.columnCount
                    val result = mutableListOf<Map<String, Any>>()

                    while (resultSet.next()) {
                        val row = mutableMapOf<String, Any>()
                        for (i in 1..columnCount) {
                            val columnName = metaData.getColumnName(i)
                            val columnType = metaData.getColumnTypeName(i)

                            when (columnType.uppercase()) {
                                "JSON" -> {
                                    val stringValue = resultSet.getString(i)
                                    if (stringValue != null) {
                                        // Parse JSON string to native types
                                        val parsedValue = parseJsonValue(stringValue)
                                        row[columnName] = parsedValue
                                    }
                                }
                                "TIMESTAMP" -> {
                                    val timestamp = resultSet.getTimestamp(i)
                                    if (timestamp != null) {
                                        // Format timestamp to ISO-8601 with timezone
                                        val formattedTimestamp = DateTimeFormatter.ISO_DATE_TIME
                                            .format(timestamp.toInstant().atZone(java.time.ZoneOffset.UTC))
                                        row[columnName] = formattedTimestamp
                                    }
                                }
                                "DATETIME" -> {
                                    val timestamp = resultSet.getTimestamp(i)
                                    if (timestamp != null) {
                                        // Format datetime to ISO-8601 without timezone
                                        val formattedDateTime = timestamp.toLocalDateTime().toString()
                                        row[columnName] = formattedDateTime
                                    }
                                }
                                "DATE" -> {
                                    val date = resultSet.getDate(i)
                                    if (date != null) {
                                        row[columnName] = date.toLocalDate().toString()
                                    }
                                }
                                "TIME" -> {
                                    val time = resultSet.getTime(i)
                                    if (time != null) {
                                        row[columnName] = time.toLocalTime().toString()
                                    }
                                }
                                "DECIMAL" -> {
                                    val decimal = resultSet.getBigDecimal(i)
                                    if (decimal != null) {
                                        row[columnName] = decimal
                                    }
                                }
                                "BIGINT" -> {
                                    val value = resultSet.getLong(i)
                                    if (!resultSet.wasNull()) {
                                        row[columnName] = value
                                    }
                                }
                                "TINYINT" -> {
                                    // MySQL BOOLEAN is stored as TINYINT(1)
                                    val value = resultSet.getBoolean(i)
                                    if (!resultSet.wasNull()) {
                                        row[columnName] = value
                                    }
                                }
                                else -> {
                                    val value = resultSet.getObject(i)
                                    if (value != null) {
                                        row[columnName] = value
                                    }
                                }
                            }
                        }
                        result.add(row)
                    }

                    return result
                }
            }
        }
    }

    private fun setParameter(statement: java.sql.PreparedStatement, index: Int, value: AirbyteValue) {
        when (value) {
            is StringValue -> statement.setString(index, value.value)
            is IntegerValue -> statement.setLong(index, value.value.toLong())
            is NumberValue -> statement.setBigDecimal(index, value.value)
            is BooleanValue -> statement.setBoolean(index, value.value)
            is TimestampWithTimezoneValue -> statement.setTimestamp(index, Timestamp.from(value.value.toInstant()))
            is TimestampWithoutTimezoneValue -> statement.setTimestamp(index, Timestamp.valueOf(value.value))
            is DateValue -> statement.setDate(index, java.sql.Date.valueOf(value.value))
            is TimeWithTimezoneValue -> statement.setTime(index, java.sql.Time.valueOf(value.value.toLocalTime()))
            is TimeWithoutTimezoneValue -> statement.setTime(index, java.sql.Time.valueOf(value.value))
            is ObjectValue, is ArrayValue -> {
                // Store JSON as string
                statement.setString(index, value.serializeToString())
            }
            is NullValue -> statement.setNull(index, java.sql.Types.VARCHAR)
            else -> {
                // Fallback: convert to string
                log.warn { "Unknown AirbyteValue type: ${value::class.simpleName}, converting to string" }
                statement.setString(index, value.toString())
            }
        }
    }

    private fun parseJsonValue(json: String): Any {
        // Simple JSON parser for test purposes
        val trimmed = json.trim()
        return when {
            trimmed == "null" -> mapOf<String, Any>()
            trimmed.startsWith("{") && trimmed.endsWith("}") -> {
                // Parse as object - use Jackson for proper parsing
                try {
                    val mapper = com.fasterxml.jackson.databind.ObjectMapper()
                    mapper.readValue(trimmed, Map::class.java) as Map<String, Any>
                } catch (e: Exception) {
                    log.warn { "Failed to parse JSON object: $trimmed" }
                    mapOf<String, Any>()
                }
            }
            trimmed.startsWith("[") && trimmed.endsWith("]") -> {
                // Parse as array
                try {
                    val mapper = com.fasterxml.jackson.databind.ObjectMapper()
                    mapper.readValue(trimmed, List::class.java) as List<Any>
                } catch (e: Exception) {
                    log.warn { "Failed to parse JSON array: $trimmed" }
                    listOf<Any>()
                }
            }
            else -> trimmed
        }
    }
}
