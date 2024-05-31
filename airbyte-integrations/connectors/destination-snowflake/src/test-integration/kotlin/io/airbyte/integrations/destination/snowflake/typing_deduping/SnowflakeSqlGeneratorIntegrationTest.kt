/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeTypeAndDedupe
import io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabaseUtils
import io.airbyte.integrations.destination.snowflake.SnowflakeSourceOperations
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.dumpFinalTable
import io.airbyte.integrations.destination.snowflake.migrations.SnowflakeState
import java.nio.file.Path
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.util.*
import java.util.function.Function
import java.util.stream.Collectors
import java.util.stream.Stream
import javax.sql.DataSource
import org.apache.commons.lang3.StringUtils
import org.apache.commons.text.StringSubstitutor
import org.junit.jupiter.api.*
import org.junit.jupiter.api.function.Executable

class SnowflakeSqlGeneratorIntegrationTest : BaseSqlGeneratorIntegrationTest<SnowflakeState>() {
    override val supportsSafeCast: Boolean
        get() = true

    override val sqlGenerator: SnowflakeSqlGenerator
        get() = SnowflakeSqlGenerator(0)

    override val destinationHandler: SnowflakeDestinationHandler
        get() = SnowflakeDestinationHandler(databaseName, database, namespace.uppercase())

    override fun buildStreamId(
        namespace: String,
        finalTableName: String,
        rawTableName: String
    ): StreamId {
        return StreamId(
            namespace.uppercase(Locale.getDefault()),
            finalTableName.uppercase(Locale.getDefault()),
            namespace.uppercase(Locale.getDefault()),
            rawTableName,
            namespace,
            finalTableName
        )
    }

    @Throws(SQLException::class)
    override fun createNamespace(namespace: String) {
        database.execute(
            "CREATE SCHEMA IF NOT EXISTS \"" + namespace.uppercase(Locale.getDefault()) + '"'
        )
    }

    @Throws(Exception::class)
    override fun createRawTable(streamId: StreamId) {
        database.execute(
            StringSubstitutor(
                    java.util.Map.of(
                        "raw_table_id",
                        streamId.rawTableId(SnowflakeSqlGenerator.QUOTE)
                    )
                )
                .replace(
                    """
            CREATE TABLE ${'$'}{raw_table_id} (
              "_airbyte_raw_id" TEXT NOT NULL,
              "_airbyte_data" VARIANT NOT NULL,
              "_airbyte_extracted_at" TIMESTAMP_TZ NOT NULL,
              "_airbyte_loaded_at" TIMESTAMP_TZ
            )
            
            """.trimIndent()
                )
        )
    }

    @Throws(Exception::class)
    override fun dumpRawTableRecords(streamId: StreamId): List<JsonNode> {
        return SnowflakeTestUtils.dumpRawTable(
            database,
            streamId.rawTableId(SnowflakeSqlGenerator.QUOTE)
        )
    }

    @Throws(Exception::class)
    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun dumpFinalTableRecords(streamId: StreamId, suffix: String?): List<JsonNode> {
        return dumpFinalTable(
            database,
            databaseName,
            streamId.finalNamespace,
            streamId.finalName + suffix!!.uppercase(Locale.getDefault())
        )
    }

    @Throws(SQLException::class)
    override fun teardownNamespace(namespace: String) {
        database.execute(
            "DROP SCHEMA IF EXISTS \"" + namespace.uppercase(Locale.getDefault()) + '"'
        )
    }

