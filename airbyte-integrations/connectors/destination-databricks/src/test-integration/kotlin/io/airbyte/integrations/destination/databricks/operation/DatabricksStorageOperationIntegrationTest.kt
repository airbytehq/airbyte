/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.operation

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation.Companion.TMP_TABLE_SUFFIX
import io.airbyte.integrations.base.destination.typing_deduping.ImportType
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.StreamId
import io.airbyte.integrations.destination.databricks.DatabricksConnectorClientsFactory
import io.airbyte.integrations.destination.databricks.DatabricksIntegrationTestUtils
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksDestinationHandler
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksNamingTransformer
import io.airbyte.integrations.destination.databricks.jdbc.DatabricksSqlGenerator
import io.airbyte.protocol.models.v0.AirbyteMessage.Type
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import java.sql.SQLException
import java.util.Arrays
import java.util.Optional
import kotlin.test.assertContains
import kotlin.test.assertEquals
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

@Execution(ExecutionMode.CONCURRENT)
class DatabricksStorageOperationIntegrationTest {
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
    private val storageOperation =
        DatabricksStorageOperation(
            sqlGenerator,
            DatabricksDestinationHandler(sqlGenerator, config.database, jdbcDatabase),
            DatabricksConnectorClientsFactory.createWorkspaceClient(
                config.hostname,
                config.authentication
            ),
            config.database,
            purgeStagedFiles = true,
        )

    @BeforeEach
    fun setup() {
        jdbcDatabase.execute("CREATE SCHEMA ${config.database}.${streamId.rawNamespace}")
    }

    @AfterEach
    fun teardown() {
        jdbcDatabase.execute("DROP SCHEMA ${config.database}.${streamId.rawNamespace} CASCADE")
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
        assertContains(
            assertThrows<SQLException> { dumpRawRecords(TMP_TABLE_SUFFIX) }.message!!,
            "TABLE_OR_VIEW_NOT_FOUND",
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
        assertContains(
            assertThrows<SQLException> { dumpRawRecords(TMP_TABLE_SUFFIX) }.message!!,
            "TABLE_OR_VIEW_NOT_FOUND",
        )
    }

    /**
     * Verify that, starting from an empty destination, we can create+replace a nonexistent temp raw
     * table.
     */
    @Test
    fun testReplaceStage() {
        assertDoesNotThrow {
            storageOperation.prepareStage(
                streamId,
                TMP_TABLE_SUFFIX,
                replace = true,
            )
        }
    }

    private fun dumpRawRecords(suffix: String): List<JsonNode> {
        return jdbcDatabase.queryJsons(
            "SELECT * FROM ${config.database}.${streamId.rawNamespace}.${streamId.rawName}$suffix"
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

    private fun writeRecords(suffix: String, vararg records: PartialAirbyteMessage) {
        DatabricksStreamOperation.Companion.writeRecords(
            FileUploadFormat.CSV,
            streamConfig,
            suffix,
            Arrays.stream(records),
            storageOperation
        )
    }

    companion object {
        private val config = DatabricksIntegrationTestUtils.oauthConfig
        private val jdbcDatabase =
            DefaultJdbcDatabase(DatabricksConnectorClientsFactory.createDataSource(config))
        private val sqlGenerator =
            DatabricksSqlGenerator(DatabricksNamingTransformer(), config.database, false)

        private const val SYNC_ID = 12L
        private const val GENERATION_ID = 42L
    }
}
