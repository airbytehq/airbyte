/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.bigquery.write.standard_insert

import com.google.cloud.RetryOption
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.JobStatus
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.DestinationRecordJsonSource
import io.airbyte.cdk.load.message.DestinationRecordProtobufSource
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableNameInfo
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.cdk.protocol.AirbyteValueProtobufEncoder
import io.airbyte.integrations.destination.bigquery.copy.BigqueryCopyContext
import io.airbyte.integrations.destination.bigquery.copy.BigqueryS3Copy
import io.airbyte.integrations.destination.bigquery.copy.StandardInsertArchiveBatch
import io.airbyte.integrations.destination.bigquery.formatter.BigQueryRecordFormatter
import io.airbyte.integrations.destination.bigquery.formatter.ProtoToBigQueryStandardInsertRecordFormatter
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryRegion
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.nio.ByteBuffer
import java.nio.charset.StandardCharsets.UTF_8
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.CoroutineStart
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import org.junit.jupiter.params.provider.EnumSource
import org.junit.jupiter.params.provider.ValueSource

class BigqueryBatchStandardInsertCopyTest {
    @ParameterizedTest
    @CsvSource("false,false", "false,true", "true,false", "true,true")
    fun `buffered JSON and proto raw and direct output is archived exactly once`(
        protobuf: Boolean,
        raw: Boolean,
    ) = runTest {
        val fixture = Fixture(protobuf, raw)
        fixture.maxWrite = 7
        val loader = fixture.loader()
        assertSame(DirectLoader.Incomplete, loader.accept(fixture.record("é☃\n\"\\")))
        loader.accept(fixture.record("second"))
        verify(exactly = 0) { fixture.bigquery.writer(any<JobId>(), any()) }
        assertEquals(0, fixture.batch.completions.size)
        loader.finish()
        fixture.assertExactBytes(2)
        assertEquals(listOf(7L), fixture.batch.completions)
        assertEquals(1, fixture.batch.closes)
        loader.close()
        verify(exactly = 1) { fixture.writer.close() }
    }

    @ParameterizedTest
    @CsvSource("false,false", "false,true", "true,false", "true,true")
    fun `streaming transition drains partial writes without reformatting`(
        protobuf: Boolean,
        raw: Boolean,
    ) = runTest {
        val fixture = Fixture(protobuf, raw)
        fixture.maxWrite = 1024 * 1024
        val loader = fixture.loader()
        loader.accept(fixture.record("before"))
        loader.accept(fixture.record("x".repeat(15 * 1024 * 1024)))
        verify(exactly = 1) { fixture.bigquery.writer(any<JobId>(), any()) }
        val bytesBefore = fixture.written.size()
        loader.accept(fixture.record("after ☃"))
        assertTrue(fixture.written.size() > bytesBefore)
        // The streaming channel receives the very array supplied to append().
        assertSame(fixture.batch.appended.last(), fixture.lastWriteArray)
        fixture.assertExactBytes(3)
        assertTrue(fixture.batch.completions.isEmpty())
        loader.finish()
        fixture.assertExactBytes(3)
    }

    @Test
    fun `15 MiB threshold stays buffered until exceeded`() = runTest {
        val fixture = Fixture()
        val formatter = mockk<RecordFormatter>()
        every { formatter.formatRecord(any()) } returns
            "x".repeat(15 * 1024 * 1024 - System.lineSeparator().toByteArray(UTF_8).size)
        val loader = fixture.loader(formatter = formatter)
        loader.accept(fixture.record())
        verify(exactly = 0) { fixture.bigquery.writer(any<JobId>(), any()) }
        every { formatter.formatRecord(any()) } returns ""
        loader.accept(fixture.record())
        verify(exactly = 1) { fixture.bigquery.writer(any<JobId>(), any()) }
        loader.close()
        assertTrue(fixture.batch.completions.isEmpty())
    }

