/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.source.IntFieldType
import io.airbyte.cdk.source.StringFieldType
import io.airbyte.cdk.source.Field
import io.airbyte.cdk.source.select.SelectQuerier
import io.airbyte.cdk.source.select.SelectQuery
import io.airbyte.cdk.test.source.TestSourceConfiguration
import io.airbyte.cdk.test.source.TestSourceConfigurationFactory
import io.airbyte.cdk.test.source.TestSourceConfigurationJsonObject
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcSelectQuerierTest {

    val h2 = H2TestFixture()

    init {
        h2.execute(
            """CREATE TABLE kv (
            |k INT PRIMARY KEY, 
            |v VARCHAR(60))
            |"""
                .trimMargin()
                .replace('\n', ' ')
        )
        h2.execute("INSERT INTO kv (k, v) VALUES (1, 'foo'), (2, 'bar'), (3, NULL);")
    }

    val columns: List<Field> =
        listOf(Field("k", IntFieldType), Field("v", StringFieldType))

    @Test
    fun testVanilla() {
        runTest(
            SelectQuery("SELECT k, v FROM kv", columns, listOf()),
            """{"k":1, "v":"foo"}""",
            """{"k":2, "v":"bar"}""",
            """{"k":3, "v":null}""",
        )
    }

    @Test
    fun testBindings() {
        runTest(
            SelectQuery(
                "SELECT k, v FROM kv WHERE k < ?",
                columns,
                listOf(SelectQuery.Binding(json(2), IntFieldType))
            ),
            """{"k":1, "v":"foo"}""",
        )
        runTest(
            SelectQuery(
                "SELECT k, v FROM kv WHERE k > ? AND k < ?",
                columns,
                listOf(
                    SelectQuery.Binding(json(1), IntFieldType),
                    SelectQuery.Binding(json(3), IntFieldType),
                )
            ),
            """{"k":2, "v":"bar"}""",
        )
    }

    @Test
    fun testProjection() {
        runTest(
            SelectQuery("SELECT v FROM kv", columns.drop(1), listOf()),
            """{"v":"foo"}""",
            """{"v":"bar"}""",
            """{"v":null}""",
        )
    }

    private fun runTest(q: SelectQuery, vararg expected: String) {
        val configPojo: TestSourceConfigurationJsonObject =
            TestSourceConfigurationJsonObject().apply {
                port = h2.port
                database = h2.database
            }
        val config: TestSourceConfiguration = TestSourceConfigurationFactory().make(configPojo)
        val querier: SelectQuerier = JdbcSelectQuerier(JdbcConnectionFactory(config))
        val actual = mutableListOf<JsonNode>()
        querier.executeQuery(q) { record: JsonNode ->
            actual.add(record)
            false
        }
        Assertions.assertEquals(expected.toList().map(Jsons::deserialize), actual)
    }

    companion object {
        val nodeFactory: JsonNodeFactory = MoreMappers.initMapper().nodeFactory

        fun json(n: Long): JsonNode = nodeFactory.numberNode(n)
    }
}
