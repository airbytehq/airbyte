/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.file.object_storage.Part
import io.airbyte.cdk.load.file.object_storage.RemoteObject
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoader
import io.airbyte.cdk.load.pipline.object_storage.UploadsInProgress
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class ObjectLoaderPartLoaderTest<T> {
    inner class MockRemoteObject(override val key: String, override val storageConfig: T) :
        RemoteObject<T>

    private val streamDescriptor = DestinationStream.Descriptor("test", "stream")
    private val destinationConfig = object : DestinationConfiguration() {}

    private lateinit var stream: DestinationStream
    private lateinit var client: ObjectStorageClient<MockRemoteObject>
    private lateinit var metadata: Map<String, String>
    private lateinit var catalog: DestinationCatalog

    @BeforeEach
    fun setup() {
        stream = mockk(relaxed = true)
        client = mockk(relaxed = true)
        catalog = mockk(relaxed = true)
        coEvery { stream.descriptor } returns streamDescriptor
        metadata = destinationConfig.metadataFor(stream)
    }

    private fun makePart(
        fileNumber: Int,
        index: Int,
        isFinal: Boolean = false,
        empty: Boolean = false
    ): ObjectLoaderPartFormatter.FormattedPart =
        ObjectLoaderPartFormatter.FormattedPart(
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

    private fun getNextState(
        output:
            BatchAccumulatorResult<
                ObjectLoaderPartLoader.State<MockRemoteObject>,
                ObjectLoaderPartLoader.PartResult<MockRemoteObject>
            >
    ): ObjectLoaderPartLoader.State<MockRemoteObject> =
        when (output) {
            is IntermediateOutput -> output.nextState
            is FinalOutput -> output.nextState!!
            else -> throw IllegalStateException("Unexpected output type: $output")
        }

    @Test
    fun `test part accumulation`() = runTest {
        val uploads =
            (0 until 2).map {
                val streamingUpload: StreamingUpload<MockRemoteObject> = mockk(relaxed = true)
                coEvery { streamingUpload.uploadPart(any(), any()) } returns Unit
                coEvery { streamingUpload.complete() } returns mockk(relaxed = true)
                streamingUpload
            }
        coEvery { client.startStreamingUpload(any(), any()) } returnsMany uploads

        val acc = ObjectLoaderPartLoader(client, catalog, UploadsInProgress(), destinationConfig)

        // First part triggers starting the upload
        val firstPartFile1 = makePart(1, 1)
        val file1State1 =
            acc.start(
                ObjectKey(streamDescriptor, firstPartFile1.part.key),
                firstPartFile1.part.partIndex
            )
        val file1State2 = getNextState(acc.accept(firstPartFile1, file1State1))
        coVerify(exactly = 1) { client.startStreamingUpload(firstPartFile1.part.key, metadata) }
        coVerify(exactly = 1) { uploads[0].uploadPart(any(), firstPartFile1.part.partIndex) }

        // All nonempty parts are added
        val file1State4 =
            (2 until 4).fold(file1State2) { state, it ->
                val nonEmptyPart = makePart(1, it)
                val nextState = getNextState(acc.accept(nonEmptyPart, state))
                coVerify(exactly = 1) { uploads[0].uploadPart(any(), nonEmptyPart.part.partIndex) }
                nextState
            }

        // New key starts new upload
        val firstPartFile2 = makePart(2, 1)
        val file2State1 =
            acc.start(
                ObjectKey(streamDescriptor, firstPartFile2.part.key),
                firstPartFile2.part.partIndex
            )
        val file2State2 = getNextState(acc.accept(firstPartFile2, file2State1))
        coVerify(exactly = 1) { client.startStreamingUpload(firstPartFile2.part.key, metadata) }

        // All non-empty parts are not added
        val file2State4 =
            (0 until 2).fold(file2State2) { state, it ->
                val emptyPartFile1 = makePart(2, it + 2)
                val nextState = getNextState(acc.accept(emptyPartFile1, state))
                // Ie, no more calls.
                coVerify(exactly = 1) {
                    uploads[0].uploadPart(any(), emptyPartFile1.part.partIndex)
                }
                nextState
            }

        // The final part will not trigger an upload
        val finalPartFile1 = makePart(1, 4, isFinal = true)
        acc.accept(finalPartFile1, file1State4)
        coVerify(exactly = 1) { uploads[0].uploadPart(any(), finalPartFile1.part.partIndex) }
        coVerify(exactly = 0) { uploads[0].complete() }

        // The final part can be empty and/or added at any time and will still count for data
        // sufficiency
        val emptyFinalPartFile2 = makePart(2, 2, isFinal = true, empty = true)
        val file2State5 = getNextState(acc.accept(emptyFinalPartFile2, file2State4))
        // empty part won't be uploaded
        coVerify(exactly = 1) { uploads[1].uploadPart(any(), emptyFinalPartFile2.part.partIndex) }

        // The missing part, even tho it isn't final, will also not trigger completion
        val nonEmptyPenultimatePartFile2 = makePart(2, 2)
        acc.accept(nonEmptyPenultimatePartFile2, file2State5)
        coVerify {
            uploads[1].uploadPart(
                nonEmptyPenultimatePartFile2.part.bytes!!,
                nonEmptyPenultimatePartFile2.part.partIndex
            )
        }
        coVerify(exactly = 0) { uploads[1].complete() }
    }
}
