/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil.getResultsOrLogAndThrowFirst
import io.airbyte.commons.concurrency.CompletableFutures
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeRawTableMigrations
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeWeirdMigrations
import io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.prepareSchemas
import io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.util.*
import java.util.concurrent.*
import java.util.function.Supplier
import kotlin.jvm.optionals.getOrDefault
import org.apache.commons.lang3.ObjectUtils
import org.apache.commons.lang3.StringUtils
import org.apache.commons.lang3.concurrent.BasicThreadFactory
import org.apache.commons.lang3.tuple.Pair

private val LOGGER = KotlinLogging.logger {}
/**
 * An abstraction over SqlGenerator and DestinationHandler. Destinations will still need to call
 * `new CatalogParser(new FooSqlGenerator()).parseCatalog()`, but should otherwise avoid interacting
 * directly with these classes.
 *
 * In a typical sync, destinations should call the methods:
 *
 * 1. [.prepareFinalTables] once at the start of the sync
 * 1. [.typeAndDedupe] as needed throughout the sync
 * 1. [.commitFinalTables] once at the end of the sync
 *
 * Note that #prepareTables() initializes some internal state. The other methods will throw an
 * exception if that method was not called.
 */
class DefaultTyperDeduper<DestinationState : MinimumDestinationState>(
    private val sqlGenerator: SqlGenerator,
    private val destinationHandler: DestinationHandler<DestinationState>,
    private val parsedCatalog: ParsedCatalog,
    private val v1V2Migrator: DestinationV1V2Migrator,
    private val v2TableMigrator: V2TableMigrator,
    private val migrations: List<Migration<DestinationState>>
) : TyperDeduper {

    private lateinit var overwriteStreamsWithTmpTable: MutableSet<StreamId>
    private val streamsWithSuccessfulSetup: MutableSet<Pair<String, String>> =
        ConcurrentHashMap.newKeySet(parsedCatalog.streams.size)
    private val initialRawTableStateByStream: MutableMap<StreamId, InitialRawTableStatus> =
        ConcurrentHashMap()
    private val executorService: ExecutorService =
        Executors.newFixedThreadPool(
            FutureUtils.countOfTypeAndDedupeThreads,
            BasicThreadFactory.Builder()
                .namingPattern(IntegrationRunner.TYPE_AND_DEDUPE_THREAD_NAME)
                .build()
        )
    private lateinit var destinationInitialStatuses:
        List<DestinationInitialStatus<DestinationState>>

    constructor(
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<DestinationState>,
        parsedCatalog: ParsedCatalog,
        v1V2Migrator: DestinationV1V2Migrator,
        migrations: List<Migration<DestinationState>>
    ) : this(
        sqlGenerator,
        destinationHandler,
        parsedCatalog,
        v1V2Migrator,
        NoopV2TableMigrator(),
        migrations
    )

    @Throws(Exception::class)
    override fun prepareSchemasAndRunMigrations() {
        // Technically kind of weird to call this here, but it's the best place we have.
        // Ideally, we'd create just airbyte_internal here, and defer creating the final table
        // schemas
        // until prepareFinalTables... but it doesn't really matter.
        prepareSchemas(sqlGenerator, destinationHandler, parsedCatalog)

        executeWeirdMigrations(
            executorService,
            sqlGenerator,
            destinationHandler,
            v1V2Migrator,
            v2TableMigrator,
            parsedCatalog
        )

        destinationInitialStatuses =
            executeRawTableMigrations(
                executorService,
                destinationHandler,
                migrations,
                destinationHandler.gatherInitialState(parsedCatalog.streams)
            )

        // Commit our destination states immediately.
        // Technically, migrations aren't done until we execute the soft reset.
        // However, our state contains a needsSoftReset flag, so we can commit that we already
        // executed the
        // migration
        // and even if we fail to run the soft reset in this sync, future syncs will see the soft
        // reset flag
        // and finish it for us.
        destinationHandler.commitDestinationStates(
            destinationInitialStatuses.associate { it.streamConfig.id to it.destinationState }
        )
    }

    @Throws(Exception::class)
    override fun prepareFinalTables() {
        check(!::overwriteStreamsWithTmpTable.isInitialized) { "Tables were already prepared." }
        overwriteStreamsWithTmpTable = ConcurrentHashMap.newKeySet()
        LOGGER.info { "Preparing tables" }

        val prepareTablesFutureResult =
            CompletableFutures.allOf(
                    destinationInitialStatuses.map { this.prepareTablesFuture(it) }
                )
                .toCompletableFuture()
                .join()
        getResultsOrLogAndThrowFirst(
            "The following exceptions were thrown attempting to prepare tables:\n",
            prepareTablesFutureResult
        )

        // If we get here, then we've executed all soft resets. Force the soft reset flag to false.
        destinationHandler.commitDestinationStates(
            destinationInitialStatuses.associate {
                it.streamConfig.id to it.destinationState.withSoftReset(false)
            }
        )
    }

    private fun prepareTablesFuture(
        initialState: DestinationInitialStatus<DestinationState>
    ): CompletionStage<Unit> {
        // For each stream, make sure that its corresponding final table exists.
        // Also, for OVERWRITE streams, decide if we're writing directly to the final table, or into
        // an
        // _airbyte_tmp table.
        return CompletableFuture.supplyAsync(
            {
                val stream = initialState.streamConfig
                try {
                    if (initialState.isFinalTablePresent) {
                        LOGGER.info { "Final Table exists for stream ${stream.id.finalName}" }
                        // The table already exists. Decide whether we're writing to it directly, or
                        // using a tmp table.
                        if (stream.minimumGenerationId != 0L) {
                            if (
                                initialState.isSchemaMismatch ||
                                    (!initialState.isFinalTableEmpty &&
                                        initialState.finalTableGenerationId != stream.generationId)
                            ) {
                                LOGGER.info { "Using temp final table" }
                                // We want to overwrite an existing table. Write into a tmp table.
                                // We'll overwrite the table at the
                                // end of the sync.
                                overwriteStreamsWithTmpTable.add(stream.id)
                                if (
                                    initialState.finalTempTableGenerationId != stream.generationId
                                ) {
                                    LOGGER.info { "Recreating temp final table" }
                                    // overwrite an existing tmp table if needed.
                                    destinationHandler.execute(
                                        sqlGenerator.createTable(
                                            stream,
                                            TMP_OVERWRITE_TABLE_SUFFIX,
                                            true
                                        )
                                    )
                                }
                                LOGGER.info {
                                    "Using temp final table for stream ${stream.id.finalName}, will overwrite existing table at end of sync"
                                }
                            } else {
                                LOGGER.info {
                                    "Final Table for stream ${stream.id.finalName} is empty and matches the expected v2 format, " +
                                        "writing to table directly"
                                }
                            }
                        } else if (
                            initialState.isSchemaMismatch ||
                                initialState.destinationState.needsSoftReset()
                        ) {
                            // We're loading data directly into the existing table.
                            // Make sure it has the right schema.
                            // Also, if a raw table migration wants us to do a soft reset, do that
                            // here.
                            TyperDeduperUtil.executeSoftReset(
                                sqlGenerator,
                                destinationHandler,
                                stream
                            )
                        }
                    } else {
                        LOGGER.info {
                            "Final Table does not exist for stream ${stream.id.finalName}, creating."
                        }
                        // The table doesn't exist. Create it. Don't force.
                        destinationHandler.execute(
                            sqlGenerator.createTable(stream, NO_SUFFIX, false)
                        )
                    }

                    val maxRawTimestemp =
                        initialState.initialRawTableStatus.maxProcessedTimestamp.getOrDefault(
                            Instant.MAX
                        )
                    val maxTempRawTimestemp =
                        initialState.initialTempRawTableStatus.maxProcessedTimestamp.getOrDefault(
                            Instant.MAX
                        )
                    val ts = ObjectUtils.min(maxRawTimestemp, maxTempRawTimestemp)
                    initialRawTableStateByStream[stream.id] =
                        InitialRawTableStatus(
                            true,
                            initialState.initialRawTableStatus.hasUnprocessedRecords ||
                                initialState.initialTempRawTableStatus.hasUnprocessedRecords,
                            if (ts == Instant.MAX) Optional.empty() else Optional.of(ts)
                        )

                    streamsWithSuccessfulSetup.add(
                        Pair.of(stream.id.originalNamespace, stream.id.originalName)
                    )

                    return@supplyAsync
                } catch (e: Exception) {
                    LOGGER.error(e) {
                        "Exception occurred while preparing tables for stream ${stream.id.originalName}"
                    }
                    throw RuntimeException(e)
                }
            },
            this.executorService
        )
    }

    @Throws(Exception::class)
    override fun typeAndDedupe(originalNamespace: String, originalName: String) {
        val streamConfig = parsedCatalog.getStream(originalNamespace, originalName)
        val task = typeAndDedupeTask(streamConfig)
        FutureUtils.reduceExceptions(
            setOf(task),
            "The Following Exceptions were thrown while typing and deduping ${originalNamespace}.${originalName}:\n",
        )
    }

    private fun streamSetupSucceeded(streamConfig: StreamConfig): Boolean {
        val originalNamespace = streamConfig.id.originalNamespace
        val originalName = streamConfig.id.originalName
        if (!streamsWithSuccessfulSetup.contains(Pair.of(originalNamespace, originalName))) {
            // For example, if T+D setup fails, but the consumer tries to run T+D on all streams
            // during close,
            // we should skip it.
            LOGGER.warn {
                "Skipping typing and deduping for $originalNamespace.$originalName because we could not set up the tables for this stream."
            }
            return false
        }
        return true
    }

    private fun typeAndDedupeTask(
        streamConfig: StreamConfig
    ): CompletableFuture<Optional<Exception>> {
        return CompletableFuture.supplyAsync(
            {
                val originalName = streamConfig.id.originalName
                try {
                    if (!streamSetupSucceeded(streamConfig)) {
                        return@supplyAsync Optional.empty<Exception>()
                    }

                    val initialRawTableStatus =
                        initialRawTableStateByStream.getValue(streamConfig.id)
                    TyperDeduperUtil.executeTypeAndDedupe(
                        sqlGenerator,
                        destinationHandler,
                        streamConfig,
                        initialRawTableStatus.maxProcessedTimestamp,
                        getFinalTableSuffix(streamConfig.id)
                    )
                    return@supplyAsync Optional.empty<Exception>()
                } catch (e: Exception) {
                    LOGGER.error(e) {
                        "Exception occurred while typing and deduping stream $originalName"
                    }
                    return@supplyAsync Optional.of<Exception>(e)
                }
            },
            this.executorService
        )
    }

    @Throws(Exception::class)
    override fun typeAndDedupe(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>) {
        LOGGER.info { "Typing and deduping all tables" }
        val typeAndDedupeTasks: MutableSet<CompletableFuture<Optional<Exception>>> = HashSet()
        parsedCatalog.streams
            .filter { streamConfig: StreamConfig ->
                // Skip if stream setup failed.
                if (!streamSetupSucceeded(streamConfig)) {
                    return@filter false
                }
                // Skip if we don't have any records for this stream.
                val streamSyncSummary = streamSyncSummaries[streamConfig.id.asStreamDescriptor()]!!
                val nonzeroRecords = streamSyncSummary.recordsWritten > 0
                val unprocessedRecordsPreexist =
                    initialRawTableStateByStream[streamConfig.id]!!.hasUnprocessedRecords
                // If this sync emitted records, or the previous sync left behind some unprocessed
                // records,
                // then the raw table has some unprocessed records right now.
                // Run T+D if either of those conditions are true.
                val shouldRunTypingDeduping =
                    (nonzeroRecords || unprocessedRecordsPreexist) &&
                        streamSyncSummary.terminalStatus ==
                            AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                if (!shouldRunTypingDeduping) {
                    LOGGER.info {
                        "Skipping typing and deduping for stream ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName} because it had no records during this sync and no unprocessed records from a previous sync."
                    }
                }
                shouldRunTypingDeduping
            }
            .forEach { streamConfig: StreamConfig ->
                typeAndDedupeTasks.add(typeAndDedupeTask(streamConfig))
            }
        CompletableFuture.allOf(*typeAndDedupeTasks.toTypedArray()).join()
        FutureUtils.reduceExceptions(
            typeAndDedupeTasks,
            "The Following Exceptions were thrown while typing and deduping tables:\n"
        )
    }

    /**
     * Does any "end of sync" work. For most streams, this is a noop.
     *
     * For OVERWRITE streams where we're writing to a temp table, this is where we swap the temp
     * table into the final table.
     */
    @Throws(Exception::class)
    override fun commitFinalTables(streamSyncSummaries: Map<StreamDescriptor, StreamSyncSummary>) {
        LOGGER.info { "Committing final tables" }
        val tableCommitTasks: MutableSet<CompletableFuture<Optional<Exception>>> = HashSet()
        for (streamConfig in parsedCatalog.streams) {
            if (
                !streamsWithSuccessfulSetup.contains(
                    Pair.of(streamConfig.id.originalNamespace, streamConfig.id.originalName)
                ) ||
                    streamSyncSummaries
                        .getValue(streamConfig.id.asStreamDescriptor())
                        .terminalStatus !=
                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
            ) {
                LOGGER.warn {
                    "Skipping committing final table for for ${streamConfig.id.originalNamespace}.${streamConfig.id.originalName} " +
                        "because we could not set up the tables for this stream."
                }
                continue
            }
            if (streamConfig.minimumGenerationId == streamConfig.generationId) {
                tableCommitTasks.add(commitFinalTableTask(streamConfig))
            }
        }
        CompletableFuture.allOf(*tableCommitTasks.toTypedArray()).join()
        FutureUtils.reduceExceptions(
            tableCommitTasks,
            "The Following Exceptions were thrown while committing final tables:\n"
        )
    }

    private fun commitFinalTableTask(
        streamConfig: StreamConfig
    ): CompletableFuture<Optional<Exception>> {
        return CompletableFuture.supplyAsync(
            Supplier supplyAsync@{
                val streamId = streamConfig.id
                val finalSuffix = getFinalTableSuffix(streamId)
                if (!StringUtils.isEmpty(finalSuffix)) {
                    val overwriteFinalTable =
                        sqlGenerator.overwriteFinalTable(streamId, finalSuffix)
                    LOGGER.info {
                        "Overwriting final table with tmp table for stream ${streamId.originalNamespace}.${streamId.originalName}"
                    }
                    try {
                        destinationHandler.execute(overwriteFinalTable)
                    } catch (e: Exception) {
                        LOGGER.error(e) {
                            "Exception Occurred while committing final table for stream ${streamId.originalName}"
                        }
                        return@supplyAsync Optional.of(e)
                    }
                }
                return@supplyAsync Optional.empty<Exception>()
            },
            this.executorService
        )
    }

    private fun getFinalTableSuffix(streamId: StreamId): String {
        return if (overwriteStreamsWithTmpTable.contains(streamId)) TMP_OVERWRITE_TABLE_SUFFIX
        else NO_SUFFIX
    }

    override fun cleanup() {
        LOGGER.info { "Cleaning Up type-and-dedupe thread pool" }
        executorService.shutdown()
    }

    companion object {

        private const val NO_SUFFIX = ""
        private const val TMP_OVERWRITE_TABLE_SUFFIX = "_airbyte_tmp"
    }
}
