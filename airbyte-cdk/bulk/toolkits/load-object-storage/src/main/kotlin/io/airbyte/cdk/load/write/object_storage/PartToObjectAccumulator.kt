/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.PartBookkeeper
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.object_storage.IncompletePartialUpload
import io.airbyte.cdk.load.message.object_storage.LoadablePart
import io.airbyte.cdk.load.message.object_storage.LoadedObject
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.CompletableDeferred

@SuppressFBWarnings("NP_NONNULL_PARAM_VIOLATION", justification = "Kotlin async continuation")
class PartToObjectAccumulator<T : RemoteObject<*>>(
    private val stream: DestinationStream,
    private val client: ObjectStorageClient<T>,
) {
    private val log = KotlinLogging.logger {}

    data class UploadInProgress<T : RemoteObject<*>>(
        val streamingUpload: CompletableDeferred<StreamingUpload<*>> = CompletableDeferred(),
        val partBookkeeper: PartBookkeeper = PartBookkeeper(),
        val hasStarted: AtomicBoolean = AtomicBoolean(false),
    )
    private val uploadsInProgress = ConcurrentHashMap<String, UploadInProgress<T>>()

    suspend fun processBatch(batch: Batch): Batch {
        batch as LoadablePart
        val upload = uploadsInProgress.getOrPut(batch.part.key) { UploadInProgress() }
        if (upload.hasStarted.setOnce()) {
            // Start the upload if we haven't already. Note that the `complete`
            // here refers to the completable deferred, not the streaming upload.
            val metadata = ObjectStorageDestinationState.metadataFor(stream)
            val streamingUpload = client.startStreamingUpload(batch.part.key, metadata)
            upload.streamingUpload.complete(streamingUpload)
        }
        val streamingUpload = upload.streamingUpload.await()

        log.info {
            "Processing loadable part ${batch.part.partIndex} of ${batch.part.key} (size=${batch.part.bytes?.size}; final=${batch.part.isFinal})"
        }

        // Upload provided bytes and update indexes.
        if (batch.part.bytes != null) {
            streamingUpload.uploadPart(batch.part.bytes, batch.part.partIndex)
        }
        upload.partBookkeeper.add(batch.part)
        if (upload.partBookkeeper.isComplete) {
            val obj = streamingUpload.complete()
            uploadsInProgress.remove(batch.part.key)

            log.info { "Completed upload of ${obj.key}" }
            return LoadedObject(remoteObject = obj, fileNumber = batch.part.fileNumber)
        } else {
            return IncompletePartialUpload(batch.part.key)
        }
    }
}
