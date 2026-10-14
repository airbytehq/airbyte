/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.component.TableOperationsFixtures as Fixtures
import io.airbyte.cdk.load.component.TableOperationsFixtures.insertRecords
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.client.execute
import io.airbyte.integrations.destination.snowflake.component.config.SnowflakeComponentTestFixtures.testMapping
import io.airbyte.integrations.destination.snowflake.component.config.SnowflakeTestTableOperationsClient
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeDirectLoadSqlGenerator
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import javax.sql.DataSource
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

/**
 * Tables created by connector versions prior to 3.10.0 lack the `_AIRBYTE_META` and
 * `_AIRBYTE_GENERATION_ID` columns. These tests verify that [SnowflakeAirbyteClient] repairs such
 * tables during `ensureSchemaMatches` when the repair feature flag (off by default) is enabled, and
 * that the write path works after the repair.
 */
@MicronautTest(environments = ["component"], resolveParameters = false)
@Property(name = "airbyte.destination.snowflake.meta-column-repair", value = "true")
@Execution(ExecutionMode.CONCURRENT)
class SnowflakeMetaColumnRepairTest(
    private val client: SnowflakeAirbyteClient,
    private val testClient: SnowflakeTestTableOperationsClient,
    private val schemaFactory: TableSchemaFactory,
    private val sqlGenerator: SnowflakeDirectLoadSqlGenerator,
    private val dataSource: DataSource,
) {
    /** Creates a table shaped like one created by a pre-3.10.0 connector version. */
    private fun createPre310Table(tableName: TableName) {
        dataSource.execute(
            """
            CREATE TABLE ${sqlGenerator.fullyQualifiedName(tableName)} (
                "_AIRBYTE_RAW_ID" VARCHAR NOT NULL,
                "_AIRBYTE_EXTRACTED_AT" TIMESTAMP_TZ NOT NULL,
                "TEST" NUMBER(38,0)
            )
            """.trimIndent()
        )
    }

    /** Inserts a row the way a pre-3.10.0 connector version would have: no meta columns. */
    private fun insertLegacyRow(tableName: TableName) {
        dataSource.execute(
            """
            INSERT INTO ${sqlGenerator.fullyQualifiedName(tableName)}
                ("_AIRBYTE_RAW_ID", "_AIRBYTE_EXTRACTED_AT", "TEST")
            VALUES ('legacy-row', CURRENT_TIMESTAMP(), 7)
            """.trimIndent()
        )
    }

    @Test
    fun `ensureSchemaMatches adds meta columns to a pre-3_10 table`() = runTest {
        val namespace = Fixtures.generateTestNamespace("meta_repair")
        val table = Fixtures.generateTestTableName("meta_repair_table", namespace)
        val tableSchema = schemaFactory.make(table, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val stream = Fixtures.createStream(table.namespace, table.name, tableSchema)
        try {
            client.createNamespace(namespace)
            createPre310Table(table)
            assertFalse(
                client
                    .describeTable(table)
                    .keys
                    .containsAll(SnowflakeColumnManager.Constants.schemaModeMetaColNames)
            )

            client.ensureSchemaMatches(stream, table, testMapping)

            val columns = client.describeTable(table).keys
            assertTrue(
                columns.containsAll(SnowflakeColumnManager.Constants.schemaModeMetaColNames),
                "Expected all Airbyte meta columns to exist after ensureSchemaMatches, got $columns",
            )

            // Prove that the COPY INTO write path (which references the meta columns explicitly)
            // now succeeds.
            testClient.insertRecords(table, Fixtures.SINGLE_TEST_RECORD_INPUT, testMapping)
            val rows = testClient.readTable(table)
            assertEquals(1, rows.size)
            assertEquals(42L, rows.first()["TEST"])

            // The next sync reads the generation id written by this one.
            assertEquals(1L, client.getGenerationId(table))
        } finally {
            testClient.dropNamespace(namespace)
        }
    }

    @Test
    fun `getGenerationId returns 0 after repairing a table with pre-existing rows`() = runTest {
        val namespace = Fixtures.generateTestNamespace("meta_repair")
        val table = Fixtures.generateTestTableName("meta_repair_legacy_rows", namespace)
        val tableSchema = schemaFactory.make(table, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val stream = Fixtures.createStream(table.namespace, table.name, tableSchema)
        try {
            client.createNamespace(namespace)
            createPre310Table(table)
            insertLegacyRow(table)

            // Before the repair the column does not exist at all.
            assertEquals(0L, client.getGenerationId(table))

            client.ensureSchemaMatches(stream, table, testMapping)

            val columns = client.describeTable(table).keys
            assertTrue(
                columns.containsAll(SnowflakeColumnManager.Constants.schemaModeMetaColNames),
                "Expected all Airbyte meta columns to exist after ensureSchemaMatches, got $columns",
            )

            // After the repair the column exists but the legacy row has a NULL generation id,
            // which reads as generation 0 (no error).
            assertEquals(0L, client.getGenerationId(table))

            val rows = testClient.readTable(table)
            assertEquals(1, rows.size)
            assertEquals(7L, rows.first()["TEST"])
        } finally {
            testClient.dropNamespace(namespace)
        }
    }

    @Test
    fun `getGenerationId returns 0 for a table without the generation id column`() = runTest {
        val namespace = Fixtures.generateTestNamespace("meta_repair")
        val table = Fixtures.generateTestTableName("meta_repair_genid", namespace)
        try {
            client.createNamespace(namespace)
            createPre310Table(table)

            assertEquals(0L, client.getGenerationId(table))
        } finally {
            testClient.dropNamespace(namespace)
        }
    }
}
