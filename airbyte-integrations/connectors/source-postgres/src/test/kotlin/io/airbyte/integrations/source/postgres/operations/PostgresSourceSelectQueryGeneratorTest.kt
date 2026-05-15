/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres.operations

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.OffsetDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.Limit
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectColumns
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class PostgresSourceSelectQueryGeneratorTest {
    @Test
    fun testSelectLimit0() {
        SelectQuerySpec(
                SelectColumns(
                    listOf(
                        EmittedField("id", IntFieldType),
                        EmittedField("name", StringFieldType),
                    ),
                ),
                From("users", "public"),
                limit = Limit(0),
            )
            .assertSqlEquals("""SELECT "id", "name" FROM "public"."users" LIMIT 0""")
    }

    @Test
    fun testSelectMaxCursorUsesOrderingForTimestamp() {
        SelectQuerySpec(
                SelectColumnMaxValue(EmittedField("updated_at", OffsetDateTimeFieldType)),
                From("orders", "public"),
            )
            .assertSqlEquals(
                """SELECT "updated_at" FROM "public"."orders" ORDER BY "updated_at" DESC NULLS LAST LIMIT 1"""
            )
    }

    @Test
    fun testSelectMaxCursorUsesOrderingForUuidMappedAsString() {
        SelectQuerySpec(
                SelectColumnMaxValue(EmittedField("id", StringFieldType)),
                From("user_steps_metric_aggregations", "public"),
            )
            .assertSqlEquals(
                """SELECT "id" FROM "public"."user_steps_metric_aggregations" ORDER BY "id" DESC NULLS LAST LIMIT 1"""
            )
    }

    @Test
    fun testSelectMaxCursorWithWhereClause() {
        val cursor = EmittedField("id", StringFieldType)
        val lowerBound = Jsons.textNode("00000000-0000-0000-0000-000000000001")
        SelectQuerySpec(
                SelectColumnMaxValue(cursor),
                From("user_steps_metric_aggregations", "public"),
                Where(Greater(cursor, lowerBound)),
            )
            .assertSqlEquals(
                """SELECT "id" FROM "public"."user_steps_metric_aggregations" WHERE "id" > ? ORDER BY "id" DESC NULLS LAST LIMIT 1""",
                lowerBound to StringFieldType,
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
        val actual = PostgresSourceSelectQueryGenerator().generate(this.optimize())
        Assertions.assertEquals(expected, actual)
    }
}
