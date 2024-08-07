/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.jdbc

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.FieldType
import io.airbyte.cdk.source.MetadataQuerier
import io.airbyte.cdk.source.TableName
import io.airbyte.cdk.source.select.From
import io.airbyte.cdk.source.select.Limit
import io.airbyte.cdk.source.select.SelectColumns
import io.airbyte.cdk.source.select.SelectQueryGenerator
import io.airbyte.cdk.source.select.SelectQuerySpec
import io.airbyte.cdk.source.select.optimize
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
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
    val config: JdbcSourceConfiguration,
    val selectQueryGenerator: SelectQueryGenerator,
    val fieldTypeMapper: FieldTypeMapper,
    jdbcConnectionFactory: JdbcConnectionFactory,
) : MetadataQuerier {
    val conn: Connection = jdbcConnectionFactory.get()

    private val log = KotlinLogging.logger {}

    override fun streamNamespaces(): List<String> =
        memoizedTableNames.mapNotNull { it.schema ?: it.catalog }.distinct()

    override fun streamNames(streamNamespace: String?): List<String> =
        memoizedTableNames.filter { (it.schema ?: it.catalog) == streamNamespace }.map { it.name }

    fun <T> swallow(supplier: () -> T): T? {
        try {
            return supplier()
        } catch (e: Exception) {
            log.debug(e) { "Metadata query triggered exception, ignoring value" }
        }
        return null
    }

    val memoizedTableNames: List<TableName> by lazy {
        log.info { "Querying table names for catalog discovery." }
        try {
            val allTables = mutableSetOf<TableName>()
            val dbmd: DatabaseMetaData = conn.metaData
            for (schema in config.schemas + config.schemas.map { it.uppercase() }) {
                dbmd.getTables(null, schema, null, null).use { rs: ResultSet ->
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
            log.info { "Discovered ${allTables.size} table(s) in schemas ${config.schemas}." }
            return@lazy allTables.toList().sortedBy {
                "${it.catalog ?: ""}.${it.schema!!}.${it.name}.${it.type}"
            }
        } catch (e: Exception) {
            throw RuntimeException("Table name discovery query failed: ${e.message}", e)
        }
    }

    fun findTableName(
        streamName: String,
        streamNamespace: String?,
    ): TableName? =
        memoizedTableNames.find {
            it.name == streamName && (it.schema ?: it.catalog) == streamNamespace
        }

    val memoizedColumnMetadata: Map<TableName, List<ColumnMetadata>> by lazy {
        val joinMap: Map<TableName, TableName> =
            memoizedTableNames.associateBy { it.copy(type = "") }
        val results = mutableListOf<Pair<TableName, ColumnMetadata>>()
        log.info { "Querying column names for catalog discovery." }
        try {
            val dbmd: DatabaseMetaData = conn.metaData
            memoizedTableNames
                .filter { it.catalog != null || it.schema != null }
                .map { it.catalog to it.schema }
                .distinct()
                .forEach { (catalog: String?, schema: String?) ->
                    dbmd.getPseudoColumns(catalog, schema, null, null).use { rs: ResultSet ->
                        while (rs.next()) {
                            val (tableName: TableName, metadata: ColumnMetadata) =
                                columnMetadataFromResultSet(rs, isPseudoColumn = true)
                            val joinedTableName: TableName = joinMap[tableName] ?: continue
                            results.add(joinedTableName to metadata)
                        }
                    }
                    dbmd.getColumns(catalog, schema, null, null).use { rs: ResultSet ->
                        while (rs.next()) {
                            val (tableName: TableName, metadata: ColumnMetadata) =
                                columnMetadataFromResultSet(rs, isPseudoColumn = false)
                            val joinedTableName: TableName = joinMap[tableName] ?: continue
                            results.add(joinedTableName to metadata)
                        }
                    }
                }
            log.info { "Discovered ${results.size} column(s) and pseudo-column(s)." }
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

    /**
     * [memoizedUserDefinedTypes] is not directly used by [JdbcMetadataQuerier]. Instead, it's
     * provided for use by other [MetadataQuerier] implementations which delegate to this.
     */
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
                            rs.getInt("DATA_TYPE"),
                            swallow { rs.getString("REMARKS").takeUnless { rs.wasNull() } },
                            swallow { rs.getInt("BASE_TYPE").takeUnless { rs.wasNull() } },
                        ),
                    )
                }
            }
            return@lazy results
        } catch (e: Exception) {
            throw RuntimeException("User-defined type discovery query failed: ${e.message}", e)
        }
    }

    override fun fields(
        streamName: String,
        streamNamespace: String?,
    ): List<Field> {
        val table: TableName = findTableName(streamName, streamNamespace) ?: return listOf()
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
                SelectColumns(columnIDs.map { Field(it, NullFieldType) }),
                From(table.name, table.schema ?: table.catalog),
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
                log.info {
                    "Failed to query $sql: " +
                        "sqlState = '${e.sqlState ?: ""}', errorCode = ${e.errorCode}, ${e.message}"
                }
                return null
            }
        }
    }

    val memoizedPrimaryKeys = mutableMapOf<TableName, List<List<String>>>()

    override fun primaryKeys(
        streamName: String,
        streamNamespace: String?,
    ): List<List<String>> {
        val table: TableName = findTableName(streamName, streamNamespace) ?: return listOf()
        val memoized: List<List<String>>? = memoizedPrimaryKeys[table]
        if (memoized != null) return memoized
        val results = mutableListOf<PrimaryKeyRow>()
        val streamPair = AirbyteStreamNameNamespacePair(streamName, streamNamespace)
        log.info { "Querying primary keys in '$streamPair' for catalog discovery." }
        try {
            val dbmd: DatabaseMetaData = conn.metaData
            dbmd.getPrimaryKeys(table.catalog, table.schema, table.name).use { rs: ResultSet ->
                while (rs.next()) {
                    results.add(
                        PrimaryKeyRow(
                            name = rs.getString("PK_NAME") ?: "",
                            ordinal = rs.getInt("KEY_SEQ"),
                            columnName = rs.getString("COLUMN_NAME"),
                        ),
                    )
                }
            }
            log.info { "Discovered all primary keys in '$streamPair'." }
        } catch (e: Exception) {
            throw RuntimeException("Primary key discovery query failed: ${e.message}", e)
        }
        return results
            .groupBy { it.name }
            .values
            .map { rowsByPK: List<PrimaryKeyRow> ->
                rowsByPK.sortedBy { it.ordinal }.map { it.columnName }
            }
            .also { memoizedPrimaryKeys[table] = it }
    }

    private data class PrimaryKeyRow(
        val name: String,
        val ordinal: Int,
        val columnName: String,
    )

    override fun close() {
        log.info { "Closing JDBC connection." }
        conn.close()
    }

    /** Default implementation of [MetadataQuerier.Factory]. */
    @Singleton
    class Factory(
        val selectQueryGenerator: SelectQueryGenerator,
        val fieldTypeMapper: FieldTypeMapper,
    ) : MetadataQuerier.Factory<JdbcSourceConfiguration> {
        /** The [JdbcSourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: JdbcSourceConfiguration): MetadataQuerier {
            val jdbcConnectionFactory = JdbcConnectionFactory(config)
            return JdbcMetadataQuerier(
                config,
                selectQueryGenerator,
                fieldTypeMapper,
                jdbcConnectionFactory,
            )
        }
    }

    /**
     * Stateless connector-specific object for mapping a [ColumnMetadata] to a [FieldType] during
     * DISCOVER.
     *
     * This interface is used by [JdbcMetadataQuerier] to discover the [FieldType]s for all columns
     * in a table, based on the [ColumnMetadata] that it collects. The mapping of the latter to the
     * former is many-to-one.
     */
    fun interface FieldTypeMapper {
        fun toFieldType(c: ColumnMetadata): FieldType
    }

    data class ColumnMetadata(
        val name: String,
        val label: String,
        val type: SourceDatabaseType,
        val nullable: Boolean? = null,
        val ordinal: Int? = null,
    )
}
