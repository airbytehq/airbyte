package io.airbyte.integrations.destination.motherduck.client

import io.airbyte.cdk.load.client.AirbyteClient
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableNativeOperations
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableSqlOperations
import io.airbyte.integrations.destination.motherduck.sql.MotherDuckDirectLoadSqlGenerator
import jakarta.inject.Singleton
import javax.sql.DataSource

@Singleton
class MotherDuckAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: MotherDuckDirectLoadSqlGenerator,
) : AirbyteClient, DirectLoadTableSqlOperations, DirectLoadTableNativeOperations {

    override suspend fun countTable(tableName: TableName): Long? {
        return try {
            dataSource.connection.use { connection ->
                val resultSet = connection.createStatement().executeQuery(sqlGenerator.countTable(tableName))
                if (resultSet.next()) {
                    resultSet.getLong(1)
                } else {
                    0L
                }
            }
        } catch (e: Exception) {
            null
        }
    }

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        execute(sqlGenerator.createTable(stream, tableName, columnNameMapping, replace))
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        val targetExists = countTable(targetTableName) != null
        if (targetExists) {
            execute(sqlGenerator.dropTable(targetTableName))
        }
        execute(sqlGenerator.renameTable(sourceTableName, targetTableName))
    }

    override suspend fun copyTable(
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(sqlGenerator.copyTable(columnNameMapping, sourceTableName, targetTableName))
    }

    override suspend fun upsertTable(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        sourceTableName: TableName,
        targetTableName: TableName
    ) {
        execute(sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName))
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun ensureSchemaMatches(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping
    ) {
    }

    override suspend fun getGenerationId(tableName: TableName): Long {
        return try {
            val sql = sqlGenerator.getGenerationId(tableName)
            dataSource.connection.use { connection ->
                val resultSet = connection.createStatement().executeQuery(sql)
                if (resultSet.next()) {
                    resultSet.getLong(1)
                } else {
                    0L
                }
            }
        } catch (e: Exception) {
            0L
        }
    }

    internal fun execute(query: String) =
        dataSource.connection.use { connection -> connection.createStatement().execute(query) }
}
