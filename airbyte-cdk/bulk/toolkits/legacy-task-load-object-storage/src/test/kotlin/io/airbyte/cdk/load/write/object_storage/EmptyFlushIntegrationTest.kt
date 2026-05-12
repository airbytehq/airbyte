/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.MockObjectStorageClient
import io.airbyte.cdk.load.MockObjectStreamingUpload
import io.airbyte.cdk.load.MockRemoteObject
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoader
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.pipline.object_storage.UploadsInProgress
import io.mockk.coEvery
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

/**
 * Drives an "empty flush" (the low-volume / zero-record flush timer scenario) end-to-end through
 * the real [ObjectLoaderPartLoader] and [ObjectLoaderUploadCompleter] with the in-memory
 * [MockObjectStorageClient]. This is the integration point that pure-mock unit tests on each
 * component miss: it exercises the fact that [ObjectLoaderPartLoader.start] always initiates a
 * streaming upload before we know whether any non-empty part will arrive, and verifies that
 * [ObjectLoaderUploadCompleter] then explicitly aborts that upload instead of leaving it
 * dangling.
 */
class EmptyFlushIntegrationTest {
    private val streamDescriptor = DestinationStream.Descriptor("test", "stream")
    private val destinationConfig = object : DestinationConfiguration() {}

    private fun newLoader():
        Pair<MockObjectStorageClient, ObjectLoaderPartLoader<MockRemoteObject>> {
        val stream: DestinationStream = mockk(relaxed = true)
        every { stream.mappedDescriptor } returns streamDescriptor

        val catalog: DestinationCatalog = mockk(relaxed = true)
        coEvery { catalog.getStream(streamDescriptor) } returns stream

        val client = MockObjectStorageClient()
        val loader =
            ObjectLoaderPartLoader(client, catalog, UploadsInProgress(), destinationConfig)
        return client to loader
    }

    private fun newCompleter(): ObjectLoaderUploadCompleter<MockRemoteObject> {
        val objectLoader: ObjectLoader = mockk(relaxed = true)
        every { objectLoader.stateAfterUpload } returns BatchState.PERSISTED
        return ObjectLoaderUploadCompleter(objectLoader)
    }

    /**
     * Build a [ObjectLoaderPartFormatter.FormattedPart] using the real [PartFactory] so the
     * resulting part index matches what the formatter would produce in the empty-flush case.
     * For zero records, only `nextPart(null, isFinal = true)` is called → partIndex = 0
     * (`PartFactory` only pre-increments when bytes != null). That `partIndex = 0` is the
     * invariant `PartBookkeeper.isComplete` relies on: `finalIndex == partIndexes.size == 0`.
     */
    private fun emptyFinalFormattedPart(key: String): ObjectLoaderPartFormatter.FormattedPart {
        val factory = PartFactory(key = key, fileNumber = 0L)
        val part = factory.nextPart(bytes = null, isFinal = true)
        return ObjectLoaderPartFormatter.FormattedPart(part)
    }

    private fun nonEmptyFinalFormattedPart(
        key: String,
        bytes: ByteArray,
    ): ObjectLoaderPartFormatter.FormattedPart {
        val factory = PartFactory(key = key, fileNumber = 0L)
        val part = factory.nextPart(bytes = bytes, isFinal = true)
        return ObjectLoaderPartFormatter.FormattedPart(part)
    }

    @Suppress("UNCHECKED_CAST")
    private fun loadedPartFromLoaderOutput(
        result: Any?,
    ): ObjectLoaderPartLoader.LoadedPart<MockRemoteObject> {
        assertTrue(result is IntermediateOutput<*, *>, "Loader should emit IntermediateOutput")
        return (result as IntermediateOutput<*, *>).output as
            ObjectLoaderPartLoader.LoadedPart<MockRemoteObject>
    }

    @Suppress("UNCHECKED_CAST")
    private fun uploadResultFromCompleterOutput(
        result: Any?,
    ): ObjectLoaderUploadCompleter.UploadResult<MockRemoteObject> {
        assertTrue(result is FinalOutput<*, *>, "Completer should emit FinalOutput")
        return (result as FinalOutput<*, *>).output as
            ObjectLoaderUploadCompleter.UploadResult<MockRemoteObject>
    }

