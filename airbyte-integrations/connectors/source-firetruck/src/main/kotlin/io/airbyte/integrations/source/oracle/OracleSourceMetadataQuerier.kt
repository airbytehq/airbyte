/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.GenericUserDefinedType
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.SourceDatabaseType
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.discover.UserDefinedArray
import io.airbyte.cdk.discover.UserDefinedType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement
import java.sql.Types

private val log = KotlinLogging.logger {}

/**
 * Delegates to [JdbcMetadataQuerier] except for [fields].
 *
 * Oracle is annoying when it comes to array types. All array types are user-defined VARRAYS. These
 * do NOT show up in a [java.sql.DatabaseMetaData.getUDTs] query. We therefore need to query
 * Oracle's system tables like ALL_COLL_TYPES to retrieve type info. Furthermore, other user-defined
 * object types also need to be handled somewhat properly: even though we're going to map them to
 * some generic type like STRING or JSONB we still need to deal with arrays of UDTs.
 *
 * We cache the results of these UDT-related queries as they are not column-specific.
 */
class OracleSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
) : MetadataQuerier by base {
    override fun fields(
        streamName: String,
        streamNamespace: String?,
    ): List<Field> {
        val table: TableName = base.findTableName(streamName, streamNamespace) ?: return listOf()
        return base
            .columnMetadata(table)
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

    val allUDTsByFQName: Map<String, UserDefinedType> by lazy {
        val otherUDTs: List<UserDefinedType> =
            base.memoizedUserDefinedTypes + collectExtraGenericTypes()
        val allUDTs: List<UserDefinedType> = collectVarrayTypes(otherUDTs) + otherUDTs
        allUDTs.reversed().associateBy { "${it.schema}.${it.typeName}" }
    }

    private fun collectExtraGenericTypes(): List<GenericUserDefinedType> =
        collectAllTypesRows().map { row: AllTypesRow ->
            GenericUserDefinedType(
                catalog = null,
                schema = row.owner,
                typeName = row.typeName,
                typeCode = systemTypeMap[row.typeName]?.typeCode ?: Types.JAVA_OBJECT,
                remarks = null,
                baseTypeCode = null,
            )
        }

    private fun collectAllTypesRows(): List<AllTypesRow> {
        val results = mutableListOf<AllTypesRow>()
        try {
            base.conn.createStatement().use { stmt: Statement ->
                stmt.executeQuery(TYPES_QUERY).use { rs: ResultSet ->
                    while (rs.next()) {
                        results.add(AllTypesRow(rs.getString("OWNER"), rs.getString("TYPE_NAME")))
                    }
                }
            }
        } catch (e: SQLException) {
            throw RuntimeException("Oracle ALL_TYPES discovery query failed: ${e.message}", e)
        }
        return results
    }

    data class AllTypesRow(
        val owner: String,
        val typeName: String,
    )

    val systemTypeMap: Map<String, SystemType> by lazy {
        val systemTypes = mutableListOf<SystemType>()
        try {
            base.conn.metaData.typeInfo.use { rs: ResultSet ->
                while (rs.next()) {
                    systemTypes.add(
                        SystemType(
                            typeName = rs.getString("TYPE_NAME"),
                            typeCode = rs.getInt("DATA_TYPE"),
                        ),
                    )
                }
            }
        } catch (e: SQLException) {
            log.info {
                "Failed to query type info: " +
                    "sqlState = '${e.sqlState ?: ""}', errorCode = ${e.errorCode}, ${e.message}"
            }
        }
        systemTypes.filter { it.typeName != null }.associateBy { it.typeName!! }
    }

    private fun collectVarrayTypes(otherUDTs: List<UserDefinedType>): List<UserDefinedType> {
        val allRows: List<AllCollTypesRow> = collectAllCollTypesRows()
        val otherUDTsByFQName: Map<String, UserDefinedType> =
            otherUDTs
                .filter { it.schema != null && it.typeName != null }
                .associateBy { "${it.schema}.${it.typeName}" }
        val varrayFQNameSet: Set<String> = allRows.map { "${it.owner}.${it.typeName}" }.toSet()
        val parentRowByFQName: Map<String, AllCollTypesRow> =
            allRows
                .filter { it.elemTypeOwner != null && it.elemTypeName != null }
                .associateBy { "${it.elemTypeOwner!!}.${it.elemTypeName!!}" }

        fun recurse(
            elementType: SourceDatabaseType,
            row: AllCollTypesRow,
        ): UserDefinedArray {
            val type =
                UserDefinedArray(
                    catalog = null,
                    schema = row.owner,
                    typeName = row.typeName,
                    elementType = elementType,
                )
            val parentRow: AllCollTypesRow =
                parentRowByFQName["${row.owner}.${row.typeName}"] ?: return type
            return recurse(type, parentRow)
        }

        return allRows
            .filter { it.elemTypeName != null }
            .filterNot { varrayFQNameSet.contains("${it.elemTypeOwner}.${it.elemTypeName}") }
            .map { row ->
                val leaf: SourceDatabaseType =
                    otherUDTsByFQName["${row.elemTypeOwner}.${row.elemTypeName}"]
                        ?: SystemType(
                            typeName = row.elemTypeName!!,
                            typeCode =
                                when (row.scale) {
                                    null -> systemTypeMap[row.elemTypeName]?.typeCode
                                            ?: Types.JAVA_OBJECT
                                    else -> Types.NUMERIC
                                },
                            precision = row.precision,
                            scale = row.scale,
                        )
                recurse(leaf, row)
            }
    }

    private fun collectAllCollTypesRows(): List<AllCollTypesRow> {
        val results = mutableListOf<AllCollTypesRow>()
        try {
            base.conn.createStatement().use { stmt: Statement ->
                stmt.executeQuery(VARRAY_QUERY).use { rs: ResultSet ->
                    while (rs.next()) {
                        results.add(
                            AllCollTypesRow(
                                rs.getString("OWNER"),
                                rs.getString("TYPE_NAME"),
                                rs.getString("ELEM_TYPE_OWNER").takeUnless { rs.wasNull() },
                                rs.getString("ELEM_TYPE_NAME").takeUnless { rs.wasNull() },
                                rs.getInt("LENGTH").takeUnless { rs.wasNull() },
                                rs.getInt("PRECISION").takeUnless { rs.wasNull() },
                                rs.getInt("SCALE").takeUnless { rs.wasNull() },
                            ),
                        )
                    }
                }
            }
        } catch (e: SQLException) {
            throw RuntimeException("Oracle VARRAY discovery query failed: ${e.message}", e)
        }
        return results
    }

    data class AllCollTypesRow(
        val owner: String,
        val typeName: String,
        val elemTypeOwner: String?,
        val elemTypeName: String?,
        val displaySize: Int?,
        val precision: Int?,
        val scale: Int?,
    )

    val memoizedPrimaryKeys: Map<TableName, List<List<String>>> by lazy {
        val results = mutableListOf<AllPrimaryKeysRow>()
        val schemas: List<String> = base.streamNamespaces()
        val sql: String = PK_QUERY_FMTSTR.format(schemas.joinToString { "\'$it\'" })
        log.info { "Querying Oracle system tables for all primary keys for catalog discovery." }
        try {
            base.conn.createStatement().use { stmt: Statement ->
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    while (rs.next()) {
                        results.add(
                            AllPrimaryKeysRow(
                                rs.getString("OWNER"),
                                rs.getString("TABLE_NAME"),
                                rs.getString("CONSTRAINT_NAME"),
                                rs.getInt("POSITION").takeUnless { rs.wasNull() },
                                rs.getString("COLUMN_NAME").takeUnless { rs.wasNull() },
                            ),
                        )
                    }
                }
            }
            log.info { "Discovered all primary keys in ${schemas.size} Oracle schema(s)." }
            return@lazy results
                .groupBy { base.findTableName(it.tableName, it.owner) }
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
            throw RuntimeException("Oracle primary key discovery query failed: ${e.message}", e)
        }
    }

    override fun primaryKey(
        streamName: String,
        streamNamespace: String?,
    ): List<List<String>> {
        val table: TableName = base.findTableName(streamName, streamNamespace) ?: return listOf()
        return memoizedPrimaryKeys[table] ?: listOf()
    }

    private data class AllPrimaryKeysRow(
        val owner: String,
        val tableName: String,
        val constraintName: String,
        val position: Int?,
        val columnName: String?,
    )

    companion object {
        const val VARRAY_QUERY =
            """
SELECT OWNER, TYPE_NAME, ELEM_TYPE_OWNER, ELEM_TYPE_NAME, LENGTH, PRECISION, SCALE
FROM ALL_COLL_TYPES
WHERE COLL_TYPE = 'VARYING ARRAY'
        """

        const val TYPES_QUERY =
            """
SELECT OWNER, TYPE_NAME
FROM ALL_TYPES 
WHERE OWNER IS NOT NULL AND TYPE_NAME IS NOT NULL           
        """

        const val PK_QUERY_FMTSTR =
            """
SELECT
    ac.OWNER,
    ac.TABLE_NAME,
    ac.CONSTRAINT_NAME,
    acc.POSITION,
    acc.COLUMN_NAME
FROM
    ALL_CONSTRAINTS ac
    JOIN ALL_CONS_COLUMNS acc
    ON ac.OWNER = acc.OWNER
    AND ac.CONSTRAINT_NAME = acc.CONSTRAINT_NAME
WHERE
    ac.CONSTRAINT_TYPE = 'P'
    AND ac.OWNER IN (%s)
            """
    }

    /** Oracle implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory(
        val selectQueryGenerator: SelectQueryGenerator,
        val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
    ) : MetadataQuerier.Factory<OracleSourceConfiguration> {
        /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: OracleSourceConfiguration): MetadataQuerier {
            val jdbcConnectionFactory = JdbcConnectionFactory(config)
            val base =
                JdbcMetadataQuerier(
                    config,
                    selectQueryGenerator,
                    fieldTypeMapper,
                    jdbcConnectionFactory,
                )
            return OracleSourceMetadataQuerier(base)
        }
    }
}