    @Test
    fun `finish waits for archive after successful BigQuery load`() = runTest {
        val fixture = Fixture()
        fixture.batch.gate = CompletableDeferred()
        val loader = fixture.loader()
        loader.accept(fixture.record())
        val finish = launch(start = CoroutineStart.UNDISPATCHED) { loader.finish() }
        assertTrue(fixture.batch.entered.isCompleted)
        assertFalse(finish.isCompleted)
        verify(exactly = 1) { fixture.job.waitFor(any<RetryOption>()) }
        assertTrue(fixture.batch.completions.isEmpty())
        fixture.batch.gate!!.complete(Unit)
        finish.join()
        assertEquals(listOf(7L), fixture.batch.completions)
    }

    enum class LoadFailure {
        CREATE,
        CLOSE,
        WAIT,
        RELOAD,
        JOB_ERROR,
        BAD_RECORDS,
        NOT_DONE,
        MISSING_JOB
    }

    @ParameterizedTest
    @EnumSource(LoadFailure::class)
    fun `BigQuery failure never completes archive`(stage: LoadFailure) = runTest {
        val fixture = Fixture()
        val error = IOException("BigQuery failure")
        when (stage) {
            LoadFailure.CREATE ->
                every { fixture.bigquery.writer(any<JobId>(), any()) } throws
                    BigQueryException(500, "create failed")
            LoadFailure.CLOSE -> every { fixture.writer.close() } throws error
            LoadFailure.WAIT -> every { fixture.job.waitFor(any<RetryOption>()) } throws error
            LoadFailure.RELOAD -> every { fixture.job.reload() } throws error
            LoadFailure.JOB_ERROR ->
                every { fixture.job.status.error } returns
                    BigQueryError("invalid", "table", "bad data")
            LoadFailure.BAD_RECORDS -> every { fixture.statistics.badRecords } returns 1L
            LoadFailure.NOT_DONE ->
                every { fixture.job.status.state } returns JobStatus.State.RUNNING
            LoadFailure.MISSING_JOB -> every { fixture.job.reload() } returns null
        }
        val loader = fixture.loader()
        loader.accept(fixture.record())
        assertThrows<Exception> { loader.finish() }
        assertTrue(fixture.batch.completions.isEmpty())
        assertFalse(fixture.batch.entered.isCompleted)
        assertEquals(1, fixture.batch.closes)
        loader.close()
        assertEquals(1, fixture.batch.closes)
    }

    @Test
    fun `archive failure fails finish and preserves primary cleanup errors`() = runTest {
        val fixture = Fixture()
        val failure = IOException("archive failed")
        val cleanup = IOException("archive cleanup failed")
        fixture.batch.completeFailure = failure
        fixture.batch.closeFailure = cleanup
        val loader = fixture.loader()
        loader.accept(fixture.record())
        assertSame(failure, assertThrows<IOException> { loader.finish() })
        assertArrayEquals(arrayOf(cleanup), failure.suppressed)
        assertEquals(1, fixture.batch.closes)
        assertTrue(fixture.batch.completions.isEmpty())
        verify(exactly = 1) { fixture.writer.close() }
    }

    @Test
    fun `cancelling finish abandons archive and cannot report completion`() = runTest {
        val fixture = Fixture()
        fixture.batch.gate = CompletableDeferred()
        val loader = fixture.loader()
        loader.accept(fixture.record())
        val finish = launch(start = CoroutineStart.UNDISPATCHED) { loader.finish() }
        assertTrue(fixture.batch.entered.isCompleted)
        finish.cancelAndJoin()
        assertTrue(fixture.batch.completions.isEmpty())
        assertEquals(1, fixture.batch.closes)
        loader.close()
        verify(exactly = 1) { fixture.writer.close() }
    }

