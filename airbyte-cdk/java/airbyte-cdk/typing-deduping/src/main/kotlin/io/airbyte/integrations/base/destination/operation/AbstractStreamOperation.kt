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
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.Optional
import java.util.stream.Stream

abstract class AbstractStreamOperation<DestinationState : MinimumDestinationState, Data>(
    private val storageOperation: StorageOperation<Data>,
    destinationInitialStatus: DestinationInitialStatus<DestinationState>,
    private val disableTypeDedupe: Boolean = false
) : StreamOperation<DestinationState> {
    private val log = KotlinLogging.logger {}

    // State maintained to make decision between async calls
    private val isTruncateSync: Boolean
    private val rawTableSuffix: String
    private val finalTmpTableSuffix: String
    // null for truncate syncs, where we don't care at all about the initial status.
    private val initialRawTableStatus: InitialRawTableStatus?

    /**
     * After running any sync setup code, we may update the destination state. This field holds that
     * updated destination state.
     */
    final override val updatedDestinationState: DestinationState

    init {
        val stream = destinationInitialStatus.streamConfig

        isTruncateSync =
            when (stream.minimumGenerationId) {
                0L -> false
                stream.generationId -> true
                else -> {
                    // This is technically already handled in CatalogParser.
                    throw IllegalArgumentException("Hybrid refreshes are not yet supported.")
                }
            }

        if (isTruncateSync) {
            prepareStageForTruncate(destinationInitialStatus, stream)
            rawTableSuffix = TMP_TABLE_SUFFIX
            initialRawTableStatus = null
        } else {
            rawTableSuffix = NO_SUFFIX
            initialRawTableStatus = prepareStageForNormalSync(stream, destinationInitialStatus)
        }

        if (!disableTypeDedupe) {
            // Prepare final tables based on sync mode.
            finalTmpTableSuffix = prepareFinalTable(destinationInitialStatus)
        } else {
            log.info { "Typing and deduping disabled, skipping final table initialization" }
            finalTmpTableSuffix = NO_SUFFIX
        }
        updatedDestinationState = destinationInitialStatus.destinationState.withSoftReset(false)
    }

    private fun prepareStageForNormalSync(
        stream: StreamConfig,
        destinationInitialStatus: DestinationInitialStatus<DestinationState>
    ): InitialRawTableStatus {
        log.info {
            "${stream.id.originalNamespace}.${stream.id.originalName}: non-truncate sync. Creating raw table if not exists."
        }
        storageOperation.prepareStage(stream.id, NO_SUFFIX)
        if (destinationInitialStatus.initialTempRawTableStatus.rawTableExists) {
            log.info {
                "${stream.id.originalNamespace}.${stream.id.originalName}: non-truncate sync, but temp raw table exists. Transferring it to real raw table."
            }
            // There was a previous truncate refresh attempt, which failed, and left some
            // records behind.
            // Retrieve those records and put them in the real stage.
            // This is necessary to avoid certain data loss scenarios.
            // (specifically: a user initiates a truncate sync, which fails, but emits some records.
            // It also emits a state message for "resumable" full refresh.
            // The user then initiates an incremental sync, which runs using that state.
            // In this case, we MUST retain the records from the truncate attempt.)
            storageOperation.transferFromTempStage(stream.id, TMP_TABLE_SUFFIX)

            // We need to combine the raw table statuses from the real and temp raw tables.
            val hasUnprocessedRecords =
                destinationInitialStatus.initialTempRawTableStatus.hasUnprocessedRecords ||
                    destinationInitialStatus.initialRawTableStatus.hasUnprocessedRecords
            // Pick the earlier min timestamp.
            val maxProcessedTimestamp: Optional<Instant> =
                destinationInitialStatus.initialRawTableStatus.maxProcessedTimestamp
                    .flatMap { realRawTableTimestamp ->
                        destinationInitialStatus.initialTempRawTableStatus.maxProcessedTimestamp
                            .flatMap { tempRawTableTimestamp ->
                                if (realRawTableTimestamp.isBefore(tempRawTableTimestamp)) {
                                    Optional.of(realRawTableTimestamp)
                                } else {
                                    Optional.of(tempRawTableTimestamp)
                                }
                            }
                            .or { Optional.of(realRawTableTimestamp) }
                    }
                    .or { destinationInitialStatus.initialTempRawTableStatus.maxProcessedTimestamp }
            log.info {
                "${stream.id.originalNamespace}.${stream.id.originalName}: After record transfer, initial raw table status is $initialRawTableStatus."
            }
            return InitialRawTableStatus(
                rawTableExists = true,
                hasUnprocessedRecords = hasUnprocessedRecords,
                maxProcessedTimestamp = maxProcessedTimestamp,
            )
        } else {
            log.info {
                "${stream.id.originalNamespace}.${stream.id.originalName}: non-truncate sync and no temp raw table. Initial raw table status is $initialRawTableStatus."
            }
            return destinationInitialStatus.initialRawTableStatus
        }
    }

    private fun prepareStageForTruncate(
        destinationInitialStatus: DestinationInitialStatus<DestinationState>,
        stream: StreamConfig
    ) {
        if (destinationInitialStatus.initialTempRawTableStatus.rawTableExists) {
            val tempStageGeneration =
                storageOperation.getStageGeneration(stream.id, TMP_TABLE_SUFFIX)
            if (tempStageGeneration == null || tempStageGeneration == stream.generationId) {
                log.info {
                    "${stream.id.originalNamespace}.${stream.id.originalName}: truncate sync, and existing temp raw table belongs to generation $tempStageGeneration (== current generation ${stream.generationId}). Retaining it."
                }
                // The temp table is from the correct generation. Set up any other resources
                // (staging file, etc.), but leave the table untouched.
                storageOperation.prepareStage(
                    stream.id,
                    TMP_TABLE_SUFFIX,
                )
            } else {
                log.info {
                    "${stream.id.originalNamespace}.${stream.id.originalName}: truncate sync, and existing temp raw table belongs to generation $tempStageGeneration (!= current generation ${stream.generationId}). Truncating it."
                }
                // The temp stage is from the wrong generation. Nuke it.
                storageOperation.prepareStage(
                    stream.id,
                    TMP_TABLE_SUFFIX,
                    replace = true,
                )
            }
            // (if the existing temp stage is from the correct generation, then we're resuming
            // a truncate refresh, and should keep the previous temp stage).
        } else {
            log.info {
                "${stream.id.originalNamespace}.${stream.id.originalName}: truncate sync, and no preexisting temp raw table. Creating it."
            }
            // We're initiating a new truncate refresh. Create a new temp stage.
            storageOperation.prepareStage(
                stream.id,
                TMP_TABLE_SUFFIX,
            )
        }
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
        if (isTruncateSync) {
            // Truncate refresh. Use a temp final table.
            return prepareFinalTableForOverwrite(initialStatus)
        } else {
            if (initialStatus.isSchemaMismatch || initialStatus.destinationState.needsSoftReset()) {
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

    private fun prepareFinalTableForOverwrite(
        initialStatus: DestinationInitialStatus<DestinationState>
    ): String {
        val stream = initialStatus.streamConfig
        if (!initialStatus.isFinalTableEmpty || initialStatus.isSchemaMismatch) {
            // overwrite an existing tmp table if needed.
            storageOperation.createFinalTable(stream, TMP_TABLE_SUFFIX, true)
            log.info {
                "Using temp final table for table ${stream.id.finalName}, this will be overwritten at end of sync"
            }
            // We want to overwrite an existing table. Write into a tmp table.
            // We'll overwrite the table at the end of the sync.
            return TMP_TABLE_SUFFIX
        }

        log.info {
            "Final Table for stream ${stream.id.finalName} is empty and matches the expected v2 format, writing to table directly"
        }
        return NO_SUFFIX
    }

    override fun writeRecords(streamConfig: StreamConfig, stream: Stream<PartialAirbyteMessage>) {
        // redirect to the appropriate raw table (potentially the temp raw table).
        writeRecordsImpl(
            streamConfig,
            // TODO it's a little annoying to have to remember which suffix goes here.
            // conceptually it's simple (writing records == writing to stage => raw table suffix)
            // but still an easy mistake to make.
            // Maybe worth defining `data class StageName(suffix: String)`
            // and `data class FinalName(suffix: String)`?
            // ... and separating those out from StreamId
            rawTableSuffix,
            stream,
        )
    }

    /** Write records will be destination type specific, Insert vs staging based on format */
    abstract fun writeRecordsImpl(
        streamConfig: StreamConfig,
        suffix: String,
        stream: Stream<PartialAirbyteMessage>
    )

    override fun finalizeTable(streamConfig: StreamConfig, syncSummary: StreamSyncSummary) {
        // Delete staging directory, implementation will handle if it has to do it or not or a No-OP
        storageOperation.cleanupStage(streamConfig.id)

        val streamSuccessful = syncSummary.terminalStatus == AirbyteStreamStatus.COMPLETE
        // Overwrite the raw table before doing anything else.
        // This ensures that if T+D fails, we can easily retain the records on the next sync.
        // It also means we don't need to run T+D using the temp raw table,
        // which is possible (`typeAndDedupe(streamConfig.id.copy(rawName = streamConfig.id.rawName
        // + suffix))`
        // but annoying and confusing.
        if (isTruncateSync && streamSuccessful) {
            log.info {
                "Overwriting raw table for ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName} because this is a truncate sync and we received a stream success message."
            }
            storageOperation.overwriteStage(streamConfig.id, rawTableSuffix)
        } else {
            log.info {
                "Not overwriting raw table for ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName}. Truncate sync: $isTruncateSync; stream success: $streamSuccessful"
            }
        }

        if (disableTypeDedupe) {
            log.info {
                "Typing and deduping disabled, skipping final table finalization. " +
                    "Raw records can be found at ${streamConfig.id.rawNamespace}.${streamConfig.id.rawName}"
            }
            return
        }

        // Normal syncs should T+D regardless of status, so the user sees progress after every
        // attempt.
        // We know this is a normal sync, so initialRawTableStatus is nonnull.
        if (
            !isTruncateSync &&
                syncSummary.recordsWritten == 0L &&
                !initialRawTableStatus!!.hasUnprocessedRecords
        ) {
            log.info {
                "Skipping typing and deduping for stream ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName} " +
                    "because it had no records during this sync and no unprocessed records from a previous sync."
            }
        } else if (isTruncateSync && (!streamSuccessful || syncSummary.recordsWritten == 0L)) {
            // But truncate syncs should only T+D if the sync was successful, since we're T+Ding
            // into a temp final table anyway. And we only need to check if _this_ sync emitted
            // records, since we've nuked the old raw data.
            log.info {
                "Skipping typing and deduping for stream ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName}. Stream success: $streamSuccessful; records written: ${syncSummary.recordsWritten}"
            }
        } else {
            // In truncate mode, we want to read all the raw records. Typically, this is equivalent
            // to filtering on timestamp, but might as well be explicit.
            val timestampFilter =
                if (!isTruncateSync) {
                    initialRawTableStatus!!.maxProcessedTimestamp
                } else {
                    Optional.empty()
                }
            storageOperation.typeAndDedupe(streamConfig, timestampFilter, finalTmpTableSuffix)
        }

        // We want to run this independently of whether we ran T+D.
        // E.g. it's valid for a sync to emit 0 records (e.g. the source table is legitimately
        // empty), in which case we want to overwrite the final table with an empty table.
        if (isTruncateSync && streamSuccessful && finalTmpTableSuffix.isNotBlank()) {
            log.info {
                "Overwriting final table for ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName} because this is a truncate sync, we received a stream success message, and we are using a temp final table.."
            }
            storageOperation.overwriteFinalTable(streamConfig, finalTmpTableSuffix)
        } else {
            log.info {
                "Not overwriting final table for ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName}. Truncate sync: $isTruncateSync; stream success: $streamSuccessful; final table suffix not blank: ${finalTmpTableSuffix.isNotBlank()}"
            }
        }
    }

    companion object {
        private const val NO_SUFFIX = ""
        const val TMP_TABLE_SUFFIX = "_airbyte_tmp"
    }
}
