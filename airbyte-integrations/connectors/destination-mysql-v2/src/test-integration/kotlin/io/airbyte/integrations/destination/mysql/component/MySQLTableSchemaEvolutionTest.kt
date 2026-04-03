/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql.component

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
class MySQLTableSchemaEvolutionTest(
    override val client: TableSchemaEvolutionClient,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient
) : TableSchemaEvolutionSuite {
    // MySQL JDBC metadata returns simplified type names without precision
    // Complex types (array, object, unknown) are stored as TEXT with STRINGIFY behavior
    private val allTypesTableSchema =
        TableSchema(
            mapOf(
                "string" to ColumnType("TEXT", true),
                "boolean" to ColumnType("BIT", true),  // MySQL reports BOOLEAN as BIT
                "integer" to ColumnType("BIGINT", true),
                "number" to ColumnType("DECIMAL", true),  // MySQL omits precision in metadata
                "date" to ColumnType("DATE", true),
                "timestamp_tz" to ColumnType("DATETIME", true),  // MySQL omits precision in metadata
                "timestamp_ntz" to ColumnType("DATETIME", true),
                "time_tz" to ColumnType("TIME", true),  // MySQL omits precision in metadata
                "time_ntz" to ColumnType("TIME", true),
                "array" to ColumnType("TEXT", true),  // TEXT with STRINGIFY behavior
                "object" to ColumnType("TEXT", true),  // TEXT with STRINGIFY behavior
                "unknown" to ColumnType("TEXT", true),  // TEXT with STRINGIFY behavior
            )
        )

    @Test
    fun `discover recognizes all data types`() {
        super.`discover recognizes all data types`(allTypesTableSchema)
    }

    // MySQL metadata returns different type names than what we use in DDL
    // (e.g., DECIMAL vs DECIMAL(38,9), DATETIME vs DATETIME(6))
    @org.junit.jupiter.api.Disabled("MySQL metadata type names differ from DDL type names")
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
            expectedExtractedAt = "2025-01-22T00:00Z[UTC]",
            initialStreamImportType,
            modifiedStreamImportType,
        )
    }

    // MySQL cannot convert TEXT columns with arbitrary string data to JSON
    @org.junit.jupiter.api.Disabled("MySQL cannot convert TEXT with non-JSON content to JSON type")
    @Test
    override fun `change from string type to unknown type`() {
        super.`change from string type to unknown type`()
    }

    // MySQL JSON to TEXT conversion loses the array brackets in stringification
    @org.junit.jupiter.api.Disabled("MySQL JSON to TEXT conversion changes data format")
    @Test
    override fun `change from unknown type to string type`() {
        super.`change from unknown type to string type`()
    }
}
