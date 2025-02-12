/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write.object_storage

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriter
import io.airbyte.cdk.load.file.object_storage.BufferedFormattingWriterFactory
import io.airbyte.cdk.load.file.object_storage.ObjectStoragePathFactory
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.object_storage.*
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import java.io.OutputStream
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class RecordToPartAccumulatorTest {
    private val partSizeBytes: Long = 2L
    private val fileSizeBytes: Long = 4L

    private lateinit var pathFactory: ObjectStoragePathFactory
    private lateinit var bufferedWriterFactory: BufferedFormattingWriterFactory<OutputStream>
    private lateinit var bufferedWriter: BufferedFormattingWriter<OutputStream>
    private lateinit var stream: DestinationStream

    @BeforeEach
    fun setup() {
        pathFactory = mockk()
        bufferedWriterFactory = mockk()
        stream = mockk()
        bufferedWriter = mockk()
        coEvery { bufferedWriterFactory.create(any()) } returns bufferedWriter
        coEvery { bufferedWriter.flush() } returns Unit
        coEvery { bufferedWriter.close() } returns Unit
    }

    private fun makeRecord(): DestinationRecordAirbyteValue =
        DestinationRecordAirbyteValue(
            DestinationStream.Descriptor("test", "stream"),
            ObjectValue(linkedMapOf()),
            0L,
            null,
        )

    private fun makeRecords(n: Int): Iterator<DestinationRecordAirbyteValue> =
        (0 until n).map { makeRecord() }.listIterator()

    private fun makeBytes(n: Int): ByteArray? =
        if (n == 0) {
            null
        } else (0 until n).map { it.toByte() }.toByteArray()

    @Test
    fun `test parts are emitted correctly`() = runTest {
        val fileNumber = AtomicLong(110L)
        val acc =
            RecordToPartAccumulator(
                pathFactory = pathFactory,
                bufferedWriterFactory = bufferedWriterFactory,
                partSizeBytes = partSizeBytes,
                fileSizeBytes = fileSizeBytes,
                stream = stream,
                fileNumber = fileNumber,
                fileNameMapper = { "$it!" },
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
        coEvery { pathFactory.supportsStaging } returns false

        // Object 1

        // part 0->1/2b of 4b total => not data sufficient, should be first and empty
        when (val batch = acc.processRecords(makeRecords(1), 0L, false) as ObjectStorageBatch) {
            is LoadablePart -> {
                assert(batch.part.isEmpty)
                assert(batch.part.partIndex == 0)
                assert(batch.part.fileNumber == 111L)
                assert(!batch.isPersisted())
                assert(!batch.part.isFinal)
                assert(batch.part.key == "path.111!")
            }
            else -> assert(false)
        }

        // empty iterator, should be still first, empty, and nonfinal
        when (val batch = acc.processRecords(makeRecords(0), 0L, false) as ObjectStorageBatch) {
            is LoadablePart -> {
                assert(batch.part.isEmpty)
                assert(batch.part.partIndex == 0)
                assert(batch.part.fileNumber == 111L)
                assert(!batch.isPersisted())
                assert(!batch.part.isFinal)
                assert(batch.part.key == "path.111!")
            }
            else -> assert(false)
        }

        // part 1->3/2b of 4b total => data sufficient for part, should be first part and nonfinal
        when (val batch = acc.processRecords(makeRecords(2), 0L, false) as ObjectStorageBatch) {
            is LoadablePart -> {
                assert(batch.part.bytes.contentEquals(makeBytes(3)))
                assert(batch.part.partIndex == 1)
                assert(batch.part.fileNumber == 111L)
                assert(!batch.isPersisted())
                assert(!batch.part.isFinal)
                assert(batch.part.key == "path.111!")
            }
            else -> assert(false)
        }

        // part 3->4/2b of 4b total => data sufficient for file (but not part! this is expected!),
        // should be second part and final (and not empty)
        when (val batch = acc.processRecords(makeRecords(1), 0L, false) as ObjectStorageBatch) {
            is LoadablePart -> {
                assert(batch.part.bytes.contentEquals(makeBytes(1)))
                assert(batch.part.partIndex == 2)
                assert(batch.part.fileNumber == 111L)
                assert(!batch.isPersisted())
                assert(batch.part.isFinal)
                assert(batch.part.key == "path.111!")
            }
            else -> assert(false)
        }

        // Object 2

        // Next part 10/4b => data sufficient, should be first and final
        when (val batch = acc.processRecords(makeRecords(10), 0L, false) as ObjectStorageBatch) {
            is LoadablePart -> {
                assert(batch.part.bytes.contentEquals(makeBytes(10)))
                assert(batch.part.partIndex == 1)
                assert(batch.part.fileNumber == 112L)
                assert(!batch.isPersisted())
                assert(batch.part.isFinal)
                assert(batch.part.key == "path.112!")
            }
            else -> assert(false)
        }

        // Object 3: empty eos, should be final and empty

        when (val batch = acc.processRecords(makeRecords(0), 0L, true) as ObjectStorageBatch) {
            is LoadablePart -> {
                assert(batch.part.isEmpty)
                assert(batch.part.partIndex == 0)
                assert(batch.part.fileNumber == 113L)
                assert(!batch.isPersisted())
                assert(batch.part.isFinal)
                assert(batch.part.key == "path.113!")
            }
            else -> assert(false)
        }

        // One flush per call, one create/close per finished object
        coVerify(exactly = 3) { bufferedWriterFactory.create(any()) }
        coVerify(exactly = 6) { bufferedWriter.flush() }
        coVerify(exactly = 3) { bufferedWriter.close() }
    }
}
