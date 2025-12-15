/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component

import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.TableSchemaEvolutionFixtures
import io.airbyte.cdk.load.component.TableSchemaEvolutionSuite
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.component.PostgresComponentTestFixtures.allTypesColumnNameMapping
import io.airbyte.integrations.destination.postgres.component.PostgresComponentTestFixtures.allTypesTableSchema
import io.airbyte.integrations.destination.postgres.component.PostgresComponentTestFixtures.idAndTestMapping
import io.airbyte.integrations.destination.postgres.component.PostgresComponentTestFixtures.testMapping
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"], resolveParameters = false)
class PostgresTableSchemaEvolutionTest(
    override val client: PostgresAirbyteClient,
    override val opsClient: PostgresAirbyteClient,
    override val testClient: PostgresTestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
) : TableSchemaEvolutionSuite {

    @Test
    fun `discover recognizes all data types`() {
        super.`discover recognizes all data types`(allTypesTableSchema, allTypesColumnNameMapping)
    }

    @Test
    fun `computeSchema handles all data types`() {
        super.`computeSchema handles all data types`(allTypesTableSchema, allTypesColumnNameMapping)
    }

    @Test
    override fun `noop diff`() {
        super.`noop diff`(testMapping)
    }

    @Test
    override fun `changeset is correct when adding a column`() {
        super.`changeset is correct when adding a column`(testMapping, idAndTestMapping)
    }

    @Test
    override fun `changeset is correct when dropping a column`() {
        super.`changeset is correct when dropping a column`(idAndTestMapping, testMapping)
    }

    @Test
    override fun `changeset is correct when changing a column's type`() {
        super.`changeset is correct when changing a column's type`(testMapping)
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
            initialColumnNameMapping =
                TableSchemaEvolutionFixtures.APPLY_CHANGESET_INITIAL_COLUMN_MAPPING,
            modifiedColumnNameMapping =
                TableSchemaEvolutionFixtures.APPLY_CHANGESET_MODIFIED_COLUMN_MAPPING,
            TableSchemaEvolutionFixtures.APPLY_CHANGESET_EXPECTED_EXTRACTED_AT,
            initialStreamImportType,
            modifiedStreamImportType,
        )
    }

    @Test
    override fun `change from string type to unknown type`() {
        super.`change from string type to unknown type`(
            idAndTestMapping,
            idAndTestMapping,
            TableSchemaEvolutionFixtures.STRING_TO_UNKNOWN_TYPE_INPUT_RECORDS,
            TableSchemaEvolutionFixtures.STRING_TO_UNKNOWN_TYPE_EXPECTED_RECORDS,
        )
    }

    @Test
    override fun `change from unknown type to string type`() {
        super.`change from unknown type to string type`(
            idAndTestMapping,
            idAndTestMapping,
            TableSchemaEvolutionFixtures.UNKNOWN_TO_STRING_TYPE_INPUT_RECORDS,
            TableSchemaEvolutionFixtures.UNKNOWN_TO_STRING_TYPE_EXPECTED_RECORDS,
        )
    }
}
