/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import com.fasterxml.jackson.databind.JsonNode
import com.google.api.gax.rpc.PermissionDeniedException
import com.google.api.gax.rpc.ServerStream
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.TableDefinition
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.storage.v1.BigQueryReadClient
import com.google.cloud.bigquery.storage.v1.ReadRowsRequest
import com.google.cloud.bigquery.storage.v1.ReadRowsResponse
import io.airbyte.cdk.Operation
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.CreateNoPartitions
import io.airbyte.cdk.read.DefaultJdbcStreamStateValue
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.bigquery.BigQueryClientFactory
import io.airbyte.integrations.source.bigquery.BigQueryLegacyStreamState
import io.airbyte.integrations.source.bigquery.BigQuerySourceConfiguration
import io.airbyte.integrations.source.bigquery.BigQueryTableTypes
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.core.annotation.Order
import io.micronaut.core.order.Ordered
import jakarta.inject.Singleton
import java.time.Clock
import java.time.Instant
import java.util.concurrent.atomic.AtomicBoolean

private val log = KotlinLogging.logger {}

/** The Storage Read API and native clients of a READ, built once from the configuration. */
@Singleton
class BigQueryReadApiClients(configuration: SourceConfiguration) {
    val config: BigQuerySourceConfiguration = configuration as BigQuerySourceConfiguration

    val readClient: BigQueryReadClient by lazy { BigQueryReadApiClientFactory.create(config) }

    val bigquery: BigQuery by lazy { BigQueryClientFactory.create(config) }
}

/**
 * [PartitionsCreatorFactory] of the Storage Read API read path.
 *
 * Accepts a [Stream] feed when the Read API is enabled (`use_storage_read_api`) and available (
 * [BigQueryReadApiAvailability]), the source is a base table (`TableDefinition.Type.TABLE`: views,
 * external tables, materialized views and snapshots cannot be read through the API) and the read is
 * a whole-table one: a `FULL_REFRESH`, or the initial snapshot of an `INCREMENTAL` stream (no
 * cursor checkpoint yet), which is pinned to one table version by BigQuery time travel and ends
 * with the same cursor checkpoint the query API path would emit. Everything else, including the
 * cursor deltas of later incremental syncs, is declined so that the `extract-jdbc` factory handles
 * it through the query API.
 */
