/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.message.object_storage.LoadablePart
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class PartToObjectAccumulatorTest {
    private val streamDescriptor = DestinationStream.Descriptor("test", "stream")

    private lateinit var stream: DestinationStream
    private lateinit var client: ObjectStorageClient<*>
    private lateinit var streamingUpload: StreamingUpload<*>
    private lateinit var metadata: Map<String, String>

    @BeforeEach
    fun setup() {
        stream = mockk(relaxed = true)
        client = mockk(relaxed = true)
        streamingUpload = mockk(relaxed = true)
        coEvery { stream.descriptor } returns streamDescriptor
        metadata = ObjectStorageDestinationState.metadataFor(stream)
        coEvery { client.startStreamingUpload(any(), any()) } returns streamingUpload
        coEvery { streamingUpload.uploadPart(any(), any()) } returns Unit
        coEvery { streamingUpload.complete() } returns mockk(relaxed = true)
    }

    private fun makePart(
        fileNumber: Int,
        index: Int,
        isFinal: Boolean = false,
        empty: Boolean = false
    ): LoadablePart =
        LoadablePart(
            Part(
                "key$fileNumber",
                fileNumber.toLong(),
                index,
                if (empty) {
                    null
                } else {
                    ByteArray(0)
                },
                isFinal
            )
        )

    @Test
    fun `test part accumulation`() = runTest {
        val acc = PartToObjectAccumulator(stream, client)

        // First part triggers starting the upload
        val firstPartFile1 = makePart(1, 1)
        acc.processBatch(firstPartFile1)
        coVerify { client.startStreamingUpload(firstPartFile1.part.key, metadata) }
        coVerify {
            streamingUpload.uploadPart(firstPartFile1.part.bytes!!, firstPartFile1.part.partIndex)
        }

        // All nonempty parts are added
        (2 until 4).forEach {
            val nonEmptyPart = makePart(1, it)
            acc.processBatch(nonEmptyPart)
            coVerify {
                streamingUpload.uploadPart(nonEmptyPart.part.bytes!!, nonEmptyPart.part.partIndex)
            }
        }

        // New key starts new upload
        val firstPartFile2 = makePart(2, 1)
        acc.processBatch(firstPartFile2)
        coVerify { client.startStreamingUpload(firstPartFile2.part.key, metadata) }

        // All empty parts are not added
        repeat(2) {
            val emptyPartFile1 = makePart(2, it + 2, empty = true)
            acc.processBatch(emptyPartFile1)
            // Ie, no more calls.
            coVerify(exactly = 1) {
                streamingUpload.uploadPart(any(), emptyPartFile1.part.partIndex)
            }
        }

        // The final part will trigger an upload
        val finalPartFile1 = makePart(1, 4, isFinal = true)
        acc.processBatch(finalPartFile1)
        coVerify(exactly = 1) { streamingUpload.complete() }

        // The final part can be empty and/or added at any time and will still count for data
        // sufficiency
        val emptyFinalPartFile2 = makePart(2, 2, isFinal = true, empty = true)
        acc.processBatch(emptyFinalPartFile2)
        // empty part won't be uploaded
        coVerify(exactly = 1) {
            streamingUpload.uploadPart(any(), emptyFinalPartFile2.part.partIndex)
        }

        // The missing part, even tho it isn't final, will trigger the completion
        val nonEmptyPenultimatePartFile2 = makePart(2, 2)
        acc.processBatch(nonEmptyPenultimatePartFile2)
        coVerify {
            streamingUpload.uploadPart(
                nonEmptyPenultimatePartFile2.part.bytes!!,
                nonEmptyPenultimatePartFile2.part.partIndex
            )
        }
        coVerify(exactly = 2) { streamingUpload.complete() }
    }
}
