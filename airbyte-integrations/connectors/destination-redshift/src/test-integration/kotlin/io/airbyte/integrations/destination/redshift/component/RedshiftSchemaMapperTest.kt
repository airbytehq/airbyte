/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.component

import io.airbyte.cdk.load.command.DestinationStreamFactory
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.component.SchemaMapperSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.schema.TableNameResolver
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.schema.TableSchemaMapper
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.redshift.sql.RedshiftDataType
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test

/**
 * Schema mapper integration test for Redshift. Validates table name resolution, column name
 * resolution, collision avoidance, and type mapping against a live Redshift instance
 */
@MicronautTest(environments = ["component"])
class RedshiftSchemaMapperTest(
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
                "table_test___________________________________",
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
        super.`column types support all airbyte types`(EXPECTED_ALL_TYPES)
    }

    @Test
    override fun `column names avoid collisions`() {
        super.`column names avoid collisions`()
    }

    companion object {
        /**
         * Expected type mapping for all Airbyte types as produced by
         * [RedshiftTableSchemaMapper.toColumnType]. Must match the actual mapper output exactly.
         */
        val EXPECTED_ALL_TYPES =
            mapOf(
                "string" to ColumnType(RedshiftDataType.VARCHAR.typeName, true),
                "boolean" to ColumnType(RedshiftDataType.BOOLEAN.typeName, true),
                "integer" to ColumnType(RedshiftDataType.BIGINT.typeName, true),
                "number" to ColumnType(RedshiftDataType.NUMERIC.typeName, true),
                "date" to ColumnType(RedshiftDataType.DATE.typeName, true),
                "timestamp_tz" to ColumnType(RedshiftDataType.TIMESTAMPTZ.typeName, true),
                "timestamp_ntz" to ColumnType(RedshiftDataType.TIMESTAMP.typeName, true),
                "time_tz" to ColumnType(RedshiftDataType.TIMETZ.typeName, true),
                "time_ntz" to ColumnType(RedshiftDataType.TIME.typeName, true),
                "array" to ColumnType(RedshiftDataType.SUPER.typeName, true),
                "object" to ColumnType(RedshiftDataType.SUPER.typeName, true),
                "union" to ColumnType(RedshiftDataType.VARCHAR.typeName, true),
                "legacy_union" to ColumnType(RedshiftDataType.VARCHAR.typeName, true),
                "unknown" to ColumnType(RedshiftDataType.VARCHAR.typeName, true),
            )
    }
}