    @Test
    fun `formatter cancellation abandons buffer without opening BigQuery`() = runTest {
        val fixture = Fixture()
        val cancellation = CancellationException("cancelled formatter")
        val formatter = mockk<RecordFormatter>()
        every { formatter.formatRecord(any()) } throws cancellation
        val loader = fixture.loader(formatter = formatter)
        assertSame(
            cancellation,
            assertThrows<CancellationException> { loader.accept(fixture.record()) }
        )
        assertEquals(1, fixture.batch.closes)
        assertTrue(fixture.batch.appended.isEmpty())
        loader.close()
        verify(exactly = 0) { fixture.bigquery.writer(any<JobId>(), any()) }
    }

    @Test
    fun `append failure closes active writer even if both cleanup operations fail`() = runTest {
        val fixture = Fixture()
        val loader = fixture.loader()
        loader.accept(fixture.record("x".repeat(15 * 1024 * 1024)))
        val primary = IOException("append failed")
        val archiveCleanup = IOException("archive close failed")
        val writerCleanup = IOException("writer close failed")
        fixture.batch.appendFailure = primary
        fixture.batch.closeFailure = archiveCleanup
        every { fixture.writer.close() } throws writerCleanup
        val bytesBefore = fixture.written.size()
        assertSame(primary, assertThrows<IOException> { loader.accept(fixture.record()) })
        assertEquals(bytesBefore, fixture.written.size())
        assertArrayEquals(arrayOf(archiveCleanup, writerCleanup), primary.suppressed)
        assertEquals(1, fixture.batch.closes)
        loader.close()
        verify(exactly = 1) { fixture.writer.close() }
        assertThrows<IllegalStateException> { loader.finish() }
        assertTrue(fixture.batch.completions.isEmpty())
    }

    @Test
    fun `transition write failure cleans up both resources`() = runTest {
        val fixture = Fixture()
        val failure = IOException("write failed")
        every { fixture.writer.write(any()) } throws failure
        val loader = fixture.loader()
        assertSame(
            failure,
            assertThrows<IOException> {
                loader.accept(fixture.record("x".repeat(15 * 1024 * 1024)))
            }
        )
        assertEquals(1, fixture.batch.closes)
        verify(exactly = 1) { fixture.writer.close() }
        assertTrue(fixture.batch.completions.isEmpty())
    }

    @Test
    fun `persistent lack of progress fails in bounded writes`() = runTest {
        val fixture = Fixture()
        // Even an inconsistent positive return value must not cause an infinite loop.
        every { fixture.writer.write(any()) } returns 1
        val loader = fixture.loader()
        loader.accept(fixture.record())
        assertThrows<IOException> { loader.finish() }
        verify(exactly = 3) { fixture.writer.write(any()) }
        assertEquals(1, fixture.batch.closes)
        assertTrue(fixture.batch.completions.isEmpty())
    }

