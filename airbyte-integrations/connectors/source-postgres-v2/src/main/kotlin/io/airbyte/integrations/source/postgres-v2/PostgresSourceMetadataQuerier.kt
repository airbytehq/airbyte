/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.check.JdbcCheckQueries
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.cdk.discover.MetadataQuerier
import io.airbyte.cdk.discover.TableName
import io.airbyte.cdk.jdbc.DefaultJdbcConstants
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.SelectQueryGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement

private val log = KotlinLogging.logger {}

/** Delegates to [JdbcMetadataQuerier] except for [fields]. */
class PostgresSourceMetadataQuerier(
    val base: JdbcMetadataQuerier,
) : MetadataQuerier by base {

    override fun extraChecks() {
        base.extraChecks()
        if (base.config.global) {
            // Extra checks for CDC
            var cdcVariableCheckQueries: List<Pair<String, String>> =
                listOf(
                    Pair("show variables where Variable_name = 'log_bin'", "ON"),
                    Pair("show variables where Variable_name = 'binlog_format'", "ROW"),
                    Pair("show variables where Variable_name = 'binlog_row_image'", "FULL"),
                )

            cdcVariableCheckQueries.forEach { runVariableCheckSql(it.first, it.second, base.conn) }

            // Note: SHOW MASTER STATUS has been deprecated in latest mysql (8.4) and going forward
            // it should be SHOW BINARY LOG STATUS. We will run both - if both have been failed we
            // will throw exception.
            try {
                base.conn.createStatement().use { stmt: Statement ->
                    stmt.execute("SHOW MASTER STATUS")
                }
            } catch (e: SQLException) {
                try {
                    base.conn.createStatement().use { stmt: Statement ->
                        stmt.execute("SHOW BINARY LOG STATUS")
                    }
                } catch (ex: SQLException) {
                    throw ConfigErrorException(
                        "Please grant REPLICATION CLIENT privilege, so that binary log files are available for CDC mode."
                    )
                }
            }
        }
    }

    private fun runVariableCheckSql(sql: String, expectedValue: String, conn: Connection) {
        try {
            conn.createStatement().use { stmt: Statement ->
                stmt.executeQuery(sql).use { rs: ResultSet ->
                    if (!rs.next()) {
                        throw ConfigErrorException("Could not query the variable $sql")
                    }
                    val resultValue: String = rs.getString("Value")
                    if (!resultValue.equals(expectedValue, ignoreCase = true)) {
                        throw ConfigErrorException(
                            String.format(
                                "The variable should be set to \"%s\", but it is \"%s\"",
                                expectedValue,
                                resultValue,
                            ),
                        )
                    }
                    if (rs.next()) {
                        throw ConfigErrorException("Could not query the variable $sql")
                    }
                }
            }
        } catch (e: Exception) {
            throw ConfigErrorException("Check query failed with: ${e.message}")
        }
    }

    override fun fields(streamID: StreamIdentifier): List<Field> {
        val table: TableName = findTableName(streamID) ?: return listOf()
        if (table !in base.memoizedColumnMetadata) return listOf()
        return base.memoizedColumnMetadata[table]!!.map {
            Field(it.label, base.fieldTypeMapper.toFieldType(it))
        }
    }

    override fun streamNamespaces(): List<String> = base.config.namespaces.toList()

    override fun streamNames(streamNamespace: String?): List<StreamIdentifier> =
        base.memoizedTableNames
            .filter { (it.schema ?: it.catalog) == streamNamespace }
            .map { StreamDescriptor().withName(it.name).withNamespace(streamNamespace) }
            .map(StreamIdentifier::from)

    fun findTableName(
        streamID: StreamIdentifier,
    ): TableName? =
        base.memoizedTableNames.find {
            it.name == streamID.name && (it.schema ?: it.catalog) == streamID.namespace
        }

    val memoizedPrimaryKeys: Map<TableName, List<List<String>>> by lazy {
        val results = mutableListOf<AllPrimaryKeysRow>()
        val schemas: List<String> = streamNamespaces()
        val sql: String = PK_QUERY_FMTSTR.format(schemas.joinToString { "\'$it\'" })
        log.info { "Querying MySQL system tables for all primary keys for catalog discovery." }
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
            log.info { "Discovered all primary keys in ${schemas.size} MySQL schema(s)." }
            return@lazy results
                .groupBy {
                    findTableName(
                        StreamIdentifier.from(
                            StreamDescriptor().withName(it.tableName).withNamespace(it.tableSchema),
                        ),
                    )
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
            throw RuntimeException("MySQL primary key discovery query failed: ${e.message}", e)
        }
    }

    override fun primaryKey(
        streamID: StreamIdentifier,
    ): List<List<String>> {
        val table: TableName = findTableName(streamID) ?: return listOf()
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

    /** MySQL implementation of [MetadataQuerier.Factory]. */
    @Singleton
    @Primary
    class Factory(
        val constants: DefaultJdbcConstants,
        val selectQueryGenerator: SelectQueryGenerator,
        val fieldTypeMapper: JdbcMetadataQuerier.FieldTypeMapper,
        val checkQueries: JdbcCheckQueries,
    ) : MetadataQuerier.Factory<MySqlSourceConfiguration> {
        /** The [SourceConfiguration] is deliberately not injected in order to support tests. */
        override fun session(config: MySqlSourceConfiguration): MetadataQuerier {
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
            return MySqlSourceMetadataQuerier(base)
        }
    }
}
