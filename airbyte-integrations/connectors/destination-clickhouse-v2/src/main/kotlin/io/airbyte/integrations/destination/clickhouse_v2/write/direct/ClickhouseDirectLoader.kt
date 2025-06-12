/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import com.clickhouse.data.ClickHouseFormat
import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.util.write
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.Constants.DELIMITER
import io.airbyte.protocol.models.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.util.UUID
import kotlinx.coroutines.future.await

private val log = KotlinLogging.logger {}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
class ClickhouseDirectLoader(
    private val descriptor: DestinationStream.Descriptor,
    private val clickhouseClient: Client,
) : DirectLoader {
    private var buffer: ByteArrayOutputStream = ByteArrayOutputStream()
    private var recordCount = 0

    object Constants {
        const val UUID = "bf7d3df8-8a91-4fd4-bd4c-89c293ba1d6b"
        const val BATCH_SIZE_RECORDS = 500000
        const val DELIMITER = "\n"

        const val FIELD_RAW_ID = "_airbyte_raw_id"
        const val FIELD_EXTRACTED_AT = "_airbyte_extracted_at"
        const val FIELD_META = "_airbyte_meta"
        const val FIELD_GEN_ID = "_airbyte_generation_id"
    }

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        val protocolRecord = record.asJsonRecord() as ObjectNode

        protocolRecord.put(Constants.FIELD_EXTRACTED_AT, record.rawData.emittedAtMs)
        protocolRecord.put(Constants.FIELD_GEN_ID, record.stream.generationId)
        protocolRecord.put(Constants.FIELD_RAW_ID, UUID.randomUUID().toString())

        val meta = Jsons.jsonNode(record.rawData.sourceMeta) as ObjectNode
        meta.put("sync_id", record.stream.syncId)
        protocolRecord.set<ObjectNode>(Constants.FIELD_META, meta)

        buffer.write(protocolRecord.toString())
        buffer.write(DELIMITER)

        recordCount++

        if (recordCount >= Constants.BATCH_SIZE_RECORDS) {
            flush()
            return DirectLoader.Complete
        }

        return DirectLoader.Incomplete
    }

    private suspend fun flush() {
        val jsonBytes = ByteArrayInputStream(buffer.toByteArray())
        buffer = ByteArrayOutputStream()

        val insertResult =
            clickhouseClient
                .insert(
                    "`${descriptor.namespace ?: "default"}`.`${descriptor.name}`",
                    jsonBytes,
                    ClickHouseFormat.JSONEachRow,
                )
                .await()

        log.info { "Finished insert of ${insertResult.writtenRows} rows into ${descriptor.name}" }
        recordCount = 0
    }

    // only calls this on force complete
    override suspend fun finish() {
        flush()
    }

    // this is always called on complete
    override fun close() {}
}
