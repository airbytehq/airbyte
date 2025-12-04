/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.client

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import com.clickhouse.client.api.command.CommandResponse
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.clickhouse.client.api.metadata.TableSchema
import com.clickhouse.client.api.query.QueryResponse
import com.clickhouse.data.ClickHouseColumn
import com.clickhouse.data.ClickHouseDataType
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TempTableNameGenerator
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlGenerator.Companion.DATETIME_WITH_PRECISION
import io.airbyte.integrations.destination.clickhouse.client.ClickhouseSqlGenerator.Companion.DECIMAL_WITH_PRECISION_AND_SCALE
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.future.await

val log = KotlinLogging.logger {}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
@Singleton
class ClickhouseAirbyteClient(
    private val client: ClickHouseClientRaw,
    private val sqlGenerator: ClickhouseSqlGenerator,
    private val tempTableNameGenerator: TempTableNameGenerator,
    private val clickhouseConfiguration: ClickhouseConfiguration,
) : TableOperationsClient, TableSchemaEvolutionClient {

    override suspend fun createNamespace(namespace: String) {
        val statement = sqlGenerator.createNamespace(namespace)

        execute(statement)
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        execute(
            sqlGenerator.createTable(
                stream,
                tableName,
                columnNameMapping,
                replace,
            ),
        )
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        execute(sqlGenerator.exchangeTable(sourceTableName, targetTableName))
        execute(sqlGenerator.dropTable(sourceTableName))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(
            sqlGenerator.copyTable(
                columnNameMapping,
                sourceTableName,
                targetTableName,
            ),
        )
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        throw NotImplementedError("We rely on Clickhouse's table engine for deduping")
    }

    override suspend fun discoverSchema(
        tableName: TableName
    ): io.airbyte.cdk.load.component.TableSchema {
        val tableSchema: TableSchema = client.getTableSchema(tableName.name, tableName.namespace)

        log.info { "Fetch the clickhouse table schema: $tableSchema" }

        val hasAllAirbyteColumn =
            tableSchema.columns.map { it.columnName }.containsAll(COLUMN_NAMES)

        if (!hasAllAirbyteColumn) {
            val message =
                "The target table ($tableName) already exists in the destination, but does not contain Airbyte's internal columns. Airbyte can only sync to Airbyte-controlled tables. To fix this error, you must either delete the target table or add a prefix in the connection configuration in order to sync to a separate table in the destination."
            log.error { message }
            throw ConfigErrorException(message)
        }

        val tableSchemaWithoutAirbyteColumns: List<ClickHouseColumn> =
            tableSchema.columns.filterNot { column -> column.columnName in COLUMN_NAMES }

        log.info { "Found Clickhouse columns: $tableSchemaWithoutAirbyteColumns" }

        return io.airbyte.cdk.load.component.TableSchema(
            tableSchemaWithoutAirbyteColumns.associate {
                it.columnName to ColumnType(it.dataType.getDataTypeAsString(), it.isNullable)
            },
        )
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): io.airbyte.cdk.load.component.TableSchema {
        val importType = stream.importType
        val primaryKey =
            if (importType is Dedupe) {
                sqlGenerator.extractPks(importType.primaryKey, columnNameMapping).toSet()
            } else {
                emptySet()
            }
        val cursor =
            if (importType is Dedupe) {
                if (importType.cursor.size > 1) {
                    throw ConfigErrorException(
                        "Only top-level cursors are supported. Got ${importType.cursor}"
                    )
                }
                importType.cursor.map { columnNameMapping[it] }.toSet()
            } else {
                emptySet()
            }
        return io.airbyte.cdk.load.component.TableSchema(
            stream.schema
                .asColumns()
                .map { (fieldName, fieldType) ->
                    val clickhouseCompatibleName = columnNameMapping[fieldName]!!
                    val nullable =
                        !primaryKey.contains(clickhouseCompatibleName) &&
                            !cursor.contains(clickhouseCompatibleName)
                    val type = fieldType.type.toDialectType(clickhouseConfiguration.enableJson)
                    clickhouseCompatibleName to
                        ColumnType(
                            type = type,
                            nullable = nullable,
                        )
                }
                .toMap(),
        )
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset,
    ) {
        // This is a bit hacky, and relies on the fact that we make all
        // non-pk/cursor columns nullable.
        // We assume that if any column changes its nullability,
        // or we want to drop a non-nullable column,
        // this indicates a change in the PK/cursor, and therefore we need to
        // reconfigure the table engine.
        val anyNullabilityChange =
            columnChangeset.columnsToChange.values.any {
                it.originalType.nullable != it.newType.nullable
            } || columnChangeset.columnsToDrop.values.any { !it.nullable }

        if (anyNullabilityChange) {
            log.info {
                "Detected deduplication change for table $tableName, applying deduplication changes"
            }
            applyDeduplicationChanges(
                stream,
                tableName,
                columnNameMapping,
                columnChangeset,
            )
        } else if (!columnChangeset.isNoop()) {
            execute(sqlGenerator.alterTable(columnChangeset, tableName))
        }
    }

    private suspend fun applyDeduplicationChanges(
        stream: DestinationStream,
        properTableName: TableName,
        columnNameMapping: ColumnNameMapping,
        columnChangeset: ColumnChangeset,
    ) {
        val tempTableName = tempTableNameGenerator.generate(properTableName)
        execute(sqlGenerator.createNamespace(tempTableName.namespace))
        execute(
            sqlGenerator.createTable(
                stream,
                tempTableName,
                columnNameMapping,
                true,
            ),
        )
        copyIntersectionColumn(
            columnChangeset.columnsToChange.keys + columnChangeset.columnsToRetain.keys,
            columnNameMapping,
            properTableName,
            tempTableName
        )
        execute(sqlGenerator.exchangeTable(tempTableName, properTableName))
        execute(sqlGenerator.dropTable(tempTableName))
    }

    internal suspend fun copyIntersectionColumn(
        columnsToCopy: Set<String>,
        columnNameMapping: ColumnNameMapping,
        properTableName: TableName,
        tempTableName: TableName
    ) {
        execute(
            sqlGenerator.copyTable(
                ColumnNameMapping(columnNameMapping.filter { columnsToCopy.contains(it.value) }),
                properTableName,
                tempTableName,
            ),
        )
    }

    override suspend fun countTable(tableName: TableName): Long? {
        try {
            val sql = sqlGenerator.countTable(tableName, "cnt")
            val response = query(sql)
            val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response)
            reader.next()
            val count = reader.getLong("cnt")
            return count
        } catch (e: Exception) {
            return null
        }
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        try {
            val sql = sqlGenerator.getGenerationId(tableName, "generation")
            val response = query(sql)
            val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(response)
            reader.next()
            val generation = reader.getLong("generation")
            return generation
        } catch (e: Exception) {
            log.error(e) { "Failed to retrieve the generation Id" }
            // TODO: open question: Do we need to raise an error here or just return 0?
            return 0
        }
    }

    internal suspend fun execute(query: String): CommandResponse {
        return client.execute(query).await()
    }

    internal suspend fun query(query: String): QueryResponse {
        return client.query(query).await()
    }

    private fun ClickHouseDataType.getDataTypeAsString(): String {
        return if (this.name == "DateTime64") {
            DATETIME_WITH_PRECISION
        } else if (this.name == "Decimal") {
            DECIMAL_WITH_PRECISION_AND_SCALE
        } else {
            this.name
        }
    }

    override suspend fun namespaceExists(namespace: String): Boolean {
        val resp = query("EXISTS DATABASE `$namespace`")
        val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(resp)
        reader.next()
        val exists = reader.getInteger("result")

        return exists == 1
    }

    override suspend fun tableExists(table: TableName): Boolean {
        val resp = query("EXISTS TABLE `${table.namespace}`.`${table.name}`")
        val reader: ClickHouseBinaryFormatReader = client.newBinaryFormatReader(resp)
        reader.next()
        val exists = reader.getInteger("result")

        return exists == 1
    }
}