    /**
     * The low-volume flush scenario: the formatter emits a single empty final part (bytes=null,
     * isFinal=true, partIndex=0) because the writer buffer is empty when the flush timer fires.
     *
     * The expected behavior is:
     * 1. The loader starts the streaming upload (it has to: it doesn't yet know whether a real
     *    part is coming).
     * 2. The loader does NOT call uploadPart (because bytes is null).
     * 3. The loader emits a LoadedPart marked empty=true, isFinal=true.
     * 4. The completer sees the empty final part, recognizes the bookkeeper is complete + empty,
     *    skips complete(), and calls abort() to release the server-side multipart upload.
     * 5. No object is created in storage; downstream receives remoteObject = null.
     */
    @Test
    fun `empty flush aborts the in-flight upload and creates no object`() = runTest {
        val (client, loader) = newLoader()
        val completer = newCompleter()

        val key = "stream/empty-flush"
        val emptyFinalPart = emptyFinalFormattedPart(key)

        // Drive the loader
        val loaderState =
            loader.start(ObjectKey(streamDescriptor, key), emptyFinalPart.part.partIndex)
        val loadedPart = loadedPartFromLoaderOutput(loader.accept(emptyFinalPart, loaderState))
        assertTrue(loadedPart.empty, "Loaded part should be marked empty")
        assertTrue(loadedPart.isFinal, "Loaded part should be marked final")

        // The loader.start() kicks off client.startStreamingUpload in an async{} block.
        // Awaiting the deferred guarantees the upload object exists and gives us a handle to
        // verify behavior on it later. This also mirrors how the completer awaits it before
        // either completing or aborting.
        val mockUpload = loadedPart.upload.await() as MockObjectStreamingUpload
        assertFalse(mockUpload.completeCalled, "complete() must not be called yet")
        assertFalse(mockUpload.abortCalled, "abort() must not be called yet")

        // Drive the completer
        val completerState =
            completer.start(ObjectKey(streamDescriptor, key), emptyFinalPart.part.partIndex)
        val uploadResult =
            uploadResultFromCompleterOutput(completer.accept(loadedPart, completerState))

        // Downstream contract: null remoteObject signals "no file was created"
        assertNull(uploadResult.remoteObject, "remoteObject must be null on empty flush")
        assertEquals(BatchState.PERSISTED, uploadResult.state)

        // The crux of the fix: abort() was called, complete() was not, and no object exists
        // in storage.
        assertFalse(mockUpload.completeCalled, "complete() must NOT be called on empty flush")
        assertTrue(
            mockUpload.abortCalled,
            "abort() MUST be called on empty flush to release the in-flight multipart upload",
        )
        assertThrows(IllegalArgumentException::class.java) {
            // MockObjectStorageClient.get(key) throws IllegalArgumentException when the key
            // does not exist — confirming no object was persisted.
            client.get(key)
        }
    }

    /**
     * Sanity check: when a non-empty part flows through the same pipeline, the upload IS
     * completed and abort() is NOT called. This ensures we didn't regress the happy path.
     */
    @Test
    fun `non-empty flush completes the upload and does not abort`() = runTest {
        val (client, loader) = newLoader()
        val completer = newCompleter()

        val key = "stream/non-empty-flush"
        val payload = "hello world".toByteArray()
        val nonEmptyFinalPart = nonEmptyFinalFormattedPart(key, payload)

        val loaderState =
            loader.start(ObjectKey(streamDescriptor, key), nonEmptyFinalPart.part.partIndex)
        val loadedPart = loadedPartFromLoaderOutput(loader.accept(nonEmptyFinalPart, loaderState))

        val mockUpload = loadedPart.upload.await() as MockObjectStreamingUpload

        val completerState =
            completer.start(ObjectKey(streamDescriptor, key), nonEmptyFinalPart.part.partIndex)
        val uploadResult =
            uploadResultFromCompleterOutput(completer.accept(loadedPart, completerState))

        assertTrue(mockUpload.completeCalled, "complete() must be called on non-empty flush")
        assertFalse(mockUpload.abortCalled, "abort() must not be called on non-empty flush")
        assertEquals(BatchState.PERSISTED, uploadResult.state)
        // remoteObject is the persisted file
        assertEquals(key, uploadResult.remoteObject!!.key)
        // And the file exists in storage with the original payload
        assertEquals(payload.decodeToString(), client.get(key).data.decodeToString())
    }
}
