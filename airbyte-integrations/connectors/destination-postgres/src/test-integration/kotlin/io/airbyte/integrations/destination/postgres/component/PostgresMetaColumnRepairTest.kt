/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.component.TableOperationsFixtures as Fixtures
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import javax.sql.DataSource
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Tables created by pre-direct-load connector versions lack the `_airbyte_meta` and
 * `_airbyte_generation_id` columns. These tests verify that [PostgresAirbyteClient] repairs such
 * tables during `ensureSchemaMatches`, and tolerates the missing generation id column before the
 * repair has run.
 */
@MicronautTest(environments = ["component"], resolveParameters = false)
class PostgresMetaColumnRepairTest(
    private val client: PostgresAirbyteClient,
    private val testClient: PostgresTestTableOperationsClient,
    private val schemaFactory: TableSchemaFactory,
    private val dataSource: DataSource,
) {
    /** Creates a table shaped like one created by a pre-direct-load connector version. */
    private fun createPreDirectLoadTable(tableName: TableName) {
        dataSource.connection.use { connection ->
            connection.createStatement().use { statement ->
                statement.execute(
                    """
                    CREATE TABLE "${tableName.namespace}"."${tableName.name}" (
                        "_airbyte_raw_id" varchar NOT NULL,
                        "_airbyte_extracted_at" timestamp with time zone NOT NULL,
                        "${Fixtures.TEST_FIELD}" bigint
                    )
                    """.trimIndent()
                )
            }
        }
    }

    @Test
    fun `ensureSchemaMatches adds meta columns to a pre-direct-load table`() = runTest {
        val namespace = Fixtures.generateTestNamespace("meta_repair")
        val table = Fixtures.generateTestTableName("meta_repair_table", namespace)
        val tableSchema = schemaFactory.make(table, Fixtures.TEST_INTEGER_SCHEMA.properties, Append)
        val stream = Fixtures.createStream(table.namespace, table.name, tableSchema)
        try {
            client.createNamespace(namespace)
            createPreDirectLoadTable(table)
            assertFalse(client.describeTable(table).containsAll(Meta.COLUMN_NAMES))

            client.ensureSchemaMatches(stream, table, Fixtures.TEST_MAPPING)

            val columns = client.describeTable(table)
            assertTrue(
                columns.containsAll(Meta.COLUMN_NAMES),
                "Expected all Airbyte meta columns to exist after ensureSchemaMatches, got $columns",
            )

            // Prove that a write referencing the meta columns now succeeds.
            testClient.insertRecords(table, Fixtures.SINGLE_TEST_RECORD_INPUT)
            val rows = testClient.readTable(table)
            assertEquals(1, rows.size)
            assertEquals(42L, rows.first()[Fixtures.TEST_FIELD])
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
            createPreDirectLoadTable(table)

            assertEquals(0L, client.getGenerationId(table))
        } finally {
            testClient.dropNamespace(namespace)
        }
    }
}
