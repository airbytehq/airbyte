package io.airbyte.integrations.destination.mysql.client

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.ColumnChangeset
import io.airbyte.cdk.load.component.TableColumns
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class MySQLAirbyteClient(
    private val dataSource: DataSource,
    private val sqlGenerator: MySQLSqlGenerator,
    private val columnUtils: MySQLColumnUtils,
) : TableOperationsClient, TableSchemaEvolutionClient {

    /**
     * Executes a SQL statement (helper method)
     */
    private fun execute(sql: String) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                log.info { "Executing SQL: ${sql.trim()}" }
                statement.execute(sql)
            }
        }
    }

    /**
     * Executes multiple SQL statements on a single connection (for upsert/dedupe operations)
     */
    private fun executeMultiple(statements: List<String>) {
        dataSource.connection.use { connection ->
            statements.forEach { sql ->
                connection.createStatement().use { statement ->
                    log.info { "Executing SQL: ${sql.trim()}" }
                    statement.execute(sql)
                }
            }
        }
    }

    override suspend fun createNamespace(namespace: String) {
        execute(sqlGenerator.createNamespace(namespace))
    }

    override suspend fun namespaceExists(namespace: String): Boolean {
        return dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sqlGenerator.namespaceExists(namespace))
                rs.next()  // Returns true if namespace exists
            }
        }
    }

    override suspend fun createTable(
        stream: DestinationStream,
        tableName: TableName,
        columnNameMapping: ColumnNameMapping,
        replace: Boolean
    ) {
        if (replace) {
            // Drop first, then create (MySQL doesn't support CREATE OR REPLACE)
            execute(sqlGenerator.dropTable(tableName))
        }
        execute(sqlGenerator.createTable(stream, tableName, columnNameMapping, false))
    }

    override suspend fun dropTable(tableName: TableName) {
        execute(sqlGenerator.dropTable(tableName))
    }

    override suspend fun tableExists(table: TableName): Boolean {
        return countTable(table) != null
    }

    override suspend fun overwriteTable(sourceTableName: TableName, targetTableName: TableName) {
        val statements = sqlGenerator.overwriteTable(sourceTableName, targetTableName)
        // Execute on same connection for consistency
        executeMultiple(statements)
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
        val statements = sqlGenerator.upsertTable(stream, columnNameMapping, sourceTableName, targetTableName)
        // Execute all statements on same connection so temp table is visible
        executeMultiple(statements)
    }

    override suspend fun countTable(tableName: TableName): Long? =
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    val rs = statement.executeQuery(sqlGenerator.countTable(tableName))
                    if (rs.next()) rs.getLong("count") else 0L
                }
            }
        } catch (e: Exception) {
            log.debug(e) { "Table ${tableName} does not exist. Returning null." }
            null  // Expected - table doesn't exist
        }

    override suspend fun getGenerationId(tableName: TableName): Long {
        return try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    val rs = statement.executeQuery(sqlGenerator.getGenerationId(tableName))
                    if (rs.next()) {
                        rs.getLong("generation_id").takeIf { !rs.wasNull() } ?: 0L
                    } else {
                        0L
                    }
                }
            }
        } catch (e: Exception) {
            log.debug(e) { "Failed to retrieve generation ID, returning 0" }
            0L
        }
    }

    override suspend fun discoverSchema(tableName: TableName): io.airbyte.cdk.load.component.TableSchema {
        val columns = mutableMapOf<String, io.airbyte.cdk.load.component.ColumnType>()

        dataSource.connection.use { connection ->
            val sql = """
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = '${tableName.namespace}'
                  AND table_name = '${tableName.name}'
            """

            connection.createStatement().use { statement ->
                val rs = statement.executeQuery(sql)

                while (rs.next()) {
                    val columnName = rs.getString("column_name")

                    // Skip Airbyte metadata columns
                    if (columnName.startsWith("_airbyte_")) continue

                    val dataType = rs.getString("data_type")
                    val nullable = rs.getString("is_nullable") == "YES"

                    columns[columnName] = io.airbyte.cdk.load.component.ColumnType(dataType, nullable)
                }
            }
        }

        return io.airbyte.cdk.load.component.TableSchema(columns)
    }

    override suspend fun applyChangeset(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping,
        tableName: TableName,
        expectedColumns: TableColumns,
        columnChangeset: ColumnChangeset
    ) {
        // For Phase 7: No-op (full implementation in Phase 12)
        // Schema evolution not needed for append mode
    }

    override fun computeSchema(
        stream: DestinationStream,
        columnNameMapping: ColumnNameMapping
    ): io.airbyte.cdk.load.component.TableSchema {
        val columns = stream.schema.asColumns()
            .filter { (name, _) -> !name.startsWith("_airbyte_") }
            .mapKeys { (name, _) -> columnNameMapping[name]!! }
            .mapValues { (_, field) ->
                val dbType = columnUtils.toDialectType(field.type)
                io.airbyte.cdk.load.component.ColumnType(dbType, field.nullable)
            }

        return io.airbyte.cdk.load.component.TableSchema(columns)
    }
}
