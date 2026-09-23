/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.JdbcMetadataQuerier.ColumnMetadata
import io.airbyte.cdk.discover.JdbcMetadataQuerier.PrimaryKeyRow
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.DefaultJdbcConstants.NamespaceKind
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.NullFieldType
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.optimize
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Value
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
 * Snowflake implementation of [MetadataQuerier].
 *
 * Snowflake uses a standard three-level namespace: catalog.schema.table where catalog is the
 * database name, schema is the schema name.
 */
class SnowflakeSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
    val schema: String? = null,
    /**
     * When true (DISCOVER only), a column probe that fails with a known object-level error (e.g. an
     * invalid view) yields an empty column list so the stream is skipped, instead of failing the
     * whole operation. Must stay false for CHECK and READ: CHECK relies on a throwing [fields] to
     * detect roles that cannot SELECT anything, and READ must fail loudly on a broken selected
     * stream.
     */
    val tolerateObjectLevelFailures: Boolean = false,
) : MetadataQuerier by base {
    private val log = KotlinLogging.logger {}

    fun TableName.namespace(): String? =
        when (base.constants.namespaceKind) {
            NamespaceKind.CATALOG_AND_SCHEMA -> schema
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
    ): List<EmittedField> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        return columnMetadata(table).map {
            EmittedField(it.label, base.fieldTypeMapper.toFieldType(it))
        }
    }

    fun columnMetadata(table: TableName): List<ColumnMetadata> {
        val columnMetadata: List<ColumnMetadata> = memoizedColumnMetadata[table] ?: listOf()
        if (columnMetadata.isEmpty() || !base.config.checkPrivileges) {
            return columnMetadata
        }
        var wholeObjectFailure = false
        val resultsFromSelectMany: List<ColumnMetadata>? =
            queryColumnMetadata(base.conn, selectLimit0(table, columnMetadata.map { it.name })) {
                e: SQLException ->
                wholeObjectFailure = isWholeObjectFailure(e)
            }
        if (resultsFromSelectMany != null) {
            return resultsFromSelectMany
        }
        if (wholeObjectFailure) {
            // The object itself is broken or missing (e.g. an invalid view whose definition no
            // longer compiles): every per-column probe would fail identically, so don't issue
            // them.
            return listOf()
        }
        log.info {
            "Not all columns of $table might be accessible, trying each column individually."
        }
        return columnMetadata.flatMap {
            queryColumnMetadata(base.conn, selectLimit0(table, listOf(it.name))) ?: listOf()
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
                SelectColumns(columnIDs.map { EmittedField(it, NullFieldType) }),
                From(table.name, table.namespace()),
                limit = Limit(0),
            )
        return base.selectQueryGenerator.generate(querySpec.optimize()).sql
    }

    private fun queryColumnMetadata(
        conn: Connection,
        sql: String,
        onToleratedFailure: (SQLException) -> Unit = {},
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
                // During DISCOVER, a column probe that fails for a known OBJECT-LEVEL reason must
                // not fail the whole operation. Returning null re-enables the tolerance machinery
                // in columnMetadata() (all-columns probe -> per-column probe -> empty fields) so a
                // single broken/inaccessible view (declared columns no longer match its query
                // body, or a view the role cannot SELECT) is skipped while the rest of the catalog
                // is still discovered.
                //
                // Tolerance is an ALLOWLIST: only failures positively identified as object-level
                // (compile errors, missing/unauthorized objects) are tolerated. Anything else —
                // network failures (driver SQLSTATE 58030), expired auth/session tokens (driver
                // reauth codes such as 390114, often SQLSTATE XX000), no-active-warehouse (401 /
                // 57P03), timeouts, and unknown unknowns — re-throws, because those affect every
                // stream and tolerating them would silently truncate or empty the catalog.
                //
                // Tolerance is also gated to the discover operation: CHECK relies on a throwing
                // fields() to detect roles that cannot SELECT any table, and READ must fail
                // loudly on a broken selected stream.
                if (!tolerateObjectLevelFailures || !isTolerableObjectError(e)) {
                    throw RuntimeException("Column name discovery query failed: ${e.message}", e)
                }
                log.warn(e) {
                    "Object-level failure during discover; this stream will be skipped and " +
                        "omitted from the catalog. Failed query: $sql, " +
                        "sqlState = '${e.sqlState ?: ""}', errorCode = ${e.errorCode}, ${e.message}"
                }
                onToleratedFailure(e)
                return null
            }
        }
    }

    /**
     * Returns true only when [e] is positively identified as an OBJECT-LEVEL failure of the probed
     * table/view — a definition that no longer compiles (SQLSTATE class '42', e.g. 42601), or an
     * object that does not exist / is not authorized (SQLSTATE class '02' or vendor codes
     * 2003/2043, per this connector's classifier in application.yml). Only these are safe to
     * tolerate during discover by skipping the stream.
     *
     * Everything else is treated as fatal, INCLUDING unrecognized errors: infrastructure failures
     * affect every stream, and the safe default for an unknown error is a loud failure, never a
     * silently truncated catalog.
     */
    fun isTolerableObjectError(e: SQLException): Boolean {
        if (e.errorCode in TOLERABLE_OBJECT_ERROR_CODES) {
            return true
        }
        val sqlStateClass: String = e.sqlState?.take(2) ?: return false
        return sqlStateClass in TOLERABLE_OBJECT_SQLSTATE_CLASSES
    }

    /**
     * Returns true when a tolerated probe failure condemns the WHOLE object — its definition does
     * not compile (SQLSTATE 42601, e.g. vendor code 2057 "view declared N columns but query
     * produces M") or it does not exist / is not authorized (2003/2043). Every per-column probe
     * would fail identically, so [columnMetadata] skips them. Other tolerated failures (e.g.
     * column-scoped access policies) still fall through to per-column probing.
     */
    fun isWholeObjectFailure(e: SQLException): Boolean =
        e.sqlState == "42601" || e.errorCode in TOLERABLE_OBJECT_ERROR_CODES

    fun <T> swallow(supplier: () -> T): T? {
        try {
            return supplier()
        } catch (e: Exception) {
            log.debug(e) { "Metadata query triggered exception, ignoring value" }
        }
        return null
    }

    override fun streamNamespaces(): List<String> =
        memoizedTableNames.mapNotNull { it.schema }.distinct()

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> {
        return memoizedTableNames
            .filter { it.schema == streamNamespace }
            .map { StreamDescriptor().withName(it.name).withNamespace(it.schema) }
            .map(StreamIdentifier::from)
    }

    fun findTableName(
        streamID: StreamIdentifier,
    ): TableName? =
        memoizedTableNames.find { it.name == streamID.name && it.schema == streamID.namespace }

    val memoizedTableNames: List<TableName> by lazy {
        try {
            val allTables = mutableSetOf<TableName>()
            val dbmd: DatabaseMetaData = base.conn.metaData

            log.info { "Querying table names for Snowflake source." }
            for (namespace in
                base.config.namespaces + base.config.namespaces.map { it.uppercase() }) {
                // Query all schemas in the current database
                dbmd.getTables(namespace, schema, null, arrayOf("TABLE", "VIEW")).use {
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

    companion object {

        /** Snowflake implementation of [MetadataQuerier.Factory]. */
        @Singleton
        @Primary
        class Factory(
            val constants: DefaultJdbcConstants,
            val selectQueryGenerator: SelectQueryGenerator,
            val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
            val checkQueries: JdbcCheckQueries,
            // The CDK selects the running operation via this property (Operation.PROPERTY);
            // object-level tolerance must apply to discover only.
            @Value("\${airbyte.connector.operation:}") val operationName: String,
        ) : MetadataQuerier.Factory<SnowflakeSourceConfiguration> {
            private val log = KotlinLogging.logger {}

            override fun session(config: SnowflakeSourceConfiguration): MetadataQuerier {
                log.info { "Snowflake source metadata session." }
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
                return SnowflakeSourceMetadataQuerier(
                    base,
                    config.schema,
                    tolerateObjectLevelFailures = operationName == "discover",
                )
            }
        }

        val EXCLUDED_NAMESPACES = setOf("INFORMATION_SCHEMA", "SNOWFLAKE_SAMPLE_DATA", "UTIL_DB")

        /**
         * Snowflake vendor error codes positively identifying an OBJECT-LEVEL failure of the probed
         * table/view: 2003 / 2043 "object does not exist or not authorized" (the same codes this
         * connector's classifier in application.yml maps to a config error) and 2057 "view declared
         * N column(s), but view query produces M column(s)". Used as a belt-and-braces complement
         * to [TOLERABLE_OBJECT_SQLSTATE_CLASSES] for exceptions with no SQLSTATE.
         */
        val TOLERABLE_OBJECT_ERROR_CODES = setOf(2003, 2043, 2057)

        /**
         * SQLSTATE classes (first two chars) positively identifying an object-level failure: '42' =
         * syntax error or access rule violation (view compile errors such as 42601, access denials
         * such as 42501), '02' = no data (Snowflake's "object does not exist or not authorized").
         * Anything outside this allowlist — connection ('08'), driver network ('58'), operator
         * intervention ('57'), driver/internal ('XX'), and unknowns — is treated as fatal.
         */
        val TOLERABLE_OBJECT_SQLSTATE_CLASSES = setOf("42", "02")
    }
}