    @Test
    fun `transient zero writes are retried and progress resets bound`() = runTest {
        val fixture = Fixture()
        fixture.maxWrite = 7
        fixture.zeroWritesBetweenProgress = 2
        val loader = fixture.loader()
        loader.accept(fixture.record())
        loader.finish()
        fixture.assertExactBytes(1)
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `close abandons buffered or streaming batch and is idempotent`(streaming: Boolean) =
        runTest {
            val fixture = Fixture()
            val loader = fixture.loader()
            loader.accept(fixture.record(if (streaming) "x".repeat(15 * 1024 * 1024) else "small"))
            loader.close()
            loader.close()
            assertEquals(1, fixture.batch.closes)
            assertTrue(fixture.batch.completions.isEmpty())
            verify(exactly = if (streaming) 1 else 0) { fixture.writer.close() }
            assertThrows<IllegalStateException> { loader.finish() }
        }

    @Test
    fun `empty finish completes archive with BigQuery zero count`() = runTest {
        val fixture = Fixture()
        every { fixture.statistics.outputRows } returns 0L
        fixture.loader().finish()
        assertEquals(0, fixture.written.size())
        assertTrue(fixture.batch.appended.isEmpty())
        assertEquals(listOf(0L), fixture.batch.completions)
    }

    @Test
    fun `default constructor leaves archive disabled`() = runTest {
        val fixture = Fixture()
        val loader =
            BigqueryBatchStandardInsertsLoader(
                fixture.bigquery,
                fixture.configuration,
                fixture.jobId,
                fixture.formatter
            )
        loader.accept(fixture.record())
        loader.finish()
        assertArrayEquals(fixture.expectedBytes(), fixture.written.toByteArray())
        assertTrue(fixture.batch.appended.isEmpty())
        assertEquals(0, fixture.batch.closes)
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `factory starts batch only when catalog stream has archive context`(enabled: Boolean) =
        runTest {
            val fixture = Fixture()
            val archive = mockk<BigqueryS3Copy>()
            val context =
                BigqueryCopyContext("stream", 42L, 42L, "schema", UUID.randomUUID(), "run/path")
            every { archive.context(fixture.stream) } returns if (enabled) context else null
            every { archive.startStandardInsertBatch(context) } returns fixture.batch
            val tableName = TableName("dataset", "table")
            val state = mockk<StreamStateStore<DirectLoadTableExecutionConfig>>()
            every { state.get(fixture.stream.mappedDescriptor) } returns
                DirectLoadTableExecutionConfig(tableName)
            val config =
                mockk<BigqueryConfiguration> {
                    every { legacyRawTablesOnly } returns false
                    every { projectId } returns "project"
                    every { jobProjectId } returns "project"
                    every { datasetLocation } returns BigqueryRegion.US
                }
            val factory =
                BigqueryBatchStandardInsertsLoaderFactory(
                    DestinationCatalog(listOf(fixture.stream)),
                    fixture.bigquery,
                    config,
                    TableCatalogByDescriptor(
                        mapOf(
                            fixture.stream.mappedDescriptor to
                                TableNameInfo(TableNames(null, tableName), fixture.mapping)
                        )
                    ),
                    null,
                    state,
                    DataChannelFormat.JSONL,
                    archive,
                )
            val loader = factory.create(fixture.stream.mappedDescriptor, 0)
            loader.accept(fixture.record())
            loader.finish()
            verify(exactly = if (enabled) 1 else 0) { archive.startStandardInsertBatch(any()) }
            assertEquals(if (enabled) listOf(7L) else emptyList<Long>(), fixture.batch.completions)
        }

    private class Batch : StandardInsertArchiveBatch {
        val appended = mutableListOf<ByteArray>()
        val completions = mutableListOf<Long>()
        val entered = CompletableDeferred<Unit>()
        var gate: CompletableDeferred<Unit>? = null
        var appendFailure: Throwable? = null
        var completeFailure: Throwable? = null
        var closeFailure: Throwable? = null
        var closes = 0

        override fun append(bytes: ByteArray) {
            appendFailure?.let { throw it }
            appended.add(bytes)
        }

        override suspend fun complete(loadedRecordCount: Long) {
            entered.complete(Unit)
            gate?.await()
            completeFailure?.let { throw it }
            completions.add(loadedRecordCount)
        }

        override fun close() {
            closes++
            closeFailure?.let { throw it }
        }
    }

    private class Fixture(private val protobuf: Boolean = false, raw: Boolean = false) {
        val stream =
            DestinationStream(
                unmappedNamespace = "namespace",
                unmappedName = "stream",
                Append,
                ObjectType(linkedMapOf("value" to FieldType(StringType, false))),
                generationId = 42,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper(),
            )
        val mapping = ColumnNameMapping(mapOf("value" to "renamed_value"))
        val bigquery = mockk<BigQuery>()
        val writer = mockk<TableDataWriteChannel>()
        val job = mockk<Job>(relaxed = true)
        val statistics = mockk<JobStatistics.LoadStatistics>()
        val jobId = JobId.of("load-job")
        val configuration =
            WriteChannelConfiguration.newBuilder(TableId.of("dataset", "table")).build()
        val batch = Batch()
        val written = ByteArrayOutputStream()
        val formatted = mutableListOf<String>()
        var maxWrite = 1024 * 1024
        var lastWriteArray: ByteArray? = null
        var zeroWritesBetweenProgress = 0
        private var stalled = 0
        private val delegate =
            if (protobuf)
                ProtoToBigQueryStandardInsertRecordFormatter(
                    stream.airbyteValueProxyFieldAccessors,
                    mapping,
                    stream,
                    raw
                )
            else BigQueryRecordFormatter(mapping, raw)
        val formatter =
            object : RecordFormatter {
                override fun formatRecord(record: DestinationRecordRaw): String =
                    delegate.formatRecord(record).also { formatted.add(it) }
            }

        init {
            every { bigquery.writer(any<JobId>(), any()) } returns writer
            every { writer.close() } returns Unit
            every { writer.job } returns job
            every { writer.write(any()) } answers
                {
                    val source = firstArg<ByteBuffer>()
                    lastWriteArray = source.array()
                    if (stalled++ < zeroWritesBetweenProgress) {
                        0
                    } else {
                        stalled = 0
                        val size = minOf(maxWrite, source.remaining())
                        val bytes = ByteArray(size)
                        source.get(bytes)
                        written.write(bytes)
                        size
                    }
                }
            every { job.waitFor(any<RetryOption>()) } returns job
            every { job.reload() } returns job
            every { job.status.error } returns null
            every { job.status.state } returns JobStatus.State.DONE
            every { job.getStatistics<JobStatistics.LoadStatistics>() } returns statistics
            every { statistics.outputRows } returns 7L
            every { statistics.badRecords } returns 0L
        }

        fun loader(formatter: RecordFormatter = this.formatter) =
            BigqueryBatchStandardInsertsLoader(bigquery, configuration, jobId, formatter, batch)

        fun record(value: String = "hello ☃"): DestinationRecordRaw {
            val source =
                if (protobuf) {
                    val record =
                        io.airbyte.protocol.protobuf.AirbyteRecordMessage
                            .AirbyteRecordMessageProtobuf
                            .newBuilder()
                            .setStreamName("stream")
                            .setEmittedAtMs(1234)
                            .addData(
                                AirbyteValueProtobufEncoder()
                                    .encode(value, LeafAirbyteSchemaType.STRING)
                            )
                            .build()
                    DestinationRecordProtobufSource(
                        io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
                            .newBuilder()
                            .setRecord(record)
                            .build()
                    )
                } else {
                    DestinationRecordJsonSource(
                        AirbyteMessage()
                            .withRecord(
                                AirbyteRecordMessage()
                                    .withEmittedAt(1234)
                                    .withData(Jsons.valueToTree(mapOf("value" to value)))
                            )
                    )
                }
            return DestinationRecordRaw(
                stream,
                source,
                serializedSizeBytes = value.length.toLong(),
                airbyteRawId = UUID.fromString("129b0dc6-826a-4e86-a50f-33250cbf63c2")
            )
        }

        fun expectedBytes() =
            formatted.joinToString("") { "$it${System.lineSeparator()}" }.toByteArray(UTF_8)

        fun assertExactBytes(records: Int) {
            assertEquals(records, formatted.size, "each record must be formatted once")
            assertEquals(records, batch.appended.size)
            val archived = ByteArrayOutputStream()
            batch.appended.forEachIndexed { index, bytes ->
                assertArrayEquals(
                    "${formatted[index]}${System.lineSeparator()}".toByteArray(UTF_8),
                    bytes
                )
                archived.write(bytes)
            }
            assertArrayEquals(expectedBytes(), archived.toByteArray())
            assertArrayEquals(archived.toByteArray(), written.toByteArray())
        }
    }
}
