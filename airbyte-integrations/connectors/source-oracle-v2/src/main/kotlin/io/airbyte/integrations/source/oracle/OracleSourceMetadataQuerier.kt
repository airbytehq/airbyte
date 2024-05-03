/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle

import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.ColumnMetadata
import io.airbyte.cdk.discover.DiscoverMapper
import io.airbyte.cdk.discover.GenericUserDefinedType
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.SourceType
import io.airbyte.cdk.discover.SystemType
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.discover.UserDefinedArray
import io.airbyte.cdk.discover.UserDefinedType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.JdbcMetadataQuerier
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement
import java.sql.Types
import oracle.jdbc.OracleArray

private val log = KotlinLogging.logger {}

/**
 * Delegates to [JdbcMetadataQuerier] except for [columnMetadata].
 *
 * Oracle is annoying when it comes to array types. All array types are user-defined VARRAYS. These
 * do NOT show up in a [java.sql.DatabaseMetaData.getUDTs] query. We therefore need to query
 * Oracle's system tables like ALL_COLL_TYPES to retrieve type info. Furthermore, other user-defined
 * object types also need to be handled somewhat properly: even though we're going to map them to
 * some generic type like STRING or JSONB we still need to deal with arrays of UDTs.
 *
 * We cache the results of these UDT-related queries as they are not column-specific.
 */
class OracleSourceMetadataQuerier(val base: JdbcMetadataQuerier) : MetadataQuerier by base {

    override fun columnMetadata(table: TableName): List<ColumnMetadata> =
        base.columnMetadata(table).map {
            it.copy(
                type =
                    when (it.type) {
                        is SystemType -> allUDTsByFQName[it.type.typeName] ?: it.type
                        else -> it.type
                    }
            )
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
                klazz = null,
                typeCode = systemTypeMap[row.typeName]?.typeCode ?: Types.JAVA_OBJECT,
                remarks = null,
                baseTypeCode = null
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
                            typeCode = rs.getInt("DATA_TYPE")
                        )
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
        fun recurse(elementType: SourceType, row: AllCollTypesRow): UserDefinedArray {
            val type =
                UserDefinedArray(
                    catalog = null,
                    schema = row.owner,
                    typeName = row.typeName,
                    klazz = OracleArray::class.java,
                    elementType = elementType
                )
            val parentRow: AllCollTypesRow =
                parentRowByFQName["${row.owner}.${row.typeName}"] ?: return type
            return recurse(type, parentRow)
        }

        return allRows
            .filter { it.elemTypeName != null }
            .filterNot { varrayFQNameSet.contains("${it.elemTypeOwner}.${it.elemTypeName}") }
            .map { row ->
                val leaf: SourceType =
                    otherUDTsByFQName["${row.elemTypeOwner}.${row.elemTypeName}"]
                        ?: SystemType(
                            typeName = row.elemTypeName!!,
                            klazz = null,
                            typeCode =
                                when (row.scale) {
                                    null -> systemTypeMap[row.elemTypeName]?.typeCode
                                            ?: Types.JAVA_OBJECT
                                    else -> Types.NUMERIC
                                },
                            signed = null,
                            displaySize = row.displaySize,
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
                                rs.getInt("SCALE").takeUnless { rs.wasNull() }
                            )
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
    }

    /** Oracle implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory(override val discoverMapper: DiscoverMapper) : MetadataQuerier.Factory {

        /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: SourceConfiguration): MetadataQuerier {
            val jdbcConnectionFactory = JdbcConnectionFactory(config)
            val base = JdbcMetadataQuerier(config, discoverMapper, jdbcConnectionFactory)
            return OracleSourceMetadataQuerier(base)
        }
    }
}
