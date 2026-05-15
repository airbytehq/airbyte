/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.postgres

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.jdbc.LosslessJdbcFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.read.From
import io.airbyte.cdk.read.SelectColumnMaxValue
import io.airbyte.cdk.read.SelectQuery
import io.airbyte.cdk.read.SelectQuerySpec
import io.airbyte.cdk.read.optimize
import io.airbyte.integrations.source.postgres.operations.PostgresSourceSelectQueryGenerator
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class PostgresSourceSelectQueryGeneratorTest {
    @Test
    fun testSelectMaxCursorUsesOrderByLimit() {
        SelectQuerySpec(
                SelectColumnMaxValue(EmittedField("cursor_col", StringFieldType)),
                From("TBL", "SC"),
            )
            .assertSqlEquals(
                """SELECT "cursor_col" FROM "SC"."TBL" ORDER BY "cursor_col" DESC NULLS LAST LIMIT 1"""
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
        Assertions.assertEquals(expected, PostgresSourceSelectQueryGenerator().generate(optimize()))
    }
}
