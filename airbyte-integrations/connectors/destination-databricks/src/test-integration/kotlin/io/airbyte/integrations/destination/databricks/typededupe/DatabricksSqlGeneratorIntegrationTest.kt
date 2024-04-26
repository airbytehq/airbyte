/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.typededupe

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.BaseSqlGeneratorIntegrationTest
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.ConnectorClientsFactory
import io.airbyte.integrations.destination.databricks.DatabricksNamingTransformer
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksStorageOperations
import io.airbyte.integrations.destination.databricks.model.DatabricksConnectorConfig
import io.airbyte.integrations.destination.databricks.sync.DatabricksStreamOperations
import java.nio.file.Files
import java.nio.file.Path
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.time.Duration
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.*
import java.util.Map
import java.util.concurrent.TimeUnit
import java.util.stream.Collectors
import java.util.stream.Stream
import kotlin.collections.List
import kotlin.streams.asSequence
import org.apache.commons.text.StringSubstitutor
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.mockito.Mockito.*

class DatabricksSqlGeneratorIntegrationTest :
    BaseSqlGeneratorIntegrationTest<MinimumDestinationState.Impl>() {
    companion object {
        private var jdbcDatabase: JdbcDatabase = mock()
        private var connectorConfig: DatabricksConnectorConfig = mock()
        @JvmStatic
        @BeforeAll
        fun setupDatabase() {
            val rawConfig = Files.readString(Path.of("secrets/new_config.json"))
            connectorConfig = DatabricksConnectorConfig.deserialize(Jsons.deserialize(rawConfig))
            jdbcDatabase =
                DefaultJdbcDatabase(ConnectorClientsFactory.createDataSource(connectorConfig))
        }
    }

    override val destinationHandler: DestinationHandler<MinimumDestinationState.Impl>
        get() =
            DatabricksDestinationHandler(
                connectorConfig.database,
                jdbcDatabase,
                connectorConfig.rawSchemaOverride,
            )
    override val sqlGenerator: SqlGenerator
        get() = DatabricksSqlGenerator(DatabricksNamingTransformer(), connectorConfig.database)
    private val databricksSqlGenerator = sqlGenerator as DatabricksSqlGenerator

    override fun createNamespace(namespace: String?) {
        destinationHandler.execute(sqlGenerator.createSchema(namespace))
    }

    override fun createRawTable(streamId: StreamId) {
        destinationHandler.execute(databricksSqlGenerator.createRawTable(streamId))
    }

    override fun createV1RawTable(v1RawTable: StreamId) {
        TODO("Not yet implemented")
    }

    override fun insertRawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        // Exercise using the original inserts code path
        val ops =
            DatabricksStorageOperations(
                sqlGenerator,
                destinationHandler,
                ConnectorClientsFactory.createWorkspaceClient(
                    connectorConfig.hostname,
                    connectorConfig.apiAuthentication,
                ),
                connectorConfig.database,
            )
        ops.prepareStagingVolume(incrementalDedupStream.id)
        val streamOps = DatabricksStreamOperations(ops, FileUploadFormat.CSV)
        val transformedRecords: Stream<PartialAirbyteMessage> =
            records.stream().map {
                PartialAirbyteMessage()
                    .withSerialized(Jsons.serialize(it.get("_airbyte_data")))
                    .withRecord(
                        PartialAirbyteRecordMessage()
                            .withEmittedAt(
                                ZonedDateTime.parse(
                                    it.get("_airbyte_extracted_at").asText(),
                                    DateTimeFormatter.ISO_ZONED_DATE_TIME,
                                )
                                    .toInstant()
                                    .toEpochMilli(),
                            ),
                    )
            }
        streamOps.writeRecords(incrementalDedupStream, transformedRecords)
    }

    override fun insertV1RawTableRecords(streamId: StreamId, records: List<JsonNode>) {
        TODO("Not yet implemented")
    }

    override fun insertFinalTableRecords(
        includeCdcDeletedAt: Boolean,
        streamId: StreamId,
        suffix: String?,
        records: List<JsonNode>
    ) {
        val columnNames =
            if (includeCdcDeletedAt) FINAL_TABLE_COLUMN_NAMES_CDC else FINAL_TABLE_COLUMN_NAMES

        val sqlValue = { value: JsonNode? ->
            value?.let {
                if (value.isTextual) "'${value.asText()}'"
                else if (value.isNumber) "$value" else "'${value}'"
            }
                ?: "NULL"
        }
        val columnStr = columnNames.joinToString { "`$it`" }
        val colNumberStr = IntRange(1, if(includeCdcDeletedAt) 19 else 18).joinToString { "`col$it`" }
        val values =
            records
                .stream()
                .asSequence()
                .map { json ->
                    columnNames
                        .stream()
                        .asSequence()
                        .map { json.get(it) }
                        .map(sqlValue)
                        .joinToString(prefix = "(", postfix = ")")
                }
                .joinToString(", \n")
        val insertRecordsSql =
            """
            | INSERT INTO ${connectorConfig.database}.${streamId.finalTableId(DatabricksSqlGenerator.QUOTE, suffix!!.lowercase())} (
            | $columnStr
            | )
            | SELECT
            | $colNumberStr
            | FROM 
            | VALUES
            |${values.replaceIndent("   ")}
        """.trimMargin()
        println(insertRecordsSql)
        jdbcDatabase.execute(insertRecordsSql)
    }

    override fun dumpRawTableRecords(streamId: StreamId): List<JsonNode> {
        TODO("Not yet implemented")
    }

    override fun dumpFinalTableRecords(streamId: StreamId, suffix: String?): List<JsonNode> {
        return jdbcDatabase.bufferedResultSetQuery<JsonNode>(
            { connection: Connection ->
                connection.createStatement().executeQuery(
                    """
                        SELECT *
                        FROM ${connectorConfig.database}.${streamId.finalTableId(DatabricksSqlGenerator.QUOTE, suffix!!)} 
                        ORDER BY ${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT} ASC
                    """.trimIndent()
                )
            },
            { queryContext: ResultSet ->
                JdbcSourceOperations().rowToJson(
                    queryContext,
                )
            },
        )
    }

    private fun dumpTable(columns: List<String>,
                          database: JdbcDatabase,
                          tableIdentifier: String): List<JsonNode> {
        return database.bufferedResultSetQuery<JsonNode>(
            { connection: Connection ->
                connection.createStatement().executeQuery(
                    """
                        SELECT ${columns.joinToString(",")}
                        FROM $tableIdentifier ORDER BY ${JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT} ASC
                    """.trimIndent()
                )
            },
            { queryContext: ResultSet ->
                JdbcSourceOperations().rowToJson(
                    queryContext,
                )
            },
        )
    }

    override fun teardownNamespace(namespace: String?) {
        jdbcDatabase.execute("DROP SCHEMA IF EXISTS ${connectorConfig.database}.${namespace!!.lowercase(Locale.getDefault())} CASCADE")
//        println("Skipping teardown for now, re-enable $namespace")
    }

    @Disabled override fun testCreateTableIncremental() {}

    @Disabled("No V1 Table migration for databricks") override fun testV1V2migration() {}

    @Timeout(value = 5, unit = TimeUnit.MINUTES)
    @Test
    fun randomTest() {
        //        createRawTable(incrementalDedupStream.id)
        createFinalTable(cdcIncrementalDedupStream, "")
        //        val sql = sqlGenerator.createTable(incrementalDedupStream, "", true)
        //        val ops = DatabricksStorageOperations(
        //            sqlGenerator,
        //            destinationHandler,
        //            ConnectorClientsFactory.createWorkspaceClient(
        //                connectorConfig.hostname,
        //                connectorConfig.apiAuthentication,
        //            ),
        //            connectorConfig.database,
        //        )
        //        ops.prepareStagingVolume(incrementalDedupStream.id)
        //        val streamOps = DatabricksStreamOperations(ops, FileUploadFormat.CSV)
        //        var records: Stream<PartialAirbyteMessage> =
        //            BaseTypingDedupingTest.readRecords("sqlgenerator/alltypes_inputrecords.jsonl")
        //                .stream()
        //                .map {
        //                    PartialAirbyteMessage()
        //                        .withSerialized(Jsons.serialize(it.get("_airbyte_data")))
        //                        .withRecord(
        //                            PartialAirbyteRecordMessage()
        //                                .withEmittedAt(ZonedDateTime
        //                                    .parse(it.get("_airbyte_extracted_at").asText(),
        // DateTimeFormatter.ISO_ZONED_DATE_TIME)
        //                                    .toInstant()
        //                                    .toEpochMilli()))
        //                }
        //        streamOps.writeRecords(incrementalDedupStream, records)
        //        records =
        // BaseTypingDedupingTest.readRecords("sqlgenerator/alltypes_inputrecords.jsonl")
        //            .stream()
        //            .map {
        //                PartialAirbyteMessage()
        //                    .withSerialized(Jsons.serialize(it.get("_airbyte_data")))
        //                    .withRecord(
        //                        PartialAirbyteRecordMessage()
        //                            .withEmittedAt(
        //                                ZonedDateTime
        //                                    .parse(
        //                                        it.get("_airbyte_extracted_at").asText(),
        //                                        DateTimeFormatter.ISO_ZONED_DATE_TIME,
        //                                    )
        //                                    .toInstant()
        //                                    .toEpochMilli(),
        //                            ),
        //                    )
        //            }
        //        streamOps.writeRecords(incrementalDedupStream, records)
        //        println(sql)
        //        println(sqlGenerator.updateTable(cdcIncrementalDedupStream, "", Optional.empty(),
        // false).transactions.first().first())
        insertFinalTableRecords(
            true,
            cdcIncrementalDedupStream.id,
            "",
            BaseTypingDedupingTest.Companion.readRecords(
                "sqlgenerator/cdcupdate_inputrecords_final.jsonl",
            ),
        )
        println(dumpFinalTableRecords(cdcIncrementalDedupStream.id, ""))
    }
}
