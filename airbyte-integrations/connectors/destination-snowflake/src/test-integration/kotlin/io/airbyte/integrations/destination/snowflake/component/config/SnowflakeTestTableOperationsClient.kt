/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component.config

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.client.execute
import io.airbyte.integrations.destination.snowflake.dataflow.SnowflakeAggregate
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDirectLoadSqlGenerator
import io.airbyte.integrations.destination.snowflake.sql.andLog
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeRecordFormatter
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
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val columnManager: SnowflakeColumnManager,
    private val snowflakeRecordFormatter: SnowflakeRecordFormatter,
) : TestTableOperationsClient {
    override suspend fun dropNamespace(namespace: String) {
        dataSource.execute(
            "DROP SCHEMA IF EXISTS ${sqlGenerator.fullyQualifiedNamespace(namespace)}".andLog()
        )
    }

    override suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) {
        // TODO: we should just pass a proper column schema
        // Since we don't pass in a proper column schema, we have to recreate one here
        // Fetch the columns and filter out the meta columns so we're just looking at user columns
        val columnTypes =
            client.describeTable(table).filterNot {
                columnManager.getMetaColumnNames().contains(it.key)
            }
        val columnSchema =
            io.airbyte.cdk.load.schema.model.ColumnSchema(
                inputToFinalColumnNames = columnTypes.keys.associateWith { it },
                finalSchema = columnTypes.mapValues { (_, _) -> ColumnType("", true) },
                inputSchema = emptyMap() // Not needed for insert buffer
            )
        val a =
            SnowflakeAggregate(
                SnowflakeInsertBuffer(
                    tableName = table,
                    snowflakeClient = client,
                    snowflakeConfiguration = snowflakeConfiguration,
                    columnSchema = columnSchema,
                    columnManager = columnManager,
                    snowflakeRecordFormatter = snowflakeRecordFormatter,
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
