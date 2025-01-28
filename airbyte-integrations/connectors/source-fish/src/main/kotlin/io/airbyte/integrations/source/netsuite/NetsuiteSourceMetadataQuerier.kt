/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.netsuite

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
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.DatabaseMetaData
import java.sql.ResultSet

/**
 * Netsuite implementation of [MetadataQuerier].
 *
 * Netsuite is a bit different - the catalog is actually account name, while schema is the role
 * name, except for SYSTEM tables where catalog is always SCHEMA and schema is SYSTEM.
 *
 * We do not require user to provide account name or role name in the configuration, thus when
 * querying we would include all tables. And since we feed accountId and roleId in the JDBC url,
 * Netsuite should only feed us tables that are accessible to the user, thus it guarantees
 * uniqueness of the table names.
 */
class NetsuiteSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
) : MetadataQuerier by base {
    // TODO: Might need a redo on all functions below.
    private val log = KotlinLogging.logger {}

    val memoizedColumnMetadata: Map<TableName, List<ColumnMetadata>> by lazy {
        val joinMap: Map<TableName, TableName> =
            memoizedTableNames.associateBy { it.copy(type = "") }
        val results = mutableListOf<Pair<TableName, ColumnMetadata>>()
        log.info { "Querying column names for catalog discovery." }
        try {
            val dbmd: DatabaseMetaData = base.conn.metaData
            memoizedTableNames
                .map { it.catalog to it.schema }
                .distinct()
                .forEach { (catalog: String?, schema: String?) ->
                    dbmd.getColumns(catalog, schema, null, null).use { rs: ResultSet ->
                        while (rs.next()) {
                            val (tableName: TableName, metadata: ColumnMetadata) =
                                columnMetadataFromResultSet(rs)
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
                typeName = rs.getString("TYPE_NAME"),
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
                ordinal = rs.getInt("ORDINAL_POSITION"),
            )
        return tableName to metadata
    }

    override fun fields(streamID: StreamIdentifier): List<Field> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        if (table !in memoizedColumnMetadata) return listOf()
        return memoizedColumnMetadata[table]!!.map {
            Field(it.label, base.fieldTypeMapper.toFieldType(it))
        }
    }

    override fun streamNamespaces(): List<String> =
        memoizedTableNames.mapNotNull { it.catalog }.distinct()

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> =
        memoizedTableNames
            .filter { it.catalog == streamNamespace }
            .map { StreamDescriptor().withName(it.name).withNamespace(it.schema) }
            .map(StreamIdentifier::from)

    fun findTableName(
        streamID: StreamIdentifier,
    ): TableName? = memoizedTableNames.find { it.name == streamID.name }

    val memoizedTableNames: List<TableName> by lazy {
        log.info { "memoized table names." }
        try {
            val allTables = mutableSetOf<TableName>()
            val dbmd: DatabaseMetaData = base.conn.metaData

            val catalog = null
            val schema = null
            log.info { "Netsuite source metadata querying." }
            dbmd.getTables(catalog, schema, null, null).use { rs: ResultSet ->
                while (rs.next()) {
                    allTables.add(
                        TableName(
                            catalog = rs.getString("TABLE_CAT"),
                            schema = rs.getString("TABLE_SCHEM"),
                            name = rs.getString("TABLE_NAME"),
                            type = rs.getString("TABLE_TYPE") ?: "",
                        ),
                    )
                    log.info {
                        "Found table:catalog: ${rs.getString("TABLE_CAT")} ; schema: ${rs.getString("TABLE_SCHEM")}; name: ${rs.getString("TABLE_NAME")}"
                    }
                }
            }
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
            val dbmd: DatabaseMetaData = base.conn.metaData

            memoizedTableNames
                .map { it.catalog to it.schema }
                .distinct()
                .forEach { (catalog: String?, schema: String?) ->
                    dbmd.getPrimaryKeys(catalog, schema, null).use { rs: ResultSet ->
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
                            val joinedTableName: TableName = joinMap[tableName] ?: continue
                            if (
                                primaryKey.name.lowercase() ==
                                    "${joinedTableName.name}_PK".lowercase()
                            ) {
                                results
                                    .getOrPut(joinedTableName) { mutableListOf() }
                                    .add(primaryKey)
                            }
                        }
                        log.info { "Discovered ${results.size} primary keys." }
                    }
                }
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

    companion object {

        /** Netsuite implementation of [MetadataQuerier.Factory]. */
        @Singleton
        @Primary
        class Factory(
            val constants: DefaultJdbcConstants,
            val selectQueryGenerator: SelectQueryGenerator,
            val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
            val checkQueries: JdbcCheckQueries,
        ) : MetadataQuerier.Factory<NetsuiteSourceConfiguration> {
            private val log = KotlinLogging.logger {}

            override fun session(config: NetsuiteSourceConfiguration): MetadataQuerier {
                log.info { "Netsuite source metadata session." }
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
                return NetsuiteSourceMetadataQuerier(base)
            }
        }
    }
}
