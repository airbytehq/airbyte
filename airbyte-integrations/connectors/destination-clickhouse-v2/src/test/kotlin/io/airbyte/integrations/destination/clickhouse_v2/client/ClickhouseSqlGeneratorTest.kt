/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.client

import com.github.vertical_blank.sqlformatter.SqlFormatter
import com.github.vertical_blank.sqlformatter.languages.Dialect
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.clickhouse_v2.model.AlterationSummary
import kotlin.test.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class ClickhouseSqlGeneratorTest {
    val clickhouseSqlGenerator = ClickhouseSqlGenerator()

    @Test
    fun testCreateNamespace() {
        val namespace = "test_namespace"
        val expected = "CREATE DATABASE IF NOT EXISTS `$namespace`;"
        val actual = clickhouseSqlGenerator.createNamespace(namespace)
        assert(expected == actual) { "Expected: $expected, but got: $actual" }
    }

    @ParameterizedTest
    @MethodSource("alterTableTestCases")
    fun testAlterTableContainsClauses(
        alterationSummary: AlterationSummary,
        expectedClauses: List<String>
    ) {
        val tableName = TableName("my_namespace", "my_table")
        val actualSql = clickhouseSqlGenerator.alterTable(alterationSummary, tableName)
        expectedClauses.forEach { clause ->
            assertTrue(
                actualSql.contains(clause),
                "Expected SQL to contain: $clause, but got: $actualSql"
            )
        }
    }

    @Test
    fun testAlterTableValidSql() {
        val alterationSummary =
            AlterationSummary(
                added = mapOf("col1" to "Int32", "col2" to "String"),
                modified = mapOf("col3" to "String", "col4" to "Int64"),
                deleted = setOf("col5", "col6")
            )
        val tableName = TableName("my_namespace", "my_table")
        val sql = clickhouseSqlGenerator.alterTable(alterationSummary, tableName)

        assertDoesNotThrow {
            // Using the StandardSql dialect as a substitute for clickhouse SQL syntax validation.
            // The formatter will parse the SQL, and an invalid statement will throw an exception.
            SqlFormatter.of(Dialect.StandardSql).format(sql)
        }
    }

    companion object {
        @JvmStatic
        fun alterTableTestCases(): List<Arguments> =
            listOf(
                Arguments.of(
                    AlterationSummary(
                        added = mapOf("new_column" to "Int32"),
                        modified = mapOf("existing_column" to "String"),
                        deleted = setOf("old_column")
                    ),
                    listOf(
                        " ADD COLUMN `new_column` Nullable(Int32)",
                        " MODIFY COLUMN `existing_column` Nullable(String)",
                        " DROP COLUMN `old_column`"
                    )
                ),
                Arguments.of(
                    AlterationSummary(
                        added = mapOf("new_column" to "Int32"),
                        modified = emptyMap(),
                        deleted = setOf()
                    ),
                    listOf(" ADD COLUMN `new_column` Nullable(Int32)")
                ),
                Arguments.of(
                    AlterationSummary(
                        added = emptyMap(),
                        modified = mapOf("existing_column" to "String"),
                        deleted = setOf()
                    ),
                    listOf(" MODIFY COLUMN `existing_column` Nullable(String)")
                ),
                Arguments.of(
                    AlterationSummary(
                        added = emptyMap(),
                        modified = emptyMap(),
                        deleted = setOf("old_column")
                    ),
                    listOf(" DROP COLUMN `old_column`")
                ),
                Arguments.of(
                    AlterationSummary(
                        added = mapOf("col1" to "Int32", "col2" to "String"),
                        modified = mapOf("col3" to "String", "col4" to "Int64"),
                        deleted = setOf("col5", "col6")
                    ),
                    listOf(
                        " ADD COLUMN `col1` Nullable(Int32)",
                        " ADD COLUMN `col2` Nullable(String)",
                        " MODIFY COLUMN `col3` Nullable(String)",
                        " MODIFY COLUMN `col4` Nullable(Int64)",
                        " DROP COLUMN `col5`",
                        " DROP COLUMN `col6`"
                    )
                ),
            )
    }
}
