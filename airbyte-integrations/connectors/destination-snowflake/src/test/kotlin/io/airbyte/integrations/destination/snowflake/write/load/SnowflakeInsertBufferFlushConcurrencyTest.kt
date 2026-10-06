/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.load.component.ColumnType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.copy.CsvCopyContext
import io.airbyte.integrations.destination.snowflake.copy.SnowflakeS3Copy
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.asCoroutineDispatcher
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

internal class SnowflakeInsertBufferFlushConcurrencyTest {
    private val table = TableName(namespace = "test", name = "flush_concurrency")
    private val columns = listOf("_AIRBYTE_RAW_ID", "VALUE")
    private val schema =
        ColumnSchema(
            inputToFinalColumnNames = mapOf("value" to "VALUE"),
            finalSchema = mapOf("VALUE" to ColumnType("VARCHAR", true)),
            inputSchema = mapOf("value" to FieldType(StringType, nullable = true)),
        )
    private val copyContext =
        CsvCopyContext(
            streamKey = "stream-key",
            generationId = 1,
            syncId = 2,
            schemaId = "schema-id",
            runPath = "fusion/run/",
        )
    private val client = mockk<SnowflakeAirbyteClient>()
    private val s3Copy = mockk<SnowflakeS3Copy>()

    @Test
    fun `Fusion disabled runs PUT and COPY on the calling thread`() {
        val putThread = AtomicReference<Thread>()
        val copyThread = AtomicReference<Thread>()
        every { client.putInStage(table, any()) } answers { putThread.set(Thread.currentThread()) }
        every { client.copyFromStage(table, any(), columns) } answers
            {
                copyThread.set(Thread.currentThread())
            }
        val buffer = buffer(fusionEnabled = false)
        val executor = Executors.newSingleThreadExecutor()
        try {
            val callerThread =
                runBlocking(executor.asCoroutineDispatcher()) {
                    buffer.flush()
                    Thread.currentThread()
                }
            assertSame(callerThread, putThread.get())
            assertSame(callerThread, copyThread.get())
        } finally {
            executor.shutdownNow()
        }
        coVerify(exactly = 0) { s3Copy.upload(any(), any(), any()) }
    }

