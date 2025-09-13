/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement

private val log = KotlinLogging.logger {}

/** Delegates to [JdbcMetadataQuerier] except for [fields]. */
class MsSqlSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
) : MetadataQuerier by base {

    override fun extraChecks() {
        base.extraChecks()
        if (base.config.global) {
            // Extra checks for CDC
            checkSqlServerAgentRunning()
            checkDatabaseCdcEnabled()
        }
    }

    private fun checkSqlServerAgentRunning() {
        try {
            base.conn.createStatement().use { stmt: Statement ->
                stmt
                    .executeQuery(
                        "SELECT servicename, status_desc FROM sys.dm_server_services WHERE servicename LIKE '%SQL Server Agent%'"
                    )
                    .use { rs: ResultSet ->
                        if (!rs.next()) {
                            throw ConfigErrorException(
                                "SQL Server Agent service is not found. CDC requires SQL Server Agent to be running."
                            )
                        }
                        val status = rs.getString("status_desc")
                        if (status != "Running") {
                            throw ConfigErrorException(
                                "SQL Server Agent is not running (status: $status). CDC requires SQL Server Agent to be running."
                            )
                        }
                    }
            }
        } catch (e: SQLException) {
            throw ConfigErrorException("Failed to check SQL Server Agent status: ${e.message}")
        }
    }

    private fun checkDatabaseCdcEnabled() {
        try {
            base.conn.createStatement().use { stmt: Statement ->
                stmt
                    .executeQuery("SELECT is_cdc_enabled FROM sys.databases WHERE name = DB_NAME()")
                    .use { rs: ResultSet ->
                        if (!rs.next()) {
                            throw ConfigErrorException(
                                "Could not determine CDC status for current database"
                            )
                        }
                        val cdcEnabled = rs.getBoolean("is_cdc_enabled")
                        if (!cdcEnabled) {
                            throw ConfigErrorException(
                                "CDC is not enabled for the database. Please enable CDC with: EXEC sys.sp_cdc_enable_db"
                            )
                        }
                    }
            }
        } catch (e: SQLException) {
            throw ConfigErrorException("Failed to check database CDC status: ${e.message}")
        }
    }

    override fun fields(streamID: StreamIdentifier): List<Field> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        if (table !in base.memoizedColumnMetadata) return listOf()
        return base.memoizedColumnMetadata[table]!!.map {
            Field(it.label, base.fieldTypeMapper.toFieldType(it))
        }
    }

    override fun streamNamespaces(): List<String> = base.config.namespaces.toList()

    val memoizedTableNames: List<TableName> by lazy {
        log.info { "Querying SQL Server table names for catalog discovery." }
        try {
            val allTables = mutableSetOf<TableName>()
            val dbmd = base.conn.metaData
            val currentDatabase = base.conn.catalog

            for (namespace in
                base.config.namespaces + base.config.namespaces.map { it.uppercase() }) {
                // For SQL Server with SCHEMA namespace kind, use current database as catalog
                dbmd.getTables(currentDatabase, namespace, null, null).use { rs ->
                    while (rs.next()) {
                        allTables.add(
                            TableName(
                                catalog = rs.getString("TABLE_CAT"),
                                schema = rs.getString("TABLE_SCHEM"),
                                name = rs.getString("TABLE_NAME"),
                                type = rs.getString("TABLE_TYPE") ?: "",
                            ),
                        )
                    }
                }
            }
            log.info {
                "Discovered ${allTables.size} table(s) in SQL Server database '$currentDatabase'."
            }
            return@lazy allTables.toList()
        } catch (e: Exception) {
            throw RuntimeException("SQL Server table discovery query failed: ${e.message}", e)
        }
    }

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> =
        memoizedTableNames
            .filter { it.schema == streamNamespace }
            .map { StreamDescriptor().withName(it.name).withNamespace(streamNamespace) }
            .map(StreamIdentifier::from)

    fun findTableName(
        streamID: StreamIdentifier,
    ): TableName? =
        memoizedTableNames.find { it.name == streamID.name && it.schema == streamID.namespace }

    val memoizedClusteredIndexKeys: Map<TableName, List<List<String>>> by lazy {
        val results = mutableListOf<AllClusteredIndexKeysRow>()
        val schemas: List<String> = streamNamespaces()
        val sql: String = CLUSTERED_INDEX_QUERY_FMTSTR.format(schemas.joinToString { "'$it'" })
        log.info {
            "Querying SQL Server system tables for all clustered index keys for catalog discovery."
        }
        try {
            base.conn.createStatement().use { stmt: Statement ->
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    while (rs.next()) {
                        results.add(
                            AllClusteredIndexKeysRow(
                                rs.getString("table_schema"),
                                rs.getString("table_name"),
                                rs.getString("index_name"),
                                rs.getInt("key_ordinal").takeUnless { rs.wasNull() },
                                rs.getString("column_name").takeUnless { rs.wasNull() },
                            ),
                        )
                    }
                }
            }
            log.info {
                "Discovered all clustered index keys in ${schemas.size} SQL Server schema(s)."
            }
            return@lazy results
                .groupBy {
                    findTableName(
                        StreamIdentifier.from(
                            StreamDescriptor().withName(it.tableName).withNamespace(it.tableSchema),
                        ),
                    )
                }
                .mapNotNull { (table, rowsByTable) ->
                    if (table == null) return@mapNotNull null
                    val clusteredIndexRows: List<AllClusteredIndexKeysRow> =
                        rowsByTable
                            .groupBy { it.indexName }
                            .filterValues { rowsByIndex: List<AllClusteredIndexKeysRow> ->
                                rowsByIndex.all { it.keyOrdinal != null && it.columnName != null }
                            }
                            .values
                            .firstOrNull()
                            ?: return@mapNotNull null
                    val clusteredIndexColumnNames: List<List<String>> =
                        clusteredIndexRows
                            .sortedBy { it.keyOrdinal }
                            .mapNotNull { it.columnName }
                            .map { listOf(it) }
                    table to clusteredIndexColumnNames
                }
                .toMap()
        } catch (e: Exception) {
            throw RuntimeException(
                "SQL Server clustered index discovery query failed: ${e.message}",
                e
            )
        }
    }

    /**
     * The logic flow:
     * 1. Check for clustered index
     * 2. If single-column clustered index exists → Use it
     * 3. If composite clustered index exists → Use primary key
     * 4. If no clustered index exists → Use primary key
     * 5. If no primary key exists → Return empty list
     */
    override fun primaryKey(
        streamID: StreamIdentifier,
    ): List<List<String>> {
        val table: TableName = findTableName(streamID) ?: return listOf()

        // First try to get clustered index keys
        val clusteredIndexKeys = memoizedClusteredIndexKeys[table]

        // Use clustered index if it exists and is a single column
        // For composite clustered indexes, fall back to primary key
        return when {
            clusteredIndexKeys != null && clusteredIndexKeys.size == 1 -> {
                log.info {
                    "Using single-column clustered index for table ${table.schema}.${table.name}"
                }
                clusteredIndexKeys
            }
            clusteredIndexKeys != null && clusteredIndexKeys.size > 1 -> {
                log.info {
                    "Clustered index is composite for table ${table.schema}.${table.name}. Falling back to primary key."
                }
                memoizedPrimaryKeys[table] ?: listOf()
            }
            else -> {
                log.info {
                    "No clustered index found for table ${table.schema}.${table.name}. Using primary key."
                }
                memoizedPrimaryKeys[table] ?: listOf()
            }
        }
    }

    val memoizedPrimaryKeys: Map<TableName, List<List<String>>> by lazy {
        val results = mutableListOf<AllPrimaryKeysRow>()
        val schemas: List<String> = streamNamespaces()
        val sql: String = PK_QUERY_FMTSTR.format(schemas.joinToString { "'$it'" })
        log.info { "Querying SQL Server system tables for all primary keys for catalog discovery." }
        try {
            // Get primary keys for the specified table
            base.conn.createStatement().use { stmt: Statement ->
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    while (rs.next()) {
                        results.add(
                            AllPrimaryKeysRow(
                                rs.getString("table_schema"),
                                rs.getString("table_name"),
                                rs.getString("constraint_name"),
                                rs.getInt("ordinal_position").takeUnless { rs.wasNull() },
                                rs.getString("column_name").takeUnless { rs.wasNull() },
                            ),
                        )
                    }
                }
            }
            log.info { "Discovered all primary keys in ${schemas.size} SQL Server schema(s)." }
            return@lazy results
                .groupBy {
                    findTableName(
                        StreamIdentifier.from(
                            StreamDescriptor().withName(it.tableName).withNamespace(it.tableSchema),
                        ),
                    )
                }
                .mapNotNull { (table, rowsByTable) ->
                    if (table == null) return@mapNotNull null
                    val pkRows: List<AllPrimaryKeysRow> =
                        rowsByTable
                            .groupBy { it.constraintName }
                            .filterValues { rowsByPK: List<AllPrimaryKeysRow> ->
                                rowsByPK.all { it.position != null && it.columnName != null }
                            }
                            .values
                            .firstOrNull()
                            ?: return@mapNotNull null
                    val pkColumnNames: List<List<String>> =
                        pkRows
                            .sortedBy { it.position }
                            .mapNotNull { it.columnName }
                            .map { listOf(it) }
                    table to pkColumnNames
                }
                .toMap()
        } catch (e: Exception) {
            throw RuntimeException("SQL Server primary key discovery query failed: ${e.message}", e)
        }
    }

    private data class AllClusteredIndexKeysRow(
        val tableSchema: String,
        val tableName: String,
        val indexName: String,
        val keyOrdinal: Int?,
        val columnName: String?,
    )

    private data class AllPrimaryKeysRow(
        val tableSchema: String,
        val tableName: String,
        val constraintName: String,
        val position: Int?,
        val columnName: String?,
    )

    companion object {

        const val CLUSTERED_INDEX_QUERY_FMTSTR =
            """
        SELECT 
            s.name as table_schema,
            t.name as table_name,
            i.name as index_name,
            ic.key_ordinal,
            c.name as column_name
        FROM 
            sys.tables t
        INNER JOIN 
            sys.schemas s ON t.schema_id = s.schema_id
        INNER JOIN 
            sys.indexes i ON t.object_id = i.object_id
        INNER JOIN 
            sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
        INNER JOIN 
            sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
        WHERE 
            s.name IN (%s)
            AND i.type = 1  -- Clustered index
            AND ic.is_included_column = 0  -- Only key columns, not included columns
        ORDER BY 
            s.name, t.name, ic.key_ordinal;
            """

        const val PK_QUERY_FMTSTR =
            """
        SELECT 
            kcu.TABLE_SCHEMA as table_schema,
            kcu.TABLE_NAME as table_name, 
            kcu.COLUMN_NAME as column_name, 
            kcu.ORDINAL_POSITION as ordinal_position, 
            kcu.CONSTRAINT_NAME as constraint_name 
        FROM 
            INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
        INNER JOIN 
            INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        ON 
            kcu.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
            AND kcu.TABLE_SCHEMA = tc.TABLE_SCHEMA
        WHERE 
            kcu.TABLE_SCHEMA IN (%s)
            AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY';
            """
    }

    /** SQL Server implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory(
        val constants: DefaultJdbcConstants,
        val selectQueryGenerator: SelectQueryGenerator,
        val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
        val checkQueries: JdbcCheckQueries,
    ) : MetadataQuerier.Factory<MsSqlServerSourceConfiguration> {
        /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: MsSqlServerSourceConfiguration): MetadataQuerier {
            val jdbcConnectionFactory = JdbcConnectionFactory(config)
            val base =
                JdbcMetadataQuerier(
                    constants,
                    config,
                    selectQueryGenerator,
                    fieldTypeMapper,
                    checkQueries,
                    jdbcConnectionFactory,
                )
            return MsSqlSourceMetadataQuerier(base)
        }
    }
}
