/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.component

import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.TableSchemaEvolutionFixtures
import io.airbyte.cdk.load.component.TableSchemaEvolutionSuite
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.integrations.destination.databricksv2.client.DatabricksAirbyteClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"], resolveParameters = false)
class DatabricksTableSchemaEvolutionTest(
    override val client: DatabricksAirbyteClient,
    override val opsClient: DatabricksAirbyteClient,
    override val testClient: DatabricksTestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
) : TableSchemaEvolutionSuite {

    @Test
    fun `discover recognizes all data types`() {
        super.`discover recognizes all data types`(
            DatabricksComponentTestFixtures.allTypesTableSchema,
        )
    }

    @Test
    fun `computeSchema handles all data types`() {
        super.`computeSchema handles all data types`(
            DatabricksComponentTestFixtures.allTypesTableSchema,
        )
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
        super.`apply changeset`(
            TableSchemaEvolutionFixtures.APPLY_CHANGESET_INITIAL_COLUMN_MAPPING,
            TableSchemaEvolutionFixtures.APPLY_CHANGESET_MODIFIED_COLUMN_MAPPING,
            TableSchemaEvolutionFixtures.APPLY_CHANGESET_EXPECTED_EXTRACTED_AT,
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
