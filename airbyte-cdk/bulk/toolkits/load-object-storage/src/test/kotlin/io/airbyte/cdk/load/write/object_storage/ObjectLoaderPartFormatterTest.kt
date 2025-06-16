/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriter
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchAccumulatorResult
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.IntermediateOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.state.DestinationStateManager
import io.airbyte.cdk.load.state.object_storage.ObjectStorageDestinationState
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.io.OutputStream
import java.util.UUID
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class ObjectLoaderPartFormatterTest {
    private val streamDescriptor = DestinationStream.Descriptor("test", "stream")
    private val partSizeBytes: Long = 2L
    private val fileSizeBytes: Long = 4L

    private lateinit var pathFactory: ObjectStoragePathFactory
    private lateinit var bufferedWriterFactory: BufferedFormattingWriterFactory<OutputStream>
    private lateinit var bufferedWriter: BufferedFormattingWriter<OutputStream>
    private lateinit var stream: DestinationStream
    private lateinit var catalog: DestinationCatalog
    private lateinit var stateManager: DestinationStateManager<ObjectStorageDestinationState>
    private lateinit var state: ObjectStorageDestinationState
    private lateinit var objectLoader: ObjectLoader
    private lateinit var partIdCounter: AtomicLong

    @BeforeEach
    fun setup() {
        pathFactory = mockk()
        bufferedWriterFactory = mockk()
        stream = mockk(relaxed = true)
        bufferedWriter = mockk()
        catalog = mockk()
        stateManager = mockk()
        objectLoader = mockk(relaxed = true)
        state = mockk(relaxed = true)
        partIdCounter = mockk(relaxed = true)
        coEvery { bufferedWriterFactory.create(any()) } returns bufferedWriter
        coEvery { bufferedWriter.accept(any()) } returns Unit
        coEvery { bufferedWriter.flush() } returns Unit
        coEvery { bufferedWriter.close() } returns Unit
        every { objectLoader.objectSizeBytes } returns fileSizeBytes
        every { stream.descriptor } returns streamDescriptor
        every { catalog.getStream(any()) } returns stream
        coEvery { pathFactory.getFinalDirectory(any()) } returns "foo"
        coEvery { stateManager.getState(any()) } returns state
        coEvery { state.getPartIdCounter("foo") } returns partIdCounter
        every { partIdCounter.incrementAndGet() } returnsMany listOf(111L, 112L)
        every { pathFactory.getPathToFile(any(), any()) } answers
            {
                val path = firstArg<String>()
                val fileNumber = secondArg<Long>()
                "${path}${fileNumber}"
            }
        coEvery { state.ensureUnique(any()) } answers
            {
                val path = firstArg<String>()
                "${path}!"
            }
    }

    private fun makeRecord(): DestinationRecordRaw =
        DestinationRecordRaw(
            stream = stream,
            rawData =
                DestinationRecordJsonSource(
                    source =
                        AirbyteMessage()
                            .withRecord(
                                AirbyteRecordMessage()
                                    .withEmittedAt(42)
                                    .withData(Jsons.createObjectNode())
                            )
                ),
            serializedSizeBytes = 0L,
            airbyteRawId = UUID.randomUUID(),
        )

    private fun makeRecords(n: Int): Iterator<DestinationRecordRaw> =
        (0 until n).map { makeRecord() }.listIterator()

    private suspend fun <T : OutputStream> threadRecords(
        nRecords: Int,
        acc: ObjectLoaderPartFormatter<T>,
        initialState: ObjectLoaderPartFormatter.State<T>
    ): BatchAccumulatorResult<
        ObjectLoaderPartFormatter.State<T>, ObjectLoaderPartFormatter.FormattedPart>? {
        var state = initialState
        var result:
            BatchAccumulatorResult<
                ObjectLoaderPartFormatter.State<T>, ObjectLoaderPartFormatter.FormattedPart>? =
            null
        makeRecords(nRecords).forEach { record ->
            result = acc.accept(record, state)
            if (result !is FinalOutput) {
                state = result!!.nextState!!
            }
        }
        return result
    }

    private fun makeBytes(n: Int): ByteArray? =
        if (n == 0) {
            null
        } else (0 until n).map { it.toByte() }.toByteArray()

    @Test
    fun `test parts are emitted correctly`() = runTest {
        val acc =
            ObjectLoaderPartFormatter(
                pathFactory = pathFactory,
                catalog = catalog,
                writerFactory = bufferedWriterFactory,
                loader = objectLoader,
                stateManager = stateManager,
                batchSizeOverride = null,
                clampedPartSizeBytes = partSizeBytes
            )

        val bufferSize = AtomicLong(0L)
        coEvery { bufferedWriter.accept(any()) } answers
            {
                bufferSize.getAndIncrement()
                Unit
            }
        coEvery { bufferedWriter.bufferSize } answers { bufferSize.get().toInt() }
        coEvery { bufferedWriter.takeBytes() } answers
            {
                val bytes = makeBytes(bufferSize.get().toInt())
                bufferSize.set(0)
                bytes
            }
        coEvery { bufferedWriter.finish() } answers
            {
                val bytes = makeBytes(bufferSize.get().toInt())
                bufferSize.set(0)
                bytes
            }

        coEvery { pathFactory.getPathToFile(any(), any()) } answers { "path.${secondArg<Long>()}" }

        val initialState = acc.start(StreamKey(stream.descriptor), 0)
        // Object 1

        // part 0->1/2b of 4b total => not data sufficient
        val result = acc.accept(makeRecords(1).next(), initialState)
        assert(result is NoOutput)

        // part 1->2/2b of 4b total => data sufficient for part, should be first part and nonfinal
        val result2 = threadRecords(1, acc, result.nextState!!)
        when (result2) {
            is IntermediateOutput -> {
                assert(result2.output.part.bytes.contentEquals(makeBytes(2)))
                assert(result2.output.part.partIndex == 1)
                assert(result2.output.part.fileNumber == 111L)
                assert(!result2.output.part.isFinal)
                assert(result2.output.part.key == "path.111!")
            }
            else -> assert(false)
        }

        // part 3->4/2b of 4b total => data sufficient for file (but not part! this is expected!),
        // should be second part and final (and not empty)
        val result3 = threadRecords(2, acc, result2!!.nextState!!)
        when (result3) {
            is FinalOutput -> {
                assert(result3.output.part.bytes.contentEquals(makeBytes(2)))
                assert(result3.output.part.partIndex == 2)
                assert(result3.output.part.fileNumber == 111L)
                assert(result3.output.part.isFinal)
                assert(result3.output.part.key == "path.111!")
            }
            else -> assert(false)
        }

        // Object 2

        // Next part 4/4b => data sufficient, should be second and final
        val initialState2 = acc.start(StreamKey(stream.descriptor), 0)
        when (val result4 = threadRecords(4, acc, initialState2)) {
            is FinalOutput -> {
                assert(result4.output.part.bytes.contentEquals(makeBytes(2)))
                assert(result4.output.part.partIndex == 2)
                assert(result4.output.part.fileNumber == 112L)
                assert(result4.output.part.isFinal)
                assert(result4.output.part.key == "path.112!")
            }
            else -> assert(false)
        }

        // One flush per call, one create/close per finished object
        coVerify(exactly = 2) { bufferedWriterFactory.create(any()) }
        coVerify(exactly = 4) { bufferedWriter.flush() }
        coVerify(exactly = 2) { bufferedWriter.finish() }
    }
}