@Singleton
class BigQueryReadApiPartitionsCreatorFactory(
    private val clients: BigQueryReadApiClients,
    private val constants: BigQueryReadApiConstants,
    private val tableTypes: BigQueryTableTypes,
    private val availability: BigQueryReadApiAvailability,
    private val registry: BigQueryReadApiProgressRegistry,
    private val resourceAcquirer: ResourceAcquirer,
    private val clock: Clock,
    private val snapshotQueries: BigQueryReadApiSnapshotQueries,
) : PartitionsCreatorFactory {

    private val config: BigQuerySourceConfiguration
        get() = clients.config

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is StreamFeedBootstrap) return null
        val stream: Stream = feedBootstrap.feed
        if (config.emulatorHost != null) {
            log.info {
                "'${stream.label}': the emulator has no usable Storage Read API; using the query API."
            }
            return null
        }
        if (!config.useStorageReadApi) {
            log.info { "'${stream.label}': 'use_storage_read_api' is off; using the query API." }
            return null
        }
        if (!availability.isAvailable) {
            log.info {
                "'${stream.label}': the Storage Read API is unavailable (${availability.reason}); " +
                    "using the query API."
            }
            return null
        }
        registry.get(stream.id)?.let { progress: BigQueryReadApiTableProgress ->
            if (progress.isComplete) {
                // A later round of the READ that finished the table: the terminal state is out and
                // must not be re-read by either path (the query API would read the cursor delta
                // from the checkpoint, inclusive, and duplicate the boundary rows).
                log.info { "'${stream.label}' was read to completion in this sync." }
                return CreateNoPartitions
            }
        }
        val cursor: EmittedField? =
            incrementalCursor(stream)
                ?: run {
                    if (stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL) return null
                    null
                }
        val facts: BigQueryTableTypes.TableFacts = tableFacts(stream.id) ?: return null
        if (facts.type != TableDefinition.Type.TABLE) {
            log.info {
                "'${stream.label}' is a ${facts.type}, which the Storage Read API cannot read; " +
                    "using the query API."
            }
            return null
        }
        BigQueryReadApiEligibility.unsupportedColumn(stream.fields)?.let { column: String ->
            log.info {
                "'${stream.label}': column '$column' has a type the Storage Read API path does " +
                    "not decode identically to the query API yet; using the query API."
            }
            return null
        }
        var plan: BigQueryReadApiPlan = plan(stream, feedBootstrap.currentState)
        (plan as? BigQueryReadApiPlan.Decline)?.let { declined ->
            log.info { "'${stream.label}': ${declined.reason}; using the query API." }
            return null
        }
        if (cursor != null && plan is BigQueryReadApiPlan.Fresh && plan.snapshot == null) {
            // Pin the initial snapshot: the table version the session reads and the cursor's
            // maximum at that same instant.
            val snapshotTime: Instant = snapshotQueries.pickSnapshotTime()
            val upperBound: JsonNode =
                snapshotQueries.cursorUpperBound(stream, cursor, snapshotTime)
                    ?: run {
                        log.info {
                            "'${stream.label}' has no '${cursor.id}' value; using the query API."
                        }
                        return null
                    }
            plan =
                BigQueryReadApiPlan.Fresh(
                    plan.reason,
                    BigQueryReadApiSnapshotSpec(
                        snapshotTime,
                        BigQueryReadApiState.CursorBound(cursor.id, upperBound),
                    ),
                )
        }
        if (plan is BigQueryReadApiPlan.Complete && cursor == null) return CreateNoPartitions
        return BigQueryReadApiPartitionsCreator(
            feedBootstrap,
            plan,
            config,
            constants,
            clients,
            registry,
            resourceAcquirer,
            terminalState = terminalStateFor(cursor, plan, feedBootstrap.currentState),
            numBytes = facts.numBytes,
            cursor = cursor,
            snapshotQueries = snapshotQueries,
        )
    }

    /**
     * The configured cursor of an incremental stream when this path can take its initial snapshot,
     * null (with a log line) when the stream is incremental but the cursor is missing or of a type
     * this path does not handle, and null silently for a full refresh.
     */
    private fun incrementalCursor(stream: Stream): EmittedField? {
        if (stream.configuredSyncMode != ConfiguredSyncMode.INCREMENTAL) return null
        val cursor: EmittedField? = stream.configuredCursor as? EmittedField
        if (cursor == null) {
            log.info {
                "'${stream.label}': incremental sync without a cursor column; using the query API."
            }
            return null
        }
        if (!BigQueryReadApiEligibility.isSupportedCursor(cursor)) {
            log.info {
                "'${stream.label}': cursor '${cursor.id}' has a type this path does not snapshot " +
                    "(${cursor.type::class.simpleName}); using the query API."
            }
            return null
        }
        return cursor
    }

    /**
     * What the readers emit once the table is read. For an incremental initial snapshot this is the
     * `extract-jdbc` toolkit's cursor checkpoint, `{"primary_key":{},"cursors":{"<cursor>": <max as
     * of the snapshot time>}}`, so that the next sync continues on the query API's delta path; for
     * a full refresh the toolkit's completed snapshot `{"primary_key":{},"cursors":{}}`.
     */
    private fun terminalStateFor(
        cursor: EmittedField?,
        plan: BigQueryReadApiPlan,
        state: OpaqueStateValue?,
    ): OpaqueStateValue {
        if (cursor == null) return DefaultJdbcStreamStateValue.snapshotCompleted
        val bound: BigQueryReadApiState.CursorBound? =
            when (plan) {
                is BigQueryReadApiPlan.Fresh -> plan.snapshot?.cursorUpperBound
                is BigQueryReadApiPlan.Resume -> plan.state.cursorUpperBound
                BigQueryReadApiPlan.Complete ->
                    BigQueryReadApiState.parseOrNull(state)?.cursorUpperBound
                is BigQueryReadApiPlan.Decline -> null
            }
        return if (bound == null) DefaultJdbcStreamStateValue.snapshotCompleted
        else DefaultJdbcStreamStateValue.cursorIncrementalCheckpoint(cursor, bound.value)
    }

    /** From the registry filled by the metadata querier at the start of the READ, else fetched. */
    private fun tableFacts(streamID: StreamIdentifier): BigQueryTableTypes.TableFacts? {
        tableTypes.factsOf(streamID)?.let {
            return it
        }
        val tableId = TableId.of(config.projectId, streamID.namespace, streamID.name)
        val table = clients.bigquery.getTable(tableId) ?: return null
        val facts =
            BigQueryTableTypes.TableFacts(
                table.getDefinition<TableDefinition>()?.type,
                table.numBytes,
                table.numRows?.toLong(),
            )
        tableTypes.register(streamID, facts)
        return facts
    }

    /**
     * Decides how to proceed from the stream's current state; see [BigQueryReadApiState]. For an
     * incremental stream, a state that already holds a cursor checkpoint (the toolkit's
     * `{"primary_key":..., "cursors":{...}}` with a non-empty `cursors`, or a legacy
     * `source-bigquery` state) is [BigQueryReadApiPlan.Decline]d: the deltas are the query API's.
     */
    fun plan(stream: Stream, state: OpaqueStateValue?): BigQueryReadApiPlan {
        val incremental: Boolean = stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL
        val cursor: EmittedField? = stream.configuredCursor as? EmittedField
        if (state == null || state.isNull) return BigQueryReadApiPlan.Fresh("no prior state")
        val readApiState: BigQueryReadApiState? = BigQueryReadApiState.parseOrNull(state)
        if (readApiState != null) {
            val spec: BigQueryReadApiSnapshotSpec? =
                if (incremental) {
                    val bound: BigQueryReadApiState.CursorBound? = readApiState.cursorUpperBound
                    val snapshotTime: Instant? = readApiState.snapshotTimeInstant
                    if (bound == null || snapshotTime == null || bound.cursor != cursor?.id) {
                        return BigQueryReadApiPlan.Fresh(
                            "a Storage Read API state without a snapshot time and an upper " +
                                "bound for cursor '${cursor?.id}'"
                        )
                    }
                    BigQueryReadApiSnapshotSpec(snapshotTime, bound, fromExpiredSession = true)
                } else null
            if (readApiState.isComplete) return BigQueryReadApiPlan.Complete
            val now: Instant = clock.instant()
            if (readApiState.isExpired(now)) {
                return BigQueryReadApiPlan.Fresh(
                    "the read session ${readApiState.session.name} expired at " +
                        "${readApiState.session.expiresAt}",
                    spec,
                )
            }
            return BigQueryReadApiPlan.Resume(readApiState)
        }
        if (isLegacyState(state)) {
            return if (incremental) {
                BigQueryReadApiPlan.Decline(
                    "a state persisted by the legacy source-bigquery connector; the query API " +
                        "resumes after its cursor"
                )
            } else BigQueryReadApiPlan.Fresh("legacy state")
        }
        if (isToolkitState(state)) {
            val pkEmpty: Boolean = state["primary_key"].isEmpty
            val cursorsEmpty: Boolean = state["cursors"].isEmpty
            if (!incremental) {
                if (pkEmpty && cursorsEmpty) return BigQueryReadApiPlan.Complete
                log.warn {
                    "'${stream.label}' has a query API snapshot in progress ($state); reading " +
                        "the table from the start on this path."
                }
                return BigQueryReadApiPlan.Fresh("a query API snapshot in progress")
            }
            if (!cursorsEmpty) {
                return BigQueryReadApiPlan.Decline(
                    "a cursor checkpoint exists; the query API reads the deltas"
                )
            }
            if (!pkEmpty) {
                return BigQueryReadApiPlan.Decline("a query API snapshot is in progress")
            }
            // A completed full refresh snapshot for a stream now configured as incremental: the
            // toolkit would reset it and start over too.
            return BigQueryReadApiPlan.Fresh("a completed full refresh snapshot")
        }
        log.warn {
            "'${stream.label}' has a state this read path does not understand ($state); " +
                "reading the table from the start."
        }
        return BigQueryReadApiPlan.Fresh("unrecognized state")
    }

    /** The `extract-jdbc` toolkit's `{"primary_key":{...},"cursors":{...}}`. */
    private fun isToolkitState(state: OpaqueStateValue): Boolean =
        state.isObject &&
            state.has("primary_key") &&
            state.has("cursors") &&
            state["primary_key"].isObject &&
            state["cursors"].isObject

    private fun isLegacyState(state: OpaqueStateValue): Boolean =
        runCatching { BigQueryLegacyStreamState.parseOrNull(state) }.getOrNull() != null
}

