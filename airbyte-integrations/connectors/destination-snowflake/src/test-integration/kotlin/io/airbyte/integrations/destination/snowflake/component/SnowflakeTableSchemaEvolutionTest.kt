/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component

import io.airbyte.cdk.load.component.TableSchemaEvolutionFixtures
import io.airbyte.cdk.load.component.TableSchemaEvolutionSuite
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.component.SnowflakeComponentTestFixtures.allTypesColumnNameMapping
import io.airbyte.integrations.destination.snowflake.component.SnowflakeComponentTestFixtures.allTypesTableSchema
import io.airbyte.integrations.destination.snowflake.component.SnowflakeComponentTestFixtures.idAndTestMapping
import io.airbyte.integrations.destination.snowflake.component.SnowflakeComponentTestFixtures.testMapping
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@MicronautTest(environments = ["component"], resolveParameters = false)
@Execution(ExecutionMode.CONCURRENT)
class SnowflakeTableSchemaEvolutionTest(
    override val client: SnowflakeAirbyteClient,
    override val opsClient: SnowflakeAirbyteClient,
    override val testClient: SnowflakeTestTableOperationsClient,
) : TableSchemaEvolutionSuite {
    override val airbyteMetaColumnMapping = Meta.COLUMN_NAMES.associateWith { it.uppercase() }

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
    override fun `apply changeset - append-append`() {
        super.`apply changeset - append-append`()
    }

    @Test
    override fun `apply changeset - append-dedup`() {
        super.`apply changeset - append-dedup`()
    }

    @Test
    override fun `apply changeset - dedup-append`() {
        super.`apply changeset - dedup-append`()
    }

    @Test
    override fun `apply changeset - dedup-dedup`() {
        super.`apply changeset - dedup-dedup`()
    }

    override fun `apply changeset`(
        initialStreamIsDedup: Boolean,
        modifiedStreamIsDedup: Boolean,
    ) {
        super.`apply changeset`(
            initialColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "id" to "ID",
                        "updated_at" to "UPDATED_AT",
                        "to_retain" to "TO_RETAIN",
                        "to_change" to "TO_CHANGE",
                        "to_drop" to "TO_DROP",
                    )
                ),
            modifiedColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "id" to "ID",
                        "updated_at" to "UPDATED_AT",
                        "to_retain" to "TO_RETAIN",
                        "to_change" to "TO_CHANGE",
                        "to_add" to "TO_ADD",
                    )
                ),
            TableSchemaEvolutionFixtures.APPLY_CHANGESET_EXPECTED_EXTRACTED_AT,
            initialStreamIsDedup,
            modifiedStreamIsDedup,
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