    @Throws(Exception::class)
    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun insertFinalTableRecords(
        includeCdcDeletedAt: Boolean,
        streamId: StreamId,
        suffix: String?,
        records: List<JsonNode>
    ) {
        val columnNames =
            if (includeCdcDeletedAt) FINAL_TABLE_COLUMN_NAMES_CDC else FINAL_TABLE_COLUMN_NAMES
        val cdcDeletedAtName = if (includeCdcDeletedAt) ",\"_AB_CDC_DELETED_AT\"" else ""
        val cdcDeletedAtExtract = if (includeCdcDeletedAt) ",column19" else ""
        val recordsText =
            records
                .stream() // For each record, convert it to a string like "(rawId, extractedAt,
                // loadedAt, data)"
                .map { record: JsonNode ->
                    columnNames
                        .stream()
                        .map { fieldName: String? -> record[fieldName] }
                        .map { node: JsonNode? -> this.dollarQuoteWrap(node) }
                        .collect(Collectors.joining(","))
                }
                .map { row: String -> "($row)" }
                .collect(Collectors.joining(","))

        database.execute(
            StringSubstitutor(
                    java.util.Map.of(
                        "final_table_id",
                        streamId.finalTableId(
                            SnowflakeSqlGenerator.QUOTE,
                            suffix!!.uppercase(Locale.getDefault())
                        ),
                        "cdc_deleted_at_name",
                        cdcDeletedAtName,
                        "cdc_deleted_at_extract",
                        cdcDeletedAtExtract,
                        "records",
                        recordsText
                    ),
                    "#{",
                    "}"
                )
                .replace( // Similar to insertRawTableRecords, some of these columns are declared as
                    // string and wrapped in
                    // parse_json().
                    """
            INSERT INTO #{final_table_id} (
              "_AIRBYTE_RAW_ID",
              "_AIRBYTE_EXTRACTED_AT",
              "_AIRBYTE_META",
              "ID1",
              "ID2",
              "UPDATED_AT",
              "STRUCT",
              "ARRAY",
              "STRING",
              "NUMBER",
              "INTEGER",
              "BOOLEAN",
              "TIMESTAMP_WITH_TIMEZONE",
              "TIMESTAMP_WITHOUT_TIMEZONE",
              "TIME_WITH_TIMEZONE",
              "TIME_WITHOUT_TIMEZONE",
              "DATE",
              "UNKNOWN"
              #{cdc_deleted_at_name}
            )
            SELECT
              column1,
              column2,
              PARSE_JSON(column3),
              column4,
              column5,
              column6,
              PARSE_JSON(column7),
              PARSE_JSON(column8),
              column9,
              column10,
              column11,
              column12,
              column13,
              column14,
              column15,
              column16,
              column17,
              PARSE_JSON(column18)
              #{cdc_deleted_at_extract}
            FROM VALUES
              #{records}
            
            """.trimIndent()
                )
        )
    }

    private fun dollarQuoteWrap(node: JsonNode?): String {
        if (node == null) {
            return "NULL"
        }
        val stringContents = if (node.isTextual) node.asText() else node.toString()
        // Use dollar quotes to avoid needing to escape quotes
        return StringUtils.wrap(stringContents.replace("$$", "\\$\\$"), "$$")
    }

