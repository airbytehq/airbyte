/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.operation

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.staging.StagingSerializedBufferFactory
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.snowflake.OssCloudEnvVarConsts
import io.airbyte.integrations.destination.snowflake.SnowflakeDatabaseUtils
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeDestinationHandler
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import java.nio.file.Files
import java.nio.file.Paths
import java.util.*
import net.snowflake.client.jdbc.SnowflakeSQLException
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock

class SnowflakeStorageOperationIntegrationTest {

    private var streamId: StreamId = mock()
    private var streamConfig: StreamConfig = mock()
    @BeforeEach
    fun setup() {
        val randomString = Strings.addRandomSuffix("", "", 10)
        streamId =
            StreamId(
                finalNamespace = "final_namespace_$randomString",
                finalName = "final_name_$randomString",
                rawNamespace = "raw_namespace_$randomString",
                rawName = "raw_name_$randomString",
                originalNamespace = "original_namespace_$randomString",
                originalName = "original_name_$randomString",
            )
        streamConfig =
            StreamConfig(
                streamId,
                ImportType.APPEND,
                emptyList(),
                Optional.empty(),
                LinkedHashMap(),
                GENERATION_ID,
                0,
                SYNC_ID,
            )
        database.execute(
            """
            CREATE SCHEMA "${streamId.rawNamespace}"
        """.trimIndent()
        )
    }

    @AfterEach
    fun teardown() {
        database.execute("DROP SCHEMA IF EXISTS \"${streamId.rawNamespace}\" CASCADE")
    }

    private fun record(recordNumber: Int): PartialAirbyteMessage {
        val serializedData = """{"record_number": $recordNumber}"""
        return PartialAirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
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

    private fun buffer(
        partialAirbyteMessage: PartialAirbyteMessage,
        callback: (buffer: SerializableBuffer) -> Unit
    ) {
        val csvBuffer =
            StagingSerializedBufferFactory.initializeBuffer(
                FileUploadFormat.CSV,
                JavaBaseConstants.DestinationColumns.V2_WITH_GENERATION
            )
        csvBuffer.use {
            it.accept(
                partialAirbyteMessage.serialized!!,
                Jsons.serialize(partialAirbyteMessage.record!!.meta),
                streamConfig.generationId,
                partialAirbyteMessage.record!!.emittedAt
            )
            it.flush()
            callback(csvBuffer)
        }
    }

    private fun dumpRawRecords(suffix: String): List<JsonNode> {
        val query =
            """
            SELECT * FROM ${streamId.rawTableId("\"", suffix)}
        """.trimIndent()
        return database.queryJsons(query)
    }

    @Test
    fun testTransferStage() {
        storageOperation.prepareStage(streamId, "")
        storageOperation.prepareStage(streamId, AbstractStreamOperation.TMP_TABLE_SUFFIX)
        // Table is currently empty, so expect null generation.
        assertNull(
            storageOperation.getStageGeneration(streamId, AbstractStreamOperation.TMP_TABLE_SUFFIX)
        )
        // Write one record to the real raw table
        buffer(record(1)) {
            storageOperation.writeToStage(
                streamConfig,
                "",
                it,
            )
        }
        println(dumpRawRecords(""))
        assertEquals(
            listOf(Jsons.deserialize("""{"record_number":1}""")),
            dumpRawRecords("").map { it["_airbyte_data"] },
        )
        // And write one record to the temp final table
        buffer(record(2)) {
            storageOperation.writeToStage(
                streamConfig,
                AbstractStreamOperation.TMP_TABLE_SUFFIX,
                it,
            )
        }
        assertEquals(
            listOf(Jsons.deserialize("""{"record_number": 2}""")),
            dumpRawRecords(AbstractStreamOperation.TMP_TABLE_SUFFIX).map { it["_airbyte_data"] },
        )
        assertEquals(
            GENERATION_ID,
            storageOperation.getStageGeneration(streamId, AbstractStreamOperation.TMP_TABLE_SUFFIX)
        )
        // If we transfer the records, we should end up with 2 records in the real raw table.
        storageOperation.transferFromTempStage(streamId, AbstractStreamOperation.TMP_TABLE_SUFFIX)
        assertEquals(
            listOf(
                Jsons.deserialize("""{"record_number": 1}"""),
                Jsons.deserialize("""{"record_number": 2}"""),
            ),
            dumpRawRecords("")
                .map { it["_airbyte_data"] }
                .sortedBy { it.get("record_number").asLong() },
        )
        // After transferring the records to the real table, the temp table should no longer exist.
        assertThrows(SnowflakeSQLException::class.java) {
            dumpRawRecords(AbstractStreamOperation.TMP_TABLE_SUFFIX)
        }
    }

    @Test
    fun testOverwriteStage() {
        // If we then create another temp raw table and _overwrite_ the real raw table,
        // we should end up with a single raw record.
        storageOperation.prepareStage(streamId, "")
        storageOperation.prepareStage(streamId, AbstractStreamOperation.TMP_TABLE_SUFFIX)
        buffer(record(3)) {
            storageOperation.writeToStage(
                streamConfig,
                "",
                it,
            )
        }
        buffer(record(4)) {
            storageOperation.writeToStage(
                streamConfig,
                AbstractStreamOperation.TMP_TABLE_SUFFIX,
                it,
            )
        }
        storageOperation.overwriteStage(streamId, AbstractStreamOperation.TMP_TABLE_SUFFIX)
        assertEquals(
            listOf(Jsons.deserialize("""{"record_number": 4}""")),
            dumpRawRecords("").map { it["_airbyte_data"] },
        )
        assertThrows(SnowflakeSQLException::class.java) {
            dumpRawRecords(AbstractStreamOperation.TMP_TABLE_SUFFIX)
        }
    }

    companion object {
        private val config =
            Jsons.deserialize(
                Files.readString(Paths.get("secrets/1s1t_internal_staging_config.json"))
            )
        private val datasource =
            SnowflakeDatabaseUtils.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS)
        private val database: JdbcDatabase = SnowflakeDatabaseUtils.getDatabase(datasource)
        private val storageOperation: SnowflakeStorageOperation =
            SnowflakeStorageOperation(
                SnowflakeSqlGenerator(0),
                SnowflakeDestinationHandler(
                    config[JdbcUtils.DATABASE_KEY].asText(),
                    database,
                    config[JdbcUtils.SCHEMA_KEY].asText(),
                ),
                0,
                SnowflakeStagingClient(database),
            )
        private const val SYNC_ID = 12L
        private const val GENERATION_ID = 42L
    }
}
