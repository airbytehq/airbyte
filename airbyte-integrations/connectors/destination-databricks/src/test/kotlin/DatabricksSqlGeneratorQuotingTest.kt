/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksNamingTransformer
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import java.util.Optional
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Tests that catalog names containing special characters (e.g., hyphens) are properly
 * backtick-quoted in all generated SQL statements.
 *
 * Regression test for https://github.com/airbytehq/airbyte/issues/76307
 */
class DatabricksSqlGeneratorQuotingTest {

    private val catalogWithHyphen = "my-catalogue"
    private val simpleCatalog = "simple_catalog"

    private val sqlGeneratorHyphen =
        DatabricksSqlGenerator(DatabricksNamingTransformer(), catalogWithHyphen)
    private val sqlGeneratorSimple =
        DatabricksSqlGenerator(DatabricksNamingTransformer(), simpleCatalog)

    private val streamId =
        StreamId(
            finalNamespace = "test_schema",
            finalName = "test_table",
            rawNamespace = "airbyte_internal",
            rawName = "raw_test_table",
            originalNamespace = "test_schema",
            originalName = "test_table",
        )

    private val streamConfig =
        StreamConfig(
            id = streamId,
            postImportAction = ImportType.APPEND,
            primaryKey = listOf(),
            cursor = Optional.empty(),
            columns =
                linkedMapOf(
                    ColumnId("name", "name", "name") to AirbyteProtocolType.STRING,
                    ColumnId("age", "age", "age") to AirbyteProtocolType.INTEGER,
                ),
            generationId = 1,
            minimumGenerationId = 1,
            syncId = 0,
        )

    private val dedupeStreamConfig =
        StreamConfig(
            id = streamId,
            postImportAction = ImportType.DEDUPE,
            primaryKey = listOf(ColumnId("name", "name", "name")),
            cursor = Optional.of(ColumnId("age", "age", "age")),
            columns =
                linkedMapOf(
                    ColumnId("name", "name", "name") to AirbyteProtocolType.STRING,
                    ColumnId("age", "age", "age") to AirbyteProtocolType.INTEGER,
                ),
            generationId = 1,
            minimumGenerationId = 1,
            syncId = 0,
        )

    /**
     * Asserts that the catalog name appears backtick-quoted in the SQL and never appears unquoted
     * (which would cause PARSE_SYNTAX_ERROR for hyphenated names).
     */
    private fun assertCatalogQuoted(sql: String, catalog: String) {
        assertTrue(
            sql.contains("`$catalog`"),
            "Expected backtick-quoted catalog `$catalog` in SQL: $sql",
        )
        // Verify the catalog name doesn't appear unquoted (i.e., not preceded by a backtick)
        // We check that every occurrence of the catalog name is surrounded by backticks
        val unquotedPattern = Regex("(?<!`)${Regex.escape(catalog)}(?!`)")
        assertFalse(
            unquotedPattern.containsMatchIn(sql),
            "Found unquoted catalog name '$catalog' in SQL: $sql",
        )
    }

    private fun sqlToString(
        sql: io.airbyte.integrations.base.destination.typing_deduping.Sql
    ): String {
        return sql.transactions.flatten().joinToString("\n")
    }

    // --- DatabricksSqlGenerator tests ---

    @Test
    fun testCreateRawTableQuotesCatalog() {
        val sql = sqlToString(sqlGeneratorHyphen.createRawTable(streamId, "", false))
        assertCatalogQuoted(sql, catalogWithHyphen)
    }

    @Test
    fun testCreateRawTableReplaceQuotesCatalog() {
        val sql = sqlToString(sqlGeneratorHyphen.createRawTable(streamId, "", true))
        assertCatalogQuoted(sql, catalogWithHyphen)
    }

    @Test
    fun testTruncateRawTableQuotesCatalog() {
        val sql = sqlToString(sqlGeneratorHyphen.truncateRawTable(streamId))
        assertCatalogQuoted(sql, catalogWithHyphen)
    }

    @Test
    fun testCreateTableQuotesCatalog() {
        val sql = sqlToString(sqlGeneratorHyphen.createTable(streamConfig, "", false))
        assertCatalogQuoted(sql, catalogWithHyphen)
    }

    @Test
    fun testCreateSchemaQuotesCatalog() {
        val sql = sqlToString(sqlGeneratorHyphen.createSchema("my_schema"))
        assertCatalogQuoted(sql, catalogWithHyphen)
    }

    @Test
    fun testUpdateTableAppendQuotesCatalog() {
        val sql =
            sqlToString(sqlGeneratorHyphen.updateTable(streamConfig, "", Optional.empty(), false))
        assertCatalogQuoted(sql, catalogWithHyphen)
    }

    @Test
    fun testUpdateTableDedupeQuotesCatalog() {
        val sql =
            sqlToString(
                sqlGeneratorHyphen.updateTable(dedupeStreamConfig, "", Optional.empty(), false)
            )
        assertCatalogQuoted(sql, catalogWithHyphen)
    }

    @Test
    fun testOverwriteFinalTableQuotesCatalog() {
        val sql = sqlToString(sqlGeneratorHyphen.overwriteFinalTable(streamId, "_tmp"))
        assertCatalogQuoted(sql, catalogWithHyphen)
    }

    @Test
    fun testClearLoadedAtQuotesCatalog() {
        val sql = sqlToString(sqlGeneratorHyphen.clearLoadedAt(streamId))
        assertCatalogQuoted(sql, catalogWithHyphen)
    }

    // Verify simple catalog names also get quoted (consistency)
    @Test
    fun testSimpleCatalogAlsoQuoted() {
        val sql = sqlToString(sqlGeneratorSimple.createSchema("my_schema"))
        assertCatalogQuoted(sql, simpleCatalog)
    }

    @Test
    fun testSimpleCatalogCreateRawTableQuoted() {
        val sql = sqlToString(sqlGeneratorSimple.createRawTable(streamId, "", false))
        assertCatalogQuoted(sql, simpleCatalog)
    }
}
