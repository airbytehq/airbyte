/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.OutputStream

@Singleton
@Secondary
class ObjectStorageStreamLoaderFactory<T : RemoteObject<*>, U : OutputStream>(
    private val client: ObjectStorageClient<T>,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
) {
    fun create(stream: DestinationStream): StreamLoader {
        return ObjectStorageStreamLoader(
            stream,
            client,
            destinationStateManager,
        )
    }
}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION", "NP_NULL_ON_SOME_PATH_FROM_RETURN_VALUE"],
    justification = "Kotlin async continuation"
)
class ObjectStorageStreamLoader<T : RemoteObject<*>>(
    override val stream: DestinationStream,
    private val client: ObjectStorageClient<T>,
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState>,
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    override suspend fun close(hadNonzeroRecords: Boolean, streamFailure: StreamProcessingFailed?) {
        if (streamFailure != null) {
            log.info { "Sync failed, persisting destination state for next run" }
        } else if (stream.shouldBeTruncatedAtEndOfSync()) {
            log.info { "Truncate sync succeeded, Removing old files" }
            val state = destinationStateManager.getState(stream)

            state.getObjectsToDelete().forEach { (generationId, objectAndPart) ->
                log.info {
                    "Deleting old object for generation $generationId: ${objectAndPart.key}"
                }
                client.delete(objectAndPart.key)
            }

            log.info { "Persisting state" }
        }
        destinationStateManager.persistState(stream)
    }
}
