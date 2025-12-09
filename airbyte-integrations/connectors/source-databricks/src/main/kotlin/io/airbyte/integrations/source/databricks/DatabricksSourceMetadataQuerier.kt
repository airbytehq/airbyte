/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.JdbcMetadataQuerier.ColumnMetadata
import io.airbyte.cdk.discover.JdbcMetadataQuerier.PrimaryKeyRow
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.DefaultJdbcConstants.NamespaceKind
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.optimize
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.lang.RuntimeException
import java.sql.Connection
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import java.sql.ResultSetMetaData
import java.sql.SQLException
import java.sql.Statement
import kotlin.use

/**
 * Databricks implementation of [MetadataQuerier].
 *
 * This class combines the connection management from DatabricksJdbcMetadataQuerier with the full
 * metadata discovery logic, eliminating the need for delegation.
 *
 * Databricks uses a standard three-level namespace: catalog.schema.table where catalog is the
 * database name, schema is the schema name.
 */
class DatabricksSourceMetadataQuerier(
    val constants: DefaultJdbcConstants,
    val config: DatabricksSourceConfiguration,
    val selectQueryGenerator: SelectQueryGenerator,
    val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
    val checkQueries: JdbcCheckQueries,
    val connectionFactory: DatabricksSourceConnectionFactory,
) : MetadataQuerier {
    private val log = KotlinLogging.logger {}

    val conn: Connection by lazy { connectionFactory.get() }

    fun TableName.namespace(): String? =
        when (constants.namespaceKind) {
            NamespaceKind.CATALOG_AND_SCHEMA -> "`$catalog`.`${config.schema}`"
            NamespaceKind.CATALOG -> "`$catalog`"
            NamespaceKind.SCHEMA -> "`${config.schema}`"
        }

    val memoizedColumnMetadata: Map<TableName, List<ColumnMetadata>> by lazy {
        val joinMap: Map<TableName, TableName> =
            memoizedTableNames.associateBy { it.copy(type = "") }
        val results = mutableListOf<Pair<TableName, ColumnMetadata>>()
        log.info { "Querying column names for catalog discovery." }
        try {
            val dbmd: DatabaseMetaData = conn.metaData
            memoizedTableNames
                .filter { it.namespace() != null }
                .map { it.catalog to it.schema }
                .distinct()
                .forEach { (catalog: String?, schema: String?) ->
                    dbmd.getColumns(catalog, schema, null, null).use { rs: ResultSet ->
                        while (rs.next()) {
                            val (tableName: TableName, metadata: ColumnMetadata) =
                                columnMetadataFromResultSet(rs, isPseudoColumn = false)
                            val joinedTableName: TableName = joinMap[tableName] ?: continue
                            results.add(joinedTableName to metadata)
                        }
                    }
                }
            log.info { "Discovered ${results.size} column(s)." }
        } catch (e: Exception) {
            throw RuntimeException("Column name discovery query failed: ${e.message}", e)
        }
        return@lazy results.groupBy({ it.first }, { it.second }).mapValues {
            (_, columnMetadataByTable: List<ColumnMetadata>) ->
            columnMetadataByTable.filter { it.ordinal == null } +
                columnMetadataByTable.filter { it.ordinal != null }.sortedBy { it.ordinal }
        }
    }

    private fun columnMetadataFromResultSet(
        rs: ResultSet,
        isPseudoColumn: Boolean,
    ): Pair<TableName, ColumnMetadata> {
        val tableName =
            TableName(
                catalog = rs.getString("TABLE_CAT"),
                schema = rs.getString("TABLE_SCHEM"),
                name = rs.getString("TABLE_NAME"),
                type = "",
            )
        val type =
            SystemType(
                typeName = if (isPseudoColumn) null else rs.getString("TYPE_NAME"),
                typeCode = rs.getInt("DATA_TYPE"),
                precision = rs.getInt("COLUMN_SIZE").takeUnless { rs.wasNull() },
                scale = rs.getInt("DECIMAL_DIGITS").takeUnless { rs.wasNull() },
            )
        val metadata =
            ColumnMetadata(
                name = rs.getString("COLUMN_NAME"),
                label = rs.getString("COLUMN_NAME"),
                type = type,
                nullable =
                    when (rs.getString("IS_NULLABLE")?.uppercase()) {
                        "NO" -> false
                        "YES" -> true
                        else -> null
                    },
                ordinal = if (isPseudoColumn) null else rs.getInt("ORDINAL_POSITION"),
            )
        return tableName to metadata
    }

    override fun fields(
        streamID: StreamIdentifier,
    ): List<Field> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        return columnMetadata(table).map { Field(it.label, fieldTypeMapper.toFieldType(it)) }
    }

    fun columnMetadata(table: TableName): List<ColumnMetadata> {
        val columnMetadata: List<ColumnMetadata> = memoizedColumnMetadata[table] ?: listOf()
        if (columnMetadata.isEmpty() || !config.checkPrivileges) {
            return columnMetadata
        }
        val resultsFromSelectMany: List<ColumnMetadata>? =
            queryColumnMetadata(conn, selectLimit0(table, columnMetadata.map { it.name }))
        if (resultsFromSelectMany != null) {
            return resultsFromSelectMany
        }
        log.info {
            "Not all columns of $table might be accessible, trying each column individually."
        }
        return columnMetadata.flatMap {
            queryColumnMetadata(conn, selectLimit0(table, listOf(it.name))) ?: listOf()
        }
    }

    /**
     * Generates SQL query used to discover [ColumnMetadata] and to verify table access permissions.
     */
    fun selectLimit0(
        table: TableName,
        columnIDs: List<String>,
    ): String {
        val querySpec =
            SelectQuerySpec(
                SelectColumns(columnIDs.map { Field(it, io.airbyte.cdk.jdbc.NullFieldType) }),
                From(table.name, table.namespace()),
                limit = Limit(0),
            )
        return selectQueryGenerator.generate(querySpec.optimize()).sql
    }

    private fun queryColumnMetadata(
        conn: Connection,
        sql: String,
    ): List<ColumnMetadata>? {
        log.info { "Querying $sql for catalog discovery." }
        conn.createStatement().use { stmt: Statement ->
            try {
                stmt.fetchSize = 1
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    val meta: ResultSetMetaData = rs.metaData
                    return (1..meta.columnCount).map {
                        val type =
                            SystemType(
                                typeName = swallow { meta.getColumnTypeName(it) },
                                typeCode = meta.getColumnType(it),
                                precision = swallow { meta.getPrecision(it) },
                                scale = swallow { meta.getScale(it) },
                            )
                        ColumnMetadata(
                            name = meta.getColumnName(it),
                            label = meta.getColumnLabel(it),
                            type = type,
                            nullable =
                                when (swallow { meta.isNullable(it) }) {
                                    ResultSetMetaData.columnNoNulls -> false
                                    ResultSetMetaData.columnNullable -> true
                                    else -> null
                                },
                        )
                    }
                }
            } catch (e: SQLException) {
                throw RuntimeException("Column name discovery query failed: ${e.message}", e)
            }
        }
    }

    fun <T> swallow(supplier: () -> T): T? {
        try {
            return supplier()
        } catch (e: Exception) {
            log.debug(e) { "Metadata query triggered exception, ignoring value" }
        }
        return null
    }

    override fun streamNamespaces(): List<String> =
        memoizedTableNames.mapNotNull { "${it.catalog}.${it.schema}" }.distinct()

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
        return memoizedTableNames
            .filter { "${it.catalog}.${it.schema}" == streamNamespace }
            .map {
                StreamDescriptor().withName(it.name).withNamespace("${it.catalog}.${it.schema}")
            }
            .map(StreamIdentifier::from)
    }

    fun findTableName(
        streamID: StreamIdentifier,
    ): TableName? =
        memoizedTableNames.find {
            it.name == streamID.name && "${it.catalog}.${it.schema}" == streamID.namespace
        }

    val memoizedTableNames: List<TableName> by lazy {
        try {
            val allTables = mutableSetOf<TableName>()
            val dbmd: DatabaseMetaData = conn.metaData

            log.info { "Querying table names for Databricks source." }
            for (namespace in config.namespaces + config.namespaces.map { it.uppercase() }) {
                // Query all schemas in the current database
                dbmd.getTables(namespace, config.schema, null, arrayOf("TABLE", "VIEW")).use {
                    rs: ResultSet ->
                    while (rs.next()) {
                        val tableName =
                            TableName(
                                catalog = rs.getString("TABLE_CAT"),
                                schema = rs.getString("TABLE_SCHEM"),
                                name = rs.getString("TABLE_NAME"),
                                type = rs.getString("TABLE_TYPE") ?: "",
                            )
                        // Filter out system schemas
                        if (!EXCLUDED_NAMESPACES.contains(tableName.schema?.uppercase())) {
                            allTables.add(tableName)
                        }
                    }
                }
            }
            log.info { "Discovered ${allTables.size} tables and views." }
            return@lazy allTables.toList()
        } catch (e: Exception) {
            throw RuntimeException("Table name discovery query failed: ${e.message}", e)
        }
    }

    val memoizedPrimaryKeys: Map<TableName, List<List<String>>> by lazy {
        val joinMap: Map<TableName, TableName> =
            memoizedTableNames.associateBy { it.copy(type = "") }
        val results = mutableMapOf<TableName, MutableList<PrimaryKeyRow>>()
        log.info { "Querying primary keys for catalog discovery." }
        try {
            val dbmd: DatabaseMetaData = conn.metaData

            memoizedTableNames.forEach { table ->
                dbmd.getPrimaryKeys(table.catalog, table.schema, table.name).use { rs: ResultSet ->
                    while (rs.next()) {
                        val primaryKey =
                            PrimaryKeyRow(
                                name = rs.getString("PK_NAME"),
                                columnName = rs.getString("COLUMN_NAME"),
                                ordinal = rs.getInt("KEY_SEQ"),
                            )
                        val tableName =
                            TableName(
                                catalog = rs.getString("TABLE_CAT"),
                                schema = rs.getString("TABLE_SCHEM"),
                                name = rs.getString("TABLE_NAME"),
                                type = "",
                            )
                        val joinedTableName: TableName = joinMap[tableName] ?: return@use
                        results.getOrPut(joinedTableName) { mutableListOf() }.add(primaryKey)
                    }
                }
            }
            log.info { "Discovered ${results.size} primary keys." }
            return@lazy results.mapValues { (_, pkCols: MutableList<PrimaryKeyRow>) ->
                pkCols.sortedBy { it.ordinal }.map { listOf(it.columnName) }
            }
        } catch (e: Exception) {
            throw RuntimeException("Primary key discovery query failed: ${e.message}", e)
        }
    }

    override fun primaryKey(
        streamID: StreamIdentifier,
    ): List<List<String>> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        return memoizedPrimaryKeys[table] ?: listOf()
    }

    override fun extraChecks() {
        // No extra checks needed for Databricks
    }

    override fun close() {
        try {
            conn.close()
        } catch (e: SQLException) {
            log.warn(e) { "Error closing connection" }
        }
    }

    companion object {

        /** Databricks implementation of [MetadataQuerier.Factory]. */
        @Singleton
        @Primary
        class Factory(
            val constants: DefaultJdbcConstants,
            val selectQueryGenerator: SelectQueryGenerator,
            val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
            val checkQueries: JdbcCheckQueries,
            val connectionFactory: DatabricksSourceConnectionFactory,
        ) : MetadataQuerier.Factory<DatabricksSourceConfiguration> {
            private val log = KotlinLogging.logger {}

            override fun session(config: DatabricksSourceConfiguration): MetadataQuerier {
                log.info { "Databricks source metadata session." }
                return DatabricksSourceMetadataQuerier(
                    constants,
                    config,
                    selectQueryGenerator,
                    fieldTypeMapper,
                    checkQueries,
                    connectionFactory
                )
            }
        }

        val EXCLUDED_NAMESPACES = setOf("INFORMATION_SCHEMA", "UTIL_DB")
    }
}
