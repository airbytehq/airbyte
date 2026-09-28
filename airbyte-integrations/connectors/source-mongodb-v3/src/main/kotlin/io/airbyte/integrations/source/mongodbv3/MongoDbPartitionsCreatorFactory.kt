/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReader
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
 * stream), in which case no partitions are created.
 * - The `Global` feed: one [MongoDbCdcPartitionReader] that reads the replica-set change stream.
 */
@Singleton
class MongoDbPartitionsCreatorFactory(
    private val sharedState: MongoDbSharedState,
) : PartitionsCreatorFactory {

    private val streamStates = ConcurrentHashMap<StreamIdentifier, MongoDbStreamState>()

    /** Re-planning guard for the single Global (change-stream) feed. */
    private val cdcStarted = AtomicBoolean(false)

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        return when (feedBootstrap) {
            is GlobalFeedBootstrap ->
                if (cdcStarted.compareAndSet(false, true)) {
                    MongoDbCdcPartitionsCreator(sharedState, feedBootstrap)
                } else {
                    CreateNoPartitions
                }
            is StreamFeedBootstrap -> {
                val streamState: MongoDbStreamState =
                    streamStates.getOrPut(feedBootstrap.feed.id) {
                        MongoDbStreamState(sharedState, feedBootstrap)
                    }
                val id: StreamIdentifier = feedBootstrap.feed.id
                if (
                    snapshotAlreadyComplete(feedBootstrap) ||
                        sharedState.completedSnapshots.contains(id) ||
                        sharedState.snapshotYielded.contains(id)
                ) {
                    log.info {
                        "No snapshot partition for $id (complete, read, or yielded to CDC)."
                    }
                    CreateNoPartitions
                } else {
                    MongoDbSnapshotPartitionsCreator(streamState)
                }
            }
            else -> null
        }
    }

    /** An incremental stream whose persisted state marks the snapshot as done reads no records. */
    private fun snapshotAlreadyComplete(feedBootstrap: StreamFeedBootstrap): Boolean {
        val state = feedBootstrap.currentState ?: return false
        return try {
            MongoDbStreamStateValue.fromOpaqueStateValue(state).status ==
                MongoDbSnapshotStatus.COMPLETE
        } catch (e: Exception) {
            log.warn(e) {
                "Could not parse state for ${feedBootstrap.feed.id}; re-running snapshot."
            }
            false
        }
    }
}

@Singleton
class MongoDbPartitionsCreatorFactorySupplier(
    private val factory: MongoDbPartitionsCreatorFactory,
) : PartitionsCreatorFactorySupplier<MongoDbPartitionsCreatorFactory> {
    override fun get(): MongoDbPartitionsCreatorFactory = factory
}

/** A [PartitionsCreator] that yields no partitions, ending its feed immediately. */
data object CreateNoPartitions : PartitionsCreator {
    override fun tryAcquireResources() = PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN

    override suspend fun run(): List<PartitionReader> = emptyList()

    override fun releaseResources() {}
}
