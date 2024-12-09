/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.spyk
import io.mockk.verify
import java.io.ByteArrayOutputStream
import java.io.File
import java.nio.file.Path
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class ObjectStorageStreamLoaderTest {
    private val stream: DestinationStream = mockk(relaxed = true)
    private val client: ObjectStorageClient<RemoteObject<Int>> = mockk(relaxed = true)
    private val compressor: StreamProcessor<ByteArrayOutputStream> = mockk(relaxed = true)
    private val pathFactory: ObjectStoragePathFactory = mockk(relaxed = true)
    private val writerFactory: BufferedFormattingWriterFactory<ByteArrayOutputStream> =
        mockk(relaxed = true)
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState> =
        mockk(relaxed = true)
    private val partSize: Long = 1

    private val objectStorageStreamLoader =
        spyk(
            ObjectStorageStreamLoader(
                stream,
                client,
                compressor,
                pathFactory,
                writerFactory,
                destinationStateManager,
                partSize
            )
        )

    @Test
    fun `test processFile`() = runTest {
        val fileUrl = "fileUrl"
        val stagingDirectory = "stagingDirectory"
        val generationId = 12L
        val destinationFile = mockk<DestinationFile>()
        every { destinationFile.fileMessage } returns
            DestinationFile.AirbyteRecordMessageFile(fileUrl = fileUrl)
        every { pathFactory.getFinalDirectory(any()) } returns stagingDirectory
        every { stream.generationId } returns generationId
        val mockedStateStorage: ObjectStorageDestinationState = mockk(relaxed = true)
        coEvery { destinationStateManager.getState(stream) } returns mockedStateStorage
        val mockedFile = mockk<File>(relaxed = true)
        every { objectStorageStreamLoader.createFile(any()) } returns mockedFile

        val expectedKey = Path.of(stagingDirectory.toString(), fileUrl).toString()
        val metadata =
            mapOf(
                ObjectStorageDestinationState.METADATA_GENERATION_ID_KEY to generationId.toString()
            )
        val mockRemoteObject: RemoteObject<Int> = mockk(relaxed = true)
        coEvery { client.streamingUpload(any(), any(), compressor, any()) } returns mockRemoteObject

        val result = objectStorageStreamLoader.processFile(destinationFile)

        coVerify { mockedStateStorage.addObject(generationId, expectedKey, 0, false) }
        coVerify { client.streamingUpload(expectedKey, metadata, compressor, any()) }
        assertEquals(
            mockRemoteObject,
            (result as ObjectStorageStreamLoader.RemoteObject<*>).remoteObject
        )
        verify { mockedFile.delete() }
    }
}
