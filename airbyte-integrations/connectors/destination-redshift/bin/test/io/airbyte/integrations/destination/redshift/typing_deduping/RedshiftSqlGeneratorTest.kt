/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.redshift.typing_deduping

import io.airbyte.commons.resources.MoreResources.readResource
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.destination.redshift.RedshiftSQLNameTransformer
import java.io.IOException
import java.time.Instant
import java.util.Arrays
import java.util.Optional
import java.util.Random
import org.jooq.DSLContext
import org.jooq.conf.Settings
import org.jooq.impl.DSL
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class RedshiftSqlGeneratorTest {
    private var streamId: StreamId? = null

    private var incrementalDedupStream: StreamConfig? = null

    private var incrementalAppendStream: StreamConfig? = null

    @BeforeEach
    fun setup() {
        streamId =
            StreamId(
                "test_schema",
                "users_final",
                "test_schema",
                "users_raw",
                "test_schema",
                "users_final"
            )
        val id1 = redshiftSqlGenerator.buildColumnId("id1")
        val id2 = redshiftSqlGenerator.buildColumnId("id2")
        val primaryKey = listOf(id1, id2)
        val cursor = redshiftSqlGenerator.buildColumnId("updated_at")

        val columns = LinkedHashMap<ColumnId, AirbyteType>()
        columns[id1] = AirbyteProtocolType.INTEGER
        columns[id2] = AirbyteProtocolType.INTEGER
        columns[cursor] = AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
        columns[redshiftSqlGenerator.buildColumnId("struct")] = Struct(LinkedHashMap())
        columns[redshiftSqlGenerator.buildColumnId("array")] = Array(AirbyteProtocolType.UNKNOWN)
        columns[redshiftSqlGenerator.buildColumnId("string")] = AirbyteProtocolType.STRING
        columns[redshiftSqlGenerator.buildColumnId("number")] = AirbyteProtocolType.NUMBER
        columns[redshiftSqlGenerator.buildColumnId("integer")] = AirbyteProtocolType.INTEGER
        columns[redshiftSqlGenerator.buildColumnId("boolean")] = AirbyteProtocolType.BOOLEAN
        columns[redshiftSqlGenerator.buildColumnId("timestamp_with_timezone")] =
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
        columns[redshiftSqlGenerator.buildColumnId("timestamp_without_timezone")] =
            AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE
        columns[redshiftSqlGenerator.buildColumnId("time_with_timezone")] =
            AirbyteProtocolType.TIME_WITH_TIMEZONE
        columns[redshiftSqlGenerator.buildColumnId("time_without_timezone")] =
            AirbyteProtocolType.TIME_WITHOUT_TIMEZONE
        columns[redshiftSqlGenerator.buildColumnId("date")] = AirbyteProtocolType.DATE
        columns[redshiftSqlGenerator.buildColumnId("unknown")] = AirbyteProtocolType.UNKNOWN
        columns[redshiftSqlGenerator.buildColumnId("_ab_cdc_deleted_at")] =
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE
        incrementalDedupStream =
            StreamConfig(
                streamId!!,
                ImportType.DEDUPE,
                primaryKey,
                Optional.of(cursor),
                columns,
                0,
                0,
                0
            )
        incrementalAppendStream =
            StreamConfig(
                streamId!!,
                ImportType.APPEND,
                primaryKey,
                Optional.of(cursor),
                columns,
                0,
                0,
                0
            )
    }

    @Test
    @Throws(IOException::class)
    fun testTypingAndDeduping() {
        val expectedSql = readResource("typing_deduping_with_cdc.sql")
        val generatedSql =
            redshiftSqlGenerator.updateTable(
                incrementalDedupStream!!,
                "unittest",
                Optional.of(Instant.parse("2023-02-15T18:35:24.00Z")),
                false
            )
        val expectedSqlLines =
            Arrays.stream(
                    expectedSql.split("\n".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
                )
                .map { obj: String -> obj.trim { it <= ' ' } }
                .toList()
        val generatedSqlLines =
            generatedSql
                .asSqlStrings("BEGIN", "COMMIT")
                .stream()
                .flatMap { statement: String ->
                    Arrays.stream(
                        statement
                            .split("\n".toRegex())
                            .dropLastWhile { it.isEmpty() }
                            .toTypedArray()
                    )
                }
                .map { obj: String -> obj.trim { it <= ' ' } }
                .filter { line: String -> line.isNotEmpty() }
                .toList()
        Assertions.assertEquals(expectedSqlLines.size, generatedSqlLines.size)
        for (i in expectedSqlLines.indices) {
            Assertions.assertEquals(expectedSqlLines[i], generatedSqlLines[i])
        }
    }

    @Test
    fun test2000ColumnSql() {
        val id1 = redshiftSqlGenerator.buildColumnId("id1")
        val id2 = redshiftSqlGenerator.buildColumnId("id2")
        val primaryKey = listOf(id1, id2)
        val cursor = redshiftSqlGenerator.buildColumnId("updated_at")

        val columns = LinkedHashMap<ColumnId, AirbyteType>()
        columns[id1] = AirbyteProtocolType.INTEGER
        columns[id2] = AirbyteProtocolType.INTEGER
        columns[cursor] = AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE

        for (i in 0..1999) {
            val columnName =
                RANDOM.ints('a'.code, 'z'.code + 1)
                    .limit(15)
                    .collect(
                        { StringBuilder() },
                        { obj: java.lang.StringBuilder, codePoint: Int ->
                            obj.appendCodePoint(codePoint)
                        },
                        { obj: java.lang.StringBuilder, s: java.lang.StringBuilder? ->
                            obj.append(s)
                        }
                    )
                    .toString()
            columns[redshiftSqlGenerator.buildColumnId(columnName)] = AirbyteProtocolType.STRING
        }
        val generatedSql =
            redshiftSqlGenerator.updateTable(
                StreamConfig(
                    streamId!!,
                    ImportType.DEDUPE,
                    primaryKey,
                    Optional.of(cursor),
                    columns,
                    0,
                    0,
                    0
                ),
                "unittest",
                Optional.of(Instant.parse("2023-02-15T18:35:24.00Z")),
                false
            )
        // This should not throw an exception.
        Assertions.assertFalse(generatedSql.transactions.isEmpty())
    }

    companion object {
        private val RANDOM = Random()

        private val redshiftSqlGenerator: RedshiftSqlGenerator =
            object : RedshiftSqlGenerator(RedshiftSQLNameTransformer(), false) {
                override val dslContext: DSLContext
                    // Override only for tests to print formatted SQL. The actual implementation
                    // should use unformatted
                    get() = DSL.using(dialect, Settings().withRenderFormatted(true))
            }
    }
}
