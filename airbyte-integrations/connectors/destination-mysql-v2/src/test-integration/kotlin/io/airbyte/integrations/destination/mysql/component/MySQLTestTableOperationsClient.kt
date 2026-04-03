/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.component

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
import io.airbyte.cdk.load.util.Jsons
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.sql.Date
import java.sql.PreparedStatement
import java.sql.Time
import java.sql.Timestamp
import java.sql.Types
import javax.sql.DataSource
import io.github.oshai.kotlinlogging.KotlinLogging

private val log = KotlinLogging.logger {}

@Requires(env = ["component"])
@Singleton
@Primary
class MySQLTestTableOperationsClient(
    private val dataSource: DataSource,
) : TestTableOperationsClient {

    override suspend fun ping() {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.executeQuery("SELECT 1")
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

    override suspend fun insertRecords(
        table: TableName,
        records: List<Map<String, AirbyteValue>>
    ) {
        if (records.isEmpty()) return

        dataSource.connection.use { connection ->
            records.forEach { record ->
                val columns = record.keys.joinToString(", ") { "`$it`" }
                val placeholders = record.keys.joinToString(", ") { "?" }
                val sql = """
                    INSERT INTO `${table.namespace}`.`${table.name}` ($columns)
                    VALUES ($placeholders)
                """

                log.info { "Executing SQL: $sql with values: ${record.values}" }
                connection.prepareStatement(sql).use { statement ->
                    record.values.forEachIndexed { index, value ->
                        setParameter(statement, index + 1, value)
                    }
                    statement.executeUpdate()
                }
            }
        }
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        val results = mutableListOf<Map<String, Any>>()

        dataSource.connection.use { connection ->
            val sql = "SELECT * FROM `${table.namespace}`.`${table.name}`"
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sql)
                val metadata = rs.metaData

                while (rs.next()) {
                    val row = mutableMapOf<String, Any>()
                    for (i in 1..metadata.columnCount) {
                        val columnName = metadata.getColumnName(i)
                        val columnType = metadata.getColumnTypeName(i)

                        when (columnType) {
                            "JSON" -> {
                                val stringValue = rs.getString(i)
                                if (stringValue != null) {
                                    val parsedValue = Jsons.readValue(stringValue, Any::class.java)
                                    row[columnName] = parsedValue
                                }
                            }
                            "DATETIME" -> {
                                // Convert MySQL DATETIME to ZonedDateTime with UTC for comparison
                                val timestamp = rs.getTimestamp(i)
                                if (timestamp != null) {
                                    row[columnName] = timestamp.toLocalDateTime()
                                        .atZone(java.time.ZoneId.of("UTC"))
                                }
                            }
                            else -> {
                                val value = rs.getObject(i)
                                if (value != null) {
                                    row[columnName] = value
                                }
                            }
                        }
                    }
                    results.add(row)
                }
            }
        }

        return results
    }

    private fun setParameter(statement: PreparedStatement, index: Int, value: AirbyteValue) {
        when (value) {
            is StringValue -> statement.setString(index, value.value)
            is IntegerValue -> statement.setLong(index, value.value.toLong())
            is NumberValue -> statement.setBigDecimal(index, value.value)
            is BooleanValue -> statement.setBoolean(index, value.value)
            is TimestampWithTimezoneValue -> statement.setTimestamp(index, Timestamp.from(value.value.toInstant()))
            is TimestampWithoutTimezoneValue -> statement.setTimestamp(index, Timestamp.valueOf(value.value))
            is DateValue -> statement.setDate(index, Date.valueOf(value.value))
            is TimeWithTimezoneValue -> statement.setTime(index, Time.valueOf(value.value.toLocalTime()))
            is TimeWithoutTimezoneValue -> statement.setTime(index, Time.valueOf(value.value))
            is ObjectValue -> statement.setString(index, Jsons.writeValueAsString(value.values))
            is ArrayValue -> statement.setString(index, Jsons.writeValueAsString(value.values))
            is NullValue -> statement.setNull(index, Types.VARCHAR)
        }
    }
}
