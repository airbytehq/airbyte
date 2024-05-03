/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.jdbc

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.DiscoverMapper
import io.airbyte.cdk.discover.GenericUserDefinedType
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.discover.UserDefinedType
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import java.sql.ResultSetMetaData
import java.sql.SQLException
import java.sql.Statement

/** Default implementation of [MetadataQuerier]. */
class JdbcMetadataQuerier(
    val config: SourceConfiguration,
    val discoverMapper: DiscoverMapper,
    jdbcConnectionFactory: JdbcConnectionFactory
) : MetadataQuerier {

    val conn: Connection = jdbcConnectionFactory.get()

    private val log = KotlinLogging.logger {}

    override fun tableNames(): List<TableName> = memoizedColumnNames.keys.toList()

    private fun <T> swallow(supplier: () -> T): T? {
        try {
            return supplier()
        } catch (e: Exception) {
            log.debug(e) { "Metadata query triggered exception, ignoring value" }
        }
        return null
    }

    val memoizedTableNames: List<TableName> by lazy {
        log.info { "Querying table names for catalog discovery." }
        val schemaSet: Set<String> = config.schemas.map { it.uppercase() }.toSet()
        try {
            val allTables = mutableListOf<TableName>()
            val dbmd: DatabaseMetaData = conn.metaData
            dbmd.getTables(null, null, null, null).use { rs: ResultSet ->
                while (rs.next()) {
                    allTables.add(
                        TableName(
                            catalog = rs.getString("TABLE_CAT"),
                            schema = rs.getString("TABLE_SCHEM"),
                            name = rs.getString("TABLE_NAME"),
                            type = rs.getString("TABLE_TYPE") ?: ""
                        )
                    )
                }
            }
            log.info { "Discovered ${allTables.size} table(s)." }
            if (allTables.isEmpty()) {
                return@lazy listOf()
            }
            return@lazy allTables
                .filter { schemaSet.contains(it.schema?.uppercase()) }
                .sortedBy { "${it.catalog ?: ""}.${it.schema!!}.${it.name}.${it.type}" }
                .also {
                    log.info { "Discovered ${it.size} table(s) in schemas ${config.schemas}." }
                }
        } catch (e: Exception) {
            throw RuntimeException("Table name discovery query failed: ${e.message}", e)
        }
    }

    val memoizedColumnNames: Map<TableName, List<String>> by lazy {
        val joinMap: Map<TableName, TableName> =
            memoizedTableNames.associateBy { it.copy(type = "") }
        val results = mutableListOf<Pair<TableName, String>>()
        log.info { "Querying column names for catalog discovery." }
        try {
            val dbmd: DatabaseMetaData = conn.metaData
            dbmd.getColumns(null, null, null, null).use { rs: ResultSet ->
                while (rs.next()) {
                    val tableName: TableName =
                        joinMap[
                            TableName(
                                catalog = rs.getString("TABLE_CAT"),
                                schema = rs.getString("TABLE_SCHEM"),
                                name = rs.getString("TABLE_NAME"),
                                type = ""
                            )
                        ]
                            ?: continue
                    results.add(tableName to rs.getString("COLUMN_NAME"))
                }
            }
            log.info { "Discovered ${results.size} column(s)." }
            return@lazy results.groupBy({ it.first }, { it.second })
        } catch (e: Exception) {
            throw RuntimeException("Column name discovery query failed: ${e.message}", e)
        }
    }

    val memoizedUserDefinedTypes: List<UserDefinedType> by lazy {
        log.info { "Querying user-defined types for catalog discovery." }
        try {
            val results = mutableListOf<UserDefinedType>()
            val dbmd: DatabaseMetaData = conn.metaData
            dbmd.getUDTs(null, null, null, null).use { rs: ResultSet ->
                while (rs.next()) {
                    results.add(
                        GenericUserDefinedType(
                            rs.getString("TYPE_CAT").takeUnless { rs.wasNull() },
                            rs.getString("TYPE_SCHEM").takeUnless { rs.wasNull() },
                            rs.getString("TYPE_NAME")!!,
                            swallow { rs.getString("CLASS_NAME")?.let { Class.forName(it) } },
                            rs.getInt("DATA_TYPE"),
                            swallow { rs.getString("REMARKS").takeUnless { rs.wasNull() } },
                            swallow { rs.getInt("BASE_TYPE").takeUnless { rs.wasNull() } },
                        )
                    )
                }
            }
            return@lazy results
        } catch (e: Exception) {
            throw RuntimeException("User-defined type discovery query failed: ${e.message}", e)
        }
    }

    override fun columnMetadata(table: TableName): List<ColumnMetadata> {
        val columnNames: List<String> = memoizedColumnNames[table] ?: listOf()
        if (columnNames.isEmpty()) {
            return listOf()
        }
        val resultsFromSelectMany: List<ColumnMetadata>? =
            queryColumnMetadata(conn, discoverMapper.selectFromTableLimit0(table, columnNames))
        if (resultsFromSelectMany != null) {
            return resultsFromSelectMany
        }
        log.info {
            "Not all columns of $table might be accessible, trying each column individually."
        }
        return columnNames.flatMap {
            val sql: String = discoverMapper.selectFromTableLimit0(table, listOf(it))
            queryColumnMetadata(conn, sql) ?: listOf()
        }
    }

    private fun queryColumnMetadata(conn: Connection, sql: String): List<ColumnMetadata>? {
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
                                klazz =
                                    swallow {
                                        meta.getColumnClassName(it)?.let { Class.forName(it) }
                                    },
                            )
                        ColumnMetadata(
                            name = meta.getColumnName(it),
                            label = meta.getColumnLabel(it),
                            type = type,
                            autoIncrement = swallow { meta.isAutoIncrement(it) },
                            caseSensitive = swallow { meta.isCaseSensitive(it) },
                            searchable = swallow { meta.isSearchable(it) },
                            currency = swallow { meta.isCurrency(it) },
                            nullable =
                                when (swallow { meta.isNullable(it) }) {
                                    ResultSetMetaData.columnNoNulls -> false
                                    ResultSetMetaData.columnNullable -> true
                                    else -> null
                                },
                            signed = swallow { meta.isSigned(it) },
                            displaySize = swallow { meta.getColumnDisplaySize(it) },
                            precision = swallow { meta.getPrecision(it) },
                            scale = swallow { meta.getScale(it) },
                        )
                    }
                }
            } catch (e: SQLException) {
                log.info {
                    "Failed to query $sql: " +
                        "sqlState = '${e.sqlState ?: ""}', errorCode = ${e.errorCode}, ${e.message}"
                }
                return null
            }
        }
    }

    val memoizedPrimaryKeys: Map<TableName, List<List<String>>> by lazy {
        val results = mutableListOf<PrimaryKeyRow>()
        val tables: List<TableName> = tableNames()
        log.info { "Querying primary keys for catalog discovery." }
        try {
            val dbmd: DatabaseMetaData = conn.metaData
            for (table in tables) {
                dbmd.getPrimaryKeys(table.catalog, table.schema, table.name).use { rs: ResultSet ->
                    while (rs.next()) {
                        results.add(
                            PrimaryKeyRow(
                                table = table,
                                name = rs.getString("PK_NAME") ?: "",
                                ordinal = rs.getInt("KEY_SEQ"),
                                columnName = rs.getString("COLUMN_NAME")
                            )
                        )
                    }
                }
            }
            log.info { "Discovered all primary keys in ${tables.size} table(s)." }
            return@lazy results
                .groupBy { it.table }
                .mapValues { (_, rowsByTable: List<PrimaryKeyRow>) ->
                    rowsByTable
                        .groupBy { it.name }
                        .values
                        .map { rowsByPK: List<PrimaryKeyRow> ->
                            rowsByPK.sortedBy { it.ordinal }.map { it.columnName }
                        }
                }
        } catch (e: Exception) {
            throw RuntimeException("Primary key discovery query failed: ${e.message}", e)
        }
    }

    override fun primaryKeys(table: TableName): List<List<String>> =
        memoizedPrimaryKeys[table] ?: listOf()

    private data class PrimaryKeyRow(
        val table: TableName,
        val name: String,
        val ordinal: Int,
        val columnName: String
    )

    override fun close() {
        log.info { "Closing JDBC connection." }
        conn.close()
    }

    /** Default implementation of [MetadataQuerier.Factory]. */
    @Singleton
    class Factory(override val discoverMapper: DiscoverMapper) : MetadataQuerier.Factory {

        /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: SourceConfiguration): MetadataQuerier {
            val jdbcConnectionFactory = JdbcConnectionFactory(config)
            return JdbcMetadataQuerier(config, discoverMapper, jdbcConnectionFactory)
        }
    }
}
