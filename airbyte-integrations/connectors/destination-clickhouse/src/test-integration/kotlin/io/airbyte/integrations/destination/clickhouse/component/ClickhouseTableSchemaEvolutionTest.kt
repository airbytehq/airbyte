/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TableSchema
import io.airbyte.cdk.load.component.TableSchemaEvolutionClient
import io.airbyte.cdk.load.component.TableSchemaEvolutionSuite
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

@MicronautTest(environments = ["component"], resolveParameters = false)
class ClickhouseTableSchemaEvolutionTest(
    override val client: TableSchemaEvolutionClient,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient
) : TableSchemaEvolutionSuite {
    private val allTypesTableSchema =
        TableSchema(
            mapOf(
                "string" to ColumnType("String", true),
                "boolean" to ColumnType("Bool", true),
                "integer" to ColumnType("Int64", true),
                "number" to ColumnType("Decimal(38, 9)", true),
                "date" to ColumnType("Date32", true),
                "timestamp_tz" to ColumnType("DateTime64(3)", true),
                "timestamp_ntz" to ColumnType("DateTime64(3)", true),
                "time_tz" to ColumnType("String", true),
                "time_ntz" to ColumnType("String", true),
                // yes, these three are different
                "array" to ColumnType("String", true),
                "object" to ColumnType("JSON", true),
                "unknown" to ColumnType("String", true),
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

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.TableSchemaEvolutionSuite#applyChangesetArguments")
    override fun `apply changeset`(
        initialStreamIsDedup: Boolean,
        modifiedStreamIsDedup: Boolean,
    ) {
        super.`apply changeset`(
            initialStreamIsDedup,
            modifiedStreamIsDedup,
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
