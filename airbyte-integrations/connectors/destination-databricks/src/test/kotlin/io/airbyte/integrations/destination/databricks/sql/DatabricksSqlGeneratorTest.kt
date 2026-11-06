/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.sql

import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.databricks.spec.CdcDeletionMode
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import io.airbyte.integrations.destination.databricks.spec.PersonalAccessTokenConfiguration
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test

class DatabricksSqlGeneratorTest {

    private val sqlGenerator =
        DatabricksSqlGenerator(
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
            ),
        )

    @Test
    fun `dropStagingVolume drops the expected fully qualified volume`() {
        val tableName = TableName(namespace = "test_schema", name = "my_table")

        assertEquals(
            "DROP VOLUME IF EXISTS `test_catalog`.`test_schema`.`my_table_staging`",
            sqlGenerator.dropStagingVolume(tableName),
        )
    }

    @Test
    fun `dropStagingVolume targets the same volume as createStagingVolume`() {
        val tableName = TableName(namespace = "test_schema", name = "my_table")

        val createdVolumeName =
            sqlGenerator.createStagingVolume(tableName).removePrefix("CREATE VOLUME IF NOT EXISTS ")
        val droppedVolumeName =
            sqlGenerator.dropStagingVolume(tableName).removePrefix("DROP VOLUME IF EXISTS ")

        assertEquals(createdVolumeName, droppedVolumeName)
    }
}
