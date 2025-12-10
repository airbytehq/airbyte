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
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
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
    val configuredCatalog: ConfiguredAirbyteCatalog? = null,
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
            // First check EngineEdition to determine if this is Azure SQL
            // EngineEdition values:
            // https://learn.microsoft.com/en-us/sql/t-sql/functions/serverproperty-transact-sql
            // 5 = Azure SQL Database
            // 8 = Azure SQL Managed Instance (SQL Server Agent is always running)
            val engineEdition: Int? =
                base.conn.createStatement().use { stmt: Statement ->
                    stmt
                        .executeQuery("SELECT ServerProperty('EngineEdition') AS EngineEdition")
                        .use { rs: ResultSet ->
                            if (rs.next()) rs.getInt("EngineEdition") else null
                        }
                }

            when (engineEdition) {
                5 -> {
                    // Azure SQL Database - SQL Server Agent is not applicable
                    // CDC in Azure SQL Database works differently and doesn't require SQL Server
                    // Agent
                    log.info {
                        "Azure SQL Database detected (EngineEdition=$engineEdition). Skipping SQL Server Agent check."
                    }
                    return
                }
                8 -> {
                    // Azure SQL Managed Instance - SQL Server Agent is always running
                    // https://learn.microsoft.com/en-us/azure/azure-sql/managed-instance/transact-sql-tsql-differences-sql-server#sql-server-agent
                    log.info {
                        "Azure SQL Managed Instance detected (EngineEdition=$engineEdition). SQL Server Agent is assumed to be running."
                    }
                    return
                }
            }

            // For on-premises SQL Server, check if SQL Server Agent is running
            base.conn.createStatement().use { stmt: Statement ->
                stmt
                    .executeQuery(
                        "SELECT servicename, status_desc FROM sys.dm_server_services WHERE servicename LIKE '%SQL Server Agent%' OR servicename LIKE '%SQL Server 代理%'"
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
            // Gracefully handle cases where sys.dm_server_services is not accessible
            // This can happen in some Azure SQL configurations or restricted permission scenarios
            log.warn { "Skipping SQL Server Agent check due to SQLException: ${e.message}" }
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
        if (table !in memoizedColumnMetadata) return listOf()
        return memoizedColumnMetadata[table]!!.map {
            Field(it.label, base.fieldTypeMapper.toFieldType(it))
        }
    }

    override fun streamNamespaces(): List<String> {
        // If no namespaces are configured, return all discovered schemas
        if (base.config.namespaces.isEmpty()) {
            return memoizedTableNames.mapNotNull { it.schema }.distinct()
        }
        return base.config.namespaces.toList()
    }

    val memoizedTableNames: List<TableName> by lazy {
        log.info { "Querying SQL Server table names for catalog discovery." }
        try {
            val allTables = mutableSetOf<TableName>()
            val dbmd = base.conn.metaData
            val currentDatabase = base.conn.catalog

            // If no namespaces are configured, discover all schemas
            if (base.config.namespaces.isEmpty()) {
                log.info {
                    "No schemas explicitly configured, discovering all non-system schemas in the database."
                }
                dbmd.getTables(currentDatabase, null, null, null).use { rs ->
                    while (rs.next()) {
                        val schema = rs.getString("TABLE_SCHEM")
                        // Filter out SQL Server system schemas unless explicitly configured
                        if (schema != null && !isSystemSchema(schema)) {
                            allTables.add(
                                TableName(
                                    catalog = rs.getString("TABLE_CAT"),
                                    schema = schema,
                                    name = rs.getString("TABLE_NAME"),
                                    type = rs.getString("TABLE_TYPE") ?: "",
                                ),
                            )
                        }
                    }
                }
            } else {
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
            }
            log.info {
                "Discovered ${allTables.size} table(s) in SQL Server database '$currentDatabase'."
            }
            return@lazy allTables.toList()
        } catch (e: Exception) {
            throw RuntimeException("SQL Server table discovery query failed: ${e.message}", e)
        }
    }

    val memoizedColumnMetadata: Map<TableName, List<JdbcMetadataQuerier.ColumnMetadata>> by lazy {
        val joinMap: Map<TableName, TableName> =
            memoizedTableNames.associateBy { it.copy(type = "") }
        val results = mutableListOf<Pair<TableName, JdbcMetadataQuerier.ColumnMetadata>>()
        log.info { "Querying SQL Server column names for catalog discovery." }
        try {
            val dbmd = base.conn.metaData
            val currentDatabase = base.conn.catalog

            fun addColumnsFromQuery(
                catalog: String?,
                schema: String?,
                tablePattern: String?,
                isPseudoColumn: Boolean
            ) {
                val rsMethod = if (isPseudoColumn) dbmd::getPseudoColumns else dbmd::getColumns
                rsMethod(catalog, schema, tablePattern, null).use { rs ->
                    while (rs.next()) {
                        val (tableName: TableName, metadata: JdbcMetadataQuerier.ColumnMetadata) =
                            base.columnMetadataFromResultSet(rs, isPseudoColumn)
                        val joinedTableName: TableName = joinMap[tableName] ?: continue
                        results.add(joinedTableName to metadata)
                    }
                }
            }

            // If no namespaces are configured, discover all schemas
            if (base.config.namespaces.isEmpty()) {
                log.info { "Querying columns for all schemas." }
                addColumnsFromQuery(currentDatabase, null, null, isPseudoColumn = true)
                addColumnsFromQuery(currentDatabase, null, null, isPseudoColumn = false)
            } else {
                for (namespace in
                    base.config.namespaces + base.config.namespaces.map { it.uppercase() }) {
                    addColumnsFromQuery(currentDatabase, namespace, null, isPseudoColumn = true)
                    addColumnsFromQuery(currentDatabase, namespace, null, isPseudoColumn = false)
                }
            }
            log.info { "Discovered ${results.size} column(s) and pseudo-column(s)." }
        } catch (e: Exception) {
            throw RuntimeException("SQL Server column discovery query failed: ${e.message}", e)
        }
        return@lazy results.groupBy({ it.first }, { it.second }).mapValues {
            (_, columnMetadataByTable) ->
            // Deduplicate columns by name to handle case-insensitive databases
            val deduplicatedColumns = columnMetadataByTable.distinctBy { it.name }
            deduplicatedColumns.filter { it.ordinal == null } +
                deduplicatedColumns.filter { it.ordinal != null }.sortedBy { it.ordinal }
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
     * Returns the primary key for discovery/catalog purposes.
     *
     * This returns the actual PRIMARY KEY constraint defined on the table, which represents the
     * logical uniqueness constraint. This is used for catalog discovery and schema definition.
     *
     * Note: This is separate from the sync strategy (which column to use for ordered column
     * loading), which is determined by [getOrderedColumnForSync].
     *
     * The logic flow:
     * 1. Check for primary key constraint
     * 2. If primary key exists → Use it
     * 3. If no primary key exists → Check configured catalog for user-defined logical PK
     * 4. If no logical PK exists → Return empty list
     */
    override fun primaryKey(
        streamID: StreamIdentifier,
    ): List<List<String>> {
        val table: TableName = findTableName(streamID) ?: return listOf()

        // First try to get the actual primary key constraint
        val databasePK = memoizedPrimaryKeys[table]
        if (!databasePK.isNullOrEmpty()) {
            log.info {
                "Found primary key for table ${table.schema}.${table.name}: ${databasePK.flatten()}"
            }
            return databasePK
        }

        // Fall back to user-defined logical PK from configured catalog
        // This handles migration from old connector where tables without physical PKs
        // could have logical PKs configured in the UI
        val logicalPK = getUserDefinedPrimaryKey(streamID)
        if (logicalPK.isNotEmpty()) {
            log.info {
                "No physical primary key found for table ${table.schema}.${table.name}. " +
                    "Using user-defined logical primary key from configured catalog: $logicalPK"
            }
            return logicalPK
        }

        log.info { "No primary key or logical PK found for table ${table.schema}.${table.name}" }
        return listOf()
    }

    /**
     * Returns the column to use for ordered column (OC) syncing strategy.
     *
     * This determines which column should be used for incremental sync with ordered column loading,
     * prioritizing SQL Server performance characteristics.
     *
     * The logic flow:
     * 1. If single-column clustered index exists → Use it (best performance for SQL Server)
     * 2. If composite clustered index or no clustered index → Use first column of primary key
     * 3. If no primary key → Use first column of logical PK from configured catalog
     * 4. If nothing available → Return null
     *
     * Note: This is separate from [primaryKey] which returns the full PK for discovery purposes.
     */
    fun getOrderedColumnForSync(streamID: StreamIdentifier): String? {
        val table: TableName = findTableName(streamID) ?: return null

        // Prefer single-column clustered index for best SQL Server performance
        val clusteredIndexKeys = memoizedClusteredIndexKeys[table]
        if (clusteredIndexKeys != null && clusteredIndexKeys.size == 1) {
            val column = clusteredIndexKeys[0][0]
            log.info {
                "Using single-column clustered index for sync: ${table.schema}.${table.name} -> $column"
            }
            return column
        }

        // Fall back to first column of primary key
        val databasePK = memoizedPrimaryKeys[table]
        if (!databasePK.isNullOrEmpty()) {
            val column = databasePK[0][0]
            log.info {
                "Clustered index is composite or not found. Using first PK column for sync: ${table.schema}.${table.name} -> $column"
            }
            return column
        }

        // Fall back to first column of logical PK
        val logicalPK = getUserDefinedPrimaryKey(streamID)
        if (logicalPK.isNotEmpty()) {
            val column = logicalPK[0][0]
            log.info {
                "No physical primary key. Using first logical PK column for sync: ${table.schema}.${table.name} -> $column"
            }
            return column
        }

        log.warn {
            "No suitable column found for ordered column sync: ${table.schema}.${table.name}"
        }
        return null
    }

    /**
     * Gets the user-defined logical primary key from the configured catalog. This is used for
     * backward compatibility with the old connector where users could configure logical PKs for
     * tables without physical PKs.
     */
    private fun getUserDefinedPrimaryKey(streamID: StreamIdentifier): List<List<String>> {
        if (configuredCatalog == null) {
            return listOf()
        }

        val configuredStream: ConfiguredAirbyteStream? =
            configuredCatalog.streams.find {
                it.stream.name == streamID.name && it.stream.namespace == streamID.namespace
            }

        return configuredStream?.primaryKey ?: listOf()
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

        /**
         * SQL Server system schemas that should be excluded from auto-discovery. These schemas
         * contain system objects and should not be synced unless explicitly configured.
         */
        private val SYSTEM_SCHEMAS =
            setOf(
                // Core system schemas (cannot be dropped)
                "sys",
                "INFORMATION_SCHEMA",

                // CDC schema (change data capture)
                "cdc",

                // Guest user schema
                "guest",

                // Fixed database role schemas (backward compatibility)
                "db_accessadmin",
                "db_backupoperator",
                "db_datareader",
                "db_datawriter",
                "db_ddladmin",
                "db_denydatareader",
                "db_denydatawriter",
                "db_owner",
                "db_securityadmin",

                // Legacy system support tables/schemas
                "spt_fallback_db",
                "spt_fallback_dev",
                "spt_fallback_usg",
                "spt_monitor",
                "spt_values",

                // Replication system schema
                "MSreplication_options"
            )

        /**
         * Checks if a schema is a SQL Server system schema. System schemas are excluded from
         * auto-discovery unless explicitly configured by the user.
         */
        private fun isSystemSchema(schema: String): Boolean {
            return SYSTEM_SCHEMAS.contains(schema)
        }

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
            AND i.is_unique = 1  -- Only unique indexes
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
        val configuredCatalog: ConfiguredAirbyteCatalog? = null,
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
            return MsSqlSourceMetadataQuerier(base, configuredCatalog)
        }
    }
}