    @Throws(Exception::class)
    override fun insertRawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        val recordsText =
            records
                .stream() // For each record, convert it to a string like "(rawId, extractedAt,
                // loadedAt, data)"
                .map { record: JsonNode ->
                    JavaBaseConstants.V2_RAW_TABLE_COLUMN_NAMES.stream()
                        .map { fieldName: String? -> record[fieldName] }
                        .map { node: JsonNode? -> this.dollarQuoteWrap(node) }
                        .collect(Collectors.joining(","))
                }
                .map { row: String -> "($row)" }
                .collect(Collectors.joining(","))
        database.execute(
            StringSubstitutor(
                    java.util.Map.of(
                        "raw_table_id",
                        streamId.rawTableId(SnowflakeSqlGenerator.QUOTE),
                        "records_text",
                        recordsText
                    ), // Use different delimiters because we're using dollar quotes in the query.
                    "#{",
                    "}"
                )
                .replace( // Snowflake doesn't let you directly insert a parse_json expression, so
                    // we have to use a subquery.
                    """
            INSERT INTO #{raw_table_id} (
              "_airbyte_raw_id",
              "_airbyte_extracted_at",
              "_airbyte_loaded_at",
              "_airbyte_data"
            )
            SELECT
              column1,
              column2,
              column3,
              PARSE_JSON(column4)
            FROM VALUES
              #{records_text};
            
            """.trimIndent()
                )
        )
    }

    override val finalMetadataColumnNames: Map<String, String>
        get() = AbstractSnowflakeTypingDedupingTest.FINAL_METADATA_COLUMN_NAMES

    @Test
    @Throws(Exception::class)
    override fun testCreateTableIncremental() {
        val sql: Sql = generator.createTable(incrementalDedupStream, "", false)
        destinationHandler.execute(sql)

        // Note that USERS_FINAL is uppercased here. This is intentional, because snowflake upcases
        // unquoted
        // identifiers.
        val tableKind =
            database
                .queryJsons(
                    java.lang.String.format(
                        "SHOW TABLES LIKE '%s' IN SCHEMA \"%s\";",
                        "USERS_FINAL",
                        namespace.uppercase()
                    )
                )
                .stream()
                .map<String> { record: JsonNode -> record["kind"].asText() }
                .findFirst()
        val columns =
            database
                .queryJsons(
                    """
        SELECT column_name, data_type, numeric_precision, numeric_scale
        FROM information_schema.columns
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        ORDER BY ordinal_position;
        
        """.trimIndent(),
                    databaseName!!,
                    namespace.uppercase(),
                    "USERS_FINAL"
                )
                .stream()
                .collect(
                    Collectors.toMap(
                        { record: JsonNode -> record["COLUMN_NAME"].asText() },
                        Function<JsonNode, String> toMap@{ record: JsonNode ->
                            val type = record["DATA_TYPE"].asText()
                            if (type == "NUMBER") {
                                return@toMap String.format(
                                    "NUMBER(%s, %s)",
                                    record["NUMERIC_PRECISION"].asText(),
                                    record["NUMERIC_SCALE"].asText()
                                )
                            }
                            type
                        }
                    )
                )
        Assertions.assertAll(
            Executable {
                Assertions.assertEquals(
                    Optional.of("TABLE"),
                    tableKind,
                    "Table should be permanent, not transient"
                )
            },
            Executable {
                Assertions.assertEquals(
                    ImmutableMap.builder<Any, Any>()
                        .put("_AIRBYTE_RAW_ID", "TEXT")
                        .put("_AIRBYTE_EXTRACTED_AT", "TIMESTAMP_TZ")
                        .put("_AIRBYTE_META", "VARIANT")
                        .put("ID1", "NUMBER(38, 0)")
                        .put("ID2", "NUMBER(38, 0)")
                        .put("UPDATED_AT", "TIMESTAMP_TZ")
                        .put("STRUCT", "OBJECT")
                        .put("ARRAY", "ARRAY")
                        .put("STRING", "TEXT")
                        .put("NUMBER", "FLOAT")
                        .put("INTEGER", "NUMBER(38, 0)")
                        .put("BOOLEAN", "BOOLEAN")
                        .put("TIMESTAMP_WITH_TIMEZONE", "TIMESTAMP_TZ")
                        .put("TIMESTAMP_WITHOUT_TIMEZONE", "TIMESTAMP_NTZ")
                        .put("TIME_WITH_TIMEZONE", "TEXT")
                        .put("TIME_WITHOUT_TIMEZONE", "TIME")
                        .put("DATE", "DATE")
                        .put("UNKNOWN", "VARIANT")
                        .build(),
                    columns
                )
            }
        )
    }

    @Throws(Exception::class)
    override fun createV1RawTable(v1RawTable: StreamId) {
        database.execute(
            java.lang.String.format(
                """
            CREATE SCHEMA IF NOT EXISTS %s;
            CREATE TABLE IF NOT EXISTS %s.%s (
              %s VARCHAR PRIMARY KEY,
              %s VARIANT,
              %s TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp()
            ) data_retention_time_in_days = 0;
        
        """.trimIndent(),
                v1RawTable.rawNamespace,
                v1RawTable.rawNamespace,
                v1RawTable.rawName,
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_DATA,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT
            )
        )
    }

    @Throws(Exception::class)
    override fun insertV1RawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        val recordsText =
            records
                .stream()
                .map { record: JsonNode ->
                    JavaBaseConstants.LEGACY_RAW_TABLE_COLUMNS.stream()
                        .map { fieldName: String? -> record[fieldName] }
                        .map { value: JsonNode? ->
                            if (value == null) "NULL"
                            else if (value.isTextual) value.asText() else value.toString()
                        }
                        .map { v: String -> if ("NULL" == v) v else StringUtils.wrap(v, "$$") }
                        .collect(Collectors.joining(","))
                }
                .map { row: String -> "($row)" }
                .collect(Collectors.joining(","))
        val insert =
            StringSubstitutor(
                    java.util.Map.of<String, String>(
                        "v1_raw_table_id",
                        java.lang.String.join(".", streamId.rawNamespace, streamId.rawName),
                        "records",
                        recordsText
                    ), // Use different delimiters because we're using dollar quotes in the query.
                    "#{",
                    "}"
                )
                .replace(
                    """
            INSERT INTO #{v1_raw_table_id} (_airbyte_ab_id, _airbyte_data, _airbyte_emitted_at)
            SELECT column1, PARSE_JSON(column2), column3 FROM VALUES
              #{records};
            
            """.trimIndent()
                )
        database.execute(insert)
    }

    @Throws(Exception::class)
    override fun dumpV1RawTableRecords(streamId: StreamId): List<JsonNode> {
        val columns: String =
            Stream.of(
                    JavaBaseConstants.COLUMN_NAME_AB_ID,
                    SnowflakeTestUtils.timestampToString(JavaBaseConstants.COLUMN_NAME_EMITTED_AT),
                    JavaBaseConstants.COLUMN_NAME_DATA
                )
                .collect(Collectors.joining(","))
        return database.bufferedResultSetQuery<JsonNode>(
            { connection: Connection ->
                connection
                    .createStatement()
                    .executeQuery(
                        StringSubstitutor(
                                java.util.Map.of<String, Any>(
                                    "columns",
                                    columns,
                                    "table",
                                    java.lang.String.join(
                                        ".",
                                        streamId.rawNamespace,
                                        streamId.rawName
                                    )
                                )
                            )
                            .replace(
                                """
            SELECT ${'$'}{columns} FROM ${'$'}{table} ORDER BY _airbyte_emitted_at ASC
            
            """.trimIndent()
                            )
                    )
            },
            { queryContext: ResultSet? -> SnowflakeSourceOperations().rowToJson(queryContext!!) }
        )
    }

    override fun migrationAssertions(v1RawRecords: List<JsonNode>, v2RawRecords: List<JsonNode>) {
        val v2RecordMap: Map<String, JsonNode> =
            v2RawRecords
                .stream()
                .collect(
                    Collectors.toMap(
                        { record: JsonNode ->
                            record[JavaBaseConstants.COLUMN_NAME_AB_RAW_ID].asText()
                        },
                        Function.identity()
                    )
                )
        Assertions.assertAll(
            Executable { Assertions.assertEquals(5, v1RawRecords.size) },
            Executable { Assertions.assertEquals(5, v2RawRecords.size) }
        )
        v1RawRecords.forEach { v1Record: JsonNode ->
            val v1id =
                v1Record[JavaBaseConstants.COLUMN_NAME_AB_ID.uppercase(Locale.getDefault())]
                    .asText()
            Assertions.assertAll(
                Executable {
                    Assertions.assertEquals(
                        v1id,
                        v2RecordMap[v1id]!![JavaBaseConstants.COLUMN_NAME_AB_RAW_ID].asText()
                    )
                },
                Executable {
                    Assertions.assertEquals(
                        v1Record[
                                JavaBaseConstants.COLUMN_NAME_EMITTED_AT.uppercase(
                                    Locale.getDefault()
                                )
                            ]
                            .asText(),
                        v2RecordMap[v1id]!![JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT].asText()
                    )
                },
                Executable {
                    Assertions.assertNull(
                        v2RecordMap[v1id]!![JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT]
                    )
                }
            )
            var originalData =
                v1Record[JavaBaseConstants.COLUMN_NAME_DATA.uppercase(Locale.getDefault())]
            var migratedData = v2RecordMap[v1id]!![JavaBaseConstants.COLUMN_NAME_DATA]
            migratedData =
                if (migratedData.isTextual) Jsons.deserializeExact(migratedData.asText())
                else migratedData
            originalData =
                if (originalData.isTextual) Jsons.deserializeExact(migratedData.asText())
                else originalData
            // hacky thing because we only care about the data contents.
            // diffRawTableRecords makes some assumptions about the structure of the blob.
            DIFFER.diffFinalTableRecords(
                java.util.List.of(originalData),
                java.util.List.of(migratedData)
            )
        }
    }

    @Disabled(
        "We removed the optimization to only set the loaded_at column for new records after certain _extracted_at"
    )
    @Test
    @Throws(Exception::class)
    override fun ignoreOldRawRecords() {
        super.ignoreOldRawRecords()
    }

    /**
     * Verify that the final table does not include NON-NULL PKs (after
     * https://github.com/airbytehq/airbyte/pull/31082)
     */
    @Test
    @Throws(Exception::class)
    fun ensurePKsAreIndexedUnique() {
        createRawTable(streamId)
        insertRawTableRecords(
            streamId,
            java.util.List.of(
                Jsons.deserialize(
                    """
            {
              "_airbyte_raw_id": "14ba7c7f-e398-4e69-ac22-28d578400dbc",
              "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
              "_airbyte_data": {
                "id1": 1,
                "id2": 2
              }
            }
            
            """.trimIndent()
                )
            )
        )

        val createTable: Sql = generator.createTable(incrementalDedupStream, "", false)

        // should be OK with new tables
        destinationHandler.execute(createTable)
        var initialStates =
            destinationHandler.gatherInitialState(java.util.List.of(incrementalDedupStream))
        Assertions.assertEquals(1, initialStates.size)
        Assertions.assertFalse(initialStates.first().isSchemaMismatch)
        destinationHandler.execute(Sql.of("DROP TABLE " + streamId.finalTableId("")))

        // Hack the create query to add NOT NULLs to emulate the old behavior
        val createTableModified: List<List<String>> =
            createTable.transactions
                .stream()
                .map<List<String>> { transaction: List<String> ->
                    transaction
                        .stream()
                        .map { statement: String ->
                            Arrays.stream(
                                    statement
                                        .split(System.lineSeparator().toRegex())
                                        .dropLastWhile { it.isEmpty() }
                                        .toTypedArray()
                                )
                                .map { line: String ->
                                    if (
                                        !line.contains("CLUSTER") &&
                                            (line.contains("id1") ||
                                                line.contains("id2") ||
                                                line.contains("ID1") ||
                                                line.contains("ID2"))
                                    )
                                        line.replace(",", " NOT NULL,")
                                    else line
                                }
                                .collect(Collectors.joining("\r\n"))
                        }
                        .toList()
                }
                .toList()
        destinationHandler.execute(Sql(createTableModified))
        initialStates =
            destinationHandler.gatherInitialState(java.util.List.of(incrementalDedupStream))
        Assertions.assertEquals(1, initialStates.size)
        Assertions.assertTrue(initialStates[0].isSchemaMismatch)
    }

    @Test
    @Throws(Exception::class)
    fun dst_test_oldSyncRunsThroughTransition_thenNewSyncRuns_dedup() {
        this.createRawTable(this.streamId)
        this.createFinalTable(this.incrementalDedupStream, "")
        this.insertRawTableRecords(
            this.streamId,
            java.util.List
                .of( // 2 records written by a sync running on the old version of snowflake
                    Jsons.deserialize(
                        """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          
                          """.trimIndent()
                    ),
                    Jsons.deserialize(
                        """
                          {
                            "_airbyte_raw_id": "post-dst local tz 2",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob00"
                            }
                          }
                          
                          """.trimIndent()
                    ), // and 2 records that got successfully loaded.
                    Jsons.deserialize(
                        """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 3",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_loaded_at": "1970-01-01T00:00:00Z",
                            "_airbyte_data": {
                              "id1": 3,
                              "id2": 100,
                              "string": "Charlie00"
                            }
                          }
                          
                          """.trimIndent()
                    ),
                    Jsons.deserialize(
                        """
                          {
                            "_airbyte_raw_id": "post-dst local tz 4",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_loaded_at": "1970-01-01T00:00:00Z",
                            "_airbyte_data": {
                              "id1": 4,
                              "id2": 100,
                              "string": "Dave00"
                            }
                          }
                          
                          """.trimIndent()
                    )
                )
        )
        this.insertFinalTableRecords(
            false,
            this.streamId,
            "",
            java.util.List.of(
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 3",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_meta": {"errors": []},
                            "id1": 3,
                            "id2": 100,
                            "string": "Charlie00"
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst local tz 4",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_meta": {"errors": []},
                            "id1": 4,
                            "id2": 100,
                            "string": "Dave00"
                          }
                          
                          """.trimIndent()
                )
            )
        )
        // Gather initial state at the start of our updated sync
        val initialState =
            destinationHandler
                .gatherInitialState(java.util.List.of(this.incrementalDedupStream))
                .first()
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // insert raw records with updates
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 3",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 3,
                              "id2": 100,
                              "string": "Charlie01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 4",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 4,
                              "id2": 100,
                              "string": "Dave01"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            this.generator,
            this.destinationHandler,
            this.incrementalDedupStream,
            initialState.initialRawTableStatus.maxProcessedTimestamp,
            ""
        )

        DIFFER.diffFinalTableRecords(
            java.util.List.of(
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }
                              
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 3",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 3,
                                "ID2": 100,
                                "STRING": "Charlie01"
                              }
                              
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 4",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 4,
                                "ID2": 100,
                                "STRING": "Dave01"
                              }
                              
                              """.trimIndent()
                )
            ),
            this.dumpFinalTableRecords(this.streamId, "")
        )
    }

    @Test
    @Throws(Exception::class)
    fun dst_test_oldSyncRunsBeforeTransition_thenNewSyncRunsThroughTransition_dedup() {
        this.createRawTable(this.streamId)
        this.createFinalTable(this.incrementalDedupStream, "")
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // record written by a sync running on the old version of snowflake
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )
        // Gather initial state at the start of our updated sync
        val initialState =
            destinationHandler
                .gatherInitialState(java.util.List.of(this.incrementalDedupStream))
                .first()
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // update the record twice
                // this never really happens, but verify that it works
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice02"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            this.generator,
            this.destinationHandler,
            this.incrementalDedupStream,
            initialState.initialRawTableStatus.maxProcessedTimestamp,
            ""
        )

        DIFFER.diffFinalTableRecords(
            java.util.List.of(
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice02"
                              }
                              
                              """.trimIndent()
                )
            ),
            this.dumpFinalTableRecords(this.streamId, "")
        )
    }

    @Test
    @Throws(Exception::class)
    fun dst_test_oldSyncRunsBeforeTransition_thenNewSyncRunsBeforeTransition_thenNewSyncRunsThroughTransition_dedup() {
        this.createRawTable(this.streamId)
        this.createFinalTable(this.incrementalDedupStream, "")
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // records written by a sync running on the old version of snowflake
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 2",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob00"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        // Gather initial state at the start of our first() new sync
        val initialState =
            destinationHandler
                .gatherInitialState(java.util.List.of(this.incrementalDedupStream))
                .first()
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // update the records
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob01"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            this.generator,
            this.destinationHandler,
            this.incrementalDedupStream,
            initialState.initialRawTableStatus.maxProcessedTimestamp,
            ""
        )

        DIFFER.diffFinalTableRecords(
            java.util.List.of(
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }
                              
                              """.trimIndent()
                )
            ),
            this.dumpFinalTableRecords(this.streamId, "")
        )

        // Gather initial state at the start of our second new sync
        val initialState2 =
            destinationHandler
                .gatherInitialState(java.util.List.of(this.incrementalDedupStream))
                .first()
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // update the records again
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice02"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob02"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            this.generator,
            this.destinationHandler,
            this.incrementalDedupStream,
            initialState2.initialRawTableStatus.maxProcessedTimestamp,
            ""
        )

        DIFFER.diffFinalTableRecords(
            java.util.List.of(
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice02"
                              }
                              
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob02"
                              }
                              
                              """.trimIndent()
                )
            ),
            this.dumpFinalTableRecords(this.streamId, "")
        )
    }

    @Test
    @Throws(Exception::class)
    fun dst_test_oldSyncRunsThroughTransition_thenNewSyncRuns_append() {
        this.createRawTable(this.streamId)
        this.createFinalTable(this.incrementalAppendStream, "")
        this.insertRawTableRecords(
            this.streamId,
            java.util.List
                .of( // 2 records written by a sync running on the old version of snowflake
                    Jsons.deserialize(
                        """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          
                          """.trimIndent()
                    ),
                    Jsons.deserialize(
                        """
                          {
                            "_airbyte_raw_id": "post-dst local tz 2",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob00"
                            }
                          }
                          
                          """.trimIndent()
                    ), // and 2 records that got successfully loaded with local TZ.
                    Jsons.deserialize(
                        """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 3",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_loaded_at": "1970-01-01T00:00:00Z",
                            "_airbyte_data": {
                              "id1": 3,
                              "id2": 100,
                              "string": "Charlie00"
                            }
                          }
                          
                          """.trimIndent()
                    ),
                    Jsons.deserialize(
                        """
                          {
                            "_airbyte_raw_id": "post-dst local tz 4",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_loaded_at": "1970-01-01T00:00:00Z",
                            "_airbyte_data": {
                              "id1": 4,
                              "id2": 100,
                              "string": "Dave00"
                            }
                          }
                          
                          """.trimIndent()
                    )
                )
        )
        this.insertFinalTableRecords(
            false,
            this.streamId,
            "",
            java.util.List.of(
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 3",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00-08:00",
                            "_airbyte_meta": {"errors": []},
                            "id1": 3,
                            "id2": 100,
                            "string": "Charlie00"
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst local tz 4",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00-07:00",
                            "_airbyte_meta": {"errors": []},
                            "id1": 4,
                            "id2": 100,
                            "string": "Dave00"
                          }
                          
                          """.trimIndent()
                )
            )
        )
        // Gather initial state at the start of our updated sync
        val initialState =
            destinationHandler
                .gatherInitialState(java.util.List.of(this.incrementalAppendStream))
                .first()
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // insert raw records with updates
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 3",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 3,
                              "id2": 100,
                              "string": "Charlie01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 4",
                            "_airbyte_extracted_at": "2024-03-10T02:02:00Z",
                            "_airbyte_data": {
                              "id1": 4,
                              "id2": 100,
                              "string": "Dave01"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            this.generator,
            this.destinationHandler,
            this.incrementalAppendStream,
            initialState.initialRawTableStatus.maxProcessedTimestamp,
            ""
        )

        DIFFER.diffFinalTableRecords(
            java.util.List.of(
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice00"
                              }
                              
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst local tz 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob00"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }
                              
                              """.trimIndent()
                ), // note local TZ here. This record was loaded by an older version of the
                // connector.
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 3",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000-08:00",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 3,
                                "ID2": 100,
                                "STRING": "Charlie00"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 3",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 3,
                                "ID2": 100,
                                "STRING": "Charlie01"
                              }
                              
                              """.trimIndent()
                ), // note local TZ here. This record was loaded by an older version of the
                // connector.
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst local tz 4",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000-07:00",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 4,
                                "ID2": 100,
                                "STRING": "Dave00"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 4",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:02:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 4,
                                "ID2": 100,
                                "STRING": "Dave01"
                              }
                              
                              """.trimIndent()
                )
            ),
            this.dumpFinalTableRecords(this.streamId, "")
        )
    }

    @Test
    @Throws(Exception::class)
    fun dst_test_oldSyncRunsBeforeTransition_thenNewSyncRunsThroughTransition_append() {
        this.createRawTable(this.streamId)
        this.createFinalTable(this.incrementalAppendStream, "")
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // record written by a sync running on the old version of snowflake
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )
        // Gather initial state at the start of our updated sync
        val initialState =
            destinationHandler
                .gatherInitialState(java.util.List.of(this.incrementalAppendStream))
                .first()
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // update the record twice
                // this never really happens, but verify that it works
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice02"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            this.generator,
            this.destinationHandler,
            this.incrementalAppendStream,
            initialState.initialRawTableStatus.maxProcessedTimestamp,
            ""
        )

        DIFFER.diffFinalTableRecords(
            java.util.List.of(
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice00"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice02"
                              }
                              
                              """.trimIndent()
                )
            ),
            this.dumpFinalTableRecords(this.streamId, "")
        )
    }

    @Test
    @Throws(Exception::class)
    fun dst_test_oldSyncRunsBeforeTransition_thenNewSyncRunsBeforeTransition_thenNewSyncRunsThroughTransition_append() {
        this.createRawTable(this.streamId)
        this.createFinalTable(this.incrementalAppendStream, "")
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // records written by a sync running on the old version of snowflake
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 1",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice00"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst local tz 2",
                            "_airbyte_extracted_at": "2024-03-10T01:59:00-08:00",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob00"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        // Gather initial state at the start of our first() new sync
        val initialState =
            destinationHandler
                .gatherInitialState(java.util.List.of(this.incrementalAppendStream))
                .first()
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // update the records
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice01"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "pre-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:00:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob01"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            this.generator,
            this.destinationHandler,
            this.incrementalAppendStream,
            initialState.initialRawTableStatus.maxProcessedTimestamp,
            ""
        )

        DIFFER.diffFinalTableRecords(
            java.util.List.of(
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice00"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob00"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }
                              
                              """.trimIndent()
                )
            ),
            this.dumpFinalTableRecords(this.streamId, "")
        )

        // Gather initial state at the start of our second new sync
        val initialState2 =
            destinationHandler
                .gatherInitialState(java.util.List.of(this.incrementalAppendStream))
                .first()
        this.insertRawTableRecords(
            this.streamId,
            java.util.List.of( // update the records again
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 1",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 1,
                              "id2": 100,
                              "string": "Alice02"
                            }
                          }
                          
                          """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                          {
                            "_airbyte_raw_id": "post-dst utc 2",
                            "_airbyte_extracted_at": "2024-03-10T02:01:00Z",
                            "_airbyte_data": {
                              "id1": 2,
                              "id2": 100,
                              "string": "Bob02"
                            }
                          }
                          
                          """.trimIndent()
                )
            )
        )

        executeTypeAndDedupe(
            this.generator,
            this.destinationHandler,
            this.incrementalAppendStream,
            initialState2.initialRawTableStatus.maxProcessedTimestamp,
            ""
        )

        DIFFER.diffFinalTableRecords(
            java.util.List.of(
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice00"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice01"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 1",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 1,
                                "ID2": 100,
                                "STRING": "Alice02"
                              }
                              
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst local tz 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T01:59:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob00"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "pre-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:00:00.000000000Z",
                                "_AIRBYTE_META": {
                                  "errors": []
                                },
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob01"
                              }
                              """.trimIndent()
                ),
                Jsons.deserialize(
                    """
                              {
                                "_AIRBYTE_RAW_ID": "post-dst utc 2",
                                "_AIRBYTE_EXTRACTED_AT": "2024-03-10T02:01:00.000000000Z",
                                "_AIRBYTE_META": {"errors": []},
                                "ID1": 2,
                                "ID2": 100,
                                "STRING": "Bob02"
                              }
                              
                              """.trimIndent()
                )
            ),
            this.dumpFinalTableRecords(this.streamId, "")
        )
    }

    // This is disabled because snowflake doesn't transform long identifiers
    @Disabled
    override fun testLongIdentifierHandling() {
        super.testLongIdentifierHandling()
    }

    companion object {
        private var config =
            Jsons.deserialize(IOs.readFile(Path.of("secrets/1s1t_internal_staging_config.json")))
        private var databaseName = config[JdbcUtils.DATABASE_KEY].asText()
        private var dataSource: DataSource =
            SnowflakeDatabaseUtils.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS)
        private var database: JdbcDatabase = SnowflakeDatabaseUtils.getDatabase(dataSource)

        @JvmStatic
        @BeforeAll
        fun setupSnowflake(): Unit {
            dataSource =
                SnowflakeDatabaseUtils.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS)
            database = SnowflakeDatabaseUtils.getDatabase(dataSource)
        }

        @JvmStatic
        @AfterAll
        @Throws(Exception::class)
        fun teardownSnowflake(): Unit {
            DataSourceFactory.close(dataSource)
        }
    }
}
