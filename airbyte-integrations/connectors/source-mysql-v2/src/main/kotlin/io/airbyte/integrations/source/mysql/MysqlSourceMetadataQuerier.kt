/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.JdbcMetadataQuerier.ColumnMetadata
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.discover.UserDefinedType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import java.sql.Statement

private val log = KotlinLogging.logger {}

/** Delegates to [JdbcMetadataQuerier] except for [fields]. */
class MysqlSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
) : MetadataQuerier by base {

    override fun fields(
        streamName: String,
        streamNamespace: String?,
    ): List<Field> {
        val table: TableName = findTableName(streamName, streamNamespace) ?: return listOf()
        if (table !in memoizedColumnMetadata) return listOf()
        return memoizedColumnMetadata[table]!!
            .map { c: JdbcMetadataQuerier.ColumnMetadata ->
                val udt: UserDefinedType? =
                    when (c.type) {
                        is SystemType -> allUDTsByFQName[c.type.typeName]
                        else -> null
                    }
                c.copy(type = udt ?: c.type)
            }
            .map { Field(it.label, base.fieldTypeMapper.toFieldType(it)) }
    }

    val memoizedColumnMetadata: Map<TableName, List<ColumnMetadata>> by lazy {
        val joinMap: Map<TableName, TableName> =
            memoizedTableNames.associateBy { it.copy(type = "") }
        val results = mutableListOf<Pair<TableName, ColumnMetadata>>()
        log.info { "Querying column names for catalog discovery." }
        try {
            val dbmd: DatabaseMetaData = base.conn.metaData
            memoizedTableNames
                .filter { it.catalog != null || it.schema != null }
                .map { it.catalog to it.schema }
                .distinct()
                .forEach { (catalog: String?, schema: String?) ->
                    dbmd.getPseudoColumns(catalog, schema, null, null).use { rs: ResultSet ->
                        while (rs.next()) {
                            val (
                                tableName: io.airbyte.cdk.discover.TableName,
                                metadata: io.airbyte.cdk.discover.JdbcMetadataQuerier.ColumnMetadata
                            ) =
                                columnMetadataFromResultSet(rs, isPseudoColumn = true)
                            val joinedTableName: TableName = joinMap[tableName] ?: continue
                            results.add(joinedTableName to metadata)
                        }
                    }
                    dbmd.getColumns(catalog, schema, null, null).use { rs: ResultSet ->
                        while (rs.next()) {
                            val (
                                tableName: io.airbyte.cdk.discover.TableName,
                                metadata: io.airbyte.cdk.discover.JdbcMetadataQuerier.ColumnMetadata
                            ) =
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

    val allUDTsByFQName: Map<String, UserDefinedType> by lazy {
        val otherUDTs: List<UserDefinedType> = base.memoizedUserDefinedTypes
        val allUDTs: List<UserDefinedType> = otherUDTs
        allUDTs.reversed().associateBy { "${it.schema}.${it.typeName}" }
    }

    override fun streamNamespaces(): List<String> = base.config.schemas.toList()

    val memoizedTableNames: List<TableName> by lazy {
        log.info { "Querying table names for catalog discovery." }
        try {
            val allTables = mutableSetOf<TableName>()
            val dbmd: DatabaseMetaData = base.conn.metaData
            for (schema in base.config.schemas + base.config.schemas.map { it.uppercase() }) {
                dbmd.getTables(schema, schema, null, null).use { rs: ResultSet ->
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
            log.info { "Discovered ${allTables.size} table(s) in schemas ${base.config.schemas}." }
            return@lazy allTables.toList().sortedBy {
                "${it.catalog ?: ""}.${it.schema}.${it.name}.${it.type}"
            }
        } catch (e: Exception) {
            throw RuntimeException("Table name discovery query failed: ${e.message}", e)
        }
    }

    override fun streamNames(streamNamespace: String?): List<String> =
        memoizedTableNames.filter { (it.schema ?: it.catalog) == streamNamespace }.map { it.name }

    fun findTableName(
        streamName: String,
        streamNamespace: String?,
    ): TableName? =
        memoizedTableNames.find {
            it.name == streamName && (it.schema ?: it.catalog) == streamNamespace
        }

    val memoizedPrimaryKeys: Map<TableName, List<List<String>>> by lazy {
        val results = mutableListOf<AllPrimaryKeysRow>()
        val schemas: List<String> = streamNamespaces()
        val sql: String = PK_QUERY_FMTSTR.format(schemas.joinToString { "\'$it\'" })
        log.info { "Querying Mysql system tables for all primary keys for catalog discovery." }
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
            log.info { "Discovered all primary keys in ${schemas.size} Mysql schema(s)." }
            return@lazy results
                .groupBy { findTableName(it.tableName, "public") }
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
            throw RuntimeException("Mysql primary key discovery query failed: ${e.message}", e)
        }
    }

    override fun primaryKey(
        streamName: String,
        streamNamespace: String?,
    ): List<List<String>> {
        val table: TableName = findTableName(streamName, streamNamespace) ?: return listOf()
        return memoizedPrimaryKeys[table] ?: listOf()
    }

    private data class AllPrimaryKeysRow(
        val tableSchema: String,
        val tableName: String,
        val constraintName: String,
        val position: Int?,
        val columnName: String?,
    )

    companion object {

        const val PK_QUERY_FMTSTR =
            """
   SELECT 
            table_schema,
            table_name, 
            column_name, 
            ordinal_position, 
            constraint_name 
        FROM 
            information_schema.key_column_usage 
        WHERE 
            table_schema IN (%s)
            AND constraint_name = 'PRIMARY';
            """
    }

    /** Mysql implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory(
        val selectQueryGenerator: SelectQueryGenerator,
        val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
    ) : MetadataQuerier.Factory<MysqlSourceConfiguration> {
        /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: MysqlSourceConfiguration): MetadataQuerier {
            val jdbcConnectionFactory = JdbcConnectionFactory(config)
            val base =
                JdbcMetadataQuerier(
                    config,
                    selectQueryGenerator,
                    fieldTypeMapper,
                    jdbcConnectionFactory,
                )
            return MysqlSourceMetadataQuerier(base)
        }
    }
}
