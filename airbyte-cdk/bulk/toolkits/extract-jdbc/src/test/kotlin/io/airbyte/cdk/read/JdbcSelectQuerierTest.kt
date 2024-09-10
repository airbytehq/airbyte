/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.h2.H2TestFixture
import io.airbyte.cdk.h2source.H2SourceConfiguration
import io.airbyte.cdk.h2source.H2SourceConfigurationFactory
import io.airbyte.cdk.h2source.H2SourceConfigurationJsonObject
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcSelectQuerierTest {
    val h2 = H2TestFixture()

    init {
        h2.execute(
            """CREATE TABLE kv (
            |k INT PRIMARY KEY, 
            |v VARCHAR(60))
            |
            """
                .trimMargin()
                .replace('\n', ' '),
        )
        h2.execute("INSERT INTO kv (k, v) VALUES (1, 'foo'), (2, 'bar'), (3, NULL);")
    }

    val columns: List<Field> = listOf(Field("k", IntFieldType), Field("v", StringFieldType))

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
                listOf(SelectQuery.Binding(Jsons.numberNode(2), IntFieldType)),
            ),
            """{"k":1, "v":"foo"}""",
        )
        runTest(
            SelectQuery(
                "SELECT k, v FROM kv WHERE k > ? AND k < ?",
                columns,
                listOf(
                    SelectQuery.Binding(Jsons.numberNode(1), IntFieldType),
                    SelectQuery.Binding(Jsons.numberNode(3), IntFieldType),
                ),
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

    private fun runTest(
        q: SelectQuery,
        vararg expectedJson: String,
    ) {
        val configPojo: H2SourceConfigurationJsonObject =
            H2SourceConfigurationJsonObject().apply {
                port = h2.port
                database = h2.database
            }
        val config: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)
        val querier: SelectQuerier = JdbcSelectQuerier(JdbcConnectionFactory(config))
        // Vanilla query
        val expected: List<JsonNode> = expectedJson.map(Jsons::readTree)
        val actual: List<ObjectNode> = querier.executeQuery(q).use { it.asSequence().toList() }
        Assertions.assertIterableEquals(expected, actual)
        // Query with reuseResultObject = true
        querier.executeQuery(q, SelectQuerier.Parameters(reuseResultObject = true)).use {
            var i = 0
            var previous: ObjectNode? = null
            for (record in it) {
                if (i > 0) {
                    Assertions.assertTrue(previous === record)
                }
                Assertions.assertEquals(expected[i++], record)
                previous = record
            }
        }
    }
}
