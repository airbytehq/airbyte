/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.partition

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.CreateNoPartitions
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.integrations.source.mongodb.discover.MongoDbSourceMetadataQuerier.Companion.DATA_FIELD
import io.airbyte.integrations.source.mongodb.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import io.airbyte.integrations.source.mongodb.discover.schemaFieldTypesOf
import io.airbyte.integrations.source.mongodb.read.cdc.MongoDbCdcPartitionReader
import io.airbyte.integrations.source.mongodb.read.cdc.MongoDbCdcState
import io.airbyte.integrations.source.mongodb.read.cdc.MongoDbSchemaModePartitionReader
import io.airbyte.integrations.source.mongodb.read.record.MongoDbSharedState
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbSnapshotPartitionReader
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbSnapshotStatus
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbStreamStateValue
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean

private val log = KotlinLogging.logger {}

/**
 * Plans a READ: one snapshot partition per `Stream` feed (none once `COMPLETE`, finished in this
 * READ, or yielded to CDC) and one [MongoDbCdcPartitionReader] for the `Global` feed, which drains
 * the change stream up to the sync's target (none at all when no stream is incremental: the CDK
 * always creates the `Global` feed, but a full-refresh-only connection has nothing to read from
 * it). Completion is tracked in memory because the CDK re-asks after every round and a full-refresh
 * stream's terminal status is not `COMPLETE`. [validateSchemaMode] and
 * [validateSyncModeAgainstState] run first.
 */
@Singleton
class MongoDbPartitionsCreatorFactory(
    private val sharedState: MongoDbSharedState,
) : PartitionsCreatorFactory {

    private val schemaModeValidated = AtomicBoolean(false)

    /** The change stream is read once per READ: the reader drains it up to the sync's target. */
    private val cdcStarted = AtomicBoolean(false)

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator {
        if (schemaModeValidated.compareAndSet(false, true)) {
            validateSchemaMode(feedBootstrap)
        }
        return when (feedBootstrap) {
            is GlobalFeedBootstrap ->
                if (!cdcStarted.compareAndSet(false, true)) {
                    CreateNoPartitions
                } else if (feedBootstrap.feed.streams.isEmpty()) {
                    log.info { "No incremental stream: the change stream is not read." }
                    MongoDbPartitionsCreator(sharedState) {
                        MongoDbSchemaModePartitionReader(sharedState, feedBootstrap)
                    }
                } else {
                    MongoDbPartitionsCreator(sharedState) {
                        MongoDbCdcPartitionReader(sharedState, feedBootstrap)
                    }
                }
            is StreamFeedBootstrap -> {
                validateSyncModeAgainstState(feedBootstrap)
                failIfInitialLoadTimedOut(feedBootstrap)
                if (snapshotIsDone(feedBootstrap)) {
                    log.info {
                        "No snapshot partition for ${feedBootstrap.feed.id} (complete, read, or " +
                            "yielded to CDC)."
                    }
                    CreateNoPartitions
                } else {
                    MongoDbPartitionsCreator(sharedState) {
                        MongoDbSnapshotPartitionReader(sharedState, feedBootstrap)
                    }
                }
            }
        }
    }

    /**
     * WASS: once an incremental snapshot has yielded on `initial_load_timeout_hours` and no stream
     * has anything left to read in this sync, the sync ends with a transient error (its state is
     * already checkpointed), so the platform retries right away and the retry reads the change
     * stream first — as the JDBC sources and the legacy connector do — instead of waiting for the
     * next scheduled sync.
     */
    private fun failIfInitialLoadTimedOut(feedBootstrap: StreamFeedBootstrap) {
        if (sharedState.snapshotYielded.isEmpty()) return
        val pending: List<Stream> =
            feedBootstrap.feeds.filterIsInstance<Stream>().filter { stream ->
                stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL &&
                    stream.id !in sharedState.completedSnapshots &&
                    stream.id !in sharedState.snapshotYielded &&
                    MongoDbStreamStateValue.fromCurrentState(feedBootstrap.currentState(stream))
                        ?.status != MongoDbSnapshotStatus.COMPLETE
            }
        if (pending.isEmpty()) {
            throw TransientErrorException(
                "Initial load exceeded initial_load_timeout_hours before the snapshot of " +
                    "${sharedState.snapshotYielded.joinToString { it.toString() }} finished; " +
                    "progress is saved and the sync will retry, reading the change stream first.",
            )
        }
    }

    private fun snapshotIsDone(feedBootstrap: StreamFeedBootstrap): Boolean {
        val id = feedBootstrap.feed.id
        val persistedComplete: Boolean =
            MongoDbStreamStateValue.fromCurrentState(feedBootstrap.currentState)?.status ==
                MongoDbSnapshotStatus.COMPLETE
        return persistedComplete ||
            id in sharedState.completedSnapshots ||
            id in sharedState.snapshotYielded
    }

    /**
     * `schema_enforced` must agree between configuration, catalog (schemaless = exactly `_id` +
     * `data`) and saved state, or records of one shape would land in a destination expecting the
     * other.
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
                ?.schemaEnforced ?: configEnforced
        if (setOf(configEnforced, catalogEnforced, stateEnforced).size > 1) {
            val remedy =
                if (configEnforced == catalogEnforced) "Please refresh or clear your data."
                else "Please refresh the source schema, then refresh or clear the streams."
            throw ConfigErrorException(
                "Mismatch between schema enforcing mode in sync configuration ($configEnforced), " +
                    "catalog ($catalogEnforced) and saved state ($stateEnforced). $remedy",
            )
        }
    }

    private fun isSchemalessStream(stream: Stream): Boolean =
        schemaFieldTypesOf(stream).keys == setOf(ID_FIELD, DATA_FIELD)

    /** The saved snapshot status must be one the configured sync mode can produce. */
    private fun validateSyncModeAgainstState(feedBootstrap: StreamFeedBootstrap) {
        val stream: Stream = feedBootstrap.feed
        val current: OpaqueStateValue? =
            feedBootstrap.currentState
                ?: if (stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH)
                    sharedState.fullRefreshInputState(stream.id)
                else null
        val saved: MongoDbSnapshotStatus =
            MongoDbStreamStateValue.fromCurrentState(current)?.status ?: return
        val allowed: Set<MongoDbSnapshotStatus> =
            when (stream.configuredSyncMode) {
                ConfiguredSyncMode.INCREMENTAL ->
                    setOf(MongoDbSnapshotStatus.IN_PROGRESS, MongoDbSnapshotStatus.COMPLETE)
                ConfiguredSyncMode.FULL_REFRESH -> setOf(MongoDbSnapshotStatus.FULL_REFRESH)
            }
        if (saved !in allowed) {
            throw ConfigErrorException(
                "Stream ${stream.name} is ${stream.configuredSyncMode} but the saved status $saved " +
                    "doesn't match. Please refresh or clear this stream",
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
