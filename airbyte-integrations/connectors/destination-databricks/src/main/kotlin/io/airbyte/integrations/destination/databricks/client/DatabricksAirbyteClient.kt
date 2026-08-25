/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.client

import com.databricks.sdk.WorkspaceClient
import com.databricks.sdk.service.files.CreateDirectoryRequest
import com.databricks.sdk.service.files.UploadRequest
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.databricks.sql.DatabricksSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.InputStream
import java.sql.ResultSet
import java.util.concurrent.ConcurrentHashMap
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class DatabricksAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: DatabricksSqlGenerator,
    private val workspaceClient: WorkspaceClient,
) : TableOperationsClient, TableSchemaEvolutionClient {

    /** Cache for describeTable results, evicted when schema changes via applyChangeset. */
    private val describeTableCache =
        ConcurrentHashMap<TableName, LinkedHashMap<String, ColumnType>>()

    /** Cache of staging volumes created in this session to skip redundant SQL + API calls. */
    private val stagingVolumeCache: MutableSet<TableName> = ConcurrentHashMap.newKeySet()

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun namespaceExists(namespace: String): Boolean =
        executeQuery(sqlGenerator.namespaceExists(namespace)) { rs ->
            rs.next() && rs.getBoolean("schema_exists")
        }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        execute(sqlGenerator.createTable(tableName, stream.tableSchema, replace))
    }

    override suspend fun tableExists(table: TableName): Boolean =
        executeQuery(sqlGenerator.tableExists(table)) { rs ->
            rs.next() && rs.getBoolean("table_exists")
        }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            executeQuery(sqlGenerator.countTable(tableName)) { rs ->
                if (rs.next()) rs.getLong(1) else 0L
            }
        } catch (_: Exception) {
            null
        }

    override suspend fun getGenerationId(tableName: TableName): Long =
        try {
            executeQuery(sqlGenerator.getGenerationId(tableName)) { rs ->
                if (rs.next()) rs.getLong(1) else 0L
            }
        } catch (e: Exception) {
            log.error(e) { "Failed to retrieve generation ID for ${tableName.toPrettyString()}" }
            0L
        }

    override suspend fun overwriteTable(
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        executeAll(sqlGenerator.overwriteTable(sourceTableName, targetTableName))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        val columnNames = buildSet {
            addAll(sqlGenerator.getMetaColumnNames())
            addAll(columnNameMapping.values)
        }
        execute(sqlGenerator.copyTable(columnNames, sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        execute(sqlGenerator.upsertTable(stream.tableSchema, sourceTableName, targetTableName))
    }

    /**
     * Returns all columns with their types for the given table in ordinal order, including Airbyte
     * meta columns. Used to provide an explicit schema to COPY INTO statements.
     *
     * Results are cached per table and evicted when [applyChangeset] modifies the schema.
     */
    fun describeTable(tableName: TableName): LinkedHashMap<String, ColumnType> =
        describeTableCache.getOrPut(tableName) {
            executeQuery(sqlGenerator.getTableSchema(tableName)) { rs ->
                val result = LinkedHashMap<String, ColumnType>()
                while (rs.next()) {
                    val name = rs.getString("column_name")
                    val type = normalizeDatabricksType(rs.getString("data_type"))
                    val nullable = rs.getString("is_nullable") == "YES"
                    result[name] = ColumnType(type, nullable)
                }
                result
            }
        }

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        val allColumns = describeTable(tableName)

        // Validate that all required meta columns exist
        if (!allColumns.keys.containsAll(COLUMN_NAMES)) {
            val missing = COLUMN_NAMES - allColumns.keys
            throw ConfigErrorException(
                "Table ${tableName.toPrettyString()} is missing Airbyte meta columns: " +
                    "$missing. Airbyte can only sync to Airbyte-managed tables.",
            )
        }

        // Return only user columns (filter out Airbyte meta columns)
        val userColumns = allColumns.filterKeys { it !in COLUMN_NAMES }
        return TableSchema(userColumns)
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
    ): TableSchema = TableSchema(stream.tableSchema.columnSchema.finalSchema)

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset,
    ) {
        if (!columnChangeset.isNoop()) {
            describeTableCache.remove(tableName)
            log.info { "Applying schema changes to ${tableName.toPrettyString()}:" }
            log.info { "  Added: ${columnChangeset.columnsToAdd.keys}" }
            log.info { "  Modified: ${columnChangeset.columnsToChange.keys}" }
            executeAll(sqlGenerator.alterTable(tableName, columnChangeset))
        }
    }

    fun createStagingVolume(tableName: TableName, stagingDirectory: String) {
        if (stagingVolumeCache.contains(tableName)) {
            return
        }
        execute(sqlGenerator.createStagingVolume(tableName))
        workspaceClient
            .files()
            .createDirectory(CreateDirectoryRequest().setDirectoryPath(stagingDirectory))
        stagingVolumeCache.add(tableName)
    }

    /** Uploads a file to a Unity Catalog Volume path. */
    fun uploadToVolume(stagedFilePath: String, inputStream: InputStream) {
        log.info { "Uploading staged file: $stagedFilePath" }
        workspaceClient
            .files()
            .upload(
                UploadRequest()
                    .setFilePath(stagedFilePath)
                    .setContents(inputStream)
                    .setOverwrite(true),
            )
    }

    /** Executes a COPY INTO statement to load a staged Avro file into the target table. */
    fun copyFromVolume(tableName: TableName, stagedFilePath: String) {
        log.info {
            "Loading staged file into ${tableName.namespace}.${tableName.name}: $stagedFilePath"
        }
        execute(sqlGenerator.copyIntoFromVolume(tableName, stagedFilePath))
    }

    /** Deletes a staged file from a Unity Catalog Volume. */
    fun deleteStagedFile(stagedFilePath: String) {
        workspaceClient.files().delete(stagedFilePath)
    }

    private fun execute(sql: String) {
        log.info { "Executing query: $sql" }
        dataSource.connection.use { conn -> conn.createStatement().use { it.execute(sql) } }
    }

    /**
     * Executes a list of SQL statements individually. Databricks does not support multi-statement
     * execution.
     */
    private fun executeAll(statements: List<String>) {
        for (sql in statements) {
            execute(sql)
        }
    }

    /**
     * Normalizes Databricks `information_schema.columns.data_type` values to match the DDL type
     * strings used during table creation. This ensures `discoverSchema()` and `computeSchema()`
     * produce identical type strings, preventing spurious schema evolution diffs.
     */
    private fun normalizeDatabricksType(dataType: String): String =
        when (dataType) {
            "DECIMAL" -> "DECIMAL(38, 10)" // information_schema omits precision/scale
            else -> dataType
        }

    private fun <T> executeQuery(sql: String, handler: (ResultSet) -> T): T {
        log.info { "Executing query: $sql" }
        return dataSource.connection.use { conn ->
            conn.createStatement().use { stmt -> stmt.executeQuery(sql).use { rs -> handler(rs) } }
        }
    }
}
