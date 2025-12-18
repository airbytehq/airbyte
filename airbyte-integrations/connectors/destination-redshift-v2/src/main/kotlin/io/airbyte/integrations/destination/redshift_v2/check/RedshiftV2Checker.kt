/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.redshift_v2.spec.RedshiftV2Configuration
import jakarta.inject.Singleton
import java.sql.Connection
import java.time.Clock
import javax.sql.DataSource

@Singleton
class RedshiftV2Checker(
    private val dataSource: DataSource,
    clock: Clock,
) : DestinationChecker<RedshiftV2Configuration> {

    private val tableName = "_airbyte_check_table_${clock.millis()}"

    override fun check(config: RedshiftV2Configuration) {
        val qualifiedTableName = "\"${config.schema}\".\"$tableName\""

        dataSource.connection.use { connection ->
            // Create schema if not exists
            connection.execute("CREATE SCHEMA IF NOT EXISTS \"${config.schema}\"")

            // Create test table
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS $qualifiedTableName (
                    test_column VARCHAR(256)
                )
                """.trimIndent()
            )

            // Insert test data
            connection.execute(
                """
                INSERT INTO $qualifiedTableName (test_column) VALUES ('test_value')
                """.trimIndent()
            )

            // Verify the insert
            val count = connection.createStatement().use { statement ->
                statement.executeQuery("SELECT COUNT(*) FROM $qualifiedTableName").use { rs ->
                    if (rs.next()) rs.getLong(1) else 0L
                }
            }

            require(count == 1L) {
                "Failed to insert expected rows into check table. Actual written: $count"
            }
        }
    }

    override fun cleanup(config: RedshiftV2Configuration) {
        val qualifiedTableName = "\"${config.schema}\".\"$tableName\""

        try {
            dataSource.connection.use { connection ->
                connection.execute("DROP TABLE IF EXISTS $qualifiedTableName")
            }
        } catch (e: Exception) {
            // Cleanup should not throw
        }
    }

    private fun Connection.execute(sql: String) {
        createStatement().use { statement ->
            statement.execute(sql)
        }
    }
}
