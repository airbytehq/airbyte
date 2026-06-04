/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.client

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAMES
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.redshift.sql.RedshiftSqlGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
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

/** PostgreSQL/Redshift SQL state for DEPENDENT_OBJECTS_STILL_EXIST. */
private const val SQLSTATE_DEPENDENT_OBJECTS_STILL_EXIST = "2BP01"

@Singleton
class RedshiftAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: RedshiftSqlGenerator,
    private val s3Client: S3Client,
) : TableSchemaEvolutionClient, TableOperationsClient {

    private val describeTableCache = ConcurrentHashMap<TableName, List<String>>()

    override suspend fun createNamespace(namespace: String) {
        try {
            execute(sqlGenerator.createNamespace(namespace))
        } catch (e: SQLException) {
            // Swallow race condition where concurrent connections both try CREATE SCHEMA
            if (e.message?.contains("already exists") != true) {
                throw e
            }
        }
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
        replace: Boolean
    ) {
        execute(sqlGenerator.createTable(stream, tableName, replace))
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        execute(sqlGenerator.overwriteTable(sourceTableName, targetTableName))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(sqlGenerator.copyTable(sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(sqlGenerator.upsertTable(stream, sourceTableName, targetTableName))
    }

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            executeQuery(sqlGenerator.countTable(tableName)) { rs ->
                if (rs.next()) {
                    rs.getLong(COUNT_TOTAL_ALIAS)
                } else {
                    0L
                }
            }
        } catch (e: SQLException) {
            log.debug(e) {
                "Table ${tableName.namespace}.${tableName.name} does not exist. " +
                    "Count returning null to signal a missing table."
            }
            null
        }

    /**
     * Efficiently checks whether a table is non-empty using `SELECT EXISTS(... LIMIT 1)`.
     *
     * Returns `true` if the table has at least one row, `false` if it is empty, or `null` if the
     * table does not exist.
     */
    suspend fun isTableNotEmpty(tableName: TableName): Boolean? =
        try {
            executeQuery(sqlGenerator.isTableNotEmpty(tableName)) { rs ->
                rs.next() && rs.getBoolean("not_empty")
            }
        } catch (e: SQLException) {
            log.debug(e) {
                "Table ${tableName.namespace}.${tableName.name} does not exist. " +
                    "Returning null to signal a missing table."
            }
            null
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
            log.error(e) { "Failed to retrieve the generation ID for table $tableName" }
            0L
        }

    override suspend fun discoverSchema(tableName: TableName): TableSchema {
        val columnsInDb = getColumnsFromDbForDiscovery(tableName)

        // Table does not exist -- return empty schema so the CDK creates it.
        if (columnsInDb.isEmpty()) {
            return TableSchema(emptyMap())
        }

        val hasAllAirbyteColumns = columnsInDb.keys.containsAll(COLUMN_NAMES)
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

        // Filter out Airbyte meta columns — return only user columns
        val userColumns = columnsInDb.filterKeys { it !in COLUMN_NAMES }
        return TableSchema(userColumns)
    }

    /**
     * Returns the column names of the given table in ordinal order (matching the physical column
     * layout)
     */
    fun describeTable(tableName: TableName): List<String> =
        describeTableCache.getOrPut(tableName) {
            executeQuery(sqlGenerator.getTableSchema(tableName)) { rs ->
                val columns = mutableListOf<String>()
                while (rs.next()) {
                    columns.add(rs.getString(COLUMN_NAME_COLUMN))
                }
                columns
            }
        }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): TableSchema {
        return TableSchema(stream.tableSchema.columnSchema.finalSchema)
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset
    ) {
        if (columnChangeset.isNoop()) {
            return
        }

        describeTableCache.remove(tableName)

        log.info { "Summary of table alterations for ${tableName.namespace}.${tableName.name}:" }
        log.info { "  Added columns: ${columnChangeset.columnsToAdd}" }
        log.info { "  Dropped columns: ${columnChangeset.columnsToDrop}" }
        log.info { "  Modified columns: ${columnChangeset.columnsToChange}" }

        execute(
            sqlGenerator.matchSchemas(
                tableName = tableName,
                columnsToAdd = columnChangeset.columnsToAdd,
                columnsToRemove = columnChangeset.columnsToDrop,
                columnsToModify = columnChangeset.columnsToChange
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

    /**
     * Executes a Redshift COPY command to load data from S3. Logging is suppressed because the
     * generated SQL contains plaintext AWS credentials in the CREDENTIALS clause.
     */
    suspend fun copyFromS3(
        tableName: TableName,
        s3Path: String,
        accessKeyId: String,
        secretAccessKey: String,
        region: String,
    ) {
        execute(
            sqlGenerator.copyFromS3(tableName, s3Path, accessKeyId, secretAccessKey, region),
            logStatement = false,
        )
    }

    /** Adds a column to an existing table. */
    suspend fun addColumn(tableName: TableName, columnName: String, columnType: String) {
        execute(sqlGenerator.addColumn(tableName, columnName, columnType))
    }

    /** Deletes a row by its `_airbyte_raw_id` using a parameterized query. */
    suspend fun deleteByRawId(tableName: TableName, rawId: String) {
        val sql = sqlGenerator.deleteByRawId(tableName)
        log.info { sql }
        dataSource.connection.use { conn ->
            conn.prepareStatement(sql).use { ps ->
                ps.setString(1, rawId)
                ps.executeUpdate()
            }
        }
    }

    /** Uploads data to S3. */
    suspend fun uploadToS3(
        bucketName: String,
        key: String,
        data: ByteArray,
        contentType: String = "application/gzip",
    ) {
        val request =
            PutObjectRequest.builder()
                .bucket(bucketName)
                .key(key)
                .contentLength(data.size.toLong())
                .contentType(contentType)
                .build()
        s3Client.putObject(request, RequestBody.fromBytes(data))
    }

    /** Deletes an object from S3. */
    suspend fun deleteFromS3(bucketName: String, key: String) {
        val request = DeleteObjectRequest.builder().bucket(bucketName).key(key).build()
        s3Client.deleteObject(request)
    }

    // ================================================================
    // Internal helpers
    // ================================================================

    internal fun getMetaColumnNames(): Set<String> = RedshiftSqlGenerator.META_COLUMNS.keys

    /**
     * Queries `information_schema.columns` for all columns in a table, including Airbyte meta
     * columns. Used by [discoverSchema] for schema evolution.
     */
    private fun getColumnsFromDbForDiscovery(tableName: TableName): Map<String, ColumnType> =
        executeQuery(sqlGenerator.getTableSchema(tableName)) { rs ->
            val columns: MutableMap<String, ColumnType> = mutableMapOf()
            while (rs.next()) {
                val columnName = rs.getString(COLUMN_NAME_COLUMN)
                val dataType = rs.getString("data_type")
                val isNullable = rs.getString("is_nullable") == "YES"
                columns[columnName] = ColumnType(normalizeRedshiftType(dataType), isNullable)
            }
            columns
        }

    /**
     * Normalizes Redshift type names from `information_schema.columns.data_type` to match the
     * internal type names used in DDL statements. Verified against a real Redshift cluster.
     *
     * Precision/scale/length are ignored: all varchars normalize to `varchar(65535)` and all
     * numerics normalize to `decimal(38,9)`
     */
    internal fun normalizeRedshiftType(redshiftType: String): String =
        when (redshiftType) {
            "character varying" -> "varchar(65535)"
            "numeric" -> "decimal(38,9)"
            "timestamp without time zone" -> "timestamp"
            "timestamp with time zone" -> "timestamptz"
            "time without time zone" -> "time"
            "time with time zone" -> "timetz"
            else -> redshiftType
        }

    /**
     * Executes a SQL statement (DDL or DML) against Redshift.
     *
     * @param logStatement set to `false` for statements that contain secrets (e.g. COPY with inline
     * AWS credentials) to prevent plaintext credentials from appearing in logs.
     */
    internal fun execute(query: String, logStatement: Boolean = true) {
        if (logStatement) {
            log.info { query.trimIndent() }
        }
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { it.execute(query) }
            }
        } catch (e: SQLException) {
            if (
                e.sqlState == SQLSTATE_DEPENDENT_OBJECTS_STILL_EXIST ||
                    e.message?.contains("depends on") == true
            ) {
                val message =
                    """
                    Failed to modify table because other database objects (such as views 
                    or rules) depend on it. Original error: ${e.message} .

                    You can enable the 'Drop tables with CASCADE' option in the destination 
                    configuration to automatically drop dependent objects during sync. 
                    WARNING: This will delete all data in dependent objects (views, etc.). 

                    Alternatively, you can manually drop the dependent views before running 
                    the sync, then recreate them afterward. To find dependent views, run: 
                    SELECT dependent_ns.nspname, dependent_view.relname 
                    FROM pg_depend 
                    JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid 
                    JOIN pg_class AS dependent_view 
                    ON pg_rewrite.ev_class = dependent_view.oid 
                    JOIN pg_namespace dependent_ns 
                    ON dependent_view.relnamespace = dependent_ns.oid 
                    WHERE pg_depend.refobjid = 'your_schema.your_table'::regclass;
                    """.trimIndent()
                log.error { message }
                throw ConfigErrorException(message, e)
            }

            // Enrich COPY load errors with details from stl_load_errors
            if (e.message?.contains("stl_load_errors") == true) {
                val details = queryLoadErrors()
                val enrichedMessage = buildString {
                    append("COPY command failed. ")
                    append(e.message)
                    if (details.isNotEmpty()) {
                        append("\n\nLoad error details from stl_load_errors:\n")
                        details.forEach { append("  - $it\n") }
                    }
                }
                log.error { enrichedMessage }
                throw SQLException(enrichedMessage, e.sqlState, e.errorCode, e)
            }

            throw e
        }
    }

    /** Executes a SQL query and processes the [ResultSet] with the given [resultProcessor]. */
    private fun <T> executeQuery(query: String, resultProcessor: (ResultSet) -> T): T {
        log.info { query.trimIndent() }
        return dataSource.connection.use { connection ->
            connection.createStatement().use {
                it.executeQuery(query).use { resultSet -> resultProcessor(resultSet) }
            }
        }
    }

    /** Queries `stl_load_errors` for the most recent COPY error within the last minute */
    private fun queryLoadErrors(): List<String> =
        try {
            executeQuery(
                """
                SELECT *
                FROM stl_load_errors
                WHERE starttime >= GETDATE() - INTERVAL '1 minute'
                ORDER BY starttime DESC
                LIMIT 1
                """.trimIndent()
            ) { rs ->
                val errors = mutableListOf<String>()
                while (rs.next()) {
                    val metadata = rs.metaData
                    val row =
                        (1..metadata.columnCount).joinToString(", ") { i ->
                            "${metadata.getColumnName(i)}=${rs.getString(i)?.trim()}"
                        }
                    errors.add(row)
                }
                errors
            }
        } catch (e: Exception) {
            log.warn(e) { "Failed to query stl_load_errors for additional details" }
            emptyList()
        }
}
