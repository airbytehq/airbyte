/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoader
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class ObjectLoaderUploadCompleterTest<T> {
    inner class MockRemoteObject(override val key: String, override val storageConfig: T) :
        RemoteObject<T>

    private val streamDescriptor = DestinationStream.Descriptor("test", "stream")

    private lateinit var objectLoader: ObjectLoader
    private lateinit var completer: ObjectLoaderUploadCompleter<MockRemoteObject>

    @BeforeEach
    fun setup() {
        objectLoader = mockk(relaxed = true)
        every { objectLoader.stateAfterUpload } returns BatchState.PERSISTED
        completer = ObjectLoaderUploadCompleter(objectLoader)
    }

    private fun makeLoadedPart(
        upload: StreamingUpload<MockRemoteObject>,
        objectKey: String,
        partIndex: Int,
        isFinal: Boolean,
        empty: Boolean = false
    ): ObjectLoaderPartLoader.LoadedPart<MockRemoteObject> =
        ObjectLoaderPartLoader.LoadedPart(
            upload = CompletableDeferred(upload),
            objectKey = objectKey,
            partIndex = partIndex,
            isFinal = isFinal,
            empty = empty,
        )

    @Test
    fun `test completing upload with non-empty parts`() = runTest {
        val upload: StreamingUpload<MockRemoteObject> = mockk(relaxed = true)
        val remoteObject = MockRemoteObject("key1", mockk())
        coEvery { upload.complete() } returns remoteObject

        val state = completer.start(ObjectKey(streamDescriptor, "key1"), 0)

        // Add a non-empty part
        val part1 = makeLoadedPart(upload, "key1", 1, isFinal = false, empty = false)
        val result1 = completer.accept(part1, state)
        assert(result1 is NoOutput)

        // Add a final non-empty part
        val part2 = makeLoadedPart(upload, "key1", 2, isFinal = true, empty = false)
        val result2 = completer.accept(part2, state)
        assert(result2 is FinalOutput)
        val uploadResult = (result2 as FinalOutput).output
        assertNotNull(uploadResult.remoteObject)
        assertEquals(remoteObject, uploadResult.remoteObject)
        assertEquals(BatchState.PERSISTED, uploadResult.state)
        coVerify(exactly = 1) { upload.complete() }
    }

    @Test
    fun `test skipping upload when all parts are empty`() = runTest {
        val upload: StreamingUpload<MockRemoteObject> = mockk(relaxed = true)

        val state = completer.start(ObjectKey(streamDescriptor, "key1"), 0)

        // Add an empty final part (bytes=null, isFinal=true, partIndex=0)
        // This simulates the flush timer firing on a writer with 0 records
        val emptyFinalPart = makeLoadedPart(upload, "key1", 0, isFinal = true, empty = true)
        val result = completer.accept(emptyFinalPart, state)

        // Should produce FinalOutput with null remoteObject (no file created)
        assert(result is FinalOutput)
        val uploadResult = (result as FinalOutput).output
        assertNull(uploadResult.remoteObject)
        assertEquals(BatchState.PERSISTED, uploadResult.state)

        // complete() should NOT have been called
        coVerify(exactly = 0) { upload.complete() }
    }

    @Test
    fun `test NoPart returns NoOutput`() = runTest {
        val state = completer.start(ObjectKey(streamDescriptor, "key1"), 0)

        val noPart = ObjectLoaderPartLoader.NoPart<MockRemoteObject>("key1")
        val result = completer.accept(noPart, state)
        assert(result is NoOutput)
    }

    @Test
    fun `test finish with empty bookkeeper returns dummy output`() = runTest {
        val state = completer.start(ObjectKey(streamDescriptor, "key1"), 0)

        val result = completer.finish(state)
        assertNull(result.output.remoteObject)
        assertEquals(BatchState.PERSISTED, result.output.state)
    }

    @Test
    fun `test finish with non-empty bookkeeper throws`() = runTest {
        val upload: StreamingUpload<MockRemoteObject> = mockk(relaxed = true)

        val state = completer.start(ObjectKey(streamDescriptor, "key1"), 0)

        // Add a non-empty non-final part to make the bookkeeper non-empty
        val part = makeLoadedPart(upload, "key1", 1, isFinal = false, empty = false)
        completer.accept(part, state)

        // finish() should throw because there's unfinished work
        assertThrows<IllegalStateException> {
            completer.finish(state)
        }
    }

    @Test
    fun `test mixed empty and non-empty parts completes upload`() = runTest {
        val upload: StreamingUpload<MockRemoteObject> = mockk(relaxed = true)
        val remoteObject = MockRemoteObject("key1", mockk())
        coEvery { upload.complete() } returns remoteObject

        val state = completer.start(ObjectKey(streamDescriptor, "key1"), 0)

        // Add a non-empty part first
        val part1 = makeLoadedPart(upload, "key1", 1, isFinal = false, empty = false)
        val result1 = completer.accept(part1, state)
        assert(result1 is NoOutput)

        // Add an empty final part
        val part2 = makeLoadedPart(upload, "key1", 1, isFinal = true, empty = true)
        val result2 = completer.accept(part2, state)

        // Should still complete because there was at least one non-empty part
        assert(result2 is FinalOutput)
        val uploadResult = (result2 as FinalOutput).output
        assertNotNull(uploadResult.remoteObject)
        coVerify(exactly = 1) { upload.complete() }
    }
}
