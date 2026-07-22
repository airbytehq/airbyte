/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.check

import io.airbyte.cdk.load.check.DestinationChecker
import io.airbyte.integrations.destination.doris.spec.DorisConfiguration
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.sql.Connection
import java.time.Clock
import org.apache.http.client.methods.HttpGet
import org.apache.http.impl.client.CloseableHttpClient

@Singleton
class DorisChecker(
    clock: Clock,
    private val config: DorisConfiguration,
    @Named("dorisJdbcConnection") private val jdbcConnection: Connection,
    @Named("dorisHttpClient") private val httpClient: CloseableHttpClient,
) : DestinationChecker {

    private val testTableName = "_airbyte_check_table_${clock.millis()}"

    override fun check() {
        // 1. Verify JDBC connectivity (MySQL protocol port)
        jdbcConnection.createStatement().use { stmt ->
            stmt.executeQuery("SELECT 1").use { rs ->
                require(rs.next()) { "Failed to execute SELECT 1 via JDBC on Doris query port." }
            }
        }

        // 2. Verify HTTP connectivity (Stream Load port)
        val httpGet = HttpGet("${config.feHttpUrl}/api/health")
        httpClient.execute(httpGet).use { response ->
            val statusCode = response.statusLine.statusCode
            require(statusCode == 200 || statusCode == 404) {
                "Failed to connect to Doris FE HTTP port at ${config.feHttpUrl}. " +
                    "Status: $statusCode"
            }
        }

        // 3. Verify write permission by creating and dropping a test table
        jdbcConnection.createStatement().use { stmt ->
            stmt.execute("CREATE DATABASE IF NOT EXISTS `${config.database}`")
            stmt.execute(
                """
                CREATE TABLE IF NOT EXISTS `${config.database}`.`$testTableName` (
                    `test_col` INT
                )
                DUPLICATE KEY(`test_col`)
                DISTRIBUTED BY HASH(`test_col`) BUCKETS AUTO
                PROPERTIES ("replication_num" = "1")
                """.trimIndent()
            )
        }
    }

    override fun cleanup() {
        jdbcConnection.createStatement().use { stmt ->
            stmt.execute("DROP TABLE IF EXISTS `${config.database}`.`$testTableName`")
        }
    }
}
