/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component

import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.component.TableSchemaEvolutionFixtures
import io.airbyte.cdk.load.component.TableSchemaEvolutionSuite
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.util.serializeToString
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
            UNKNOWN_TO_STRING_TYPE_INPUT_RECORDS,
            TableSchemaEvolutionFixtures.UNKNOWN_TO_STRING_TYPE_EXPECTED_RECORDS,
        )
    }

    /**
     * [io.airbyte.integrations.destination.snowflake.write.transform.SnowflakeValueCoercer.map]
     * serializes union/unknownType values into strings, so that Snowflake understands how to parse
     * them from the CSV file. Emulate that behavior here.
     */
    private val UNKNOWN_TO_STRING_TYPE_INPUT_RECORDS =
        TableSchemaEvolutionFixtures.UNKNOWN_TO_STRING_TYPE_INPUT_RECORDS.map { record ->
            val mutableRecord = record.toMutableMap()
            mutableRecord["test"] = StringValue(record["test"].serializeToString())
            mutableRecord
        }
}
