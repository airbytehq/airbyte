/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.sync

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.integrations.destination.databricks.staging.SerializableBufferFactory
import io.airbyte.integrations.destination.sync.StorageOperations
import io.airbyte.integrations.destination.sync.StreamOperations
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import java.util.stream.Stream
import org.apache.commons.io.FileUtils

class DatabricksStreamOperations(
    private val storageOperations: StorageOperations,
    private val fileUploadFormat: FileUploadFormat,
    destinationInitialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>,
) : StreamOperations<MinimumDestinationState.Impl> {
    private val log = KotlinLogging.logger {}

    // State maintained to make decision between async calls
    private val finalTmpTableSuffix: String
    private val initialRawTableStatus: InitialRawTableStatus =
        destinationInitialStatus.initialRawTableStatus
    init {
        val stream = destinationInitialStatus.streamConfig
        storageOperations.prepareStage(stream.id, stream.destinationSyncMode)
        storageOperations.createFinalSchema(stream.id)
        // Prepare final tables based on sync mode.
        finalTmpTableSuffix = prepareFinalTable(destinationInitialStatus)
    }

    companion object {
        private const val NO_SUFFIX = ""
        private const val TMP_OVERWRITE_TABLE_SUFFIX = "_airbyte_tmp"
    }

    private fun prepareFinalTable(
        initialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>
    ): String {
        val stream = initialStatus.streamConfig
        // No special handling if final table doesn't exist, just create and return
        if (!initialStatus.isFinalTablePresent) {
            log.info {
                "Final table does not exist for stream ${initialStatus.streamConfig.id.finalName}, creating."
            }
            storageOperations.createFinalTable(stream, NO_SUFFIX, false)
            return NO_SUFFIX
        }

        log.info { "Final Table exists for stream ${stream.id.finalName}" }
        // The table already exists. Decide whether we're writing to it directly, or
        // using a tmp table.
        when (stream.destinationSyncMode) {
            DestinationSyncMode.OVERWRITE -> return prepareFinalTableForOverwrite(initialStatus)
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP -> {
                if (
                    initialStatus.isSchemaMismatch ||
                        initialStatus.destinationState.needsSoftReset()
                ) {
                    // We're loading data directly into the existing table.
                    // Make sure it has the right schema.
                    // Also, if a raw table migration wants us to do a soft reset, do that
                    // here.
                    storageOperations.softResetFinalTable(stream)
                }
                return NO_SUFFIX
            }
        }
    }

    private fun prepareFinalTableForOverwrite(
        initialStatus: DestinationInitialStatus<MinimumDestinationState.Impl>
    ): String {
        val stream = initialStatus.streamConfig
        if (!initialStatus.isFinalTableEmpty || initialStatus.isSchemaMismatch) {
            // overwrite an existing tmp table if needed.
            storageOperations.createFinalTable(stream, TMP_OVERWRITE_TABLE_SUFFIX, true)
            log.info {
                "Using temp final table for stream ${stream.id.finalName}, will overwrite existing table at end of sync"
            }
            // We want to overwrite an existing table. Write into a tmp table.
            // We'll overwrite the table at the
            // end of the sync.
            return TMP_OVERWRITE_TABLE_SUFFIX
        }

        log.info {
            "Final Table for stream ${stream.id.finalName} is empty and matches the expected v2 format, writing to table directly"
        }
        return NO_SUFFIX
    }

    override fun writeRecords(streamConfig: StreamConfig, stream: Stream<PartialAirbyteMessage>) {
        val writeBuffer = SerializableBufferFactory.createBuffer(fileUploadFormat)
        writeBuffer.use {
            stream.forEach { record: PartialAirbyteMessage ->
                it.accept(
                    record.serialized!!,
                    Jsons.serialize(record.record!!.meta),
                    record.record!!.emittedAt
                )
            }
            it.flush()
            log.info {
                "Buffer flush complete for stream ${streamConfig.id.originalName} (${FileUtils.byteCountToDisplaySize(it.byteCount)}) to staging"
            }
            storageOperations.writeToStage(streamConfig.id, writeBuffer)
        }
    }

    override fun finalizeTable(streamConfig: StreamConfig, syncSummary: StreamSyncSummary) {
        // Legacy logic that if recordsWritten or not tracked then it could be non-zero
        val shouldRunFinalizer =
            syncSummary.recordsWritten.map { it > 0 }.orElse(true) ||
                initialRawTableStatus.hasUnprocessedRecords
        if (!shouldRunFinalizer) {
            log.info {
                "Skipping typing and deduping for stream ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName} " +
                    "because it had no records during this sync and no unprocessed records from a previous sync."
            }
            return
        }

        storageOperations.typeAndDedupe(
            streamConfig,
            initialRawTableStatus.maxProcessedTimestamp,
            finalTmpTableSuffix
        )

        // Delete staging directory, implementation will handle if it has to do it or not or a No-OP
        storageOperations.cleanupStage(streamConfig.id)

        // For overwrite, its wasteful to do T+D so we don't do soft-reset in prepare. Instead we do
        // type-dedupe
        // on a suffixed table and do a swap here when we have to for schema mismatches
        if (streamConfig.destinationSyncMode == DestinationSyncMode.OVERWRITE) {
            storageOperations.overwriteFinalTable(streamConfig, finalTmpTableSuffix)
        }
    }
}
