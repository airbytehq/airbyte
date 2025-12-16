/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component

import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import javax.sql.DataSource

@Requires(env = ["component"])
@Singleton
class PostgresTestTableOperationsClient(
    private val dataSource: DataSource,
    private val client: PostgresAirbyteClient,
) : TestTableOperationsClient {
    override suspend fun ping() {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement -> statement.executeQuery("SELECT 1") }
        }
    }

    override suspend fun dropNamespace(namespace: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.execute("DROP SCHEMA IF EXISTS \"$namespace\" CASCADE")
            }
        }
    }

    override suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) {
        if (records.isEmpty()) return

        // Get column types from database to handle jsonb columns properly
        val columnTypes = getColumnTypes(table)

        // Get all unique columns from ALL records to handle sparse data (e.g., CDC deletion column)
        val columns = records.flatMap { it.keys }.distinct().toList()
        val columnNames = columns.joinToString(", ") { "\"$it\"" }
        val placeholders = columns.indices.joinToString(", ") { "?" }

        val sql =
            """
            INSERT INTO "${table.namespace}"."${table.name}" ($columnNames)
            VALUES ($placeholders)
        """

        dataSource.connection.use { connection ->
            connection.prepareStatement(sql).use { statement ->
                for (record in records) {
                    columns.forEachIndexed { index, column ->
                        val value = record[column]
                        val columnType = columnTypes[column]
                        setParameterValue(statement, index + 1, value, columnType)
                    }
                    statement.addBatch()
                }
                statement.executeBatch()
            }
        }
    }

    private fun getColumnTypes(table: TableName): Map<String, String> {
        val columnTypes = mutableMapOf<String, String>()
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement
                    .executeQuery(
                        """
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = '${table.namespace}'
                    AND table_name = '${table.name}'
                """
                    )
                    .use { resultSet ->
                        while (resultSet.next()) {
                            columnTypes[resultSet.getString("column_name")] =
                                resultSet.getString("data_type")
                        }
                    }
            }
        }
        return columnTypes
    }

    private fun setParameterValue(
        statement: java.sql.PreparedStatement,
        index: Int,
        value: AirbyteValue?,
        columnType: String?
    ) {
        // If column is jsonb, serialize any value as JSON
        if (columnType == "jsonb") {
            if (value == null || value is io.airbyte.cdk.load.data.NullValue) {
                statement.setNull(index, java.sql.Types.OTHER)
            } else {
                val pgObject = org.postgresql.util.PGobject()
                pgObject.type = "jsonb"
                pgObject.value = serializeToJson(value)
                statement.setObject(index, pgObject)
            }
            return
        }

        when (value) {
            null,
            is io.airbyte.cdk.load.data.NullValue -> statement.setNull(index, java.sql.Types.NULL)
            is io.airbyte.cdk.load.data.StringValue -> statement.setString(index, value.value)
            is io.airbyte.cdk.load.data.IntegerValue ->
                statement.setLong(index, value.value.toLong())
            is io.airbyte.cdk.load.data.NumberValue -> statement.setBigDecimal(index, value.value)
            is io.airbyte.cdk.load.data.BooleanValue -> statement.setBoolean(index, value.value)
            is io.airbyte.cdk.load.data.TimestampWithTimezoneValue -> {
                val offsetDateTime = OffsetDateTime.parse(value.value.toString())
                statement.setObject(index, offsetDateTime)
            }
            is io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue -> {
                val localDateTime = java.time.LocalDateTime.parse(value.value.toString())
                statement.setObject(index, localDateTime)
            }
            is io.airbyte.cdk.load.data.DateValue -> {
                val localDate = java.time.LocalDate.parse(value.value.toString())
                statement.setObject(index, localDate)
            }
            is io.airbyte.cdk.load.data.TimeWithTimezoneValue -> {
                statement.setString(index, value.value.toString())
            }
            is io.airbyte.cdk.load.data.TimeWithoutTimezoneValue -> {
                val localTime = java.time.LocalTime.parse(value.value.toString())
                statement.setObject(index, localTime)
            }
            is io.airbyte.cdk.load.data.ObjectValue -> {
                val pgObject = org.postgresql.util.PGobject()
                pgObject.type = "jsonb"
                pgObject.value = Jsons.writeValueAsString(value.values)
                statement.setObject(index, pgObject)
            }
            is io.airbyte.cdk.load.data.ArrayValue -> {
                val pgObject = org.postgresql.util.PGobject()
                pgObject.type = "jsonb"
                pgObject.value = Jsons.writeValueAsString(value.values)
                statement.setObject(index, pgObject)
            }
            else -> {
                // For unknown types, try to serialize as string
                statement.setString(index, value.toString())
            }
        }
    }

    private fun serializeToJson(value: AirbyteValue): String {
        return when (value) {
            is io.airbyte.cdk.load.data.StringValue -> Jsons.writeValueAsString(value.value)
            is io.airbyte.cdk.load.data.IntegerValue -> value.value.toString()
            is io.airbyte.cdk.load.data.NumberValue -> value.value.toString()
            is io.airbyte.cdk.load.data.BooleanValue -> value.value.toString()
            is io.airbyte.cdk.load.data.ObjectValue -> Jsons.writeValueAsString(value.values)
            is io.airbyte.cdk.load.data.ArrayValue -> Jsons.writeValueAsString(value.values)
            is io.airbyte.cdk.load.data.NullValue -> "null"
            else -> Jsons.writeValueAsString(value.toString())
        }
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement
                    .executeQuery("""SELECT * FROM "${table.namespace}"."${table.name}"""")
                    .use { resultSet ->
                        val metaData = resultSet.metaData
                        val columnCount = metaData.columnCount
                        val result = mutableListOf<Map<String, Any>>()

                        while (resultSet.next()) {
                            val row = mutableMapOf<String, Any>()
                            for (i in 1..columnCount) {
                                val columnName = metaData.getColumnName(i)
                                val columnType = metaData.getColumnTypeName(i)
                                when (columnType.lowercase()) {
                                    "timestamptz" -> {
                                        val value =
                                            resultSet.getObject(i, OffsetDateTime::class.java)
                                        if (value != null) {
                                            val formattedTimestamp =
                                                DateTimeFormatter.ISO_OFFSET_DATE_TIME.format(
                                                    value.withOffsetSameInstant(ZoneOffset.UTC)
                                                )
                                            row[columnName] = formattedTimestamp
                                        }
                                    }
                                    "timestamp" -> {
                                        val value = resultSet.getTimestamp(i)
                                        if (value != null) {
                                            val localDateTime = value.toLocalDateTime()
                                            row[columnName] =
                                                DateTimeFormatter.ISO_LOCAL_DATE_TIME.format(
                                                    localDateTime
                                                )
                                        }
                                    }
                                    "jsonb",
                                    "json" -> {
                                        val stringValue: String? = resultSet.getString(i)
                                        if (stringValue != null) {
                                            val parsedValue =
                                                Jsons.readValue(stringValue, Any::class.java)
                                            val actualValue =
                                                when (parsedValue) {
                                                    is Int -> parsedValue.toLong()
                                                    else -> parsedValue
                                                }
                                            row[columnName] = actualValue
                                        }
                                    }
                                    else -> {
                                        val value = resultSet.getObject(i)
                                        if (value != null) {
                                            // For varchar columns that may contain JSON (from
                                            // schema evolution),
                                            // normalize the JSON to compact format for comparison
                                            if (
                                                value is String &&
                                                    (value.startsWith("{") || value.startsWith("["))
                                            ) {
                                                try {
                                                    val parsed =
                                                        Jsons.readValue(value, Any::class.java)
                                                    row[columnName] =
                                                        Jsons.writeValueAsString(parsed)
                                                } catch (_: Exception) {
                                                    row[columnName] = value
                                                }
                                            } else {
                                                row[columnName] = value
                                            }
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
}
