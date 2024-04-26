/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.jdbc

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.DiscoverMapper
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.JDBCType
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

    override fun tableNames(): List<TableName> {
        log.info { "Querying table names for catalog discovery." }
        try {
            val results = mutableListOf<TableName>()
            for (schema in config.schemas) {
                val rs: ResultSet = conn.metaData.getTables(null, schema, null, null)
                while (rs.next()) {
                    val tableName =
                        TableName(
                            catalog = rs.getString("TABLE_CAT"),
                            schema = rs.getString("TABLE_SCHEM"),
                            name = rs.getString("TABLE_NAME"),
                            type = rs.getString("TABLE_TYPE") ?: "",
                        )
                    results.add(tableName)
                }
            }
            log.info { "Discovered ${results.size} table(s)." }
            return results.sortedBy {
                "${it.catalog ?: ""}.${it.schema ?: ""}.${it.name}.${it.type}"
            }
        } catch (e: Exception) {
            throw RuntimeException("Table name discovery query failed: ${e.message}", e)
        }
    }

    override fun columnMetadata(table: TableName): List<ColumnMetadata> {
        val sql: String = discoverMapper.selectStarFromTableLimit0(table)
        log.info { "Querying $sql for catalog discovery." }
        try {
            table.catalog?.let { conn.catalog = it }
            table.schema?.let { conn.schema = it }
            conn.createStatement().use { stmt: Statement ->
                stmt.fetchSize = 1
                val meta: ResultSetMetaData = stmt.executeQuery(sql).metaData
                log.info { "Discovered ${meta.columnCount} columns in $table." }
                return (1..meta.columnCount).map {
                    ColumnMetadata(
                        name = meta.getColumnName(it),
                        label = meta.getColumnLabel(it),
                        type = swallow { meta.getColumnType(it) }?.let { JDBCType.valueOf(it) },
                        typeName = swallow { meta.getColumnTypeName(it) },
                        klazz = swallow { meta.getColumnClassName(it) }?.let { Class.forName(it) },
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
            throw RuntimeException("Column metadata query failed with exception.", e)
        }
    }

    private fun <T> swallow(supplier: () -> T): T? {
        try {
            return supplier()
        } catch (e: SQLException) {
            log.debug(e) { "Metadata query triggered exception, ignoring value" }
        }
        return null
    }

    override fun primaryKeys(table: TableName): List<List<String>> {
        log.info { "Querying primary key metadata for $table for catalog discovery." }
        val pksMap = mutableMapOf<String?, MutableMap<Int, String>>()
        try {
            val rs: ResultSet =
                conn.metaData.getPrimaryKeys(table.catalog, table.schema, table.name)
            while (rs.next()) {
                val pkName: String = rs.getString("PK_NAME") ?: ""
                val pkMap: MutableMap<Int, String> = pksMap.getOrDefault(pkName, mutableMapOf())
                val pkOrdinal: Int = rs.getInt("KEY_SEQ")
                val pkCol: String = rs.getString("COLUMN_NAME")
                pkMap[pkOrdinal] = pkCol
                pksMap[pkName] = pkMap
            }
        } catch (e: SQLException) {
            throw RuntimeException("Primary key metadata query failed with exception.", e)
        }
        log.info { "Found ${pksMap.size} primary key(s) in $table." }
        return pksMap.toSortedMap(Comparator.naturalOrder<String>()).values.map {
            it.toSortedMap().values.toList()
        }
    }

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
