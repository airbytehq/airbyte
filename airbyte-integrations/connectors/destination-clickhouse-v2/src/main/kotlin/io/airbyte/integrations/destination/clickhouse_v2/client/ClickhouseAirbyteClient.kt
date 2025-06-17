/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.client

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import com.clickhouse.client.api.command.CommandResponse
import com.clickhouse.client.api.data_formats.ClickHouseBinaryFormatReader
import com.clickhouse.client.api.query.QueryResponse
import com.clickhouse.data.ClickHouseColumn
import com.clickhouse.data.ClickHouseDataType
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.integrations.destination.clickhouse_v2.client.ClickhouseSqlGenerator.Companion.DATETIME_WITH_PRECISION
import io.airbyte.integrations.destination.clickhouse_v2.config.ClickhouseFinalTableNameGenerator
import io.airbyte.integrations.destination.clickhouse_v2.model.AlterationSummary
import io.airbyte.integrations.destination.clickhouse_v2.model.isEmpty
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
    private val nameGenerator: ClickhouseFinalTableNameGenerator,
) : AirbyteClient, DirectLoadTableSqlOperations, DirectLoadTableNativeOperations {

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
        execute(
            sqlGenerator.wrapInTransaction(
                sqlGenerator.dropTable(targetTableName),
                sqlGenerator.swapTable(sourceTableName, targetTableName),
            ),
        )
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
        execute(
            sqlGenerator.upsertTable(
                stream,
                columnNameMapping,
                sourceTableName,
                targetTableName,
            ),
        )
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
        val properTableName = nameGenerator.getTableName(stream.descriptor)
        val tableSchema = client.getTableSchema(properTableName.name, properTableName.namespace)

        val tableSchemaWithoutAirbyteColumns: List<ClickHouseColumn> =
            tableSchema.columns
                .filterNot { column -> column.columnName in COLUMN_NAMES }
                .map { column ->
                    ClickHouseColumn.of(
                        columnNameMapping[column.columnName] ?: column.columnName,
                        column.dataType,
                        column.isNullable,
                    )
                }

        if (!stream.schema.isObject) {
            val error =
                "The root of the schema is not an Object which is not expected, the schema changes won't be propagated"
            log.error { error }
            throw IllegalStateException(error)
        }

        val airbyteSchemaWithClickhouseType: Map<String, String> =
            stream.schema
                .asColumns()
                .map { (fieldName, fieldType) ->
                    // We don't need to nullable information here because we are setting all fields
                    // as
                    // nullable in the destination
                    // Add map key
                    fieldName to fieldType.type.toDialectType()
                }
                .toMap()

        val columnChanges: AlterationSummary =
            getChangedColumns(
                tableSchemaWithoutAirbyteColumns,
                airbyteSchemaWithClickhouseType,
            )
        if (columnChanges.isEmpty()) {
            log.info { "No changes detected for table $properTableName" }
            return
        }
        execute(
            sqlGenerator.alterTable(
                columnChanges,
                properTableName,
            ),
        )
    }

    internal fun getChangedColumns(
        tableColumns: List<ClickHouseColumn>,
        catalogColumns: Map<String, String>,
    ): AlterationSummary {

        val modified = mutableMapOf<String, String>()
        val deleted = mutableSetOf<String>()
        val mutableCatalogColumns: MutableMap<String, String> = catalogColumns.toMutableMap()

        tableColumns.forEach { clickhouseColumn ->
            if (!mutableCatalogColumns.containsKey(clickhouseColumn.columnName)) {
                deleted.add(clickhouseColumn.columnName)
            } else {
                val clickhouseType = clickhouseColumn.dataType.getDataTypeAsString()
                if (mutableCatalogColumns[clickhouseColumn.columnName] != clickhouseType) {
                    modified[clickhouseColumn.columnName] =
                        mutableCatalogColumns[clickhouseColumn.columnName]!!
                }
                mutableCatalogColumns.remove(clickhouseColumn.columnName)
            }
        }

        val added: Map<String, String> = mutableCatalogColumns

        val result =
            AlterationSummary(
                added = added,
                modified = modified,
                deleted = deleted,
            )

        return result
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
        } else {
            this.name
        }
    }
}
