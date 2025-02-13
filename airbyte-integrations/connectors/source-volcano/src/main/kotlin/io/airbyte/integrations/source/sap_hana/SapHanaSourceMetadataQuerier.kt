/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.sap_hana

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.*
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.ResultSet
import java.sql.Statement

private val log = KotlinLogging.logger {}

/**
 * Delegates to [JdbcMetadataQuerier] except for [fields].
 *
 * We cache the results of these UDT-related queries as they are not column-specific.
 */
class SapHanaSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
) : MetadataQuerier by base {

    override fun fields(streamID: StreamIdentifier): List<Field> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        if (table !in base.memoizedColumnMetadata) return listOf()
        return base.memoizedColumnMetadata[table]!!.map {
            Field(it.label, base.fieldTypeMapper.toFieldType(it))
        }
    }

    fun findTableName(
        streamID: StreamIdentifier,
    ): TableName? =
        base.memoizedTableNames.find {
            it.name == streamID.name && (it.schema ?: it.catalog) == streamID.namespace
        }

    val memoizedPrimaryKeys: Map<TableName, List<List<String>>> by lazy {
        val results = mutableListOf<AllPrimaryKeysRow>()
        val schemas: List<String> = base.streamNamespaces()
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
                    base.findTableName(StreamIdentifier.from(desc))
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
        val table: TableName = base.findTableName(streamID) ?: return listOf()
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
            return SapHanaSourceMetadataQuerier(base)
        }
    }
}
