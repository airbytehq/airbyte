/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.check

import com.databricks.sdk.WorkspaceClient
import io.airbyte.integrations.destination.databricks.client.DatabricksAirbyteClient
import io.airbyte.integrations.destination.databricks.spec.CdcDeletionMode
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import io.airbyte.integrations.destination.databricks.spec.PersonalAccessTokenConfiguration
import io.airbyte.integrations.destination.databricks.sql.DatabricksSqlGenerator
import io.mockk.every
import io.mockk.mockk
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import javax.sql.DataSource
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test

class DatabricksCheckerSqlTest {

    @Test
    fun `check and cleanup drop the staging volume created by check`() {
        val config =
            DatabricksConfiguration(
                hostname = "test.cloud.databricks.com",
                httpPath = "sql/1.0/warehouses/abc123",
                port = "443",
                database = "test_catalog",
                schema = "test_schema",
                authType = PersonalAccessTokenConfiguration("test-token"),
                purgeStagingData = true,
                acceptTerms = true,
                cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
            )
        val sqlStatements = mutableListOf<String>()
        val statement = mockk<Statement>(relaxed = true)
        every { statement.execute(any()) } answers
            {
                sqlStatements.add(firstArg())
                true
            }

        val schemaRows =
            listOf(
                Triple("_airbyte_raw_id", "STRING", "NO"),
                Triple("_airbyte_extracted_at", "TIMESTAMP", "NO"),
                Triple("_airbyte_meta", "STRING", "NO"),
                Triple("_airbyte_generation_id", "LONG", "YES"),
            )
        var schemaRowIndex = -1
        val schemaResultSet =
            mockk<ResultSet>(relaxed = true).also { resultSet ->
                every { resultSet.next() } answers { ++schemaRowIndex < schemaRows.size }
                every { resultSet.getString("column_name") } answers
                    {
                        schemaRows[schemaRowIndex].first
                    }
                every { resultSet.getString("data_type") } answers
                    {
                        schemaRows[schemaRowIndex].second
                    }
                every { resultSet.getString("is_nullable") } answers
                    {
                        schemaRows[schemaRowIndex].third
                    }
            }
        val countResultSet =
            mockk<ResultSet>(relaxed = true) {
                every { next() } returns true
                every { getLong(1) } returns 1L
            }
        every { statement.executeQuery(any()) } answers
            {
                val sql = firstArg<String>()
                sqlStatements.add(sql)
                if (sql.contains("information_schema.columns")) schemaResultSet else countResultSet
            }

        val connection =
            mockk<Connection>(relaxed = true) { every { createStatement() } returns statement }
        val dataSource = mockk<DataSource>()
        every { dataSource.connection } returns connection
        val sqlGenerator = DatabricksSqlGenerator(config)
        val databricksClient =
            DatabricksAirbyteClient(
                dataSource,
                sqlGenerator,
                mockk<WorkspaceClient>(relaxed = true)
            )
        val checker = DatabricksChecker(databricksClient, config)

        checker.check()
        checker.cleanup()

        val createVolumeStatements =
            sqlStatements.filter { it.startsWith("CREATE VOLUME IF NOT EXISTS ") }
        assertEquals(1, createVolumeStatements.size)
        val volumeName =
            createVolumeStatements.single().removePrefix("CREATE VOLUME IF NOT EXISTS ")
        assertTrue(
            sqlStatements.contains("DROP VOLUME IF EXISTS $volumeName"),
            "Expected executed statement DROP VOLUME IF EXISTS $volumeName",
        )
        assertTrue(
            sqlStatements.any {
                it.startsWith("DROP TABLE IF EXISTS `test_catalog`.`test_schema`.`_airbyte_check_")
            },
        )
    }
}
