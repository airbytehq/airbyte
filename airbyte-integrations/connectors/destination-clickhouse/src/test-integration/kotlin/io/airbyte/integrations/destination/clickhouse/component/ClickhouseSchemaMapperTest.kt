/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.component

import io.airbyte.cdk.load.command.DestinationStreamFactory
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.component.SchemaMapperSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.schema.TableNameResolver
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

@MicronautTest(environments = ["component"])
class ClickhouseSchemaMapperTest(
    override val tableSchemaMapper: TableSchemaMapper,
    override val schemaFactory: TableSchemaFactory,
    override val opsClient: TableOperationsClient,
    override val streamFactory: DestinationStreamFactory,
    override val tableNameResolver: TableNameResolver,
    override val namespaceMapper: NamespaceMapper,
) : SchemaMapperSuite {
    @Test
    fun `simple table name`() {
        super.`simple table name`(TableName("namespace_test", "table_test"))
    }

    @Test
    fun `funky chars in table name`() {
        super.`funky chars in table name`(
            TableName(
                "namespace_test___________________________________",
                "table_test___________________________________"
            )
        )
    }

    @Test
    fun `table name starts with non-letter character`() {
        super.`table name starts with non-letter character`(TableName("_1foo", "_1foo"))
    }

    @Test
    fun `table name is reserved keyword`() {
        super.`table name is reserved keyword`(TableName("table", "table"))
    }

    @Test
    fun `simple temp table name`() {
        super.`simple temp table name`(TableName("foo", "foobar601b8ba9fdecdc2856c1983a55e6a8cf"))
    }

    @Test
    override fun `stream names avoid collisions`() {
        super.`stream names avoid collisions`()
    }

    @Test
    fun `simple column name`() {
        super.`simple column name`("column_test")
    }

    @Test
    fun `column name with funky chars`() {
        super.`column name with funky chars`("column_test___________________________________")
    }

    @Test
    fun `column name starts with non-letter character`() {
        super.`column name starts with non-letter character`("_1foo")
    }

    @Test
    fun `column name is reserved keyword`() {
        super.`column name is reserved keyword`("table")
    }

    @Test
    fun `column types support all airbyte types`() {
        super.`column types support all airbyte types`(
            ClickhouseTableSchemaEvolutionTest.allTypesSchema.columns
        )
    }

    @Test
    override fun `column names avoid collisions`() {
        super.`column names avoid collisions`()
    }
}
