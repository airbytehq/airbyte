/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.object_storage.ObjectStorageUploadConfiguration
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.io.File
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class FilePartAccumulatorTest {
    private val pathFactory: ObjectStoragePathFactory = mockk(relaxed = true)
    private val stream: DestinationStream = mockk(relaxed = true)
    private val outputQueue: MultiProducerChannel<BatchEnvelope<*>> = mockk(relaxed = true)

    private val filePartAccumulator = FilePartAccumulator(pathFactory, stream, outputQueue)

    private val fileRelativePath = "relativePath"
    private val descriptor = DestinationStream.Descriptor("namespace", "name")

    @BeforeEach
    fun init() {
        every { stream.descriptor } returns descriptor
    }

    @Test
    fun testFilePartAccumulatorSmall() = runTest {
        val finalDirectory = "finalDirectory"
        every { pathFactory.getFinalDirectory(stream) } returns finalDirectory
        val file = createFile(10)
        val index = 21L
        val fileMessage = createFileMessage(file)

        filePartAccumulator.processFilePart(fileMessage, index)

        coVerify(exactly = 1) { outputQueue.publish(any()) }
    }

    @Test
    fun testFilePartAccumulatorExactlyPartSize() = runTest {
        val finalDirectory = "finalDirectory"
        every { pathFactory.getFinalDirectory(stream) } returns finalDirectory
        val file = createFile(ObjectStorageUploadConfiguration.DEFAULT_FILE_SIZE_BYTES.toInt())
        val index = 21L
        val fileMessage = createFileMessage(file)

        filePartAccumulator.processFilePart(fileMessage, index)

        coVerify(exactly = 2) { outputQueue.publish(any()) }
    }

    @Test
    fun testFilePartAccumulatorBig() = runTest {
        val finalDirectory = "finalDirectory"
        every { pathFactory.getFinalDirectory(stream) } returns finalDirectory
        val file =
            createFile(ObjectStorageUploadConfiguration.DEFAULT_FILE_SIZE_BYTES.toInt() + 1000)
        val index = 21L
        val fileMessage = createFileMessage(file)

        filePartAccumulator.processFilePart(fileMessage, index)

        coVerify(exactly = 2) { outputQueue.publish(any()) }
    }

    private fun createFile(sizeInBytes: Int): File {
        val file = File.createTempFile("test", ".txt")
        val text = CharArray(sizeInBytes) { 'a' }.concatToString()
        file.writeText(text)
        return file
    }

    private fun createFileMessage(file: File): DestinationFile {
        return DestinationFile(
            descriptor,
            0,
            "",
            DestinationFile.AirbyteRecordMessageFile(
                fileUrl = file.absolutePath,
                fileRelativePath = fileRelativePath,
            )
        )
    }
}
