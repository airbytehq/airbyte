/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.jdbc.DoubleFieldType
import io.airbyte.cdk.jdbc.IntFieldType
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
                        Field("k", IntFieldType),
                        Field("v", StringFieldType),
                    ),
                ),
                From("TBL", "SC"),
                limit = Limit(0),
            )
            .assertSqlEquals("""SELECT TOP 0 k, v FROM SC.TBL""")
    }

    @Test
    fun testSelectMaxCursor() {
        SelectQuerySpec(
                SelectColumnMaxValue(Field("ts", OffsetDateTimeFieldType)),
                From("TBL", "SC"),
            )
            .assertSqlEquals("""SELECT MAX(ts) FROM SC.TBL""")
    }

    @Test
    fun testSelectForNonResumableInitialSync() {
        SelectQuerySpec(
                SelectColumns(
                    listOf(
                        Field("k", IntFieldType),
                        Field("v", StringFieldType),
                    ),
                ),
                From("TBL", "SC"),
            )
            .assertSqlEquals("""SELECT k, v FROM SC.TBL""")
    }

    @Test
    fun testSelectForResumableInitialSync() {
        val k1 = Field("k1", IntFieldType)
        val v1 = Jsons.numberNode(10)
        val k2 = Field("k2", IntFieldType)
        val v2 = Jsons.numberNode(20)
        val k3 = Field("k3", IntFieldType)
        val v3 = Jsons.numberNode(30)
        SelectQuerySpec(
                SelectColumns(listOf(k1, k2, k3, Field("msg", StringFieldType))),
                From("TBL", "SC"),
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
                """SELECT TOP 1000 k1, k2, k3, msg FROM """ +
                    """SC.TBL WHERE (k1 > ?) OR """ +
                    """((k1 = ?) AND (k2 > ?)) OR """ +
                    """((k1 = ?) AND (k2 = ?) AND (k3 > ?)) """ +
                    """ORDER BY k1, k2, k3""",
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
        val c = Field("c", DoubleFieldType)
        val lb = Jsons.numberNode(0.5)
        val ub = Jsons.numberNode(0.5)
        SelectQuerySpec(
                SelectColumns(listOf(Field("msg", StringFieldType), c)),
                From("TBL", "SC"),
                Where(And(listOf(Greater(c, lb), LesserOrEqual(c, ub)))),
                OrderBy(listOf(c)),
                Limit(1000),
            )
            .assertSqlEquals(
                """SELECT TOP 1000 msg, c FROM """ +
                    """SC.TBL """ +
                    """WHERE (c > ?) AND (c <= ?) ORDER BY c""",
                lb to DoubleFieldType,
                ub to DoubleFieldType,
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
        val actual: SelectQuery = MsSqlServerSelectQueryGenerator().generate(this.optimize())
        Assertions.assertEquals(expected, actual)
    }
}
