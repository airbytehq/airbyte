/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import com.fasterxml.jackson.databind.JsonNode
import com.google.api.gax.rpc.PermissionDeniedException
import com.google.cloud.bigquery.storage.v1.BigQueryReadClient
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.generatePartitionId
import io.airbyte.integrations.source.bigquery.BigQuerySourceConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import kotlin.math.ceil

private val log = KotlinLogging.logger {}

/** Everything the partition readers of one table share. */
class BigQueryReadApiTable(
    val stream: Stream,
    val streamFeedBootstrap: StreamFeedBootstrap,
    val progress: BigQueryReadApiTableProgress,
    val client: BigQueryReadClient,
    val resourceAcquirer: ResourceAcquirer,
    /** The state emitted once every read stream is complete. */
    val terminalState: OpaqueStateValue,
    val jobProjectId: String,
    val constants: BigQueryReadApiConstants,
)

/**
 * What pins the initial snapshot of an incremental stream: the table version the read session reads
 * ([snapshotTime]) and the cursor's maximum at that same instant ([cursorUpperBound]), which
 * becomes the cursor checkpoint once the snapshot is complete. [fromExpiredSession] marks a spec
 * recovered from the state of an expired session: the creator reopens a session at the same instant
 * so the stored bound stays valid, and takes a new snapshot only if BigQuery refuses (the table's
 * time travel window, 2 to 7 days, has passed).
 */
data class BigQueryReadApiSnapshotSpec(
    val snapshotTime: Instant,
    val cursorUpperBound: BigQueryReadApiState.CursorBound,
    val fromExpiredSession: Boolean = false,
)

/** How [BigQueryReadApiPartitionsCreator] should proceed, decided from the stream's state. */
sealed interface BigQueryReadApiPlan {
    /**
     * No usable session: create one and read the table from the start; for an incremental stream
     * [snapshot] pins the table version and the cursor upper bound (null until the factory computed
     * them).
     */
    data class Fresh(val reason: String, val snapshot: BigQueryReadApiSnapshotSpec? = null) :
        BigQueryReadApiPlan

    /** Continue the session described by [state]. */
    data class Resume(val state: BigQueryReadApiState) : BigQueryReadApiPlan

    /** Nothing left to read. */
    data object Complete : BigQueryReadApiPlan

    /** This path must not touch the stream: the `extract-jdbc` factory continues it. */
    data class Decline(val reason: String) : BigQueryReadApiPlan
}

/**
 * Splits a table into its Storage Read API read streams (one [BigQueryReadApiPartitionReader] per
 * read stream still to read, in session order), creating the session on the first round and
 * resuming it on later rounds and retried attempts.
 */
