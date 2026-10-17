/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.component

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.redshift_v2.client.RedshiftAirbyteClient
import io.airbyte.integrations.destination.redshift_v2.dataflow.RedshiftStagingAggregate
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.time.Clock
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import javax.sql.DataSource
import software.amazon.awssdk.services.s3.S3AsyncClient

private val log = KotlinLogging.logger {}

@Requires(env = ["component"])
@Singleton
class RedshiftTestTableOperationsClient(
    private val client: RedshiftAirbyteClient,
    private val dataSource: DataSource,
    private val s3Client: S3AsyncClient,
    private val config: RedshiftV2Configuration,
    private val clock: Clock,
) : TestTableOperationsClient {

    override suspend fun ping() {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement -> statement.executeQuery("SELECT 1") }
        }
    }

    override suspend fun dropNamespace(namespace: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.execute("""DROP SCHEMA IF EXISTS "$namespace" CASCADE""")
            }
        }
    }

    override suspend fun insertRecords(table: TableName, records: List<Map<String, AirbyteValue>>) {
        // Get the actual table columns so we only insert columns that exist
        val tableColumns = getTableColumns(table)

        // TODO: we should just pass a proper column schema
        // Since we don't pass in a proper column schema, we have to recreate one here
        // Fetch the columns and filter out the meta columns so we're just looking at user columns
        val columnTypes =
            client.discoverSchema(table).columns.filterNot { Meta.COLUMN_NAMES.contains(it.key) }
        val columnSchema =
            io.airbyte.cdk.load.schema.model.ColumnSchema(
                inputToFinalColumnNames = columnTypes.keys.associateWith { it },
                finalSchema = columnTypes.mapValues { (_, _) -> ColumnType("", true) },
                inputSchema = emptyMap() // not needed
            )

        val aggregate: Aggregate =
            RedshiftStagingAggregate(
                table,
                dataSource,
                s3Client,
                config.s3Config,
                clock,
                columnSchema,
            )
        records.forEach { record ->
            // Filter record to only include columns that exist in the table
            val filteredRecord =
                record.filterKeys { key ->
                    tableColumns.contains(key) || key.startsWith("_airbyte")
                }
            aggregate.accept(RecordDTO(filteredRecord, PartitionKey(""), 0, 0))
        }
        aggregate.flush()
    }

    private fun getTableColumns(table: TableName): Set<String> {
        return dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                val sql =
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = '${table.namespace}'
                      AND table_name = '${table.name}'
                """.trimIndent()
                val resultSet = statement.executeQuery(sql)
                val columns = mutableSetOf<String>()
                while (resultSet.next()) {
                    columns.add(resultSet.getString("column_name"))
                }
                columns
            }
        }
    }

    override suspend fun readTable(table: TableName): List<Map<String, Any>> {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                val resultSet =
                    statement.executeQuery("""SELECT * FROM "${table.namespace}"."${table.name}"""")
                val metaData = resultSet.metaData
                val columnCount = metaData.columnCount
                val result = mutableListOf<Map<String, Any>>()

                while (resultSet.next()) {
                    val row = mutableMapOf<String, Any>()
                    for (i in 1..columnCount) {
                        val columnName = metaData.getColumnName(i)
                        val columnType = metaData.getColumnTypeName(i).uppercase()

                        when (columnType) {
                            "TIMESTAMPTZ" -> {
                                val value = resultSet.getObject(i, OffsetDateTime::class.java)
                                if (value != null) {
                                    row[columnName] = DateTimeFormatter.ISO_DATE_TIME.format(value)
                                }
                            }
                            "SUPER" -> {
                                val stringValue = resultSet.getString(i)
                                if (stringValue != null) {
                                    try {
                                        val parsedValue =
                                            Jsons.readValue(stringValue, Any::class.java)
                                        val actualValue =
                                            when (parsedValue) {
                                                is Int -> parsedValue.toLong()
                                                else -> parsedValue
                                            }
                                        row[columnName] = actualValue
                                    } catch (e: Exception) {
                                        row[columnName] = stringValue
                                    }
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
