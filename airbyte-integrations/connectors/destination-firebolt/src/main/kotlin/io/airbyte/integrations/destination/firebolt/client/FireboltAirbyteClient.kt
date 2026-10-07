/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.client

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.firebolt.sql.FireboltSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.util.concurrent.ConcurrentHashMap
import javax.sql.DataSource
import software.amazon.awssdk.core.sync.RequestBody
import software.amazon.awssdk.services.s3.S3Client
import software.amazon.awssdk.services.s3.model.DeleteObjectRequest
import software.amazon.awssdk.services.s3.model.PutObjectRequest

private val log = KotlinLogging.logger {}

private const val COUNT_TOTAL_ALIAS = "total"
private const val COLUMN_NAME_COLUMN = "column_name"

/** JDBC client for executing SQL against Firebolt and implementing CDK table operations. */
@Singleton
class FireboltAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: FireboltSqlGenerator,
    private val s3Client: S3Client,
) : TableOperationsClient, TableSchemaEvolutionClient {

    private val describeTableCache = ConcurrentHashMap<TableName, List<String>>()

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun namespaceExists(namespace: String): Boolean =
        executeQuery(sqlGenerator.namespaceExists(namespace)) { rs ->
            rs.next() && rs.getBoolean(1)
        }

    override suspend fun tableExists(table: TableName): Boolean =
        executeQuery(sqlGenerator.tableExists(table)) { rs -> rs.next() && rs.getBoolean(1) }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean,
    ) {
        if (replace) {
            execute(sqlGenerator.dropTable(tableName))
        }
        execute(sqlGenerator.createTable(stream, tableName))
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        execute(sqlGenerator.dropTable(targetTableName))
        execute(sqlGenerator.overwriteTable(sourceTableName, targetTableName))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        execute(sqlGenerator.copyTable(sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName,
    ) {
        execute(sqlGenerator.upsertTable(stream, sourceTableName, targetTableName))
    }

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            executeQuery(sqlGenerator.countTable(tableName)) { rs ->
                if (rs.next()) rs.getLong(COUNT_TOTAL_ALIAS) else 0L
            }
        } catch (e: SQLException) {
            if (isTableNotFoundException(e)) null else throw e
        }

    suspend fun isTableNotEmpty(tableName: TableName): Boolean? =
        try {
            executeQuery(sqlGenerator.isTableNotEmpty(tableName)) { rs ->
                rs.next() && rs.getBoolean("not_empty")
            }
        } catch (e: SQLException) {
            if (isTableNotFoundException(e)) null else throw e
        }

    override suspend fun getGenerationId(tableName: TableName): Long =
        try {
            executeQuery(sqlGenerator.getGenerationId(tableName)) { rs ->
                if (rs.next()) {
                    rs.getLong(COLUMN_NAME_AB_GENERATION_ID)
                } else {
                    log.warn { "No generation ID found for table $tableName, returning 0" }
                    0L
                }
            }
        } catch (e: SQLException) {
            if (isTableNotFoundException(e)) 0L else throw e
        }

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        val columnsInDb = getColumnsFromDbForDiscovery(tableName)

        // Table does not exist -- return empty schema so the CDK creates it.
        if (columnsInDb.isEmpty()) {
            return TableSchema(emptyMap())
        }

        val hasAllAirbyteColumns =
            columnsInDb.keys.containsAll(FireboltSqlGenerator.META_COLUMNS.keys)
        if (!hasAllAirbyteColumns) {
            val message =
                """
                The target table (${tableName.namespace}.${tableName.name}) already exists \
                in the destination, but does not contain Airbyte's internal columns. \
                Airbyte can only sync to Airbyte-controlled tables. To fix this error, \
                you must either delete the target table or add a prefix in the connection \
                configuration in order to sync to a separate table in the destination.
                """.trimIndent()
            log.error { message }
            throw ConfigErrorException(message)
        }

        val userColumns = columnsInDb.filterKeys { it !in FireboltSqlGenerator.META_COLUMNS.keys }
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
        if (columnChangeset.isNoop()) {
            return
        }

        describeTableCache.remove(tableName)

        log.info { "Summary of table alterations for ${tableName.namespace}.${tableName.name}:" }
        log.info { "  Added columns: ${columnChangeset.columnsToAdd}" }
        log.info { "  Modified columns: ${columnChangeset.columnsToChange}" }

        execute(
            sqlGenerator.matchSchemas(
                tableName = tableName,
                columnsToAdd = columnChangeset.columnsToAdd,
                columnsToModify = columnChangeset.columnsToChange,
            )
        )
    }

    // ================================================================
    // Checker / staging operations
    // ================================================================

    /** Validates JDBC connectivity by executing a trivial query. */
    suspend fun ping() {
        execute("SELECT 1")
    }

    /** Executes a Firebolt COPY FROM statement to load gzip CSV from the given S3 path. */
    suspend fun copyFromS3(
        tableName: TableName,
        s3Path: String,
        accessKeyId: String,
        secretAccessKey: String,
    ) {
        execute(
            sqlGenerator.copyFromS3(tableName, s3Path, accessKeyId, secretAccessKey),
            logStatement = false,
        )
    }

    /** Upload raw bytes to S3. */
    fun uploadToS3(bucket: String, key: String, bytes: ByteArray) {
        val request =
            PutObjectRequest.builder()
                .bucket(bucket)
                .key(key)
                .contentLength(bytes.size.toLong())
                .contentType("application/gzip")
                .build()
        s3Client.putObject(request, RequestBody.fromBytes(bytes))
    }

    /** Delete an S3 object. */
    fun deleteFromS3(bucket: String, key: String) {
        val request = DeleteObjectRequest.builder().bucket(bucket).key(key).build()
        s3Client.deleteObject(request)
    }

    /**
     * Returns the column names of the given table in ordinal order (matching the physical column
     * layout). Used by the S3 staging dataflow to build CSV headers.
     */
    fun describeTable(tableName: TableName): List<String> =
        describeTableCache.getOrPut(tableName) {
            getColumnsFromDbForDiscovery(tableName).keys.toList()
        }

    // ================================================================
    // Internal helpers
    // ================================================================

    internal fun getMetaColumnNames(): Set<String> = FireboltSqlGenerator.META_COLUMNS.keys

    private fun getColumnsFromDbForDiscovery(tableName: TableName): Map<String, ColumnType> =
        executeQuery(sqlGenerator.getTableSchema(tableName)) { rs ->
            val columns: MutableMap<String, ColumnType> = mutableMapOf()
            while (rs.next()) {
                val columnName = rs.getString(COLUMN_NAME_COLUMN)
                val dataType = rs.getString("data_type")
                val isNullable = rs.getString("is_nullable") == "YES"
                columns[columnName] = ColumnType(normalizeFireboltType(dataType), isNullable)
            }
            columns
        }

    /** Normalizes Firebolt type names from information_schema to the DDL names we use. */
    internal fun normalizeFireboltType(fireboltType: String): String =
        when (fireboltType) {
            "integer" -> "int"
            "character varying" -> "text"
            "double precision" -> "double precision"
            "numeric" -> "numeric(38,9)"
            "timestamp without time zone" -> "timestamp"
            "timestamp with time zone" -> "timestamptz"
            "date" -> "date"
            "boolean" -> "boolean"
            "text" -> "text"
            "json" -> "json"
            "bytea" -> "bytea"
            "geography" -> "geography"
            else -> fireboltType
        }

    /**
     * Executes a SQL statement (DDL or DML) against Firebolt.
     *
     * @param logStatement set to false for statements that contain secrets (e.g. COPY FROM with
     * inline AWS credentials) to prevent plaintext credentials from appearing in logs.
     */
    internal fun execute(query: String, logStatement: Boolean = true) {
        if (logStatement) {
            log.info { query.trimIndent() }
        }
        dataSource.connection.use { connection ->
            connection.createStatement().use { it.execute(query) }
        }
    }

    private fun isTableNotFoundException(e: SQLException): Boolean =
        e.sqlState == "42P01" || e.message?.contains("does not exist") == true

    /** Executes a SQL query and processes the [ResultSet] with the given [resultProcessor]. */
    private fun <T> executeQuery(query: String, resultProcessor: (ResultSet) -> T): T {
        log.info { query.trimIndent() }
        return dataSource.connection.use { connection: Connection ->
            connection.createStatement().use {
                it.executeQuery(query).use { resultSet -> resultProcessor(resultSet) }
            }
        }
    }
}
