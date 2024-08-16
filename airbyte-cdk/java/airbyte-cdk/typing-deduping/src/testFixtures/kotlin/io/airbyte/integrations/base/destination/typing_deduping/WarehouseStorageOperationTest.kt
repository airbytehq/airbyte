package io.airbyte.integrations.base.destination.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteRecordMessage
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.string.Strings
import io.airbyte.integrations.base.destination.operation.AbstractStreamOperation.Companion.TMP_TABLE_SUFFIX
import io.airbyte.integrations.base.destination.operation.StorageOperation
import io.airbyte.protocol.models.v0.AirbyteMessage.Type
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import java.util.Optional
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

abstract class WarehouseStorageOperationTest<Data>(
    private val storageOperation: StorageOperation<Data>
) {
    private val randomString = Strings.addRandomSuffix("", "", 10)
    protected val streamId =
        StreamId(
            finalNamespace = "final_namespace_$randomString",
            finalName = "final_name_$randomString",
            rawNamespace = "raw_namespace_$randomString",
            rawName = "raw_name_$randomString",
            originalNamespace = "original_namespace_$randomString",
            originalName = "original_name_$randomString",
        )
    protected val streamConfig =
        StreamConfig(
            streamId,
            ImportType.APPEND,
            emptyList(),
            Optional.empty(),
            LinkedHashMap(),
            GENERATION_ID,
            minimumGenerationId = 0,
            SYNC_ID,
        )

    abstract fun toData(vararg records: PartialAirbyteMessage): Data
    abstract fun dumpRawRecords(suffix: String): List<JsonNode>
    open fun assertThrowsTableNotFound(f: () -> Unit) {
        assertThrows<Throwable>(f)
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
            toData(record(1)),
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
            toData(record(2)),
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
        assertThrowsTableNotFound { dumpRawRecords(TMP_TABLE_SUFFIX) }
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
        private const val SYNC_ID = 12L
        private const val GENERATION_ID = 42L
    }
}
