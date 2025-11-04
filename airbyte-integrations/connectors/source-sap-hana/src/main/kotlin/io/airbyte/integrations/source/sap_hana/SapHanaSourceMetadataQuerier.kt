/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.*
import io.airbyte.cdk.discover.JdbcMetadataQuerier.ColumnMetadata
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.DefaultJdbcConstants.NamespaceKind
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.DatabaseMetaData
import java.sql.ResultSet
import java.sql.Statement
import kotlin.use

private val log = KotlinLogging.logger {}

/**
 * Delegates to [JdbcMetadataQuerier] except for table and column discovery methods.
 *
 * Overrides [streamNamespaces], [streamNames], [fields], and [primaryKey] to use filtered table
 * discovery, preventing the base class from querying all tables in the schema. This is critical for
 * performance when table filters are configured.
 */
class SapHanaSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
    config: SapHanaSourceConfiguration
) : MetadataQuerier by base {

    override fun streamNamespaces(): List<String> =
        memoizedTableNames.mapNotNull { it.namespace() }.distinct()

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> =
        memoizedTableNames
            .filter { it.namespace() == streamNamespace }
            .map { StreamDescriptor().withName(it.name).withNamespace(it.namespace()) }
            .map(StreamIdentifier::from)

    override fun fields(streamID: StreamIdentifier): List<Field> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        if (table !in memoizedColumnMetadata) return listOf()
        return memoizedColumnMetadata[table]!!.map {
            Field(it.label, base.fieldTypeMapper.toFieldType(it))
        }
    }

    fun TableName.namespace(): String? =
        when (base.constants.namespaceKind) {
            NamespaceKind.CATALOG_AND_SCHEMA,
            NamespaceKind.CATALOG -> catalog
            NamespaceKind.SCHEMA -> schema
        }

    val memoizedColumnMetadata: Map<TableName, List<ColumnMetadata>> by lazy {
        val joinMap: Map<TableName, TableName> =
            memoizedTableNames.associateBy { it.copy(type = "") }
        val results = mutableListOf<Pair<TableName, ColumnMetadata>>()
        log.info { "Querying column names for catalog discovery." }
        try {
            val dbmd: DatabaseMetaData = base.conn.metaData

            fun addColumnsFromQuery(
                catalog: String?,
                schema: String?,
                tablePattern: String?,
                isPseudoColumn: Boolean
            ) {
                val rsMethod = if (isPseudoColumn) dbmd::getPseudoColumns else dbmd::getColumns
                rsMethod(catalog, schema, tablePattern, null).use { rs: ResultSet ->
                    while (rs.next()) {
                        val (tableName: TableName, metadata: ColumnMetadata) =
                            columnMetadataFromResultSet(rs, isPseudoColumn)
                        val joinedTableName: TableName = joinMap[tableName] ?: continue
                        results.add(joinedTableName to metadata)
                    }
                }
            }

            // Query columns using the same pattern as table discovery:
            // - If schema has filters, query per filter pattern
            // - If no filters, query entire schema at once
            for (namespace in base.config.namespaces) {
                val (catalog: String?, schema: String?) =
                    when (base.constants.namespaceKind) {
                        NamespaceKind.CATALOG -> namespace to null
                        NamespaceKind.SCHEMA -> null to namespace
                        NamespaceKind.CATALOG_AND_SCHEMA -> namespace to namespace
                    }

                val patterns = tableFiltersBySchema[namespace]
                if (patterns != null && patterns.isNotEmpty()) {
                    for (pattern in patterns) {
                        addColumnsFromQuery(catalog, schema, pattern, isPseudoColumn = true)
                        addColumnsFromQuery(catalog, schema, pattern, isPseudoColumn = false)
                    }
                } else {
                    addColumnsFromQuery(catalog, schema, null, isPseudoColumn = true)
                    addColumnsFromQuery(catalog, schema, null, isPseudoColumn = false)
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

    val tableFiltersBySchema: Map<String, List<String>> =
        config.filters
            .groupBy { it.schemaName }
            .mapValues { (_, filters) -> filters.flatMap { it.patterns } }

    val memoizedTableNames: List<TableName> by lazy {
        log.info { "Querying table names for catalog discovery." }
        try {
            val allTables = mutableSetOf<TableName>()
            val dbmd: DatabaseMetaData = base.conn.metaData

            fun addTablesFromQuery(catalog: String?, schema: String?, pattern: String?) {
                dbmd.getTables(catalog, schema, pattern, null).use { rs: ResultSet ->
                    while (rs.next()) {
                        allTables.add(
                            TableName(
                                catalog = rs.getString("TABLE_CAT"),
                                schema = rs.getString("TABLE_SCHEM"),
                                name = rs.getString("TABLE_NAME"),
                                type = rs.getString("TABLE_TYPE") ?: "",
                            )
                        )
                    }
                }
            }

            for (namespace in base.config.namespaces) {
                val (catalog: String?, schema: String?) =
                    when (base.constants.namespaceKind) {
                        NamespaceKind.CATALOG -> namespace to null
                        NamespaceKind.SCHEMA -> null to namespace
                        NamespaceKind.CATALOG_AND_SCHEMA -> namespace to namespace
                    }

                val patterns = tableFiltersBySchema[namespace]
                if (patterns != null && patterns.isNotEmpty()) {
                    for (pattern in patterns) {
                        addTablesFromQuery(catalog, schema, pattern)
                    }
                } else {
                    addTablesFromQuery(catalog, schema, null)
                }
            }
            log.info {
                "Discovered ${allTables.size} table(s) in namespaces ${base.config.namespaces}."
            }
            return@lazy allTables.toList().sortedBy { "${it.namespace()}.${it.name}.${it.type}" }
        } catch (e: Exception) {
            throw RuntimeException("Table name discovery query failed: ${e.message}", e)
        }
    }

    fun findTableName(
        streamID: StreamIdentifier,
    ): TableName? =
        memoizedTableNames.find { it.name == streamID.name && it.namespace() == streamID.namespace }

    val memoizedPrimaryKeys: Map<TableName, List<List<String>>> by lazy {
        val results = mutableListOf<AllPrimaryKeysRow>()
        val schemas: List<String> = streamNamespaces()
        val sql: String = PK_QUERY_FMTSTR.format(schemas.joinToString { "\'$it\'" })
        log.info { "Querying SAP HANA system tables for all primary keys for catalog discovery." }
        try {
            base.conn.createStatement().use { stmt: Statement ->
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    while (rs.next()) {
                        results.add(
                            AllPrimaryKeysRow(
                                rs.getString("SCHEMA_NAME"),
                                rs.getString("TABLE_NAME"),
                                rs.getString("CONSTRAINT_NAME"),
                                rs.getInt("POSITION").takeUnless { rs.wasNull() },
                                rs.getString("COLUMN_NAME").takeUnless { rs.wasNull() },
                            ),
                        )
                    }
                }
            }
            log.info { "Discovered all primary keys in ${schemas.size} schema(s)." }
            return@lazy results
                .groupBy {
                    val desc =
                        StreamDescriptor().withName(it.tableName).withNamespace(it.schemaName)
                    findTableName(StreamIdentifier.from(desc))
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
            throw RuntimeException("Primary key discovery query failed: ${e.message}", e)
        }
    }

    override fun primaryKey(
        streamID: StreamIdentifier,
    ): List<List<String>> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        return memoizedPrimaryKeys[table] ?: listOf()
    }

    private data class AllPrimaryKeysRow(
        val schemaName: String,
        val tableName: String,
        val constraintName: String,
        val position: Int?,
        val columnName: String?,
    )

    companion object {

        const val PK_QUERY_FMTSTR =
            """
SELECT 
    SCHEMA_NAME,
    TABLE_NAME,
    CONSTRAINT_NAME,
    POSITION,
    COLUMN_NAME
FROM CONSTRAINTS
WHERE IS_PRIMARY_KEY = 'TRUE'
AND SCHEMA_NAME IN (%s);
            """
    }

    /** Sap Hana implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory(
        val constants: DefaultJdbcConstants,
        val selectQueryGenerator: SelectQueryGenerator,
        val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
        val checkQueries: JdbcCheckQueries,
    ) : MetadataQuerier.Factory<SapHanaSourceConfiguration> {
        /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: SapHanaSourceConfiguration): MetadataQuerier {
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
            return SapHanaSourceMetadataQuerier(base, config)
        }
    }
}
