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
import io.airbyte.cdk.load.message.Meta as CDKConstants
import io.airbyte.cdk.load.util.write
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse_v2.config.UUIDGenerator
import io.airbyte.integrations.destination.clickhouse_v2.write.direct.ClickhouseDirectLoader.Constants.DELIMITER
import io.airbyte.protocol.models.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import kotlinx.coroutines.future.await

private val log = KotlinLogging.logger {}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "suspend and fb's non-null analysis don't play well"
)
class ClickhouseDirectLoader(
    private val descriptor: DestinationStream.Descriptor,
    private val clickhouseClient: Client,
    private val uuidGenerator: UUIDGenerator,
) : DirectLoader {
    private var buffer: ByteArrayOutputStream = ByteArrayOutputStream()
    private var recordCount = 0

    object Constants {
        const val BATCH_SIZE_RECORDS = 500000
        const val DELIMITER = "\n"
    }

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        // TODO: validate and coerce data if necessary
        val meta = Jsons.jsonNode(record.rawData.sourceMeta) as ObjectNode
        meta.put(CDKConstants.AIRBYTE_META_SYNC_ID_KEY, record.stream.syncId)
        // add internal columns
        val protocolRecord = record.asJsonRecord() as ObjectNode
        protocolRecord.set<ObjectNode>(CDKConstants.COLUMN_NAME_AB_META, meta)
        protocolRecord.put(CDKConstants.COLUMN_NAME_AB_EXTRACTED_AT, record.rawData.emittedAtMs)
        protocolRecord.put(CDKConstants.COLUMN_NAME_AB_GENERATION_ID, record.stream.generationId)
        protocolRecord.put(CDKConstants.COLUMN_NAME_AB_RAW_ID, uuidGenerator.v7().toString())

        // serialize and buffer
        buffer.write(protocolRecord.toString())
        buffer.write(DELIMITER)

        recordCount++

        // determine whether we're complete
        if (recordCount >= Constants.BATCH_SIZE_RECORDS) {
            // upload
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
