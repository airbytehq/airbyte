/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.mongodbv3.MongoDbSourceMetadataQuerier.Companion.DATA_FIELD
import io.airbyte.integrations.source.mongodbv3.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean

private val log = KotlinLogging.logger {}

/**
 * Plans a READ into partitions.
 * - `Stream` feeds: one snapshot partition per collection, unless the collection's persisted state
 * says its snapshot is already `COMPLETE` (an incremental stream that has moved to the change
 * stream), it finished in this READ, or it yielded to CDC (WASS) — in which case no partitions.
 * - The `Global` feed: one [MongoDbCdcPartitionReader] that reads the replica-set change stream.
 *
 * The CDK re-asks the factory after every round, so completion is tracked in memory for this READ
 * (see `MongoDbSharedState.completedSnapshots`); relying on the state alone would re-read a
 * full-refresh stream forever, since its terminal status is not `COMPLETE`.
 *
 * Before planning anything it runs the legacy connector's two consistency guards, turning what
 * would otherwise be silent shape corruption or a confusing failure into an actionable config
 * error:
 * - the `schema_enforced` mode must agree between the configuration, the configured catalog and the
 * saved CDC state ([validateSchemaMode]);
 * - a stream's configured sync mode must agree with its saved snapshot status (
 * [validateSyncModeAgainstState]).
 */
@Singleton
class MongoDbPartitionsCreatorFactory(
    private val sharedState: MongoDbSharedState,
) : PartitionsCreatorFactory {

    private val streamStates = ConcurrentHashMap<StreamIdentifier, MongoDbStreamState>()

    /** Re-planning guard for the single Global (change-stream) feed. */
    private val cdcStarted = AtomicBoolean(false)

    private val schemaModeValidated = AtomicBoolean(false)

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (schemaModeValidated.compareAndSet(false, true)) {
            validateSchemaMode(feedBootstrap)
        }
        return when (feedBootstrap) {
            is GlobalFeedBootstrap ->
                if (cdcStarted.compareAndSet(false, true)) {
                    MongoDbPartitionsCreator(sharedState) {
                        MongoDbCdcPartitionReader(sharedState, feedBootstrap)
                    }
                } else {
                    CreateNoPartitions
                }
            is StreamFeedBootstrap -> {
                validateSyncModeAgainstState(feedBootstrap)
                val id: StreamIdentifier = feedBootstrap.feed.id
                if (snapshotIsDone(feedBootstrap)) {
                    log.info {
                        "No snapshot partition for $id (complete, read, or yielded to CDC)."
                    }
                    CreateNoPartitions
                } else {
                    val streamState: MongoDbStreamState =
                        streamStates.getOrPut(id) { MongoDbStreamState(sharedState, feedBootstrap) }
                    MongoDbPartitionsCreator(sharedState) {
                        MongoDbSnapshotPartitionReader(streamState)
                    }
                }
            }
            else -> null
        }
    }

    private fun snapshotIsDone(feedBootstrap: StreamFeedBootstrap): Boolean {
        val id: StreamIdentifier = feedBootstrap.feed.id
        val persistedComplete: Boolean =
            MongoDbStreamStateValue.fromOpaqueStateValueOrNull(feedBootstrap.currentState)
                ?.status == MongoDbSnapshotStatus.COMPLETE
        return persistedComplete ||
            id in sharedState.completedSnapshots ||
            id in sharedState.snapshotYielded
    }

    /**
     * `schema_enforced` must agree between the configuration, the configured catalog (a schemaless
     * catalog has exactly `_id` + `data` per stream) and the saved CDC state. Toggling it without a
     * reset would emit records in one shape into a destination expecting the other.
     */
    private fun validateSchemaMode(feedBootstrap: FeedBootstrap<*>) {
        val streams: List<Stream> = feedBootstrap.feeds.filterIsInstance<Stream>()
        if (streams.isEmpty()) return
        val configEnforced: Boolean = sharedState.configuration.schemaEnforced
        val catalogEnforced: Boolean = !streams.all(::isSchemalessStream)
        val stateEnforced: Boolean =
            feedBootstrap.feeds
                .filterIsInstance<Global>()
                .firstNotNullOfOrNull {
                    MongoDbCdcState.fromOpaqueStateValue(feedBootstrap.currentState(it))
                }
                ?.schemaEnforced
                ?: configEnforced
        if (setOf(configEnforced, catalogEnforced, stateEnforced).size > 1) {
            val remedy =
                if (configEnforced == catalogEnforced) "Please reset your data."
                else "Please refresh source schema and reset streams."
            throw ConfigErrorException(
                "Mismatch between schema enforcing mode in sync configuration ($configEnforced), " +
                    "catalog ($catalogEnforced) and saved state ($stateEnforced). $remedy",
            )
        }
    }

    private fun isSchemalessStream(stream: Stream): Boolean =
        schemaFieldTypesOf(stream).keys == setOf(ID_FIELD, DATA_FIELD)

    /**
     * A stream's saved snapshot status must be one its configured sync mode can produce:
     * `INCREMENTAL` ↔ `IN_PROGRESS`/`COMPLETE`, `FULL_REFRESH` ↔ `FULL_REFRESH`. Anything else
     * means the sync mode was changed without a reset.
     */
    private fun validateSyncModeAgainstState(feedBootstrap: StreamFeedBootstrap) {
        val stream: Stream = feedBootstrap.feed
        val saved: MongoDbSnapshotStatus =
            MongoDbStreamStateValue.fromOpaqueStateValueOrNull(feedBootstrap.currentState)?.status
                ?: return
        val allowed: Set<MongoDbSnapshotStatus> =
            when (stream.configuredSyncMode) {
                ConfiguredSyncMode.INCREMENTAL ->
                    setOf(MongoDbSnapshotStatus.IN_PROGRESS, MongoDbSnapshotStatus.COMPLETE)
                ConfiguredSyncMode.FULL_REFRESH -> setOf(MongoDbSnapshotStatus.FULL_REFRESH)
            }
        if (saved !in allowed) {
            throw ConfigErrorException(
                "Stream ${stream.name} is ${stream.configuredSyncMode} but the saved status $saved " +
                    "doesn't match. Please reset this stream",
            )
        }
    }
}

@Singleton
class MongoDbPartitionsCreatorFactorySupplier(
    private val factory: MongoDbPartitionsCreatorFactory,
) : PartitionsCreatorFactorySupplier<MongoDbPartitionsCreatorFactory> {
    override fun get(): MongoDbPartitionsCreatorFactory = factory
}
