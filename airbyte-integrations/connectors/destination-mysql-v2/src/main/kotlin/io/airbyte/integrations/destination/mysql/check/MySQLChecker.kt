/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.mysql.spec.MySQLConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlinx.coroutines.runBlocking
import java.time.Clock
import javax.sql.DataSource

private val log = KotlinLogging.logger {}

@Singleton
class MySQLChecker(
    clock: Clock,
    private val dataSource: DataSource,
) : DestinationChecker<MySQLConfiguration> {

    private val tableName = "_airbyte_check_table_${clock.millis()}"

    override fun check(config: MySQLConfiguration) {
        val resolvedTableName = "${config.database}.$tableName"

        dataSource.connection.use { connection ->
            // Create test table
            connection.createStatement().use { statement ->
                statement.execute(
                    """
                    CREATE TABLE IF NOT EXISTS `${config.database}`.`$tableName` (
                        test INT
                    )
                    """.trimIndent()
                )
            }

            // Insert test data
            connection.prepareStatement(
                "INSERT INTO `${config.database}`.`$tableName` (test) VALUES (?)"
            ).use { ps ->
                ps.setInt(1, 42)
                val rowsInserted = ps.executeUpdate()
                require(rowsInserted == 1) {
                    "Failed to insert expected rows into check table. Actual written: $rowsInserted"
                }
            }

            log.info { "Connection check passed for database: ${config.database}" }
        }
    }

    override fun cleanup(config: MySQLConfiguration) {
        try {
            dataSource.connection.use { connection ->
                connection.createStatement().use { statement ->
                    statement.execute("DROP TABLE IF EXISTS `${config.database}`.`$tableName`")
                }
            }
            log.info { "Cleaned up test table: $tableName" }
        } catch (e: Exception) {
            log.warn(e) { "Failed to cleanup test table: $tableName" }
        }
    }
}
