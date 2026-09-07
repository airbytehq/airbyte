/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.component

import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.TableSchemaEvolutionFixtures
import io.airbyte.cdk.load.component.TableSchemaEvolutionSuite
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.integrations.destination.redshift_v2.client.RedshiftAirbyteClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@MicronautTest(environments = ["component"])
@Execution(ExecutionMode.CONCURRENT)
class RedshiftTableSchemaEvolutionTest(
    override val client: RedshiftAirbyteClient,
    override val opsClient: RedshiftAirbyteClient,
    override val testClient: RedshiftTestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
) : TableSchemaEvolutionSuite {
    // Redshift uses lowercase column names
    override val airbyteMetaColumnMapping = Meta.COLUMN_NAMES.associateWith { it }

    @Test
    fun `discover recognizes all data types`() {
        super.`discover recognizes all data types`(
            RedshiftComponentTestFixtures.allTypesTableSchema,
            RedshiftComponentTestFixtures.allTypesColumnNameMapping
        )
    }

    @Test
    fun `computeSchema handles all data types`() {
        super.`computeSchema handles all data types`(
            RedshiftComponentTestFixtures.allTypesTableSchema,
            RedshiftComponentTestFixtures.allTypesColumnNameMapping
        )
    }

    @Test
    override fun `noop diff`() {
        super.`noop diff`(RedshiftComponentTestFixtures.testMapping)
    }

    @Test
    override fun `changeset is correct when adding a column`() {
        super.`changeset is correct when adding a column`(
            RedshiftComponentTestFixtures.testMapping,
            RedshiftComponentTestFixtures.idAndTestMapping
        )
    }

    @Test
    override fun `changeset is correct when dropping a column`() {
        super.`changeset is correct when dropping a column`(
            RedshiftComponentTestFixtures.idAndTestMapping,
            RedshiftComponentTestFixtures.testMapping
        )
    }

    @Test
    override fun `changeset is correct when changing a column's type`() {
        super.`changeset is correct when changing a column's type`(
            RedshiftComponentTestFixtures.testMapping
        )
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
        // Redshift uses lowercase column names
        super.`apply changeset`(
            initialColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "id" to "id",
                        "updated_at" to "updated_at",
                        "to_retain" to "to_retain",
                        "to_change" to "to_change",
                        "to_drop" to "to_drop",
                    )
                ),
            modifiedColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "id" to "id",
                        "updated_at" to "updated_at",
                        "to_retain" to "to_retain",
                        "to_change" to "to_change",
                        "to_add" to "to_add",
                    )
                ),
            TableSchemaEvolutionFixtures.APPLY_CHANGESET_EXPECTED_EXTRACTED_AT,
            initialStreamImportType,
            modifiedStreamImportType,
        )
    }

    @Test
    override fun `change from string type to unknown type`() {
        super.`change from string type to unknown type`(
            RedshiftComponentTestFixtures.idAndTestMapping,
            RedshiftComponentTestFixtures.idAndTestMapping,
            TableSchemaEvolutionFixtures.STRING_TO_UNKNOWN_TYPE_INPUT_RECORDS,
            TableSchemaEvolutionFixtures.STRING_TO_UNKNOWN_TYPE_EXPECTED_RECORDS,
        )
    }

    @Test
    override fun `change from unknown type to string type`() {
        super.`change from unknown type to string type`(
            RedshiftComponentTestFixtures.idAndTestMapping,
            RedshiftComponentTestFixtures.idAndTestMapping,
            UNKNOWN_TO_STRING_TYPE_INPUT_RECORDS,
            UNKNOWN_TO_STRING_TYPE_EXPECTED_RECORDS,
        )
    }

    /**
     * Redshift stores UnknownType as SUPER (JSON). When converting from UnknownType to StringType,
     * the values need to be serialized to strings.
     */
    private val UNKNOWN_TO_STRING_TYPE_INPUT_RECORDS =
        TableSchemaEvolutionFixtures.UNKNOWN_TO_STRING_TYPE_INPUT_RECORDS.map { record ->
            val mutableRecord = record.toMutableMap()
            mutableRecord["test"] = StringValue(record["test"].serializeToString())
            mutableRecord
        }

    /**
     * When Redshift CASTs SUPER (JSON) to VARCHAR, string values are preserved with JSON quoting.
     * So a JSON string "foo" becomes the VARCHAR value "foo" (with quotes).
     */
    private val UNKNOWN_TO_STRING_TYPE_EXPECTED_RECORDS =
        listOf(
            // String value "foo" in SUPER becomes "\"foo\"" when cast to VARCHAR
            mapOf("id" to 1L, "test" to "\"foo\""),
            // Object stays as JSON representation
            mapOf("id" to 2L, "test" to """{"foo":"bar"}"""),
            // Boolean stays as string representation
            mapOf("id" to 3L, "test" to "true"),
            // Integer stays as string representation
            mapOf("id" to 4L, "test" to "0"),
        )
}
