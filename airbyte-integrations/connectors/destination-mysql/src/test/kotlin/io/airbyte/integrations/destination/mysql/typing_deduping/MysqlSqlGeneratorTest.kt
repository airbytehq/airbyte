/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.mysql.typing_deduping

import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import java.util.Optional
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class MysqlSqlGeneratorTest {

    private val generator = MysqlSqlGenerator()

    /**
     * Build a StreamConfig with the given columns and generate the T+D SQL via updateTable. Returns
     * all the SQL statements concatenated for assertion.
     */
    private fun generateUpdateSql(columns: LinkedHashMap<ColumnId, AirbyteType>): String {
        val id1 = generator.buildColumnId("id1")
        val cursor = generator.buildColumnId("updated_at")

        // Ensure id1 and cursor are in the columns map
        val allColumns = LinkedHashMap(columns)
        allColumns.putIfAbsent(id1, AirbyteProtocolType.INTEGER)
        allColumns.putIfAbsent(cursor, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE)

        val streamId = generator.buildStreamId("test_ns", "test_stream", "test_raw_ns")
        val streamConfig =
            StreamConfig(
                streamId,
                SyncMode.INCREMENTAL,
                DestinationSyncMode.APPEND,
                listOf(id1),
                Optional.of(cursor),
                allColumns,
            )
        val sql = generator.updateTable(streamConfig, "", Optional.empty(), false)
        return sql.transactions.joinToString("\n") { transaction -> transaction.joinToString("\n") }
    }

    @Test
    fun testStringColumnUsesReturningClause() {
        val columns =
            linkedMapOf<ColumnId, AirbyteType>(
                generator.buildColumnId("my_string") to AirbyteProtocolType.STRING,
            )
        val sql = generateUpdateSql(columns)
        assertTrue(
            sql.contains("RETURNING CHAR(65535)"),
            "Expected SQL to contain 'RETURNING CHAR(65535)' but got: $sql"
        )
    }

    @Test
    fun testIntegerColumnUsesReturningClause() {
        val columns =
            linkedMapOf<ColumnId, AirbyteType>(
                generator.buildColumnId("my_int") to AirbyteProtocolType.INTEGER,
            )
        val sql = generateUpdateSql(columns)
        assertTrue(
            sql.contains("RETURNING CHAR(65535)"),
            "Expected SQL to contain 'RETURNING CHAR(65535)' for INTEGER but got: $sql"
        )
    }

    @Test
    fun testStructUsesJsonExtractNotJsonValue() {
        val columns =
            linkedMapOf<ColumnId, AirbyteType>(
                generator.buildColumnId("my_struct") to Struct(linkedMapOf()),
            )
        val sql = generateUpdateSql(columns)
        // Struct columns should use JSON_EXTRACT/JSON_TYPE with a CASE expression,
        // NOT JSON_VALUE. Look for the struct-specific pattern in the SQL.
        assertTrue(
            sql.contains(
                """JSON_TYPE(JSON_EXTRACT(`_airbyte_data`, '$."my_struct"')) <> 'OBJECT'"""
            ),
            "Expected struct column to use JSON_TYPE/JSON_EXTRACT pattern but got: $sql"
        )
        // The struct column itself should not go through JSON_VALUE
        assertFalse(
            sql.contains("""JSON_VALUE(JSON_EXTRACT(`_airbyte_data`, '$."my_struct"')"""),
            "Expected struct column to NOT use JSON_VALUE but got: $sql"
        )
    }

    @Test
    fun testArrayUsesJsonExtractNotJsonValue() {
        val columns =
            linkedMapOf<ColumnId, AirbyteType>(
                generator.buildColumnId("my_array") to Array(AirbyteProtocolType.STRING),
            )
        val sql = generateUpdateSql(columns)
        assertTrue(
            sql.contains("""JSON_TYPE(JSON_EXTRACT(`_airbyte_data`, '$."my_array"')) <> 'ARRAY'"""),
            "Expected array column to use JSON_TYPE/JSON_EXTRACT pattern but got: $sql"
        )
        assertFalse(
            sql.contains("""JSON_VALUE(JSON_EXTRACT(`_airbyte_data`, '$."my_array"')"""),
            "Expected array column to NOT use JSON_VALUE but got: $sql"
        )
    }
}
