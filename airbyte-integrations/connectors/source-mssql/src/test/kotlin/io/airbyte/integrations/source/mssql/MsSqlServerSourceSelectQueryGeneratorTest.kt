/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.And
import io.airbyte.cdk.read.Equal
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.FromSample
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
                        EmittedField("id", IntFieldType),
                        EmittedField("name", StringFieldType),
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
                SelectColumnMaxValue(EmittedField("updated_at", OffsetDateTimeFieldType)),
                From("orders", "dbo"),
            )
            .assertSqlEquals("""SELECT MAX([updated_at]) FROM [dbo].[orders]""")
    }

    @Test
    fun testSelectForNonResumableInitialSync() {
        SelectQuerySpec(
                SelectColumns(
                    listOf(
                        EmittedField("id", IntFieldType),
                        EmittedField("description", StringFieldType),
                    ),
                ),
                From("products", "dbo"),
            )
            .assertSqlEquals("""SELECT [id], [description] FROM [dbo].[products]""")
    }

    @Test
    fun testSelectForResumableInitialSync() {
        val k1 = EmittedField("pk1", IntFieldType)
        val v1 = Jsons.numberNode(100)
        val k2 = EmittedField("pk2", IntFieldType)
        val v2 = Jsons.numberNode(200)
        val k3 = EmittedField("pk3", IntFieldType)
        val v3 = Jsons.numberNode(300)
        SelectQuerySpec(
                SelectColumns(listOf(k1, k2, k3, EmittedField("data", StringFieldType))),
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
        val c = EmittedField("last_modified", DoubleFieldType)
        val lb = Jsons.numberNode(1.5)
        val ub = Jsons.numberNode(3.5)
        SelectQuerySpec(
                SelectColumns(listOf(EmittedField("content", StringFieldType), c)),
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
        val hierarchyField =
            EmittedField("org_node", MsSqlSourceOperations.MsSqlServerHierarchyFieldType)
        SelectQuerySpec(
                SelectColumns(
                    listOf(
                        EmittedField("employee_id", IntFieldType),
                        hierarchyField,
                        EmittedField("employee_name", StringFieldType),
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
                        EmittedField("col1", IntFieldType),
                        EmittedField("col2", StringFieldType),
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
        val cursor = EmittedField("sequence_id", LongFieldType)
        val startValue = Jsons.numberNode(1000000L)
        SelectQuerySpec(
                SelectColumns(listOf(cursor, EmittedField("payload", StringFieldType))),
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
        val created = EmittedField("created_at", OffsetDateTimeFieldType)
        val updated = EmittedField("updated_at", OffsetDateTimeFieldType)
        val createdAfter = Jsons.textNode("2025-01-01T00:00:00Z")
        val updatedBefore = Jsons.textNode("2025-12-31T23:59:59Z")

        SelectQuerySpec(
                SelectColumns(listOf(EmittedField("id", IntFieldType), created, updated)),
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
        val endField = EmittedField("End", OffsetDateTimeFieldType)
        val startField = EmittedField("Start", OffsetDateTimeFieldType)
        val orderField = EmittedField("Order", IntFieldType)

        SelectQuerySpec(
                SelectColumns(
                    listOf(EmittedField("Id", IntFieldType), startField, endField, orderField)
                ),
                From("CustomerAgreementProfiles", "dbo"),
                limit = Limit(100),
            )
            .assertSqlEquals(
                """SELECT TOP 100 [Id], [Start], [End], [Order] FROM [dbo].[CustomerAgreementProfiles]"""
            )
    }

    @Test
    fun testSamplingQueryProjectsExplicitColumns() {
        // Regression test for https://github.com/airbytehq/oncall/issues/12048:
        // the inner TABLESAMPLE subquery must project the same explicit column list as the outer
        // SELECT, not `*`. Otherwise HIDDEN columns on system-versioned temporal tables
        // (PERIOD FOR SYSTEM_TIME) are dropped from the derived table and the outer SELECT fails
        // with "Invalid column name".
        val id = EmittedField("id", IntFieldType)
        val name = EmittedField("name", StringFieldType)
        SelectQuerySpec(
                SelectColumns(listOf(id, name)),
                FromSample(
                    name = "users",
                    namespace = "dbo",
                    sampleRateInvPow2 = 6,
                    sampleSize = 1024,
                ),
                orderBy = OrderBy(listOf(id)),
                limit = Limit(1024),
            )
            .assertSqlEquals(
                """SELECT TOP 1024 [id], [name] FROM """ +
                    """(SELECT TOP 1024 [id], [name] FROM [dbo].[users] """ +
                    """TABLESAMPLE (1.562500 PERCENT)  ORDER BY NEWID()) AS randomly_sampled """ +
                    """ORDER BY [id]""",
            )
    }

    @Test
    fun testSamplingQueryWithHierarchyIdProjectsRawColumn() {
        // Regression test: the inner TABLESAMPLE subquery must project the raw hierarchyid
        // column (e.g. `[org_node]`) rather than `[org_node].ToString()`. If the inner subquery
        // projected the transformed expression, SQL Server would reject the query with
        // "No column name was specified for column N of 'randomly_sampled'", and the outer
        // SELECT (which calls `.ToString()` itself) would have no raw column to reference.
        val employeeId = EmittedField("employee_id", IntFieldType)
        val orgNode = EmittedField("org_node", MsSqlSourceOperations.MsSqlServerHierarchyFieldType)
        SelectQuerySpec(
                SelectColumns(listOf(employeeId, orgNode)),
                FromSample(
                    name = "employees",
                    namespace = "hr",
                    sampleRateInvPow2 = 5,
                    sampleSize = 512,
                ),
                orderBy = OrderBy(listOf(employeeId)),
                limit = Limit(512),
            )
            .assertSqlEquals(
                """SELECT TOP 512 [employee_id], [org_node].ToString() FROM """ +
                    """(SELECT TOP 512 [employee_id], [org_node] FROM [hr].[employees] """ +
                    """TABLESAMPLE (3.12500 PERCENT)  ORDER BY NEWID()) AS randomly_sampled """ +
                    """ORDER BY [employee_id]""",
            )
    }

    @Test
    fun testSamplingQueryIncludesHiddenTemporalColumns() {
        // Simulates a catalog for a SQL Server system-versioned temporal table where the user has
        // selected the HIDDEN period columns (HistoryStart/HistoryEnd) explicitly. The generated
        // SQL must name those columns in both the inner sample subquery and the outer SELECT so
        // that SELECT * in the inner query does not drop them.
        val id = EmittedField("Id", IntFieldType)
        val payload = EmittedField("Payload", StringFieldType)
        val historyStart = EmittedField("HistoryStart", OffsetDateTimeFieldType)
        val historyEnd = EmittedField("HistoryEnd", OffsetDateTimeFieldType)
        val sql =
            SelectQuerySpec(
                    SelectColumns(listOf(id, payload, historyStart, historyEnd)),
                    FromSample(
                        name = "TemporalRecords",
                        namespace = "dbo",
                        sampleRateInvPow2 = 7,
                        sampleSize = 2048,
                    ),
                    orderBy = OrderBy(listOf(id)),
                    limit = Limit(2048),
                )
                .let { MsSqlSourceOperations().generate(it.optimize()).sql }
        // Both the inner and outer projections must name the HIDDEN columns explicitly.
        Assertions.assertTrue(sql.contains("[HistoryStart]")) {
            "Expected HistoryStart column to appear in generated SQL: $sql"
        }
        Assertions.assertTrue(sql.contains("[HistoryEnd]")) {
            "Expected HistoryEnd column to appear in generated SQL: $sql"
        }
        // Guard against regression: the inner sample subquery must not use SELECT *.
        Assertions.assertFalse(sql.contains("SELECT TOP 2048 *")) {
            "Inner sample subquery must not project * (it drops HIDDEN columns): $sql"
        }
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