    /**
     * Mirrors the CDK's PipelineCompletionHandler: each final flush runs in `async` on a
     * `limitedParallelism` dispatcher. PUT/COPY must not escape that bound, otherwise every
     * remaining aggregate checks out a pooled Snowflake connection at once.
     */
    @OptIn(ExperimentalCoroutinesApi::class)
    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `final flush PUT and COPY concurrency is bounded by the caller's dispatcher`(
        fusionEnabled: Boolean,
    ) {
        val parallelism = 2
        val inFlight = AtomicInteger()
        val maxInFlight = AtomicInteger()
        every { client.putInStage(table, any()) } answers
            {
                maxInFlight.accumulateAndGet(inFlight.incrementAndGet(), ::maxOf)
                Thread.sleep(100)
            }
        every { client.copyFromStage(table, any(), columns) } answers
            {
                Thread.sleep(100)
                inFlight.decrementAndGet()
            }
        coEvery { s3Copy.upload(any(), copyContext, 1) } coAnswers { delay(50) }
        val buffers = List(8) { buffer(fusionEnabled) }
        val dispatcher = Dispatchers.Default.limitedParallelism(parallelism)

        runBlocking {
            withTimeout(30_000) { buffers.map { async(dispatcher) { it.flush() } }.awaitAll() }
        }

        assertEquals(parallelism, maxInFlight.get())
        verify(exactly = buffers.size) { client.putInStage(table, any()) }
        verify(exactly = buffers.size) { client.copyFromStage(table, any(), columns) }
        coVerify(exactly = if (fusionEnabled) buffers.size else 0) {
            s3Copy.upload(any(), any(), any())
        }
        buffers.forEach { assertNull(it.csvFilePath) }
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `PUT failure propagates and cleans up`(fusionEnabled: Boolean) {
        val failure = IOException("PUT failed")
        val uploadStarted = CountDownLatch(1)
        val uploadCancelled = AtomicBoolean(false)
        every { client.putInStage(table, any()) } answers
            {
                if (fusionEnabled) {
                    check(uploadStarted.await(10, TimeUnit.SECONDS)) { "S3 upload never started" }
                }
                throw failure
            }
        coEvery { s3Copy.upload(any(), copyContext, 1) } coAnswers
            {
                uploadStarted.countDown()
                try {
                    awaitCancellation()
                } finally {
                    uploadCancelled.set(true)
                }
            }
        val buffer = buffer(fusionEnabled)
        val path = requireNotNull(buffer.csvFilePath)

        val thrown =
            assertThrows<IOException> { runBlocking { withTimeout(10_000) { buffer.flush() } } }

        assertFailure(failure, thrown)
        verify(exactly = 0) { client.copyFromStage(any(), any(), any()) }
        assertEquals(fusionEnabled, uploadCancelled.get())
        assertCleaned(buffer, path)
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `COPY failure propagates and cleans up`(fusionEnabled: Boolean) {
        val failure = IOException("COPY failed")
        every { client.putInStage(table, any()) } returns Unit
        every { client.copyFromStage(table, any(), columns) } throws failure
        coEvery { s3Copy.upload(any(), copyContext, 1) } returns Unit
        val buffer = buffer(fusionEnabled)
        val path = requireNotNull(buffer.csvFilePath)

        val thrown = assertThrows<IOException> { runBlocking { buffer.flush() } }

        assertFailure(failure, thrown)
        assertCleaned(buffer, path)
    }

    @Test
    fun `Fusion S3 failure propagates after Snowflake success and cleans up`() {
        val failure = IOException("S3 failed")
        every { client.putInStage(table, any()) } returns Unit
        every { client.copyFromStage(table, any(), columns) } returns Unit
        coEvery { s3Copy.upload(any(), copyContext, 1) } coAnswers
            {
                withContext(Dispatchers.IO) { throw failure }
            }
        val buffer = buffer(fusionEnabled = true)
        val path = requireNotNull(buffer.csvFilePath)

        val thrown = assertThrows<IOException> { runBlocking { buffer.flush() } }

        assertFailure(failure, thrown)
        verify(exactly = 1) { client.copyFromStage(table, any(), columns) }
        assertCleaned(buffer, path)
    }

    private fun assertFailure(expected: Throwable, actual: Throwable) {
        // Coroutine stack-trace recovery may copy the exception; the original stays in the chain.
        assertTrue(generateSequence(actual) { it.cause }.any { it === expected })
    }

    private fun assertCleaned(buffer: SnowflakeInsertBuffer, path: Path) {
        assertFalse(Files.exists(path))
        assertNull(buffer.csvFilePath)
        assertNull(buffer.csvWriter)
        assertEquals(0, buffer.recordCount)
    }

    private fun buffer(fusionEnabled: Boolean) =
        SnowflakeInsertBuffer(
                tableName = table,
                snowflakeClient = client,
                snowflakeConfiguration = mockk(relaxed = true),
                columnSchema = schema,
                columnManager = mockk { every { getTableColumnNames(schema) } returns columns },
                snowflakeRecordFormatter = SnowflakeSchemaRecordFormatter(),
                s3Copy = s3Copy,
                copyContext = if (fusionEnabled) copyContext else null,
            )
            .apply {
                accumulate(
                    mapOf(
                        "VALUE" to StringValue("payload"),
                        Meta.COLUMN_NAME_AB_RAW_ID to StringValue("raw-id"),
                        Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(1234),
                        Meta.COLUMN_NAME_AB_META to StringValue("{}"),
                        Meta.COLUMN_NAME_AB_GENERATION_ID to NullValue,
                    )
                )
            }
}
