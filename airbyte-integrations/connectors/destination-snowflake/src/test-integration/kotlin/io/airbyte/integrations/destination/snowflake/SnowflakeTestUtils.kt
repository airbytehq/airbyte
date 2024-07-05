/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.util.*
import java.util.Map
import java.util.stream.Collectors
import kotlin.collections.List
import org.apache.commons.text.StringSubstitutor

object SnowflakeTestUtils {
    @Throws(SQLException::class)
    fun dumpRawTable(database: JdbcDatabase, tableIdentifier: String?): List<JsonNode> {
        return dumpTable(
            listOf(
                quote(JavaBaseConstants.COLUMN_NAME_AB_RAW_ID),
                timestampToString(quote(JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)),
                timestampToString(quote(JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT)),
                quote(JavaBaseConstants.COLUMN_NAME_DATA),
                quote(JavaBaseConstants.COLUMN_NAME_AB_META),
                quote(JavaBaseConstants.COLUMN_NAME_AB_GENERATION_ID)
            ),
            database,
            tableIdentifier, // Raw tables still have lowercase names
            false
        )
    }

    @Throws(SQLException::class)
    fun dumpFinalTable(
        database: JdbcDatabase,
        databaseName: String,
        schema: String,
        table: String
    ): List<JsonNode> {
        // We have to discover the column names, because if we just SELECT * then snowflake will
        // upcase all
        // column names.
        val columns =
            database
                .queryJsons(
                    """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        ORDER BY ordinal_position;
        
        """.trimIndent(),
                    unescapeIdentifier(databaseName).uppercase(Locale.getDefault()),
                    unescapeIdentifier(schema).uppercase(Locale.getDefault()),
                    unescapeIdentifier(table).uppercase(Locale.getDefault())
                )
                .stream()
                .map { column: JsonNode ->
                    val quotedName = quote(column["COLUMN_NAME"].asText())
                    val type = column["DATA_TYPE"].asText()
                    when (type) {
                        "TIMESTAMP_TZ" -> timestampToString(quotedName)
                        "TIMESTAMP_NTZ",
                        "TIMESTAMP_LTZ" ->
                            "TO_VARCHAR($quotedName, 'YYYY-MM-DD\"T\"HH24:MI:SS.FF') as $quotedName"
                        "TIME" -> "TO_VARCHAR($quotedName, 'HH24:MI:SS.FF') as $quotedName"
                        "DATE" -> "TO_VARCHAR($quotedName, 'YYYY-MM-DD') as $quotedName"
                        else -> quotedName
                    }
                }
                .toList()
        return dumpTable(columns, database, quote(schema) + "." + quote(table), true)
    }

    /**
     * This is mostly identical to SnowflakeInsertDestinationAcceptanceTest, except it doesn't
     * verify table type.
     *
     * The columns param is a list of column names/aliases. For example, `"_airbyte_extracted_at ::
     * varchar AS "_airbyte_extracted_at"`.
     *
     * @param tableIdentifier Table identifier (e.g. "schema.table"), with quotes if necessary.
     */
    @Throws(SQLException::class)
    fun dumpTable(
        columns: List<String>,
        database: JdbcDatabase,
        tableIdentifier: String?,
        upcaseExtractedAt: Boolean
    ): List<JsonNode> {
        return database.bufferedResultSetQuery(
            { connection: Connection ->
                connection
                    .createStatement()
                    .executeQuery(
                        StringSubstitutor(
                                Map.of(
                                    "columns",
                                    columns.stream().collect(Collectors.joining(",")),
                                    "table",
                                    tableIdentifier,
                                    "extracted_at",
                                    if (upcaseExtractedAt) "_AIRBYTE_EXTRACTED_AT"
                                    else "\"_airbyte_extracted_at\""
                                )
                            )
                            .replace(
                                """
            SELECT ${'$'}{columns} FROM ${'$'}{table} ORDER BY ${'$'}{extracted_at} ASC
            
            """.trimIndent()
                            )
                    )
            },
            { queryResult: ResultSet -> SnowflakeSourceOperations().rowToJson(queryResult) }
        )
    }

    private fun quote(name: String): String {
        return '"'.toString() + SnowflakeSqlGenerator.escapeJsonIdentifier(name) + '"'
    }

    fun timestampToString(quotedName: String): String {
        return "TO_VARCHAR($quotedName, 'YYYY-MM-DD\"T\"HH24:MI:SS.FFTZH:TZM') as $quotedName"
    }

    private fun unescapeIdentifier(escapedIdentifier: String?): String {
        return escapedIdentifier!!.replace("\"\"", "\"")
    }
}