/**
 * Decides once per READ, before any feed starts, whether the service account may use the Storage
 * Read API: one read session on the first base table of the catalog, restricted to a single column
 * and a single read stream, and one `ReadRows` response. A `PERMISSION_DENIED` on either call marks
 * the API unavailable for the whole READ, and the connector falls back to the query API. Any other
 * failure keeps the API enabled; the partition readers report it with the table's context.
 */
@Singleton
@Requires(property = Operation.PROPERTY, value = "read")
class BigQueryReadApiAvailabilityProbe(
    private val clients: BigQueryReadApiClients,
    private val catalog: ConfiguredAirbyteCatalog,
    private val tableTypes: BigQueryTableTypes,
    private val availability: BigQueryReadApiAvailability,
    private val constants: BigQueryReadApiConstants,
) {
    private val done = AtomicBoolean(false)

    private val config: BigQuerySourceConfiguration
        get() = clients.config

    fun runOnce() {
        if (!done.compareAndSet(false, true)) return
        if (config.emulatorHost != null || !config.useStorageReadApi) {
            log.info {
                "The Storage Read API is not used (emulator: ${config.emulatorHost != null}, " +
                    "use_storage_read_api: ${config.useStorageReadApi}): tables are read through " +
                    "the standard query API."
            }
            return
        }
        val candidate: ConfiguredAirbyteStream =
            catalog.streams.firstOrNull { configured ->
                tableTypes.typeOf(StreamIdentifier.from(configured.stream)) ==
                    TableDefinition.Type.TABLE
            }
                ?: run {
                    log.info { "No base table in the catalog: the Storage Read API is not probed." }
                    return
                }
        val streamID: StreamIdentifier = StreamIdentifier.from(candidate.stream)
        val firstColumn: String? =
            candidate.stream.jsonSchema
                ?.get("properties")
                ?.fieldNames()
                ?.asSequence()
                ?.firstOrNull()
        try {
            val session: BigQueryReadSession =
                BigQueryReadSession.create(
                    client = clients.readClient,
                    jobProjectId = config.jobProjectId,
                    dataProjectId = config.projectId,
                    dataset = streamID.namespace ?: config.datasetId ?: config.projectId,
                    table = streamID.name,
                    selectedFields = firstColumn?.let { listOf(it) },
                    maxReadStreams = 1,
                    arrowBufferCompression = "NONE",
                )
            if (session.readStreams.isNotEmpty()) {
                val responses: ServerStream<ReadRowsResponse> =
                    clients.readClient
                        .readRowsCallable()
                        .call(
                            ReadRowsRequest.newBuilder()
                                .setReadStream(session.readStreams.first())
                                .setOffset(0L)
                                .build(),
                            BigQueryReadApiPartitionReader.callContext(constants),
                        )
                val iterator: Iterator<ReadRowsResponse> = responses.iterator()
                if (iterator.hasNext()) iterator.next()
                responses.cancel()
            }
            log.info {
                "The Storage Read API is available (probed on '${streamID}' in project " +
                    "'${config.jobProjectId}')."
            }
        } catch (e: PermissionDeniedException) {
            val reason: String = BigQueryReadSession.permissionDeniedMessage(config.jobProjectId)
            availability.markUnavailable(reason)
            log.warn(e) {
                "Falling back to the standard query API for every table, which is much slower on " +
                    "large tables. $reason"
            }
        } catch (e: Exception) {
            log.warn(e) {
                "The Storage Read API probe on '$streamID' failed for a reason other than a " +
                    "missing permission; the Read API stays enabled."
            }
        }
    }
}

