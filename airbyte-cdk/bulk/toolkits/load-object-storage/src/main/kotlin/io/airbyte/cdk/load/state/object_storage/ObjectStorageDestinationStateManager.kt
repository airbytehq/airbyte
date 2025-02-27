/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state.object_storage

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.PathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.state.DestinationState
import io.airbyte.cdk.load.state.DestinationStatePersister
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.flow.filter
import kotlinx.coroutines.flow.fold
import kotlinx.coroutines.flow.mapNotNull
import kotlinx.coroutines.flow.toList

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class ObjectStorageDestinationState(
    private val stream: DestinationStream,
    private val client: ObjectStorageClient<*>,
    private val pathFactory: PathFactory,
) : DestinationState {
    private val log = KotlinLogging.logger {}

    private val countByKey: ConcurrentHashMap<String, AtomicLong> = ConcurrentHashMap()
    private val fileNumbersByPath: ConcurrentHashMap<String, AtomicLong> = ConcurrentHashMap()
    private val matcher =
        pathFactory.getPathMatcher(stream, suffixPattern = OPTIONAL_ORDINAL_SUFFIX_PATTERN)

    companion object {
        const val METADATA_GENERATION_ID_KEY = "ab-generation-id"
        const val OPTIONAL_ORDINAL_SUFFIX_PATTERN = "(-[0-9]+)?"

        fun metadataFor(stream: DestinationStream): Map<String, String> =
            mapOf(METADATA_GENERATION_ID_KEY to stream.generationId.toString())
    }

    /**
     * Returns (generationId, object) for all objects that should be cleaned up.
     *
     * "should be cleaned up" means
     * * stream.shouldBeTruncatedAtEndOfSync() is true
     * * object's generation id exists and is less than stream.minimumGenerationId
     */
    suspend fun getObjectsToDelete(): List<Pair<Long, RemoteObject<*>>> {
        if (!stream.shouldBeTruncatedAtEndOfSync()) {
            return emptyList()
        }

        val prefix = pathFactory.getLongestStreamConstantPrefix(stream)
        log.info {
            "Searching $prefix for objects to delete (minGenId=${stream.minimumGenerationId}; matcher=${matcher.regex})"
        }

        return client
            .list(prefix)
            .filter { matcher.match(it.key) != null }
            .toList() // Force the list call to complete before initiating metadata calls
            .mapNotNull { obj ->
                val generationId =
                    client.getMetadata(obj.key)[METADATA_GENERATION_ID_KEY]?.toLongOrNull() ?: 0L
                if (generationId < stream.minimumGenerationId) {
                    Pair(generationId, obj)
                } else {
                    null
                }
            }
    }

    /**
     * Ensures the key is unique by appending `-${max_suffix + 1}` if there is a conflict. If the
     * key is unique, it is returned as-is.
     */
    suspend fun ensureUnique(key: String): String {
        val count =
            countByKey
                .getOrPut(key) {
                    client
                        .list(key)
                        .mapNotNull { matcher.match(it.key) }
                        .fold(-1L) { acc, match ->
                            maxOf(match.customSuffix?.removePrefix("-")?.toLongOrNull() ?: 0L, acc)
                        }
                        .let { AtomicLong(it) }
                }
                .incrementAndGet()

        return if (count == 0L) {
            key
        } else {
            "$key-$count"
        }
    }

    /** Returns a shared atomic long referencing the max {part_number} for any given path. */
    suspend fun getPartIdCounter(path: String): AtomicLong {
        return fileNumbersByPath.getOrPut(path) {
            client
                .list(path)
                .mapNotNull { matcher.match(it.key) }
                .fold(-1L) { acc, match -> maxOf(match.partNumber ?: 0L, acc) }
                .let { AtomicLong(it) }
        }
    }
}

/**
 * Note: there's no persisting yet. This will require either a client-provided path to store data or
 * a guaranteed sortable set of file names so that we can send the high watermark to the platform.
 */
@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
@Singleton
class ObjectStorageFallbackPersister(
    private val client: ObjectStorageClient<*>,
    private val pathFactory: PathFactory
) : DestinationStatePersister<ObjectStorageDestinationState> {
    override suspend fun load(stream: DestinationStream): ObjectStorageDestinationState {
        return ObjectStorageDestinationState(stream, client, pathFactory)
    }

    override suspend fun persist(stream: DestinationStream, state: ObjectStorageDestinationState) {
        // No-op; state is persisted when the generation id is set on the object metadata
    }
}
