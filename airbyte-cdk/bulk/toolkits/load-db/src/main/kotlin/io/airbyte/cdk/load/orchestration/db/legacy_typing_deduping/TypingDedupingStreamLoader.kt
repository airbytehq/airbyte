/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.TableNames.Companion.NO_SUFFIX
import io.airbyte.cdk.load.orchestration.db.TableNames.Companion.TMP_TABLE_SUFFIX
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant

private val logger = KotlinLogging.logger {}

class TypingDedupingStreamLoader(
    override val stream: DestinationStream,
    private val initialStatus: TypingDedupingDatabaseInitialStatus,
    private val tableNames: TableNames,
    private val columnNameMapping: ColumnNameMapping,
    private val rawTableOperations: TypingDedupingRawTableOperations,
    private val finalTableOperations: TypingDedupingFinalTableOperations,
    private val disableTypeDedupe: Boolean,
    private val streamStateStore: StreamStateStore<TypingDedupingExecutionConfig>,
) : StreamLoader {
    private val isTruncateSync =
        when (stream.minimumGenerationId) {
            0L -> false
            stream.generationId -> true
            else -> {
                throw IllegalArgumentException("Hybrid refreshes are not yet supported.")
            }
        }
    private lateinit var rawTableSuffix: String
    private lateinit var finalTmpTableSuffix: String
    /**
     * The status of the raw table that "matters" for this sync. Specifically:
     * * For normal syncs / merge refreshes, this is the status of the real raw table)
     * * For truncate refreshes, this is the status of the temp raw table (because we never even
     * look at the real raw table)
     */
    private lateinit var initialRawTableStatus: RawTableInitialStatus

    override suspend fun start() {
        if (isTruncateSync) {
            val (rawTableStatus, suffix) = prepareStageForTruncate()
            initialRawTableStatus = rawTableStatus
            rawTableSuffix = suffix
        } else {
            rawTableSuffix = NO_SUFFIX
            initialRawTableStatus = prepareStageForNormalSync()
        }

        if (!disableTypeDedupe) {
            // Prepare final tables based on sync mode.
            finalTmpTableSuffix = prepareFinalTable()
        } else {
            logger.info { "Typing and deduping disabled, skipping final table initialization" }
            finalTmpTableSuffix = NO_SUFFIX
        }

        streamStateStore.put(
            stream.descriptor,
            TypingDedupingExecutionConfig(rawTableSuffix),
        )
    }

    private fun prepareStageForTruncate(): Pair<RawTableInitialStatus, String> {
        /*
        tl;dr:
        * if a temp raw table exists, check whether it belongs to the correct generation.
          * if wrong generation, truncate it.
          * regardless, write into the temp raw table.
        * else, if a real raw table exists, check its generation.
          * if wrong generation, write into a new temp raw table.
          * else, write into the preexisting real raw table.
        * else, create a new temp raw table and write into it.
         */
        if (initialStatus.tempRawTableStatus != null) {
            val tempStageGeneration =
                rawTableOperations.getRawTableGeneration(
                    tableNames.rawTableName!!,
                    TMP_TABLE_SUFFIX
                )
            if (tempStageGeneration == null || tempStageGeneration == stream.generationId) {
                logger.info {
                    "${stream.descriptor.toPrettyString()}: truncate sync, and existing temp raw table belongs to generation $tempStageGeneration (== current generation ${stream.generationId}). Retaining it."
                }
                // The temp table is from the correct generation. Set up any other resources
                // (staging file, etc.), but leave the table untouched.
                rawTableOperations.prepareRawTable(
                    tableNames.rawTableName,
                    TMP_TABLE_SUFFIX,
                )
                return Pair(initialStatus.tempRawTableStatus.reify(), TMP_TABLE_SUFFIX)
            } else {
                logger.info {
                    "${stream.descriptor.toPrettyString()}: truncate sync, and existing temp raw table belongs to generation $tempStageGeneration (!= current generation ${stream.generationId}). Truncating it."
                }
                // The temp stage is from the wrong generation. Nuke it.
                rawTableOperations.prepareRawTable(
                    tableNames.rawTableName,
                    TMP_TABLE_SUFFIX,
                    replace = true,
                )
                // We nuked the temp raw table, so create a new initial raw table status.
                return Pair(
                    RawTableInitialStatus.emptyTableStatus,
                    TMP_TABLE_SUFFIX,
                )
            }
        } else if (initialStatus.rawTableStatus != null) {
            // It's possible to "resume" a truncate sync that was previously already finalized.
            // In this case, there is no existing temp raw table, and there is a real raw table
            // which already belongs to the correct generation.
            // Check for that case now.
            val realStageGeneration =
                rawTableOperations.getRawTableGeneration(tableNames.rawTableName!!, NO_SUFFIX)
            if (realStageGeneration == null || realStageGeneration == stream.generationId) {
                logger.info {
                    "${stream.descriptor.toPrettyString()}: truncate sync, no existing temp raw table, and existing real raw table belongs to generation $realStageGeneration (== current generation ${stream.generationId}). Retaining it."
                }
                // The real raw table is from the correct generation. Set up any other resources
                // (staging file, etc.), but leave the table untouched.
                rawTableOperations.prepareRawTable(tableNames.rawTableName, NO_SUFFIX)
                return Pair(initialStatus.rawTableStatus.reify(), NO_SUFFIX)
            } else {
                logger.info {
                    "${stream.descriptor.toPrettyString()}: truncate sync, existing real raw table belongs to generation $realStageGeneration (!= current generation ${stream.generationId}), and no preexisting temp raw table. Creating a temp raw table."
                }
                // We're initiating a new truncate refresh. Create a new temp stage.
                rawTableOperations.prepareRawTable(
                    tableNames.rawTableName,
                    TMP_TABLE_SUFFIX,
                )
                return Pair(
                    // Create a fresh raw table status, since we created a fresh temp stage.
                    RawTableInitialStatus.emptyTableStatus,
                    TMP_TABLE_SUFFIX,
                )
            }
        } else {
            logger.info {
                "${stream.descriptor.toPrettyString()}: truncate sync, and no preexisting temp or  raw table. Creating a temp raw table."
            }
            // We're initiating a new truncate refresh. Create a new temp stage.
            rawTableOperations.prepareRawTable(
                tableNames.rawTableName!!,
                TMP_TABLE_SUFFIX,
            )
            return Pair(
                // Create a fresh raw table status, since we created a fresh temp stage.
                RawTableInitialStatus.emptyTableStatus,
                TMP_TABLE_SUFFIX,
            )
        }
    }

    private fun prepareStageForNormalSync(): RawTableInitialStatus {
        logger.info {
            "${stream.descriptor.toPrettyString()}: non-truncate sync. Creating raw table if not exists."
        }
        rawTableOperations.prepareRawTable(tableNames.rawTableName!!, NO_SUFFIX)
        if (initialStatus.tempRawTableStatus != null) {
            logger.info {
                "${stream.descriptor.toPrettyString()}: non-truncate sync, but temp raw table exists. Transferring it to real raw table."
            }
            // There was a previous truncate refresh attempt, which failed, and left some
            // records behind.
            // Retrieve those records and put them in the real stage.
            // This is necessary to avoid certain data loss scenarios.
            // (specifically: a user initiates a truncate sync, which fails, but emits some records.
            // It also emits a state message for "resumable" full refresh.
            // The user then initiates an incremental sync, which runs using that state.
            // In this case, we MUST retain the records from the truncate attempt.)
            rawTableOperations.transferFromTempRawTable(tableNames.rawTableName, TMP_TABLE_SUFFIX)

            // We need to combine the raw table statuses from the real and temp raw tables.
            val hasUnprocessedRecords =
                initialStatus.tempRawTableStatus.hasUnprocessedRecords ||
                    (initialStatus.rawTableStatus?.hasUnprocessedRecords ?: false)
            // Pick the earlier min timestamp.
            val maxProcessedTimestamp: Instant? =
                initialStatus.rawTableStatus?.maxProcessedTimestamp?.let { realRawTableTimestamp ->
                    initialStatus.tempRawTableStatus.maxProcessedTimestamp?.let {
                        tempRawTableTimestamp ->
                        if (realRawTableTimestamp.isBefore(tempRawTableTimestamp)) {
                            realRawTableTimestamp
                        } else {
                            tempRawTableTimestamp
                        }
                    }
                        ?: realRawTableTimestamp
                }
                    ?: initialStatus.tempRawTableStatus.maxProcessedTimestamp
            val updatedStatus =
                RawTableInitialStatus(
                    hasUnprocessedRecords = hasUnprocessedRecords,
                    maxProcessedTimestamp = maxProcessedTimestamp,
                )
            logger.info {
                "${stream.descriptor.toPrettyString()}: After record transfer, initial raw table status is $updatedStatus."
            }
            return updatedStatus
        } else {
            val initialRawTableStatus = initialStatus.rawTableStatus.reify()
            logger.info {
                "${stream.descriptor.toPrettyString()}: non-truncate sync and no temp raw table. Initial raw table status is $initialRawTableStatus."
            }
            return initialRawTableStatus
        }
    }

    private fun prepareFinalTable(): String {
        // No special handling if final table doesn't exist, just create and return
        if (initialStatus.finalTableStatus == null) {
            logger.info {
                "Final table does not exist for stream ${stream.descriptor.toPrettyString()}, creating ${tableNames.finalTableName!!.toPrettyString()}."
            }
            finalTableOperations.createFinalTable(
                stream,
                tableNames.finalTableName!!,
                columnNameMapping,
                NO_SUFFIX,
                replace = false
            )
            return NO_SUFFIX
        }

        logger.info { "Final Table exists for stream ${stream.descriptor.toPrettyString()}" }
        // The table already exists. Decide whether we're writing to it directly, or
        // using a tmp table.
        if (isTruncateSync) {
            if (
                initialStatus.finalTableStatus.isEmpty ||
                    initialStatus.finalTableStatus.finalTableGenerationId == null
            ) {
                if (!initialStatus.finalTableStatus.isSchemaMismatch) {
                    logger.info {
                        "Truncate sync, and final table is empty and has correct schema. Writing to it directly."
                    }
                    return NO_SUFFIX
                } else {
                    // No point soft resetting an empty table. We'll just do an overwrite later.
                    logger.info {
                        "Truncate sync, and final table is empty, but has the wrong schema. Using a temp final table."
                    }
                    return prepareFinalTableForOverwrite()
                }
            } else if (
                initialStatus.finalTableStatus.finalTableGenerationId >= stream.minimumGenerationId
            ) {
                if (!initialStatus.finalTableStatus.isSchemaMismatch) {
                    logger.info {
                        "Truncate sync, and final table matches our generation and has correct schema. Writing to it directly."
                    }
                    return NO_SUFFIX
                } else {
                    logger.info {
                        "Truncate sync, and final table matches our generation, but has the wrong schema. Writing to it directly, but triggering a soft reset first."
                    }
                    finalTableOperations.softResetFinalTable(stream, tableNames, columnNameMapping)
                    return NO_SUFFIX
                }
            } else {
                // The final table is in the wrong generation. Use a temp final table.
                return prepareFinalTableForOverwrite()
            }
        } else {
            if (initialStatus.finalTableStatus.isSchemaMismatch) {
                // We're loading data directly into the existing table.
                // Make sure it has the right schema.
                // Also, if a raw table migration wants us to do a soft reset, do that
                // here.
                logger.info { "Executing soft-reset on final table of stream ${stream.descriptor}" }
                finalTableOperations.softResetFinalTable(stream, tableNames, columnNameMapping)
            }
            return NO_SUFFIX
        }
    }

    private fun prepareFinalTableForOverwrite(): String {
        if (
            initialStatus.finalTableStatus?.isEmpty != true ||
                initialStatus.finalTableStatus.isSchemaMismatch
        ) {
            // overwrite an existing tmp table if needed.
            finalTableOperations.createFinalTable(
                stream,
                tableNames.finalTableName!!,
                columnNameMapping,
                TMP_TABLE_SUFFIX,
                replace = true
            )
            logger.info {
                "Using temp final table for table ${stream.descriptor.toPrettyString()}, this will be overwritten at end of sync"
            }
            // We want to overwrite an existing table. Write into a tmp table.
            // We'll overwrite the table at the end of the sync.
            return TMP_TABLE_SUFFIX
        }

        logger.info {
            "Final Table for stream ${stream.descriptor.toPrettyString()} is empty and matches the expected v2 format, writing to table directly"
        }
        return NO_SUFFIX
    }

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        val streamSuccessful = streamFailure == null
        // Overwrite the raw table before doing anything else.
        // This ensures that if T+D fails, we can easily retain the records on the next sync.
        // It also means we don't need to run T+D using the temp raw table,
        // which is possible (`typeAndDedupe(streamConfig.id.copy(rawName = streamConfig.id.rawName
        // + suffix))`
        // but annoying and confusing.
        if (isTruncateSync && streamSuccessful && rawTableSuffix.isNotEmpty()) {
            logger.info {
                "Overwriting raw table for ${stream.descriptor.toPrettyString()} because this is a truncate sync, we received a stream success message, and are using a temporary raw table."
            }
            rawTableOperations.overwriteRawTable(tableNames.rawTableName!!, rawTableSuffix)
        } else {
            logger.info {
                "Not overwriting raw table for ${stream.descriptor.toPrettyString()}. Truncate sync: $isTruncateSync; stream success: $streamSuccessful; raw table suffix: \"$rawTableSuffix\""
            }
        }

        if (disableTypeDedupe) {
            logger.info {
                "Typing and deduping disabled, skipping final table finalization. Raw records can be found at ${tableNames.rawTableName!!.toPrettyString()}"
            }
            return
        }

        // Normal syncs should T+D regardless of status, so the user sees progress after every
        // attempt.
        // We know this is a normal sync, so initialRawTableStatus is nonnull.
        if (!isTruncateSync && !hadNonzeroRecords && !initialRawTableStatus.hasUnprocessedRecords) {
            logger.info {
                "Skipping typing and deduping for stream ${stream.descriptor.toPrettyString()} because it had no records during this sync and no unprocessed records from a previous sync."
            }
        } else if (
            isTruncateSync &&
                (!streamSuccessful ||
                    (!hadNonzeroRecords && !initialRawTableStatus.hasUnprocessedRecords))
        ) {
            // But truncate syncs should only T+D if the sync was successful, since we're T+Ding
            // into a temp final table anyway.
            // We only run T+D if the current sync had some records, or a previous attempt wrote
            // some records to the temp raw table.
            logger.info {
                "Skipping typing and deduping for stream ${stream.descriptor.toPrettyString()} running as truncate sync. Stream success: $streamSuccessful; had nonzero records: $hadNonzeroRecords; temp raw table had records: ${initialRawTableStatus.hasUnprocessedRecords}"
            }
        } else {
            // When targeting the temp final table, we want to read all the raw records
            // because the temp final table is always a full rebuild. Typically, this is equivalent
            // to filtering on timestamp, but might as well be explicit.
            val maxProcessedTimestamp =
                if (finalTmpTableSuffix.isEmpty()) {
                    initialRawTableStatus.maxProcessedTimestamp
                } else {
                    null
                }
            finalTableOperations.typeAndDedupe(
                stream,
                tableNames,
                columnNameMapping,
                maxProcessedTimestamp = maxProcessedTimestamp,
                finalTableSuffix = finalTmpTableSuffix
            )
        }

        // We want to run this independently of whether we ran T+D.
        // E.g. it's valid for a sync to emit 0 records (e.g. the source table is legitimately
        // empty), in which case we want to overwrite the final table with an empty table.
        if (isTruncateSync && streamSuccessful && finalTmpTableSuffix.isNotBlank()) {
            logger.info {
                "Overwriting final table for ${stream.descriptor.toPrettyString()} because this is a truncate sync, we received a stream success message, and we are using a temp final table.."
            }
            finalTableOperations.overwriteFinalTable(
                stream,
                tableNames.finalTableName!!,
                finalTableSuffix = finalTmpTableSuffix
            )
        } else {
            logger.info {
                "Not overwriting final table for ${stream.descriptor.toPrettyString()}. Truncate sync: $isTruncateSync; stream success: $streamSuccessful; final table suffix not blank: ${finalTmpTableSuffix.isNotBlank()}"
            }
        }
    }
}