/**
 * Registers the Read API factory ahead of the `extract-jdbc` one (the CDK tries the factories in
 * order and uses the first that accepts a feed) and runs the availability probe before the READ
 * starts its feeds.
 */
@Singleton
@Order(BigQueryReadApiPartitionsCreatorFactorySupplier.ORDER)
@Requires(property = Operation.PROPERTY, value = "read")
class BigQueryReadApiPartitionsCreatorFactorySupplier(
    private val factory: BigQueryReadApiPartitionsCreatorFactory,
    private val probe: BigQueryReadApiAvailabilityProbe,
) : PartitionsCreatorFactorySupplier<BigQueryReadApiPartitionsCreatorFactory>, Ordered {

    override fun get(): BigQueryReadApiPartitionsCreatorFactory {
        probe.runOnce()
        return factory
    }

    /** Same value as the annotation, for the code paths Micronaut orders by instance. */
    override fun getOrder(): Int = ORDER

    companion object {
        /**
         * Before the `extract-jdbc` supplier, which is neither annotated nor [Ordered] and so sorts
         * at [Ordered.LOWEST_PRECEDENCE] (Micronaut sorts the lowest value first). Verified in the
         * READ log: "Attempting bootstrap using class ...BigQueryReadApiPartitionsCreatorFactory"
         * precedes the JDBC factory for every feed.
         */
        const val ORDER: Int = -100
    }
}
