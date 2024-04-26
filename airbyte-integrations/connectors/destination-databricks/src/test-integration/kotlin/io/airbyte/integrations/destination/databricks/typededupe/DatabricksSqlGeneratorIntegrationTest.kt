/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.typededupe

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
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
import java.time.ZonedDateTime
import java.time.format.DateTimeFormatter
import java.util.*
import java.util.stream.Stream
import kotlin.streams.asSequence
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
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
                connectorConfig.rawSchemaOverride
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
                                        DateTimeFormatter.ISO_ZONED_DATE_TIME
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
            |   _airbyte_raw_id,
            |   _airbyte_extracted_at,
            |   _airbyte_meta,
            |   `id1`, 
            |   `id2`, 
            |   `updated_at`, 
            |   `struct`, 
            |   `array`, 
            |   `string`, 
            |   `number`, 
            |   `integer`, 
            |   `boolean`, 
            |   `timestamp_with_timezone`, 
            |   `timestamp_without_timezone`, 
            |   `time_with_timezone`, 
            |   `time_without_timezone`, 
            |   `date`, 
            |   `unknown`${if(includeCdcDeletedAt) ", `_ab_cdc_deleted_at`" else ""}
            | )
            | SELECT
            |   `col1`,
            |   `col2`,
            |   `col3`,
            |   `col4`,
            |   `col5`,
            |   `col6`,
            |   `col7`,
            |   `col8`,
            |   `col9`,
            |   `col10`,
            |   `col11`,
            |   `col12`,
            |   `col13`,
            |   `col14`,
            |   `col15`,
            |   `col16`,
            |   `col17`,
            |   `col18`${if(includeCdcDeletedAt) ", `col19`" else ""}
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
        TODO("Not yet implemented")
    }

    override fun teardownNamespace(namespace: String?) {
        // jdbcDatabase.execute("DROP SCHEMA IF EXISTS
        // ${connectorConfig.database}.${namespace!!.lowercase(Locale.getDefault())} CASCADE")
        println("Skipping teardown for now, re-enable $namespace")
    }

    @Disabled override fun testCreateTableIncremental() {}

    @Disabled("No V1 Table migration for databricks") override fun testV1V2migration() {}

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
    }
}
