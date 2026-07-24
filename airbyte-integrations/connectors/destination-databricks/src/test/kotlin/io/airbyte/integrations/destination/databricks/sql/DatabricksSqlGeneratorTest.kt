/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.sql

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.integrations.destination.databricks.spec.CdcDeletionMode
import io.airbyte.integrations.destination.databricks.spec.DatabricksConfiguration
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class DatabricksSqlGeneratorTest {

    private val config: DatabricksConfiguration = mockk()
    private lateinit var generator: DatabricksSqlGenerator

    @BeforeEach
    fun setUp() {
        every { config.database } returns "test_database"
        every { config.cdcDeletionMode } returns CdcDeletionMode.SOFT_DELETE
        generator = DatabricksSqlGenerator(config)
    }

    private fun tableSchema(primaryKey: List<List<String>>): StreamTableSchema =
        StreamTableSchema(
            tableNames = TableNames(finalTableName = TARGET_TABLE, tempTableName = SOURCE_TABLE),
            columnSchema =
                ColumnSchema(
                    inputToFinalColumnNames =
                        mapOf("id" to "id", "org_id" to "org_id", "updated_at" to "updated_at"),
                    finalSchema =
                        mapOf(
                            "id" to ColumnType("STRING", true),
                            "org_id" to ColumnType("STRING", true),
                            "updated_at" to ColumnType("TIMESTAMP", true),
                        ),
                    inputSchema =
                        mapOf(
                            "id" to FieldType(StringType, nullable = true),
                            "org_id" to FieldType(StringType, nullable = true),
                            "updated_at" to FieldType(StringType, nullable = true),
                        ),
                ),
            importType = Dedupe(primaryKey = primaryKey, cursor = listOf("updated_at")),
        )

    @Test
    fun `upsert merge condition matches null primary key values`() {
        val sql =
            generator.upsertTable(tableSchema(listOf(listOf("id"))), SOURCE_TABLE, TARGET_TABLE)

        assertTrue(
            sql.contains(
                "ON (final.`id` = staging.`id` OR (final.`id` IS NULL AND staging.`id` IS NULL))",
            ),
            "MERGE ON clause must use a null-safe primary key comparison, but was:\n$sql",
        )
        // A plain equality join would let records with a NULL primary key fall through to the
        // INSERT branch on every sync.
        assertFalse(sql.contains("ON final.`id` = staging.`id`"), sql)
    }

    @Test
    fun `upsert merge condition is null-safe for every column of a composite primary key`() {
        val sql =
            generator.upsertTable(
                tableSchema(listOf(listOf("id"), listOf("org_id"))),
                SOURCE_TABLE,
                TARGET_TABLE,
            )

        assertTrue(
            sql.contains(
                "ON (final.`id` = staging.`id` OR (final.`id` IS NULL AND staging.`id` IS NULL)) " +
                    "AND (final.`org_id` = staging.`org_id` OR " +
                    "(final.`org_id` IS NULL AND staging.`org_id` IS NULL))",
            ),
            "MERGE ON clause must be null-safe for each primary key column, but was:\n$sql",
        )
    }

    companion object {
        private val SOURCE_TABLE = TableName(namespace = "test_namespace", name = "source")
        private val TARGET_TABLE = TableName(namespace = "test_namespace", name = "target")
    }
}
