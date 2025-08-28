/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse.client

import com.github.vertical_blank.sqlformatter.SqlFormatter
import com.github.vertical_blank.sqlformatter.languages.Dialect
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.integrations.destination.clickhouse.model.AlterationSummary
import io.airbyte.integrations.destination.clickhouse.spec.ClickhouseConfiguration
import io.mockk.mockk
import kotlin.test.assertTrue
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class ClickhouseSqlGeneratorTest {
    private val clickhouseConfiguration: ClickhouseConfiguration = mockk(relaxed = true)

    private val clickhouseSqlGenerator = ClickhouseSqlGenerator(clickhouseConfiguration)

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
                deleted = setOf("col5", "col6"),
                hasDedupChange = false
            )
        val tableName = TableName("my_namespace", "my_table")
        val sql = clickhouseSqlGenerator.alterTable(alterationSummary, tableName)

        assertDoesNotThrow {
            // Using the StandardSql dialect as a substitute for clickhouse SQL syntax validation.
            // The formatter will parse the SQL, and an invalid statement will throw an exception.
            SqlFormatter.of(Dialect.StandardSql).format(sql)
        }
    }

    @Test
    fun `test extractPks with single primary key`() {
        val primaryKey = listOf(listOf("id"))
        val columnNameMapping = ColumnNameMapping(mapOf("id" to "id_column"))
        val expected = listOf("id_column")
        val actual = clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test extractPks with multiple primary keys`() {
        val primaryKey = listOf(listOf("id"), listOf("name"))
        val columnNameMapping =
            ColumnNameMapping(mapOf("id" to "id_column", "name" to "name_column"))
        val expected = listOf("id_column", "name_column")
        val actual = clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test extractPks with empty primary key list`() {
        val primaryKey = emptyList<List<String>>()
        val columnNameMapping = ColumnNameMapping(emptyMap<String, String>())
        val expected = listOf<String>()
        val actual = clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test extractPks without column mapping`() {
        val primaryKey = listOf(listOf("id"))
        val columnNameMapping = ColumnNameMapping(mapOf())
        val expected = listOf("id")
        val actual = clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        Assertions.assertEquals(expected, actual)
    }

    @Test
    fun `test extractPks with nested primary key`() {
        val primaryKey = listOf(listOf("user", "id"))
        val columnNameMapping =
            ColumnNameMapping(
                mapOf("user.id" to "user_id_column")
            ) // This mapping is not used but here for completeness.
        assertThrows<UnsupportedOperationException> {
            clickhouseSqlGenerator.extractPks(primaryKey, columnNameMapping)
        }
    }

    @Test
    fun `test exchangeTable`() {
        val sourceTable = TableName("source_db", "source_table")
        val targetTable = TableName("target_db", "target_table")
        val expectedSql =
            """
            EXCHANGE TABLES `source_db`.`source_table`
                AND `target_db`.`target_table`;
        """.trimIndent()
        val actualSql = clickhouseSqlGenerator.exchangeTable(sourceTable, targetTable)

        Assertions.assertEquals(actualSql, expectedSql)
    }

    @Test
    fun `test copyTable`() {
        val sourceTable = TableName("source_namespace", "source_table")
        val targetTable = TableName("target_namespace", "target_table")
        val columnNameMapping =
            ColumnNameMapping(mapOf("source_col1" to "target_col1", "source_col2" to "target_col2"))

        val expectedSql =
            """
            INSERT INTO `target_namespace`.`target_table`
            (
                _airbyte_raw_id,
                _airbyte_extracted_at,
                _airbyte_meta,
                _airbyte_generation_id,
                target_col1,target_col2
            )
            SELECT
                _airbyte_raw_id,
                _airbyte_extracted_at,
                _airbyte_meta,
                _airbyte_generation_id,
                target_col1,target_col2
            FROM `source_namespace`.`source_table`
        """.trimIndent()

        val actualSql =
            clickhouseSqlGenerator.copyTable(columnNameMapping, sourceTable, targetTable)
        Assertions.assertEquals(expectedSql, actualSql)
    }

    companion object {
        @JvmStatic
        fun alterTableTestCases(): List<Arguments> =
            listOf(
                Arguments.of(
                    AlterationSummary(
                        added = mapOf("new_column" to "Int32"),
                        modified = mapOf("existing_column" to "String"),
                        deleted = setOf("old_column"),
                        hasDedupChange = false,
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
                        deleted = setOf(),
                        hasDedupChange = false,
                    ),
                    listOf(" ADD COLUMN `new_column` Nullable(Int32)")
                ),
                Arguments.of(
                    AlterationSummary(
                        added = emptyMap(),
                        modified = mapOf("existing_column" to "String"),
                        deleted = setOf(),
                        hasDedupChange = false,
                    ),
                    listOf(" MODIFY COLUMN `existing_column` Nullable(String)")
                ),
                Arguments.of(
                    AlterationSummary(
                        added = emptyMap(),
                        modified = emptyMap(),
                        deleted = setOf("old_column"),
                        hasDedupChange = false,
                    ),
                    listOf(" DROP COLUMN `old_column`")
                ),
                Arguments.of(
                    AlterationSummary(
                        added = mapOf("col1" to "Int32", "col2" to "String"),
                        modified = mapOf("col3" to "String", "col4" to "Int64"),
                        deleted = setOf("col5", "col6"),
                        hasDedupChange = false,
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