class BigQueryReadApiPartitionsCreator(
    private val streamFeedBootstrap: StreamFeedBootstrap,
    private val plan: BigQueryReadApiPlan,
    private val config: BigQuerySourceConfiguration,
    private val constants: BigQueryReadApiConstants,
    /** Built lazily: the credentials are only needed once a read stream is actually read. */
    private val clients: BigQueryReadApiClients,
    private val registry: BigQueryReadApiProgressRegistry,
    private val resourceAcquirer: ResourceAcquirer,
    /**
     * The state emitted once every read stream is complete, as decided from the plan; for an
     * incremental stream it is recomputed from the progress when the creator had to take a new
     * snapshot (see [terminalStateFor]).
     */
    private val terminalState: OpaqueStateValue,
    /** Logical size of the table in bytes, for sizing the read streams; null when unknown. */
    private val numBytes: Long?,
    /** The configured cursor of an incremental stream whose initial snapshot this is; else null. */
    private val cursor: EmittedField? = null,
    /** Computes a fresh snapshot time and cursor upper bound; required when [cursor] is set. */
    private val snapshotQueries: BigQueryReadApiSnapshotQueries? = null,
) : PartitionsCreator {

    val stream: Stream = streamFeedBootstrap.feed

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus =
        PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN

    override fun releaseResources() {}

    override suspend fun run(): List<PartitionReader> {
        if (plan is BigQueryReadApiPlan.Complete) {
            log.info { "'${stream.label}' is complete." }
            return listOf(CheckpointOnlyPartitionReader())
        }
        val progress: BigQueryReadApiTableProgress = progress()
        registry.put(stream.id, progress)
        if (progress.isComplete) {
            log.info { "Every read stream of '${stream.label}' is complete." }
            return listOf(CheckpointOnlyPartitionReader())
        }
        val remaining: List<BigQueryReadApiState.ReadStreamWork> = progress.remainingWork()
        log.info {
            "'${stream.label}': ${remaining.size} of ${progress.session.readStreams.size} read " +
                "streams to read (${remaining.count { it.offset > 0 }} resumed at an offset)."
        }
        val table =
            BigQueryReadApiTable(
                stream,
                streamFeedBootstrap,
                progress,
                clients.readClient,
                resourceAcquirer,
                terminalStateFor(progress),
                config.jobProjectId,
                constants,
            )
        return remaining.map { BigQueryReadApiPartitionReader(table, it) }
    }

    /**
     * The cursor checkpoint `{"primary_key":{},"cursors":{"<cursor>":<max>}}` of an incremental
     * initial snapshot, exactly what the `extract-jdbc` path emits when its snapshot completes, so
     * that the next sync reads the deltas through the query API; else the plan's terminal state.
     */
    private fun terminalStateFor(progress: BigQueryReadApiTableProgress): OpaqueStateValue {
        val c: EmittedField = cursor ?: return terminalState
        val bound: BigQueryReadApiState.CursorBound =
            progress.cursorUpperBound ?: return terminalState
        return DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(c, bound.value)
    }

    private fun progress(): BigQueryReadApiTableProgress {
        val existing: BigQueryReadApiTableProgress? = registry.get(stream.id)
        when (plan) {
            is BigQueryReadApiPlan.Resume -> {
                if (existing != null && existing.session.name == plan.state.session.name) {
                    // A later round of the same READ: the in-memory progress is authoritative.
                    return existing
                }
                val session =
                    BigQueryReadSession(
                        name = plan.state.session.name,
                        expiresAt = plan.state.session.expiresAtInstant,
                        readStreams = plan.state.session.readStreams,
                        arrowSchema = null,
                        estimatedRowCount = null,
                        estimatedBytes = null,
                    )
                log.info { "Resuming '${stream.label}' from $session." }
                return BigQueryReadApiTableProgress(session, plan.state)
            }
            is BigQueryReadApiPlan.Fresh -> {
                log.info { "Reading '${stream.label}' from the start: ${plan.reason}." }
                return freshProgress(plan)
            }
            BigQueryReadApiPlan.Complete ->
                throw IllegalStateException("complete plan has no progress")
            is BigQueryReadApiPlan.Decline ->
                throw IllegalStateException("declined plan has no progress")
        }
    }

    /**
     * A new session. For an incremental stream the session is opened at the plan's snapshot time;
     * when that time comes from an expired session and BigQuery no longer serves it (the table's
     * time travel window has passed), a new snapshot time and cursor upper bound are taken.
     */
    private fun freshProgress(plan: BigQueryReadApiPlan.Fresh): BigQueryReadApiTableProgress {
        val c: EmittedField =
            cursor ?: return BigQueryReadApiTableProgress(createSession(snapshotTime = null))
        val stored: BigQueryReadApiSnapshotSpec? = plan.snapshot
        if (stored != null && stored.fromExpiredSession) {
            try {
                val session: BigQueryReadSession = createSession(stored.snapshotTime)
                log.info {
                    "'${stream.label}': reopened a read session as of ${stored.snapshotTime}; " +
                        "the cursor upper bound ${stored.cursorUpperBound.value} stays valid."
                }
                return BigQueryReadApiTableProgress(
                    session,
                    snapshotTime = stored.snapshotTime,
                    cursorUpperBound = stored.cursorUpperBound,
                )
            } catch (e: ConfigErrorException) {
                throw e
            } catch (e: RuntimeException) {
                log.warn(e) {
                    "'${stream.label}': BigQuery no longer serves the table as of " +
                        "${stored.snapshotTime} (time travel window passed?); taking a new snapshot."
                }
            }
        }
        val pinned: BigQueryReadApiSnapshotSpec =
            if (stored != null && !stored.fromExpiredSession) stored
            else {
                val queries: BigQueryReadApiSnapshotQueries =
                    snapshotQueries
                        ?: throw IllegalStateException(
                            "incremental snapshot without snapshot queries"
                        )
                val snapshotTime: Instant = queries.pickSnapshotTime()
                val bound: JsonNode? = queries.cursorUpperBound(stream, c, snapshotTime)
                if (bound == null) {
                    log.warn {
                        "'${stream.label}' has no '${c.id}' value as of $snapshotTime; the " +
                            "snapshot completes without a cursor checkpoint."
                    }
                    return BigQueryReadApiTableProgress(
                        createSession(snapshotTime),
                        snapshotTime = snapshotTime,
                    )
                }
                BigQueryReadApiSnapshotSpec(
                    snapshotTime,
                    BigQueryReadApiState.CursorBound(c.id, bound),
                )
            }
        log.info {
            "'${stream.label}': initial snapshot as of ${pinned.snapshotTime}, cursor upper " +
                "bound ${pinned.cursorUpperBound.value}."
        }
        return BigQueryReadApiTableProgress(
            createSession(pinned.snapshotTime),
            snapshotTime = pinned.snapshotTime,
            cursorUpperBound = pinned.cursorUpperBound,
        )
    }

    private fun createSession(snapshotTime: Instant?): BigQueryReadSession {
        val target: Long = constants.readStreamTargetBytes.coerceAtLeast(1L)
        val bySize: Int = numBytes?.let { ceil(it.toDouble() / target.toDouble()).toInt() } ?: 0
        val maxReadStreams: Int =
            bySize.coerceIn(
                config.maxConcurrency,
                constants.maxReadStreams.coerceAtLeast(config.maxConcurrency)
            )
        log.info {
            "'${stream.label}': requesting up to $maxReadStreams read streams " +
                "(table bytes: ${numBytes ?: "unknown"}, target per read stream: $target)."
        }
        return try {
            BigQueryReadSession.create(
                client = clients.readClient,
                jobProjectId = config.jobProjectId,
                dataProjectId = config.projectId,
                dataset = stream.namespace ?: config.datasetId ?: config.projectId,
                table = stream.name,
                selectedFields = stream.fields.map { it.id },
                maxReadStreams = maxReadStreams,
                arrowBufferCompression = constants.arrowBufferCompression,
                snapshotTime = snapshotTime,
            )
        } catch (e: PermissionDeniedException) {
            throw ConfigErrorException(
                BigQueryReadSession.permissionDeniedMessage(config.jobProjectId),
                e,
            )
        }
    }

    /** Emits the terminal state of a table with nothing (left) to read. */
    inner class CheckpointOnlyPartitionReader : PartitionReader {
        override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus =
            PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN

        override suspend fun run() {}

        override fun checkpoint(): PartitionReadCheckpoint =
            PartitionReadCheckpoint(
                terminalState,
                0,
                when (streamFeedBootstrap.dataChannelMedium) {
                    SOCKET -> generatePartitionId(4)
                    STDIO -> null
                },
            )

        override fun releaseResources() {}
    }
}
