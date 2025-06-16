/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.PipelineMessage
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointValue
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.io.File
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class FilePartAccumulatorLegacyTest {
    private val pathFactory: ObjectStoragePathFactory = mockk(relaxed = true)
    private val stream: DestinationStream = mockk(relaxed = true)
    private val outputQueue:
        PartitionedQueue<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>> =
        mockk(relaxed = true)
    private val loadStrategy: ObjectLoader = mockk(relaxed = true)

    private val filePartAccumulatorLegacy =
        FilePartAccumulatorLegacy(pathFactory, stream, outputQueue, loadStrategy)

    private val fileRelativePath = "relativePath"
    private val descriptor = DestinationStream.Descriptor("namespace", "name")

    @BeforeEach
    fun init() {
        every { stream.descriptor } returns descriptor
        every { loadStrategy.numUploadWorkers } returns 1
    }

    @Test
    fun testFilePartAccumulatorSmall() = runTest {
        val finalDirectory = "finalDirectory"
        every { pathFactory.getFinalDirectory(stream) } returns finalDirectory
        val file = createFile(10)
        val index = 21L
        val fileMessage = createFileMessage(file)

        filePartAccumulatorLegacy.handleFileMessage(fileMessage, index, CheckpointId("0"))

        coVerify(exactly = 1) {
            outputQueue.publish(
                match {
                    (it as PipelineMessage).checkpointCounts ==
                        mapOf(CheckpointId("0") to CheckpointValue(1, 1))
                },
                0
            )
        }
    }

    @Test
    fun testFilePartAccumulatorExactlyPartSize() = runTest {
        val finalDirectory = "finalDirectory"
        every { pathFactory.getFinalDirectory(stream) } returns finalDirectory
        val file = createFile(ObjectStorageUploadConfiguration.DEFAULT_PART_SIZE_BYTES.toInt())
        val index = 21L
        val fileMessage = createFileMessage(file)

        filePartAccumulatorLegacy.handleFileMessage(fileMessage, index, CheckpointId("0"))

        coVerify(exactly = 2) { outputQueue.publish(any(), 0) }
    }

    @Test
    fun testFilePartAccumulatorBig() = runTest {
        val finalDirectory = "finalDirectory"
        every { pathFactory.getFinalDirectory(stream) } returns finalDirectory
        val file =
            createFile(ObjectStorageUploadConfiguration.DEFAULT_PART_SIZE_BYTES.toInt() + 1000)
        val index = 21L
        val fileMessage = createFileMessage(file)

        filePartAccumulatorLegacy.handleFileMessage(fileMessage, index, CheckpointId("0"))

        coVerify(exactly = 2) { outputQueue.publish(any(), 0) }
    }

    private fun createFile(sizeInBytes: Int): File {
        val file = File.createTempFile("test", ".txt")
        val text = CharArray(sizeInBytes) { 'a' }.concatToString()
        file.writeText(text)
        return file
    }

    private fun createFileMessage(file: File): DestinationFile {
        return DestinationFile(
            stream,
            0,
            DestinationFile.AirbyteRecordMessageFile(
                fileUrl = file.absolutePath,
                fileRelativePath = fileRelativePath,
            )
        )
    }
}
