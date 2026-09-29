/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.StreamFeedBootstrap
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
 */
@Singleton
class MongoDbPartitionsCreatorFactory(
    private val sharedState: MongoDbSharedState,
) : PartitionsCreatorFactory {

    private val streamStates = ConcurrentHashMap<StreamIdentifier, MongoDbStreamState>()

    /** Re-planning guard for the single Global (change-stream) feed. */
    private val cdcStarted = AtomicBoolean(false)

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? =
        when (feedBootstrap) {
            is GlobalFeedBootstrap ->
                if (cdcStarted.compareAndSet(false, true)) {
                    MongoDbPartitionsCreator(sharedState) {
                        MongoDbCdcPartitionReader(sharedState, feedBootstrap)
                    }
                } else {
                    CreateNoPartitions
                }
            is StreamFeedBootstrap -> {
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

    private fun snapshotIsDone(feedBootstrap: StreamFeedBootstrap): Boolean {
        val id: StreamIdentifier = feedBootstrap.feed.id
        val persistedComplete: Boolean =
            MongoDbStreamStateValue.fromOpaqueStateValueOrNull(feedBootstrap.currentState)
                ?.status == MongoDbSnapshotStatus.COMPLETE
        return persistedComplete ||
            id in sharedState.completedSnapshots ||
            id in sharedState.snapshotYielded
    }
}

@Singleton
class MongoDbPartitionsCreatorFactorySupplier(
    private val factory: MongoDbPartitionsCreatorFactory,
) : PartitionsCreatorFactorySupplier<MongoDbPartitionsCreatorFactory> {
    override fun get(): MongoDbPartitionsCreatorFactory = factory
}
