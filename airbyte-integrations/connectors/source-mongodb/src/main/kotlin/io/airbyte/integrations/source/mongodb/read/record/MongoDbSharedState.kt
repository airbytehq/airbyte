/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.read.record

import com.mongodb.client.MongoClient
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.GlobalInputState
import io.airbyte.cdk.command.InputState
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.command.StreamInputState
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.airbyte.integrations.source.mongodb.MongoDbDiagnostics
import io.airbyte.integrations.source.mongodb.config.MongoDbClientFactory
import io.airbyte.integrations.source.mongodb.config.MongoDbSourceConfiguration
import io.airbyte.integrations.source.mongodb.read.snapshot.MongoDbIdTypes
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.annotation.PreDestroy
import jakarta.inject.Singleton
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import org.bson.BsonDocument
import org.bson.Document

private val log = KotlinLogging.logger {}

/** State shared by a READ's creators and readers: config, one [MongoClient], CDK resources. */
@Singleton
class MongoDbSharedState(
    val configuration: MongoDbSourceConfiguration,
    private val concurrencyResource: ConcurrencyResource,
    private val resourceAcquirer: ResourceAcquirer,
    private val inputState: InputState,
    /** Test hook: a snapshot batch size below the driver's maximum (`0` = maximum). */
    @Value("\${airbyte.connector.extract.mongodb.snapshot-batch-size:0}")
    private val snapshotBatchSizeHook: Int,
) {
    /**
     * Documents per snapshot batch: as many as fit the 16MB reply unless the test hook says less.
     */
    val snapshotBatchSize: Int =
        if (snapshotBatchSizeHook > 0) snapshotBatchSizeHook else Int.MAX_VALUE

    /** One client for the whole READ; MongoDB pools connections internally. */
    val client: MongoClient by lazy {
        MongoDbClientFactory.create(configuration).also {
            MongoDbDiagnostics.logConnection(it, configuration)
        }
    }

    /**
     * The checkpoint the READ was given for a full-refresh stream. Every checkpoint is written
     * inside the GLOBAL state message, but the CDK seeds a full-refresh stream's current state from
     * STREAM messages only, so the `Stream` feed starts with none; this reads it from where it was
     * written, so an interrupted full refresh continues after its last `_id`.
     */
    fun fullRefreshInputState(streamId: StreamIdentifier): OpaqueStateValue? =
        when (val state: InputState = inputState) {
            is GlobalInputState -> state.globalStreams[streamId] ?: state.nonGlobalStreams[streamId]
            is StreamInputState -> state.streams[streamId]
            else -> null
        }

    /**
     * Whether the server accepts `fullDocumentBeforeChange` (MongoDB 6.0+): a change stream opened
     * with it on an older server fails with an unrecognized-field error.
     */
    val supportsPreImages: Boolean by lazy {
        val buildInfo: Document = client.getDatabase("admin").runCommand(Document("buildInfo", 1))
        val major: Int = (buildInfo["versionArray"] as? List<*>)?.firstOrNull() as? Int ?: 0
        major >= 6
    }

    private val diagnosed: MutableSet<Any> = ConcurrentHashMap.newKeySet()

    /** Logs [MongoDbDiagnostics.oplogLine] once per READ, before the change stream is read. */
    fun logOplog(savedToken: BsonDocument?) {
        if (diagnosed.add(OPLOG_DIAGNOSTIC)) {
            MongoDbDiagnostics.logGuarded("the oplog statistics") {
                MongoDbDiagnostics.oplogLine(client, savedToken)
            }
        }
    }

    /**
     * Logs [MongoDbDiagnostics.collectionLine] once per stream per READ, as its snapshot starts;
     * true on that first call, so the reader can warn once about the collection.
     */
    fun logStreamStart(streamId: StreamIdentifier): Boolean {
        if (!diagnosed.add(streamId)) return false
        MongoDbDiagnostics.logGuarded("the statistics of ${streamId.namespace}.${streamId.name}") {
            MongoDbDiagnostics.collectionLine(client, streamId)
        }
        return true
    }

    /**
     * The BSON types of the collection's `_id`s ([MongoDbIdTypes.present]); empty when they could
     * not be read, which is a warning, never a failure: the answer only drives a warning.
     */
    fun idTypes(streamId: StreamIdentifier): List<String> =
        try {
            MongoDbIdTypes.present(
                client.getDatabase(streamId.namespace!!).getCollection(streamId.name),
            )
        } catch (e: Exception) {
            log.warn {
                "Could not read the _id types of ${streamId.namespace}.${streamId.name} " +
                    "(${e.message}); continuing."
            }
            emptyList()
        }

    /** Snapshot streams that finished in this READ, so the factory stops re-planning them. */
    val completedSnapshots: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /** Incremental snapshots that hit the WASS budget and yielded so the next sync drains CDC. */
    val snapshotYielded: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    /** When an incremental snapshot yields to CDC (WASS); fixed on first access for the READ. */
    val snapshotDeadline: Instant by lazy {
        Instant.now().plus(checkNotNull(configuration.maxSnapshotReadDuration))
    }

    fun tryAcquireResourcesForCreator(): AutoCloseable? = concurrencyResource.tryAcquire()

    fun tryAcquireResourcesForReader(
        resourceTypes: List<ResourceType>,
    ): Map<ResourceType, Resource.Acquired>? = resourceAcquirer.tryAcquire(resourceTypes)

    @PreDestroy
    fun close() {
        client.close()
    }

    private companion object {
        const val OPLOG_DIAGNOSTIC = "oplog"
    }
}
