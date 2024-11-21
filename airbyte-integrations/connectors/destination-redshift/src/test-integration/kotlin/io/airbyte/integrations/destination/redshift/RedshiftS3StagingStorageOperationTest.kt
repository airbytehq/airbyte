/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift

import com.amazon.redshift.util.RedshiftException
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.staging.StagingSerializedBufferFactory
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation.Companion.TMP_TABLE_SUFFIX
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.redshift.operation.RedshiftStagingStorageOperation
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftDestinationHandler
import io.airbyte.integrations.destination.redshift.typing_deduping.RedshiftSqlGenerator
import io.airbyte.integrations.destination.redshift.util.RedshiftUtil
import io.airbyte.protocol.models.v0.AirbyteMessage.Type
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import java.nio.file.Files
import java.nio.file.Path
import java.util.Optional
import kotlin.test.assertEquals
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@Execution(ExecutionMode.CONCURRENT)
class RedshiftS3StagingStorageOperationTest {
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
            ImportType.APPEND,
            emptyList(),
            Optional.empty(),
            LinkedHashMap(),
            GENERATION_ID,
            0,
            SYNC_ID,
        )
    private val storageOperation = getStorageOperation(dropCascade = false)

    @BeforeEach
    fun setup() {
        jdbcDatabase.execute("CREATE SCHEMA ${streamId.rawNamespace}")
    }

    @AfterEach
    fun teardown() {
        jdbcDatabase.execute("DROP SCHEMA ${streamId.rawNamespace} CASCADE")
    }

    @Test
    fun testTransferStage() {
        storageOperation.prepareStage(streamId, "")
        storageOperation.prepareStage(streamId, TMP_TABLE_SUFFIX)
        // Table is currently empty, so expect null generation.
        assertEquals(null, storageOperation.getStageGeneration(streamId, TMP_TABLE_SUFFIX))

        // Write one record to the real raw table
        writeRecords(suffix = "", record(1))
        assertEquals(
            listOf("""{"record_number":1}"""),
            // We write the raw data as a string column, not a JSON column, so use asText().
            dumpRawRecords("").map { it["_airbyte_data"].asText() },
        )

        // And write one record to the temp final table
        writeRecords(suffix = TMP_TABLE_SUFFIX, record(2))
        assertEquals(
            listOf("""{"record_number":2}"""),
            dumpRawRecords(TMP_TABLE_SUFFIX).map { it["_airbyte_data"].asText() },
        )
        assertEquals(GENERATION_ID, storageOperation.getStageGeneration(streamId, TMP_TABLE_SUFFIX))

        // If we transfer the records, we should end up with 2 records in the real raw table.
        storageOperation.transferFromTempStage(streamId, TMP_TABLE_SUFFIX)
        assertEquals(
            listOf(
                """{"record_number":1}""",
                """{"record_number":2}""",
            ),
            dumpRawRecords("")
                .sortedBy {
                    Jsons.deserialize(it["_airbyte_data"].asText())["record_number"].asLong()
                }
                .map { it["_airbyte_data"].asText() },
        )

        // After transferring the records to the real table, the temp table should no longer exist.
        assertEquals(
            """ERROR: relation "${streamId.rawNamespace}.${streamId.rawName}$TMP_TABLE_SUFFIX" does not exist""",
            assertThrows<RedshiftException> { dumpRawRecords(TMP_TABLE_SUFFIX) }.message,
        )
    }

    @Test
    fun testOverwriteStage() {
        // If we then create another temp raw table and _overwrite_ the real raw table,
        // we should end up with a single raw record.
        storageOperation.prepareStage(streamId, "")
        storageOperation.prepareStage(streamId, TMP_TABLE_SUFFIX)
        writeRecords(suffix = "", record(3))
        writeRecords(suffix = TMP_TABLE_SUFFIX, record(4))

        storageOperation.overwriteStage(streamId, TMP_TABLE_SUFFIX)

        assertEquals(
            listOf("""{"record_number":4}"""),
            dumpRawRecords("").map { it["_airbyte_data"].asText() },
        )
        assertEquals(
            """ERROR: relation "${streamId.rawNamespace}.${streamId.rawName}$TMP_TABLE_SUFFIX" does not exist""",
            assertThrows<RedshiftException> { dumpRawRecords(TMP_TABLE_SUFFIX) }.message,
        )
    }

    @Test
    fun testOverwriteStageDropCascade() {
        // create a new storage op with dropCascade = true
        val storageOperationWithCascade = getStorageOperation(dropCascade = true)

        // Create the real+temp tables, and write a record to the temp table
        storageOperation.prepareStage(streamId, "")
        storageOperation.prepareStage(streamId, TMP_TABLE_SUFFIX)
        writeRecords(suffix = TMP_TABLE_SUFFIX, record(5))
        // Create a view on top of the real table
        jdbcDatabase.execute(
            """CREATE VIEW ${streamId.rawNamespace}.test_view AS SELECT * FROM ${streamId.rawNamespace}.${streamId.rawName}"""
        )

        // Check that we're set up correctly: Trying to drop the real table without cascade should
        // fail
        val configError =
            assertThrows<ConfigErrorException> {
                storageOperation.overwriteStage(
                    streamId,
                    TMP_TABLE_SUFFIX,
                )
            }
        assertEquals(
            "Failed to drop table without the CASCADE option. Consider changing the drop_cascade configuration parameter",
            configError.message,
        )
        // Then check that dropping with CASCADE succeeds
        assertDoesNotThrow {
            storageOperationWithCascade.overwriteStage(streamId, TMP_TABLE_SUFFIX)
        }
        // And verify that we still correctly moved the record to the real table
        assertEquals(
            listOf("""{"record_number":5}"""),
            dumpRawRecords("").map { it["_airbyte_data"].asText() },
        )
        // And verify that the temp table is gone
        assertEquals(
            """ERROR: relation "${streamId.rawNamespace}.${streamId.rawName}$TMP_TABLE_SUFFIX" does not exist""",
            assertThrows<RedshiftException> { dumpRawRecords(TMP_TABLE_SUFFIX) }.message,
        )
    }

    private fun dumpRawRecords(suffix: String): List<JsonNode> {
        return jdbcDatabase.queryJsons(
            "SELECT * FROM ${streamId.rawNamespace}.${streamId.rawName}$suffix"
        )
    }

    private fun record(recordNumber: Int): PartialAirbyteMessage {
        val serializedData = """{"record_number":$recordNumber}"""
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

    /**
     * Utility method to create the SerializableBuffer, write records into it, and then push that
     * buffer into [storageOperation].
     */
    private fun writeRecords(suffix: String, vararg records: PartialAirbyteMessage) {
        val writeBuffer =
            StagingSerializedBufferFactory.initializeBuffer(
                FileUploadFormat.CSV,
                JavaBaseConstants.DestinationColumns.V2_WITH_GENERATION
            )

        writeBuffer.use {
            records.forEach { record: PartialAirbyteMessage ->
                it.accept(
                    record.serialized!!,
                    Jsons.serialize(record.record!!.meta),
                    GENERATION_ID,
                    record.record!!.emittedAt
                )
            }
            it.flush()
            storageOperation.writeToStage(streamConfig, suffix, writeBuffer)
        }
    }

    private fun getStorageOperation(dropCascade: Boolean): RedshiftStagingStorageOperation {
        return RedshiftStagingStorageOperation(
            s3Config,
            keepStagingFiles = false,
            s3StorageOperations,
            RedshiftSqlGenerator(RedshiftSQLNameTransformer(), config),
            RedshiftDestinationHandler(databaseName, jdbcDatabase, streamId.rawNamespace),
            dropCascade,
        )
    }

    companion object {
        private val config =
            Jsons.deserialize(Files.readString(Path.of("secrets/1s1t_config_staging.json")))
        private val s3Config =
            S3DestinationConfig.getS3DestinationConfig(RedshiftUtil.findS3Options(config))
        private val s3StorageOperations =
            S3StorageOperations(RedshiftSQLNameTransformer(), s3Config.getS3Client(), s3Config)
        private val jdbcDatabase =
            RedshiftDestination().run {
                val dataSource = getDataSource(config)
                getDatabase(dataSource)
            }
        private val databaseName = config[JdbcUtils.DATABASE_KEY].asText()

        private const val SYNC_ID = 12L
        private const val GENERATION_ID = 42L
    }
}
