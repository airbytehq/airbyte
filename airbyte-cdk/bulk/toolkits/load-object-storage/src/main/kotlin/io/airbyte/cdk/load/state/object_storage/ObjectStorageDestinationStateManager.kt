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
import io.airbyte.cdk.load.state.DestinationState
import io.airbyte.cdk.load.state.DestinationStatePersister
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlinx.coroutines.flow.mapNotNull
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class ObjectStorageDestinationState(
    // (State -> (GenerationId -> (Key -> PartNumber)))
    @JsonProperty("generations_by_state")
    var generationMap: MutableMap<State, MutableMap<Long, MutableMap<String, Long>>> =
        mutableMapOf(),
) : DestinationState {
    enum class State {
        STAGED,
        FINALIZED
    }

    companion object {
        const val METADATA_GENERATION_ID_KEY = "ab-generation-id"

        fun metadataFor(stream: DestinationStream): Map<String, String> =
            mapOf(METADATA_GENERATION_ID_KEY to stream.generationId.toString())
    }

    @JsonIgnore private val accessLock = Mutex()

    suspend fun addObject(
        generationId: Long,
        key: String,
        partNumber: Long,
        isStaging: Boolean = false
    ) {
        val state = if (isStaging) State.STAGED else State.FINALIZED
        accessLock.withLock {
            generationMap
                .getOrPut(state) { mutableMapOf() }
                .getOrPut(generationId) { mutableMapOf() }[key] = partNumber
        }
    }

    suspend fun removeObject(generationId: Long, key: String, isStaging: Boolean = false) {
        val state = if (isStaging) State.STAGED else State.FINALIZED
        accessLock.withLock { generationMap[state]?.get(generationId)?.remove(key) }
    }

    suspend fun dropGenerationsBefore(minimumGenerationId: Long) {
        accessLock.withLock {
            State.entries.forEach { state ->
                (0 until minimumGenerationId).forEach { generationMap[state]?.remove(it) }
            }
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

    @get:JsonIgnore
    val generations: Sequence<Generation>
        get() =
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
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class ObjectStorageStagingPersister(
    private val client: ObjectStorageClient<*>,
    private val pathFactory: PathFactory
) : DestinationStatePersister<ObjectStorageDestinationState> {
    private val log = KotlinLogging.logger {}

    companion object {
        const val STATE_FILENAME = "__airbyte_state.json"
    }

    private fun keyFor(stream: DestinationStream): String =
        pathFactory.getStagingDirectory(stream).resolve(STATE_FILENAME).toString()

    override suspend fun load(stream: DestinationStream): ObjectStorageDestinationState {
        val key = keyFor(stream)
        try {
            log.info { "Loading destination state from $key" }
            return client.get(key) { inputStream ->
                Jsons.readTree(inputStream).let {
                    Jsons.treeToValue(it, ObjectStorageDestinationState::class.java)
                }
            }
        } catch (e: Exception) {
            log.info { "No destination state found at $key: $e" }
            return ObjectStorageDestinationState()
        }
    }

    override suspend fun persist(stream: DestinationStream, state: ObjectStorageDestinationState) {
        client.put(keyFor(stream), state.serializeToJsonBytes())
    }
}

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class ObjectStorageFallbackPersister(
    private val client: ObjectStorageClient<*>,
    private val pathFactory: PathFactory
) : DestinationStatePersister<ObjectStorageDestinationState> {
    override suspend fun load(stream: DestinationStream): ObjectStorageDestinationState {
        val prefix = pathFactory.prefix
        val matcher = pathFactory.getPathMatcher(stream)
        client
            .list(prefix)
            .mapNotNull { matcher.match(it.key) }
            .toList()
            .groupBy {
                client
                    .getMetadata(it.path)[ObjectStorageDestinationState.METADATA_GENERATION_ID_KEY]
                    ?.toLong()
                    ?: 0L
            }
            .mapValues { (_, matches) ->
                matches.associate { it.path to (it.partNumber ?: 0L) }.toMutableMap()
            }
            .toMutableMap()
            .let {
                return ObjectStorageDestinationState(
                    mutableMapOf(ObjectStorageDestinationState.State.FINALIZED to it)
                )
            }
    }

    override suspend fun persist(stream: DestinationStream, state: ObjectStorageDestinationState) {
        // No-op; state is persisted when the generation id is set on the object metadata
    }
}

@Factory
class ObjectStorageDestinationStatePersisterFactory<T : RemoteObject<*>>(
    private val client: ObjectStorageClient<T>,
    private val pathFactory: PathFactory
) {
    @Singleton
    @Secondary
    fun create(): DestinationStatePersister<ObjectStorageDestinationState> =
        if (pathFactory.supportsStaging) {
            ObjectStorageStagingPersister(client, pathFactory)
        } else {
            ObjectStorageFallbackPersister(client, pathFactory)
        }
}
