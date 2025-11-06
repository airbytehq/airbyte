/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionSuite
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@Execution(ExecutionMode.CONCURRENT)
class SnowflakeTableSchemaEvolutionTest(
    override val client: SnowflakeAirbyteClient,
    override val opsClient: SnowflakeAirbyteClient,
    override val testClient: SnowflakeTestTableOperationsClient,
) : TableSchemaEvolutionSuite {
    override val airbyteMetaColumnMapping = Meta.COLUMN_NAMES.associateWith { it.uppercase() }

    private val allTypesTableSchema =
        TableSchema(
            mapOf(
                "string" to ColumnType("VARCHAR", true),
                "boolean" to ColumnType("BOOLEAN", true),
                // NUMBER == NUMBER(38, 0)
                "integer" to ColumnType("NUMBER", true),
                // we use FLOAT instead of NUMBER(38, 9) for historical reasons
                "number" to ColumnType("FLOAT", true),
                "date" to ColumnType("DATE", true),
                "timestamp_tz" to ColumnType("TIMESTAMP_TZ", true),
                "timestamp_ntz" to ColumnType("TIMESTAMP_NTZ", true),
                "time_tz" to ColumnType("VARCHAR", true),
                "time_ntz" to ColumnType("TIME", true),
                "array" to ColumnType("ARRAY", true),
                "object" to ColumnType("OBJECT", true),
                "unknown" to ColumnType("VARIANT", true),
            )
        )

    @Test
    fun discover() {
        super.discover(allTypesTableSchema)
    }

    @Test
    fun computeSchema() {
        super.computeSchema(allTypesTableSchema)
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
    override fun `basic apply changeset`() {
        super.`basic apply changeset`(
            initialColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "to_retain" to "TO_RETAIN",
                        "to_change" to "TO_CHANGE",
                        "to_drop" to "TO_DROP",
                    )
                ),
            modifiedColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "to_retain" to "TO_RETAIN",
                        "to_change" to "TO_CHANGE",
                        "to_add" to "TO_ADD",
                    )
                ),
        )
    }
}
