/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.read.partition

import io.airbyte.cdk.ConfigErrorException
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
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbSourceMetadataQuerier.Companion.DATA_FIELD
import io.airbyte.integrations.source.mongodbv3.discover.MongoDbSourceMetadataQuerier.Companion.ID_FIELD
import io.airbyte.integrations.source.mongodbv3.discover.schemaFieldTypesOf
import io.airbyte.integrations.source.mongodbv3.read.cdc.MongoDbCdcPartitionReader
import io.airbyte.integrations.source.mongodbv3.read.cdc.MongoDbCdcState
import io.airbyte.integrations.source.mongodbv3.read.record.MongoDbSharedState
import io.airbyte.integrations.source.mongodbv3.read.snapshot.MongoDbSnapshotPartitionReader
import io.airbyte.integrations.source.mongodbv3.read.snapshot.MongoDbSnapshotStatus
import io.airbyte.integrations.source.mongodbv3.read.snapshot.MongoDbStreamStateValue
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicBoolean

private val log = KotlinLogging.logger {}

/**
 * Plans a READ: one snapshot partition per `Stream` feed (none once `COMPLETE`, finished in this
 * READ, or yielded to CDC) and one [MongoDbCdcPartitionReader] for the `Global` feed. Completion is
 * tracked in memory because the CDK re-asks after every round and a full-refresh stream's terminal
 * status is not `COMPLETE`. [validateSchemaMode] and [validateSyncModeAgainstState] run first.
 */
@Singleton
class MongoDbPartitionsCreatorFactory(
    private val sharedState: MongoDbSharedState,
) : PartitionsCreatorFactory {

    /** Re-planning guard for the single Global (change-stream) feed. */
    private val cdcStarted = AtomicBoolean(false)

    private val schemaModeValidated = AtomicBoolean(false)

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator {
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

    /** The saved snapshot status must be one the configured sync mode can produce. */
    private fun validateSyncModeAgainstState(feedBootstrap: StreamFeedBootstrap) {
        val stream: Stream = feedBootstrap.feed
        val saved: MongoDbSnapshotStatus =
            MongoDbStreamStateValue.fromCurrentState(feedBootstrap.currentState)?.status ?: return
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
