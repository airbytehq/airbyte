/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.operation

import com.fasterxml.jackson.databind.JsonNode
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.DatasetId
import com.google.cloud.bigquery.DatasetInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableResult
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation.Companion.TMP_TABLE_SUFFIX
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.bigquery.BigQueryConsts
import io.airbyte.integrations.destination.bigquery.BigQueryDestination
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQueryDestinationHandler
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGenerator
import io.airbyte.integrations.destination.bigquery.typing_deduping.BigQuerySqlGeneratorIntegrationTest
import io.airbyte.protocol.models.v0.AirbyteMessage.Type
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.DestinationSyncMode
import java.nio.file.Files
import java.nio.file.Path
import java.util.Optional
import java.util.stream.Stream
import kotlin.test.assertEquals
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

/**
 * Extremely barebones integration test for the direct inserts storage op. We should eventually:
 * * Make something similar for the GCS storage op
 * * Genericize this and put it in the CDK
 * * Add assertions for all the columns, not just airbyte_data
 * * Actually test all the methods on StorageOperation
 */
@Execution(ExecutionMode.CONCURRENT)
class BigQueryDirectLoadingStorageOperationTest {
    private val randomString = Strings.addRandomSuffix("", "", 10)
    private val streamId =
        StreamId(
            finalNamespace = "final_namespace_$randomString",
            finalName = "final_name_$randomString",
            rawNamespace = "raw_namespace_$randomString",
            rawName = "raw_name_$randomString",
            originalNamespace = "original_namespace_$randomString",
            originalName = "original_name_$randomString",
        )
    private val streamConfig =
        StreamConfig(
            streamId,
            DestinationSyncMode.APPEND,
            emptyList(),
            Optional.empty(),
            LinkedHashMap(),
            GENERATION_ID,
            0,
            SYNC_ID,
        )

    @BeforeEach
    fun setup() {
        bq.create(DatasetInfo.of(streamId.rawNamespace))
    }

    @AfterEach
    fun teardown() {
        bq.delete(
            DatasetId.of(streamId.rawNamespace),
            BigQuery.DatasetDeleteOption.deleteContents()
        )
    }

    @Test
    fun testTransferStage() {
        storageOperation.prepareStage(streamId, "")
        storageOperation.prepareStage(streamId, TMP_TABLE_SUFFIX)
        // Table is currently empty, so expect null generation.
        assertEquals(null, storageOperation.getStageGeneration(streamId, TMP_TABLE_SUFFIX))

        // Write one record to the real raw table
        storageOperation.writeToStage(
            streamConfig,
            "",
            Stream.of(record(1)),
        )
        assertEquals(
            listOf("""{"record_number": 1}"""),
            // We write the raw data as a string column, not a JSON column, so use asText().
            dumpRawRecords("").map { it["_airbyte_data"].asText() },
        )

        // And write one record to the temp final table
        storageOperation.writeToStage(
            streamConfig,
            TMP_TABLE_SUFFIX,
            Stream.of(record(2)),
        )
        assertEquals(
            listOf("""{"record_number": 2}"""),
            dumpRawRecords(TMP_TABLE_SUFFIX).map { it["_airbyte_data"].asText() },
        )
        assertEquals(GENERATION_ID, storageOperation.getStageGeneration(streamId, TMP_TABLE_SUFFIX))

        // If we transfer the records, we should end up with 2 records in the real raw table.
        storageOperation.transferFromTempStage(streamId, TMP_TABLE_SUFFIX)
        assertEquals(
            listOf(
                """{"record_number": 1}""",
                """{"record_number": 2}""",
            ),
            dumpRawRecords("")
                .sortedBy {
                    Jsons.deserialize(it["_airbyte_data"].asText())["record_number"].asLong()
                }
                .map { it["_airbyte_data"].asText() },
        )

        // After transferring the records to the real table, the temp table should no longer exist.
        assertEquals(404, assertThrows<BigQueryException> { dumpRawRecords(TMP_TABLE_SUFFIX) }.code)
    }

    @Test
    fun testOverwriteStage() {
        // If we then create another temp raw table and _overwrite_ the real raw table,
        // we should end up with a single raw record.
        storageOperation.prepareStage(streamId, "")
        storageOperation.prepareStage(streamId, TMP_TABLE_SUFFIX)
        storageOperation.writeToStage(
            streamConfig,
            "",
            Stream.of(record(3)),
        )
        storageOperation.writeToStage(
            streamConfig,
            TMP_TABLE_SUFFIX,
            Stream.of(record(4)),
        )

        storageOperation.overwriteStage(streamId, TMP_TABLE_SUFFIX)

        assertEquals(
            listOf("""{"record_number": 4}"""),
            dumpRawRecords("").map { it["_airbyte_data"].asText() },
        )
        assertEquals(404, assertThrows<BigQueryException> { dumpRawRecords(TMP_TABLE_SUFFIX) }.code)
    }

    private fun dumpRawRecords(suffix: String): List<JsonNode> {
        val result: TableResult =
            bq.query(
                QueryJobConfiguration.of(
                    "SELECT * FROM " + streamId.rawTableId(BigQuerySqlGenerator.QUOTE, suffix)
                ),
            )
        return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result)
    }

    private fun record(recordNumber: Int): PartialAirbyteMessage {
        val serializedData = """{"record_number": $recordNumber}"""
        return PartialAirbyteMessage()
            .withType(Type.RECORD)
            .withSerialized(serializedData)
            .withRecord(
                PartialAirbyteRecordMessage()
                    .withNamespace(streamId.originalNamespace)
                    .withStream(streamId.originalName)
                    .withEmittedAt(10_000)
                    .withMeta(
                        AirbyteRecordMessageMeta()
                            .withChanges(emptyList())
                            .withAdditionalProperty(
                                JavaBaseConstants.AIRBYTE_META_SYNC_ID_KEY,
                                SYNC_ID,
                            ),
                    )
                    .withData(Jsons.deserialize(serializedData)),
            )
    }

    companion object {
        private val config =
            Jsons.deserialize(Files.readString(Path.of("secrets/credentials-gcs-staging.json")))
        private val bq = BigQueryDestination.getBigQuery(config)
        private val projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText()
        private val datasetLocation = config.get(BigQueryConsts.CONFIG_DATASET_LOCATION).asText()
        private val storageOperation =
            BigQueryDirectLoadingStorageOperation(
                bq,
                15,
                BigQueryRecordFormatter(),
                BigQuerySqlGenerator(projectId, datasetLocation),
                BigQueryDestinationHandler(bq, datasetLocation),
                datasetLocation,
            )

        private const val SYNC_ID = 12L
        private const val GENERATION_ID = 42L
    }
}
