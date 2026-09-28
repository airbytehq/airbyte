/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.mongodb.client.MongoCollection
import com.mongodb.client.model.Sorts
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.cdk.read.UnlimitedTimePartitionReader
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import org.bson.Document

private val log = KotlinLogging.logger {}

/**
 * Reads a whole collection in one pass, ordered by `_id` ascending, and emits every document as a
 * record. This is the v1 initial-snapshot reader; splitting a collection into concurrent `_id`
 * ranges is a deliberate later optimization (see SKILL.md, Phase 1 "Concurrency").
 *
 * It is an [UnlimitedTimePartitionReader] because it does not yet resume mid-collection: it reads
 * to the end and checkpoints once, with the terminal snapshot status and the last `_id` seen.
 */
class MongoDbSnapshotPartitionReader(
    private val streamState: MongoDbStreamState,
) : UnlimitedTimePartitionReader {

    private val sharedState: MongoDbSharedState = streamState.sharedState
    private val stream: Stream = streamState.stream
    private val converter = MongoDbRecordConverter(sharedState.configuration.schemaEnforced)

    private val numRecords = AtomicLong(0L)
    private val lastId = AtomicReference<Any?>(null)

    interface AcquiredResource : AutoCloseable {
        val resource: Resource.Acquired?
    }
    private val acquiredResources = AtomicReference<Map<ResourceType, AcquiredResource>>()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resources: Map<ResourceType, AcquiredResource> =
            sharedState.tryAcquireResourcesForReader(listOf(ResourceType.RESOURCE_DB_CONNECTION))
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        val recordConsumer: StreamRecordConsumer =
            streamState.streamFeedBootstrap.streamRecordConsumers()[stream.id]
                ?: throw IllegalStateException("No record consumer for stream ${stream.id}")
        val collection: MongoCollection<Document> =
            sharedState.client.getDatabase(stream.namespace!!).getCollection(stream.name)
        log.info { "Reading collection ${stream.namespace}.${stream.name} ordered by _id." }
        collection
            .find()
            .sort(Sorts.ascending(MongoDbSourceMetadataQuerier.ID_FIELD))
            .cursor()
            .use { cursor ->
                while (cursor.hasNext()) {
                    currentCoroutineContext().ensureActive()
                    val document: Document = cursor.next()
                    val (payload: NativeRecordPayload, rawId: Any?) =
                        converter.toPayloadWithId(document)
                    recordConsumer.accept(payload, null)
                    lastId.set(rawId)
                    numRecords.incrementAndGet()
                }
            }
        log.info {
            "Finished collection ${stream.namespace}.${stream.name}: ${numRecords.get()} records."
        }
    }

    override fun checkpoint(): PartitionReadCheckpoint =
        PartitionReadCheckpoint(
            MongoDbStreamStateValue.fromLastId(lastId.get(), streamState.terminalStatus)
                .toOpaqueStateValue(),
            numRecords.get(),
        )

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
    }
}
