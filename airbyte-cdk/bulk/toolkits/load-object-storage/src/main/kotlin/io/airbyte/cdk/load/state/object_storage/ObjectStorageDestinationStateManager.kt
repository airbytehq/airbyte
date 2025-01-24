/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state.object_storage

import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.PathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StateObjectStorageLite
import io.airbyte.cdk.load.state.DestinationState
import io.airbyte.cdk.load.state.DestinationStatePersister
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState.Companion.OPTIONAL_ORDINAL_SUFFIX_PATTERN
import io.airbyte.cdk.load.util.readIntoClass
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.nio.file.Paths
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.flow.mapNotNull
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class ObjectStorageDestinationState(
    // (State -> (GenerationId -> (Key -> PartNumber)))
    @JsonProperty("generations_by_state")
    var generationMap:
        ConcurrentHashMap<State, ConcurrentHashMap<Long, ConcurrentHashMap<String, Long>>> =
        ConcurrentHashMap(),
    @JsonProperty("count_by_key") var countByKey: MutableMap<String, Long> = mutableMapOf()
) : DestinationState {
    enum class State {
        STAGED,
        FINALIZED
    }

    @JsonIgnore private val countByKeyLock = Mutex()

    companion object {
        const val METADATA_GENERATION_ID_KEY = "ab-generation-id"
        const val STREAM_NAMESPACE_KEY = "ab-stream-namespace"
        const val STREAM_NAME_KEY = "ab-stream-name"
        const val OPTIONAL_ORDINAL_SUFFIX_PATTERN = "(-[0-9]+)?"

        fun metadataFor(stream: DestinationStream): Map<String, String> =
            mapOf(METADATA_GENERATION_ID_KEY to stream.generationId.toString())
    }

    suspend fun addObject(
        generationId: Long,
        key: String,
        partNumber: Long?,
        isStaging: Boolean = false
    ) {
        val state = if (isStaging) State.STAGED else State.FINALIZED
        generationMap
            .getOrPut(state) { ConcurrentHashMap() }
            .getOrPut(generationId) { ConcurrentHashMap() }[key] = partNumber ?: 0L
    }

    suspend fun removeObject(generationId: Long, key: String, isStaging: Boolean = false) {
        val state = if (isStaging) State.STAGED else State.FINALIZED
        generationMap[state]?.get(generationId)?.remove(key)
    }

    suspend fun dropGenerationsBefore(minimumGenerationId: Long) {
        State.entries.forEach { state ->
            (0 until minimumGenerationId).forEach { generationMap[state]?.remove(it) }
        }
    }

    data class Generation(
        val isStaging: Boolean,
        val generationId: Long,
        val objects: List<ObjectAndPart>
    )

    data class ObjectAndPart(
        val key: String,
        val partNumber: Long,
    )

    suspend fun getGenerations(): Sequence<Generation> =
        generationMap.entries
            .asSequence()
            .map { (state, gens) ->
                val isStaging = state == State.STAGED
                gens.map { (generationId, objects) ->
                    Generation(
                        isStaging,
                        generationId,
                        objects.map { (key, partNumber) -> ObjectAndPart(key, partNumber) }
                    )
                }
            }
            .flatten()

    suspend fun getNextPartNumber(): Long =
        getGenerations().flatMap { it.objects }.map { it.partNumber }.maxOrNull()?.plus(1) ?: 0L

    /** Returns generationId -> objectAndPart for all staged objects that should be kept. */
    suspend fun getStagedObjectsToFinalize(
        minimumGenerationId: Long
    ): Sequence<Pair<Long, ObjectAndPart>> =
        getGenerations()
            .filter { it.isStaging && it.generationId >= minimumGenerationId }
            .flatMap { it.objects.map { obj -> it.generationId to obj } }

    /**
     * Returns generationId -> objectAndPart for all objects (staged and unstaged) that should be
     * cleaned up.
     */
    suspend fun getObjectsToDelete(minimumGenerationId: Long): Sequence<Pair<Long, ObjectAndPart>> {
        val (toKeep, toDrop) = getGenerations().partition { it.generationId >= minimumGenerationId }
        val keepKeys = toKeep.flatMap { it.objects.map { obj -> obj.key } }.toSet()
        return toDrop.asSequence().flatMap {
            it.objects.filter { obj -> obj.key !in keepKeys }.map { obj -> it.generationId to obj }
        }
    }

    /** Used to guarantee the uniqueness of a key */
    suspend fun ensureUnique(key: String): String {
        val ordinal =
            countByKeyLock.withLock {
                countByKey.merge(key, 0L) { old, new -> maxOf(old + 1, new) }
            }
                ?: 0L
        return if (ordinal > 0L) {
            "$key-$ordinal"
        } else {
            key
        }
    }
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class ObjectStorageStagingPersister(
    private val client: ObjectStorageClient<*>,
    private val pathFactory: PathFactory
) : DestinationStatePersister<ObjectStorageDestinationState> {
    private val log = KotlinLogging.logger {}
//    private val fallbackPersister = ObjectStorageFallbackPersister(client, pathFactory)

    companion object {
        const val STATE_FILENAME = "__airbyte_state.json"
    }

    private fun keyFor(stream: DestinationStream): String =
        Paths.get(pathFactory.getStagingDirectory(stream), STATE_FILENAME).toString()

    override suspend fun load(stream: DestinationStream): ObjectStorageDestinationState {
        val key = keyFor(stream)
        try {
            log.info { "Loading destination state from $key" }
            return client.get(key) { inputStream ->
                inputStream.readIntoClass(ObjectStorageDestinationState::class.java)
            }
        } catch (e: Exception) {
            log.info { "No destination state found at $key: $e; falling back to metadata search" }
//            return fallbackPersister.load(stream)
            throw e
        }
    }

    override suspend fun persist(stream: DestinationStream, state: ObjectStorageDestinationState) {
        client.put(keyFor(stream), state.serializeToJsonBytes())
    }
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class ObjectStorageFallbackPersister(
//    private val client: ObjectStorageClient<*>,
    private val client: StateObjectStorageLite<RemoteObject<*>>,
    private val pathFactory: PathFactory
) : DestinationStatePersister<ObjectStorageDestinationState> {
    private val log = KotlinLogging.logger {}
    override suspend fun load(stream: DestinationStream): ObjectStorageDestinationState {
        // Add a suffix matching an OPTIONAL -[0-9]+ ordinal
        val matcher =
            pathFactory.getPathMatcher(stream, suffixPattern = OPTIONAL_ORDINAL_SUFFIX_PATTERN)
        val longestUnambiguous =
            pathFactory.getLongestStreamConstantPrefix(stream, isStaging = false)
        log.info {
            "Searching path $longestUnambiguous (matching ${matcher.regex}) for destination state metadata"
        }
        val matches = client.list(longestUnambiguous).mapNotNull { matcher.match(it.key) }.toList()

        /* Initialize the unique key counts. */
        val countByKey = mutableMapOf<String, Long>()
        matches.forEach {
            val key = it.path.replace(Regex("-[0-9]+$"), "")
            val ordinal = it.customSuffix?.substring(1)?.toLongOrNull() ?: 0
            countByKey.merge(key, ordinal) { a, b -> maxOf(a, b) }
        }

        /* Build (generationId -> (key -> fileNumber)). */
        val generationIdToKeyAndFileNumber =
            ConcurrentHashMap(
                matches
                    .groupBy {
                        client
                            .getMetadata(it.path)[
                                ObjectStorageDestinationState.METADATA_GENERATION_ID_KEY]
                            ?.toLong()
                            ?: 0L
                    }
                    .mapValues { (_, matches) ->
                        ConcurrentHashMap(matches.associate { it.path to (it.partNumber ?: 0L) })
                    }
            )

        return ObjectStorageDestinationState(
            ConcurrentHashMap(
                mapOf(
                    ObjectStorageDestinationState.State.FINALIZED to generationIdToKeyAndFileNumber
                )
            ),
            countByKey
        )
    }

    override suspend fun persist(stream: DestinationStream, state: ObjectStorageDestinationState) {
        // No-op; state is persisted when the generation id is set on the object metadata
    }
}

@Factory
class ObjectStorageDestinationStatePersisterFactory<T : RemoteObject<*>>(
    private val client: StateObjectStorageLite<RemoteObject<*>>,
    private val pathFactory: PathFactory
) {
    @Singleton
    @Secondary
    fun create(): DestinationStatePersister<ObjectStorageDestinationState> =
//        if (pathFactory.supportsStaging) {
//            ObjectStorageStagingPersister(client, pathFactory)
//        } else {
            ObjectStorageFallbackPersister(client, pathFactory)
//        }
}
