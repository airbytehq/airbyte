/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.LongFieldType
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.Greater
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.Where
import io.airbyte.cdk.read.optimize
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator
import io.airbyte.integrations.source.postgres.operations.types.PostgresUuidFieldType
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class PostgresSourceSelectQueryGeneratorTest {
    private val uuidCursor = EmittedField("cursor_col", PostgresUuidFieldType)
    private val stringCursor = EmittedField("cursor_col", StringFieldType)
    private val from = From("TBL", "SC")

    @Test
    fun uuidCursorUpperBoundIsReadByOrderingWithNotNullPredicate() {
        // The IS NOT NULL predicate and the absence of NULLS LAST are what let Postgres answer
        // this with a backward index scan; see PostgresSourceSelectQueryGenerator.
        SelectQuerySpec(SelectColumnMaxValue(uuidCursor), from)
            .assertSqlEquals(
                """SELECT "cursor_col" FROM "SC"."TBL" WHERE "cursor_col" IS NOT NULL """ +
                    """ORDER BY "cursor_col" DESC LIMIT 1""",
            )
    }

    @Test
    fun uuidCursorUpperBoundKeepsTheWhereClauseAndItsBindings() {
        val bound: JsonNode = Jsons.numberNode(5L)
        SelectQuerySpec(
                SelectColumnMaxValue(uuidCursor),
                from,
                Where(Greater(EmittedField("id", LongFieldType), bound)),
            )
            .assertSqlEquals(
                """SELECT "cursor_col" FROM "SC"."TBL" WHERE ("id" > ?) AND "cursor_col" IS NOT NULL """ +
                    """ORDER BY "cursor_col" DESC LIMIT 1""",
                bound to LongFieldType,
            )
    }

    @Test
    fun otherCursorTypesKeepUsingMax() {
        SelectQuerySpec(SelectColumnMaxValue(stringCursor), from)
            .assertSqlEquals("""SELECT MAX("cursor_col") FROM "SC"."TBL"""")
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
        Assertions.assertEquals(expected, PostgresSourceSelectQueryGenerator().generate(optimize()))
    }
}
