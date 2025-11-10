/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.Equal
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.LesserOrEqual
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.Or
import io.airbyte.cdk.read.OrderBy
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MsSqlServerSourceSelectQueryGeneratorTest {
    @Test
    fun testSelectLimit0() {
        SelectQuerySpec(
                SelectColumns(
                    listOf(
                        Field("id", IntFieldType),
                        Field("name", StringFieldType),
                    ),
                ),
                From("users", "dbo"),
                limit = Limit(0),
            )
            .assertSqlEquals("""SELECT TOP 0 [id], [name] FROM [dbo].[users]""")
    }

    @Test
    fun testSelectMaxCursor() {
        SelectQuerySpec(
                SelectColumnMaxValue(Field("updated_at", OffsetDateTimeFieldType)),
                From("orders", "dbo"),
            )
            .assertSqlEquals("""SELECT MAX([updated_at]) FROM [dbo].[orders]""")
    }

    @Test
    fun testSelectForNonResumableInitialSync() {
        SelectQuerySpec(
                SelectColumns(
                    listOf(
                        Field("id", IntFieldType),
                        Field("description", StringFieldType),
                    ),
                ),
                From("products", "dbo"),
            )
            .assertSqlEquals("""SELECT [id], [description] FROM [dbo].[products]""")
    }

    @Test
    fun testSelectForResumableInitialSync() {
        val k1 = Field("pk1", IntFieldType)
        val v1 = Jsons.numberNode(100)
        val k2 = Field("pk2", IntFieldType)
        val v2 = Jsons.numberNode(200)
        val k3 = Field("pk3", IntFieldType)
        val v3 = Jsons.numberNode(300)
        SelectQuerySpec(
                SelectColumns(listOf(k1, k2, k3, Field("data", StringFieldType))),
                From("composite_table", "dbo"),
                Where(
                    Or(
                        listOf(
                            And(listOf(Greater(k1, v1))),
                            And(listOf(Equal(k1, v1), Greater(k2, v2))),
                            And(listOf(Equal(k1, v1), Equal(k2, v2), Greater(k3, v3))),
                        ),
                    ),
                ),
                OrderBy(listOf(k1, k2, k3)),
                Limit(1000),
            )
            .assertSqlEquals(
                """SELECT TOP 1000 [pk1], [pk2], [pk3], [data] FROM """ +
                    """[dbo].[composite_table] WHERE ([pk1] > ?) OR """ +
                    """(([pk1] = ?) AND ([pk2] > ?)) OR """ +
                    """(([pk1] = ?) AND ([pk2] = ?) AND ([pk3] > ?)) """ +
                    """ORDER BY [pk1], [pk2], [pk3]""",
                v1 to IntFieldType,
                v1 to IntFieldType,
                v2 to IntFieldType,
                v1 to IntFieldType,
                v2 to IntFieldType,
                v3 to IntFieldType,
            )
    }

    @Test
    fun testSelectForCursorBasedIncrementalSync() {
        val c = Field("last_modified", DoubleFieldType)
        val lb = Jsons.numberNode(1.5)
        val ub = Jsons.numberNode(3.5)
        SelectQuerySpec(
                SelectColumns(listOf(Field("content", StringFieldType), c)),
                From("documents", "dbo"),
                Where(And(listOf(Greater(c, lb), LesserOrEqual(c, ub)))),
                OrderBy(listOf(c)),
                Limit(500),
            )
            .assertSqlEquals(
                """SELECT TOP 500 [content], [last_modified] FROM """ +
                    """[dbo].[documents] """ +
                    """WHERE ([last_modified] > ?) AND ([last_modified] <= ?) ORDER BY [last_modified]""",
                lb to DoubleFieldType,
                ub to DoubleFieldType,
            )
    }

    @Test
    fun testSelectWithHierarchyId() {
        // Test special handling for hierarchyid field type in SQL Server
        val hierarchyField = Field("org_node", MsSqlSourceOperations.MsSqlServerHierarchyFieldType)
        SelectQuerySpec(
                SelectColumns(
                    listOf(
                        Field("employee_id", IntFieldType),
                        hierarchyField,
                        Field("employee_name", StringFieldType),
                    ),
                ),
                From("employees", "hr"),
            )
            .assertSqlEquals(
                """SELECT [employee_id], [org_node].ToString(), [employee_name] FROM [hr].[employees]"""
            )
    }

    @Test
    fun testSelectWithoutNamespace() {
        // Test query generation without namespace (schema)
        SelectQuerySpec(
                SelectColumns(
                    listOf(
                        Field("col1", IntFieldType),
                        Field("col2", StringFieldType),
                    ),
                ),
                From("simple_table", null),
                limit = Limit(10),
            )
            .assertSqlEquals("""SELECT TOP 10 [col1], [col2] FROM [simple_table]""")
    }

    @Test
    fun testSelectWithLargeLimit() {
        // Test with a large limit value
        val cursor = Field("sequence_id", LongFieldType)
        val startValue = Jsons.numberNode(1000000L)
        SelectQuerySpec(
                SelectColumns(listOf(cursor, Field("payload", StringFieldType))),
                From("events", "dbo"),
                Where(Greater(cursor, startValue)),
                OrderBy(listOf(cursor)),
                Limit(10000),
            )
            .assertSqlEquals(
                """SELECT TOP 10000 [sequence_id], [payload] FROM [dbo].[events] WHERE [sequence_id] > ? ORDER BY [sequence_id]""",
                startValue to LongFieldType,
            )
    }

    @Test
    fun testSelectWithMultipleDateTimeFields() {
        // Test with multiple datetime fields for time-based filtering
        val created = Field("created_at", OffsetDateTimeFieldType)
        val updated = Field("updated_at", OffsetDateTimeFieldType)
        val createdAfter = Jsons.textNode("2025-01-01T00:00:00Z")
        val updatedBefore = Jsons.textNode("2025-12-31T23:59:59Z")

        SelectQuerySpec(
                SelectColumns(listOf(Field("id", IntFieldType), created, updated)),
                From("records", "dbo"),
                Where(
                    And(
                        listOf(
                            Greater(created, createdAfter),
                            LesserOrEqual(updated, updatedBefore)
                        )
                    )
                ),
                OrderBy(listOf(created, updated)),
                Limit(100),
            )
            .assertSqlEquals(
                """SELECT TOP 100 [id], [created_at], [updated_at] FROM [dbo].[records] """ +
                    """WHERE ([created_at] > ?) AND ([updated_at] <= ?) ORDER BY [created_at], [updated_at]""",
                createdAfter to OffsetDateTimeFieldType,
                updatedBefore to OffsetDateTimeFieldType,
            )
    }

    @Test
    fun testSelectWithReservedKeywords() {
        // Test with reserved SQL Server keywords as column names (e.g., "End", "Start")
        val endField = Field("End", OffsetDateTimeFieldType)
        val startField = Field("Start", OffsetDateTimeFieldType)
        val orderField = Field("Order", IntFieldType)

        SelectQuerySpec(
                SelectColumns(listOf(Field("Id", IntFieldType), startField, endField, orderField)),
                From("CustomerAgreementProfiles", "dbo"),
                limit = Limit(100),
            )
            .assertSqlEquals(
                """SELECT TOP 100 [Id], [Start], [End], [Order] FROM [dbo].[CustomerAgreementProfiles]"""
            )
    }

    private fun SelectQuerySpec.assertSqlEquals(
        sql: String,
        vararg bindings: Pair<JsonNode, LosslessJdbcFieldType<*, *>>,
    ) {
        val expected =
            SelectQuery(
                sql,
                select.columns,
                bindings.map { SelectQuery.Binding(it.first, it.second) },
            )
        val actual: SelectQuery = MsSqlSourceOperations().generate(this.optimize())
        Assertions.assertEquals(expected, actual)
    }
}
