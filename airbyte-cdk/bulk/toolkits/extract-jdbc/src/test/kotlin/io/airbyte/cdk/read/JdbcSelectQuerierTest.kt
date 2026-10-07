/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.h2.H2TestFixture
import io.airbyte.cdk.h2source.H2SourceConfiguration
import io.airbyte.cdk.h2source.H2SourceConfigurationFactory
import io.airbyte.cdk.h2source.H2SourceConfigurationSpecification
import io.airbyte.cdk.jdbc.IntFieldType
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.jdbc.LocalDateFieldType
import io.airbyte.cdk.jdbc.LocalDateTimeFieldType
import io.airbyte.cdk.jdbc.StringFieldType
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import java.lang.reflect.InvocationTargetException
import java.lang.reflect.Method
import java.lang.reflect.Proxy
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException
import java.time.LocalDate
import java.time.LocalDateTime

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

    val columns: List<EmittedField> =
        listOf(EmittedField("k", IntFieldType), EmittedField("v", StringFieldType))

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

    @Test
    fun testTemporalAccessorsPreserveNullAndFlagConversionFailures() {
        h2.execute("CREATE TABLE temporal (k INT PRIMARY KEY, d DATE, t TIMESTAMP)")
        h2.execute(
            """
            INSERT INTO temporal (k, d, t) VALUES
                (1, '2024-03-01', '2024-03-01 01:02:03'),
                (2, NULL, NULL),
                (3, '0001-01-01', '0001-01-01 00:00:00'),
                (4, '0002-02-02', '0002-02-02 00:00:00')
            """,
        )

        val configPojo =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
            }
        val config = H2SourceConfigurationFactory().make(configPojo)
        val connectionFactory =
            object : JdbcConnectionFactory(config) {
                override fun get(): Connection = wrapTemporalTestConnection(super.get())
            }
        val dateField = EmittedField("d", LocalDateFieldType)
        val timestampField = EmittedField("t", LocalDateTimeFieldType)
        val querier = JdbcSelectQuerier(connectionFactory)
        val rows =
            querier
                .executeQuery(
                    SelectQuery(
                        "SELECT k, d, t FROM temporal ORDER BY k",
                        listOf(EmittedField("k", IntFieldType), dateField, timestampField),
                        listOf(),
                    ),
                ).use { result ->
                    result.asSequence().map { row ->
                        QuerierRowSnapshot(
                            row.data.mapValues { (_, value) ->
                                (value as FieldValueEncoder<*>).fieldValue
                            },
                            row.changes.toMap(),
                        )
                    }.toList()
                }

        Assertions.assertEquals(4, rows.size)
        Assertions.assertEquals(LocalDate.of(2024, 3, 1), rows[0].data["d"])
        Assertions.assertEquals(LocalDateTime.of(2024, 3, 1, 1, 2, 3), rows[0].data["t"])
        Assertions.assertEquals(emptyMap<EmittedField, FieldValueChange>(), rows[0].changes)

        Assertions.assertNull(rows[1].data["d"])
        Assertions.assertNull(rows[1].data["t"])
        Assertions.assertEquals(emptyMap<EmittedField, FieldValueChange>(), rows[1].changes)

        Assertions.assertNull(rows[2].data["d"])
        Assertions.assertNull(rows[2].data["t"])
        Assertions.assertEquals(emptyMap<EmittedField, FieldValueChange>(), rows[2].changes)

        Assertions.assertNull(rows[3].data["d"])
        Assertions.assertNull(rows[3].data["t"])
        Assertions.assertEquals(
            mapOf(
                dateField to FieldValueChange.RETRIEVAL_FAILURE_TOTAL,
                timestampField to FieldValueChange.RETRIEVAL_FAILURE_TOTAL,
            ),
            rows[3].changes,
        )
    }

    private fun runTest(
        q: SelectQuery,
        vararg expectedJson: String,
    ) {
        val configPojo: H2SourceConfigurationSpecification =
            H2SourceConfigurationSpecification().apply {
                port = h2.port
                database = h2.database
            }
        val config: H2SourceConfiguration = H2SourceConfigurationFactory().make(configPojo)
        val querier: SelectQuerier = JdbcSelectQuerier(JdbcConnectionFactory(config))
        // Vanilla query
        val expected: List<JsonNode> = expectedJson.map(Jsons::readTree)
        val actual: List<NativeRecordPayload> =
            querier.executeQuery(q).use { it.asSequence().toList().map { it.data } }
        val actualJson = actual.map { it.toJson() }.toList()
        Assertions.assertIterableEquals(expected, actualJson)
        // Query with reuseResultObject = true
        querier.executeQuery(q, SelectQuerier.Parameters(reuseResultObject = true)).use {
            var i = 0
            var previous: NativeRecordPayload? = null
            for (row in it) {
                if (i > 0) {
                    Assertions.assertTrue(previous === row.data)
                }
                Assertions.assertEquals(actual[i++].toJson(), row.data.toJson())
                previous = row.data
            }
        }
    }
}

private data class QuerierRowSnapshot(
    val data: Map<String, Any?>,
    val changes: Map<EmittedField, FieldValueChange>,
)

private fun wrapTemporalTestConnection(connection: Connection): Connection =
    Proxy.newProxyInstance(
        Connection::class.java.classLoader,
        arrayOf(Connection::class.java),
    ) { _, method, args ->
        if (method.name == "prepareStatement") {
            wrapTemporalTestStatement(
                invokeDelegate(connection, method, args) as PreparedStatement,
            )
        } else {
            invokeDelegate(connection, method, args)
        }
    } as Connection

private fun wrapTemporalTestStatement(statement: PreparedStatement): PreparedStatement =
    Proxy.newProxyInstance(
        PreparedStatement::class.java.classLoader,
        arrayOf(PreparedStatement::class.java),
    ) { _, method, args ->
        if (method.name == "executeQuery" && args.isNullOrEmpty()) {
            wrapTemporalTestResultSet(invokeDelegate(statement, method, args) as ResultSet)
        } else {
            invokeDelegate(statement, method, args)
        }
    } as PreparedStatement

private fun wrapTemporalTestResultSet(resultSet: ResultSet): ResultSet =
    Proxy.newProxyInstance(
        ResultSet::class.java.classLoader,
        arrayOf(ResultSet::class.java),
    ) { _, method, args ->
        if (
            method.name in setOf("getDate", "getTimestamp") &&
                args?.size == 1 &&
                args[0] is Int
        ) {
            when {
                resultSet.getString(args[0] as Int)?.startsWith("0001-01-01") == true -> null
                resultSet.getString(args[0] as Int)?.startsWith("0002-02-02") == true ->
                    throw SQLException(
                        "Value '2026-00-01' can not be represented as java.sql.Timestamp",
                    )
                else -> invokeDelegate(resultSet, method, args)
            }
        } else {
            invokeDelegate(resultSet, method, args)
        }
    } as ResultSet

private fun invokeDelegate(
    delegate: Any,
    method: Method,
    args: Array<out Any?>?,
): Any? =
    try {
        method.invoke(delegate, *(args ?: emptyArray()))
    } catch (e: InvocationTargetException) {
        throw e.targetException
    }
