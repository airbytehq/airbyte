/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component

import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.client.execute
import io.airbyte.integrations.destination.snowflake.dataflow.SnowflakeAggregate
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeSqlNameUtils
import io.airbyte.integrations.destination.snowflake.sql.andLog
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.sql.Timestamp
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import javax.sql.DataSource
import net.snowflake.client.jdbc.SnowflakeTimestampWithTimezone

@Requires(env = ["component"])
@Singleton
class SnowflakeTestTableOperationsClient(
    private val client: SnowflakeAirbyteClient,
    private val dataSource: DataSource,
    private val snowflakeSqlNameUtils: SnowflakeSqlNameUtils,
    private val snowflakeColumnUtils: SnowflakeColumnUtils,
    private val snowflakeConfiguration: SnowflakeConfiguration,
) : TestTableOperationsClient {
    override suspend fun dropNamespace(namespace: String) {
        dataSource.execute(
            "DROP SCHEMA IF EXISTS ${snowflakeSqlNameUtils.fullyQualifiedNamespace(namespace)}".andLog()
        )
    }

    override suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) {
        val a =
            SnowflakeAggregate(
                SnowflakeInsertBuffer(
                    table,
                    client.describeTable(table),
                    client,
                    snowflakeConfiguration,
                    snowflakeColumnUtils,
                )
            )
        records.forEach { a.accept(RecordDTO(it, PartitionKey(""), 0, 0)) }
        a.flush()
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement
                    .executeQuery("""SELECT * FROM "${table.namespace}"."${table.name}";""")
                    .use { resultSet ->
                        val metaData = resultSet.metaData
                        val columnCount = metaData.columnCount
                        val result = mutableListOf<Map<String, Any>>()

                        while (resultSet.next()) {
                            val row = mutableMapOf<String, Any>()
                            for (i in 1..columnCount) {
                                val columnName = metaData.getColumnName(i)
                                val columnType = metaData.getColumnTypeName(i)
                                when (columnType) {
                                    "TIMESTAMPTZ" -> {
                                        resultSet.getTimestamp(i)?.let {
                                            val odt =
                                                when (it) {
                                                    // Most timestamps are returned as
                                                    // SnowflakeTimestampWithTimezone,
                                                    // which has a toZonedDateTime function
                                                    is SnowflakeTimestampWithTimezone ->
                                                        it.toZonedDateTime().toOffsetDateTime()
                                                    // Some timestamps are returned as
                                                    // java.sql.Timestamp,
                                                    // so we just assume UTC.
                                                    is Timestamp ->
                                                        it.toLocalDateTime()
                                                            .atOffset(ZoneOffset.UTC)
                                                }
                                            row[columnName] =
                                                DateTimeFormatter.ISO_DATE_TIME.format(odt)
                                        }
                                    }
                                    "TIMESTAMPNTZ" -> {
                                        resultSet.getTimestamp(i)?.let {
                                            row[columnName] = it.toLocalDateTime()
                                        }
                                    }
                                    "TIME" -> {
                                        // resultSet.getObject (and .getTime) returns a
                                        // java.sql.Time object, which only stores milliseconds
                                        // precision.
                                        // Snowflake supports up to nanoseconds precision, so we
                                        // need retrieve the object as a timestamp, and convert that
                                        // back to LocalTime.
                                        resultSet.getTimestamp(i)?.let {
                                            row[columnName] =
                                                it.toLocalDateTime().toLocalTime().toString()
                                        }
                                    }
                                    "DATE" -> {
                                        // resultSet.getObject returns a java.sql.Date object,
                                        // but its underlying `cdate` value is offset by someone's
                                        // local timezone (unclear whether that's our snowflake user
                                        // timezone, or the TZ of the computer running the test),
                                        // and that breaks equality comparison.
                                        // So just convert to String.
                                        resultSet.getDate(i)?.let {
                                            row[columnName] = it.toString()
                                        }
                                    }
                                    "VARIANT",
                                    "OBJECT",
                                    "ARRAY" -> {
                                        val stringValue: String? = resultSet.getString(i)
                                        if (stringValue != null) {
                                            // Automatically convert values to their native type.
                                            // (map, list, etc.)
                                            val parsedValue =
                                                Jsons.readValue(stringValue, Any::class.java)
                                            // but handle some annoying edge cases
                                            val actualValue =
                                                when (parsedValue) {
                                                    is Integer -> parsedValue.toLong()
                                                    else -> parsedValue
                                                }
                                            row[columnName] = actualValue
                                        }
                                    }
                                    // We need to return as bigdecimal instead of double, so use
                                    // getBigDecimal instead of getObject.
                                    // Snowflake returns values that aren't actually representable
                                    // as a Java double. E.g.
                                    // 1.7976931348623157e308 (Double.MAX_VALUE)
                                    // 1.79769313486232e308 (actual Snowflake value)
                                    // Note that the snowflake value is rounded _upward_, and
                                    // therefore exceeds Double.MAX_VALUE.
                                    "DOUBLE" -> row[columnName] = resultSet.getBigDecimal(i)
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
}
