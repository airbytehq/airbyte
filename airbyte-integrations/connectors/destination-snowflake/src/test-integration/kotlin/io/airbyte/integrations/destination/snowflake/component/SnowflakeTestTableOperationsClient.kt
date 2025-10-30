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
                                        val value =
                                            resultSet.getTimestamp(i)
                                                as SnowflakeTimestampWithTimezone?
                                        if (value != null) {
                                            val formattedTimestamp =
                                                DateTimeFormatter.ISO_DATE_TIME.format(
                                                    value.toZonedDateTime().toOffsetDateTime()
                                                )
                                            row[columnName] = formattedTimestamp
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
