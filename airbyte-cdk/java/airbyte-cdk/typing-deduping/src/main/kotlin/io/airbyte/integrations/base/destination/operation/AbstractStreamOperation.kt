/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.operation

import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.Optional
import java.util.stream.Stream

abstract class AbstractStreamOperation<DestinationState : MinimumDestinationState, Data>(
    private val storageOperation: StorageOperation<Data>,
    destinationInitialStatus: DestinationInitialStatus<DestinationState>,
    private val disableTypeDedupe: Boolean = false
) : StreamOperation<DestinationState> {
    private val log = KotlinLogging.logger {}

    // State maintained to make decision between async calls
    private val finalTmpTableSuffix: String
    private val initialRawTableStatus: InitialRawTableStatus =
        destinationInitialStatus.initialRawTableStatus

    /**
     * After running any sync setup code, we may update the destination state. This field holds that
     * updated destination state.
     */
    final override val updatedDestinationState: DestinationState

    init {
        val stream = destinationInitialStatus.streamConfig
        storageOperation.prepareStage(stream.id, stream.destinationSyncMode)
        if (!disableTypeDedupe) {
            // Prepare final tables based on sync mode.
            finalTmpTableSuffix = prepareFinalTable(destinationInitialStatus)
        } else {
            log.info { "Typing and deduping disabled, skipping final table initialization" }
            finalTmpTableSuffix = NO_SUFFIX
        }
        updatedDestinationState = destinationInitialStatus.destinationState.withSoftReset(false)
    }

    companion object {
        private const val NO_SUFFIX = ""
        private const val TMP_OVERWRITE_TABLE_SUFFIX = "_airbyte_tmp"
    }

    private fun prepareFinalTable(
        initialStatus: DestinationInitialStatus<DestinationState>
    ): String {
        val stream = initialStatus.streamConfig
        // No special handling if final table doesn't exist, just create and return
        if (!initialStatus.isFinalTablePresent) {
            log.info {
                "Final table does not exist for stream ${initialStatus.streamConfig.id.finalName}, creating."
            }
            storageOperation.createFinalTable(stream, NO_SUFFIX, false)
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
                    log.info { "Executing soft-reset on final table of stream $stream" }
                    storageOperation.softResetFinalTable(stream)
                }
                return NO_SUFFIX
            }
        }
    }

    private fun prepareFinalTableForOverwrite(
        initialStatus: DestinationInitialStatus<DestinationState>
    ): String {
        val stream = initialStatus.streamConfig
        if (!initialStatus.isFinalTableEmpty || initialStatus.isSchemaMismatch) {
            // overwrite an existing tmp table if needed.
            storageOperation.createFinalTable(stream, TMP_OVERWRITE_TABLE_SUFFIX, true)
            log.info {
                "Using temp final table for table ${stream.id.finalName}, this will be overwritten at end of sync"
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

    /** Write records will be destination type specific, Insert vs staging based on format */
    abstract override fun writeRecords(
        streamConfig: StreamConfig,
        stream: Stream<PartialAirbyteMessage>
    )

    override fun finalizeTable(streamConfig: StreamConfig, syncSummary: StreamSyncSummary) {
        // Delete staging directory, implementation will handle if it has to do it or not or a No-OP
        storageOperation.cleanupStage(streamConfig.id)
        if (disableTypeDedupe) {
            log.info {
                "Typing and deduping disabled, skipping final table finalization. " +
                    "Raw records can be found at ${streamConfig.id.rawNamespace}.${streamConfig.id.rawName}"
            }
            return
        }

        // Legacy logic that if recordsWritten or not tracked then it could be non-zero
        val isNotOverwriteSync = streamConfig.destinationSyncMode != DestinationSyncMode.OVERWRITE
        // Legacy logic that if recordsWritten or not tracked then it could be non-zero.
        // But for OVERWRITE syncs, we don't need to look at old records.
        val shouldRunTypingDeduping =
            syncSummary.recordsWritten.map { it > 0 }.orElse(true) ||
                (initialRawTableStatus.hasUnprocessedRecords && isNotOverwriteSync)
        if (!shouldRunTypingDeduping) {
            log.info {
                "Skipping typing and deduping for stream ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName} " +
                    "because it had no records during this sync and no unprocessed records from a previous sync."
            }
        } else {
            // In overwrite mode, we want to read all the raw records. Typically, this is equivalent
            // to filtering on timestamp, but might as well be explicit.
            val timestampFilter =
                if (isNotOverwriteSync) {
                    initialRawTableStatus.maxProcessedTimestamp
                } else {
                    Optional.empty()
                }
            storageOperation.typeAndDedupe(streamConfig, timestampFilter, finalTmpTableSuffix)
        }

        // For overwrite, it's wasteful to do T+D, so we don't do soft-reset in prepare. Instead, we
        // do
        // type-dedupe
        // on a suffixed table and do a swap here when we have to for schema mismatches
        if (
            streamConfig.destinationSyncMode == DestinationSyncMode.OVERWRITE &&
                finalTmpTableSuffix.isNotBlank()
        ) {
            storageOperation.overwriteFinalTable(streamConfig, finalTmpTableSuffix)
        }
    }
}
