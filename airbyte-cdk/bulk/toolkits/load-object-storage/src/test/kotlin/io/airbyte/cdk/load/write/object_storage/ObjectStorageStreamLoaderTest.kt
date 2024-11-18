/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.StreamProcessor
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.ObjectStorageFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.io.ByteArrayOutputStream
import java.nio.file.Path
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class ObjectStorageStreamLoaderTest {
    private val stream: DestinationStream = mockk(relaxed = true)
    private val client: ObjectStorageClient<RemoteObject<Int>> = mockk(relaxed = true)
    private val compressor: StreamProcessor<ByteArrayOutputStream> = mockk(relaxed = true)
    private val pathFactory: ObjectStoragePathFactory = mockk(relaxed = true)
    private val writerFactory: ObjectStorageFormattingWriterFactory = mockk(relaxed = true)
    private val destinationStateManager: DestinationStateManager<ObjectStorageDestinationState> =
        mockk(relaxed = true)

    private val objectStorageStreamLoader =
        ObjectStorageStreamLoader(
            stream,
            client,
            compressor,
            pathFactory,
            writerFactory,
            destinationStateManager
        )

    @Test
    fun `test processFile`() = runTest {
        val fileUrl = "fileUrl"
        val stagingDirectory = Path.of("stagingDirectory")
        val generationId = 12L
        val destinationFile = mockk<DestinationFile>()
        every { destinationFile.fileMessage } returns
            DestinationFile.AirbyteRecordMessageFile(fileUrl = fileUrl)
        every { pathFactory.getStagingDirectory(any()) } returns stagingDirectory
        every { stream.generationId } returns generationId

        val expectedKey = Path.of(stagingDirectory.toString(), fileUrl).toString()
        val metadata =
            mapOf(
                ObjectStorageDestinationState.METADATA_GENERATION_ID_KEY to generationId.toString()
            )
        val mockRemoteObject: RemoteObject<Int> = mockk()
        coEvery { client.streamingUpload(any(), any(), compressor, any()) } returns mockRemoteObject

        val result = objectStorageStreamLoader.processFile(destinationFile)

        coVerify { client.streamingUpload(expectedKey, metadata, compressor, any()) }
        assertEquals(
            mockRemoteObject,
            (result as ObjectStorageStreamLoader.FileObject<*>).remoteObject
        )
    }
}
