/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.firebolt.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.ResultSet
import javax.sql.DataSource

/** JDBC client for executing SQL against Firebolt and implementing CDK table operations. */
@Singleton
class FireboltAirbyteClient(private val dataSource: DataSource) :
    TableOperationsClient, TableSchemaEvolutionClient {

    /** Execute a single SQL statement. */
    fun execute(sql: String): Unit {
        dataSource.connection.use { conn: Connection ->
            conn.createStatement().use { stmt ->
                stmt.execute(sql)
            }
        }
    }

    /** Execute a query and process the [ResultSet]. */
    fun <T> executeQuery(sql: String, block: (ResultSet) -> T): T {
        return dataSource.connection.use { conn: Connection ->
            conn.createStatement().use { stmt ->
                stmt.executeQuery(sql).use { rs -> block(rs) }
            }
        }
    }

    // ================================================================
    // TableOperationsClient
    // ================================================================

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        TODO("Firebolt createTable not yet implemented")
    }

    override suspend fun dropTable(tableName: TableName) {
        TODO("Firebolt dropTable not yet implemented")
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        TODO("Firebolt overwriteTable not yet implemented")
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        TODO("Firebolt copyTable not yet implemented")
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        TODO("Firebolt upsertTable not yet implemented")
    }

    // ================================================================
    // TableSchemaEvolutionClient
    // ================================================================

    override suspend fun discoverSchema(tableName: TableName): TableSchema = TableSchema(emptyMap())

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): TableSchema = TableSchema(stream.tableSchema.columnSchema.finalSchema)

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset
    ) {
        if (columnChangeset.isNoop()) {
            return
        }
        TODO("Firebolt schema evolution not yet implemented")
    }

    /** Validates JDBC connectivity by executing a trivial query. */
    suspend fun ping() {
        execute("SELECT 1")
    }

    /** Upload raw bytes to S3. Not yet implemented. */
    fun uploadToS3(bucket: String, key: String, bytes: ByteArray) {
        TODO("S3 upload implementation pending")
    }

    /** Delete an S3 object. Not yet implemented. */
    fun deleteFromS3(bucket: String, key: String) {
        TODO("S3 delete implementation pending")
    }
}
