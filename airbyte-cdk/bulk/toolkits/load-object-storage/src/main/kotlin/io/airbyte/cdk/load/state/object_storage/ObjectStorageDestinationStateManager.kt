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
import io.airbyte.cdk.load.state.DestinationState
import io.airbyte.cdk.load.state.DestinationStatePersister
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class ObjectStorageDestinationState(
    @JsonProperty("generations_by_state")
    var generationMap: MutableMap<State, MutableMap<Long, MutableMap<String, Long>>> =
        mutableMapOf(),
) : DestinationState {
    enum class State {
        STAGED,
        FINALIZED
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

@Factory
class ObjectStorageDestinationStatePersisterFactory(
    private val client: ObjectStorageClient<*>,
    private val pathFactory: PathFactory
) {
    @Singleton
    @Secondary
    fun create(): DestinationStatePersister<ObjectStorageDestinationState> =
        ObjectStorageStagingPersister(client, pathFactory)
}
