/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component

import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionFixtures
import io.airbyte.cdk.load.component.TableSchemaEvolutionSuite
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"], resolveParameters = false)
class PostgresTableSchemaEvolutionTest(
    override val client: TableSchemaEvolutionClient,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient
) : TableSchemaEvolutionSuite {

    // PostgreSQL type mappings based on PostgresColumnUtils.toDialectType()
    private val allTypesTableSchema =
        TableSchema(
            mapOf(
                "string" to ColumnType("varchar", true),
                "boolean" to ColumnType("boolean", true),
                "integer" to ColumnType("bigint", true),
                "number" to ColumnType("decimal", true),
                "date" to ColumnType("date", true),
                "timestamp_tz" to ColumnType("timestamp with time zone", true),
                "timestamp_ntz" to ColumnType("timestamp", true),
                "time_tz" to ColumnType("time with time zone", true),
                "time_ntz" to ColumnType("time", true),
                "array" to ColumnType("jsonb", true),
                "object" to ColumnType("jsonb", true),
                "unknown" to ColumnType("jsonb", true),
            )
        )

    @Test
    fun `discover recognizes all data types`() {
        super.`discover recognizes all data types`(allTypesTableSchema)
    }

    @Test
    fun `computeSchema handles all data types`() {
        super.`computeSchema handles all data types`(allTypesTableSchema)
    }

    @Test
    override fun `noop diff`() {
        super.`noop diff`()
    }

    @Test
    override fun `changeset is correct when adding a column`() {
        super.`changeset is correct when adding a column`()
    }

    @Test
    override fun `changeset is correct when dropping a column`() {
        super.`changeset is correct when dropping a column`()
    }

    @Test
    override fun `changeset is correct when changing a column's type`() {
        super.`changeset is correct when changing a column's type`()
    }

    @Test
    override fun `apply changeset - handle sync mode append`() {
        super.`apply changeset - handle sync mode append`()
    }

    @Test
    override fun `apply changeset - handle changing sync mode from append to dedup`() {
        super.`apply changeset - handle changing sync mode from append to dedup`()
    }

    @Test
    override fun `apply changeset - handle changing sync mode from dedup to append`() {
        super.`apply changeset - handle changing sync mode from dedup to append`()
    }

    @Test
    override fun `apply changeset - handle sync mode dedup`() {
        super.`apply changeset - handle sync mode dedup`()
    }

    override fun `apply changeset`(
        initialStreamImportType: ImportType,
        modifiedStreamImportType: ImportType,
    ) {
        `apply changeset`(
            TableSchemaEvolutionFixtures.APPLY_CHANGESET_INITIAL_COLUMN_MAPPING,
            TableSchemaEvolutionFixtures.APPLY_CHANGESET_MODIFIED_COLUMN_MAPPING,
            expectedExtractedAt = "2025-01-22T00:00:00Z",
            initialStreamImportType,
            modifiedStreamImportType,
        )
    }

    @Test
    override fun `change from string type to unknown type`() {
        super.`change from string type to unknown type`()
    }

    @Test
    override fun `change from unknown type to string type`() {
        super.`change from unknown type to string type`()
    }
}
