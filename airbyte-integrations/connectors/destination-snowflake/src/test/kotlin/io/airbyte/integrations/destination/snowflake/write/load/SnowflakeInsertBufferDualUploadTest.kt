/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.snowflake.write.load

import io.airbyte.cdk.fusion.FusionConfiguration
import io.airbyte.cdk.fusion.testing.ControlledFusionUploader
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
import io.airbyte.integrations.destination.snowflake.copy.EnabledSnowflakeS3Copy
import io.airbyte.integrations.destination.snowflake.copy.SnowflakeS3Copy
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.util.UUID
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.zip.GZIPInputStream
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.async
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

internal class SnowflakeInsertBufferDualUploadTest {
    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `either pending upload prevents successful flush and temporary file deletion`(
        archiveFinishesFirst: Boolean,
    ) {
        val fixture = Fixture()
        exercise(fixture) { flush ->
            if (archiveFinishesFirst) {
                fixture.releaseArchive.complete(Unit)
                fixture.releaseReader.complete(Unit)
                fixture.archiveFinished.await()
                assertFalse(fixture.snowflakeFinished.isCompleted)
            } else {
                fixture.releaseSnowflake.countDown()
                fixture.snowflakeFinished.await()
                assertFalse(fixture.archiveFinished.isCompleted)
            }
            fixture.assertPending(flush)
            fixture.releaseAll()
            assertTrue(flush.await().isSuccess)
            fixture.assertCleaned()
            fixture.verifyUploads()
        }
    }

    @Test
    fun `S3 failure after Snowflake success propagates after its reader finishes`() {
        val failure = IOException("S3 upload failed after Snowflake succeeded")
        val fixture = Fixture(archiveFailure = failure)
        exercise(fixture) { flush ->
            fixture.releaseSnowflake.countDown()
            fixture.snowflakeFinished.await()
            fixture.releaseArchive.complete(Unit)
            // The failing upload is still draining its reader, even though it already knows
            // the remote request failed. Flush must neither succeed nor unlink its input yet.
            fixture.readerCleanupEntered.await()
            fixture.assertPending(flush)
            fixture.releaseReader.complete(Unit)
            assertFailureCause(failure, flush.await().exceptionOrNull())
            fixture.assertCleaned()
            fixture.verifyUploads()
        }
    }

    @Test
    fun `Snowflake failure waits for cancellation resistant S3 reader before deleting file`() {
        val failure = IOException("Snowflake COPY failed")
        val fixture = Fixture(snowflakeFailure = failure)
        exercise(fixture) { flush ->
            fixture.releaseSnowflake.countDown()
            fixture.snowflakeFinished.await()
            // Do not release the normal upload gate: sibling failure cancels that wait.
            // The fake then retains a real open reader in NonCancellable cleanup.
            fixture.readerCleanupEntered.await()
            assertFalse(fixture.releaseArchive.isCompleted)
            fixture.assertPending(flush)
            fixture.releaseReader.complete(Unit)
            assertFailureCause(failure, flush.await().exceptionOrNull())
            fixture.assertCleaned()
            fixture.verifyUploads()
        }
    }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `real archive service waits for both Snowflake and S3 future in either order`(
        archiveFinishesFirst: Boolean,
    ) {
        val uploader = ControlledFusionUploader()
        realArchive(uploader).use { service ->
            val fixture = Fixture(suppliedArchive = service)
            exercise(fixture, releaseUpload = { uploader.close() }) { flush ->
                val upload = withContext(Dispatchers.IO) { uploader.awaitUpload() }
                assertEquals(fixture.path, upload.path)
                assertEquals("1", upload.metadata["record-count"])
                assertEquals("schema-id", upload.metadata["schema-id"])
                assertTrue(upload.key.endsWith(".csv.gz"))
                assertArrayEquals(Files.readAllBytes(fixture.path), upload.bytes)
                if (archiveFinishesFirst) {
                    upload.result.complete(Unit)
                    assertFalse(fixture.snowflakeFinished.isCompleted)
                } else {
                    fixture.releaseSnowflake.countDown()
                    fixture.snowflakeFinished.await()
                    assertFalse(upload.result.isDone)
                }
                fixture.assertPending(flush)
                fixture.releaseSnowflake.countDown()
                upload.result.complete(Unit)
                assertTrue(flush.await().isSuccess)
                fixture.assertCleaned()
                fixture.verifyUploads()
                assertEquals(1, uploader.uploads.size)
                assertTrue(uploader.jsonUploads.isEmpty())
            }
        }
    }

    @Test
    fun `real archive exceptional future propagates after Snowflake success`() {
        val failure = IOException("S3 failed after COPY succeeded")
        val uploader = ControlledFusionUploader()
        realArchive(uploader).use { service ->
            val fixture = Fixture(suppliedArchive = service)
            exercise(fixture, releaseUpload = { uploader.close() }) { flush ->
                val upload = withContext(Dispatchers.IO) { uploader.awaitUpload() }
                fixture.releaseSnowflake.countDown()
                fixture.snowflakeFinished.await()
                fixture.assertPending(flush)
                upload.result.completeExceptionally(failure)
                val thrown = flush.await().exceptionOrNull()
                assertNotNull(thrown)
                // EnabledSnowflakeS3Copy uses Future.get(), which wraps the S3 failure.
                assertFailureCause(failure, thrown)
                fixture.assertCleaned()
                fixture.verifyUploads()
                assertEquals(1, uploader.uploads.size)
            }
        }
    }

    @Test
    fun `real archive pending future retains file after Snowflake failure`() {
        val failure = IOException("Snowflake COPY failed with S3 still pending")
        val uploader = ControlledFusionUploader()
        realArchive(uploader).use { service ->
            val fixture = Fixture(snowflakeFailure = failure, suppliedArchive = service)
            exercise(fixture, releaseUpload = { uploader.close() }) { flush ->
                val upload = withContext(Dispatchers.IO) { uploader.awaitUpload() }
                fixture.releaseSnowflake.countDown()
                fixture.snowflakeFinished.await()
                assertFalse(upload.result.isDone)
                fixture.assertPending(flush)
                assertTrue(
                    Files.exists(upload.path),
                    "The real archive service still owns this file"
                )
                upload.result.complete(Unit)
                val thrown = flush.await().exceptionOrNull()
                assertNotNull(thrown)
                assertFailureCause(failure, thrown)
                fixture.assertCleaned()
                fixture.verifyUploads()
                assertEquals(1, uploader.uploads.size)
            }
        }
    }

    private fun assertFailureCause(expected: Throwable, actual: Throwable?) {
        assertNotNull(actual)
        assertTrue(
            generateSequence(actual) { it.cause }.any { it === expected },
            "The original failure must survive coroutine stack-trace recovery and Future.get wrapping",
        )
    }

    private fun realArchive(uploader: ControlledFusionUploader) =
        EnabledSnowflakeS3Copy(
            config =
                FusionConfiguration(
                    roleArn = "arn:aws:iam::123456789012:role/archive",
                    bucket = "archive",
                    region = "us-east-1",
                    connectionId = UUID(0, 1),
                    workspaceId = UUID(0, 2),
                    sourceId = UUID(0, 3),
                    organizationId = UUID(0, 4),
                    destinationId = UUID(0, 5),
                    prefix = "fusion",
                    externalId = null,
                ),
            columnManager = mockk(relaxed = true),
            snowflakeConfiguration = mockk(relaxed = true),
            uploader = uploader,
        )

    private fun exercise(
        fixture: Fixture,
        releaseUpload: () -> Unit = {},
        assertions: suspend (Deferred<Result<Unit>>) -> Unit,
    ) = runBlocking {
        // Catch inside the child so a flush failure is an observable result, not cancellation
        // of the test driver before it can release the reader gates.
        val flush = async { runCatching { fixture.buffer.flush() } }
        try {
            withTimeout(10_000) {
                fixture.snowflakeEntered.await()
                if (fixture.simulatedReader)
                    assertEquals(fixture.path, fixture.archiveEntered.await())
                assertions(flush)
            }
        } finally {
            fixture.releaseAll()
            releaseUpload()
            withContext(NonCancellable) { flush.cancelAndJoin() }
            fixture.buffer.csvWriter?.close()
            Files.deleteIfExists(fixture.path)
        }
    }

    private class Fixture(
        private val snowflakeFailure: Throwable? = null,
        private val archiveFailure: Throwable? = null,
        suppliedArchive: SnowflakeS3Copy? = null,
    ) {
        private val table = TableName(namespace = "test", name = "dual_upload")
        private val client = mockk<SnowflakeAirbyteClient>()
        val simulatedReader = suppliedArchive == null
        private val archive = suppliedArchive ?: mockk<SnowflakeS3Copy>()
        private val columns =
            listOf(
                "_AIRBYTE_RAW_ID",
                "_AIRBYTE_EXTRACTED_AT",
                "_AIRBYTE_META",
                "_AIRBYTE_GENERATION_ID",
                "VALUE"
            )
        private val schema =
            ColumnSchema(
                inputToFinalColumnNames = mapOf("value" to "VALUE"),
                finalSchema = mapOf("VALUE" to ColumnType("VARCHAR", true)),
                inputSchema = mapOf("value" to FieldType(StringType, nullable = true)),
            )
        private val columnManager =
            mockk<SnowflakeColumnManager> { every { getTableColumnNames(schema) } returns columns }
        private val copyContext =
            CsvCopyContext(
                streamKey = "stream-key",
                generationId = 7,
                syncId = 42,
                schemaId = "schema-id",
                runId = UUID.randomUUID(),
                connectionId = UUID.randomUUID(),
                runPath = "fusion/streams/public/stream/runs/run/1750000000/",
                epochSeconds = 1750000000,
            )
        val snowflakeEntered = CompletableDeferred<Unit>()
        val snowflakeFinished = CompletableDeferred<Unit>()
        val archiveEntered = CompletableDeferred<Path>()
        val archiveFinished = CompletableDeferred<Unit>()
        val readerCleanupEntered = CompletableDeferred<Unit>()
        val releaseSnowflake = CountDownLatch(1)
        val releaseArchive = CompletableDeferred<Unit>()
        val releaseReader = CompletableDeferred<Unit>()
        val buffer =
            SnowflakeInsertBuffer(
                tableName = table,
                snowflakeClient = client,
                snowflakeConfiguration = mockk(relaxed = true),
                columnSchema = schema,
                columnManager = columnManager,
                snowflakeRecordFormatter = SnowflakeSchemaRecordFormatter(),
                s3Copy = archive,
                copyContext = copyContext,
            )
        val path: Path

        init {
            buffer.accumulate(
                mapOf(
                    "VALUE" to StringValue("nonempty payload ☃"),
                    Meta.COLUMN_NAME_AB_RAW_ID to StringValue("raw-id"),
                    Meta.COLUMN_NAME_AB_EXTRACTED_AT to IntegerValue(1234),
                    Meta.COLUMN_NAME_AB_META to StringValue("{}"),
                    Meta.COLUMN_NAME_AB_GENERATION_ID to NullValue,
                )
            )
            path = requireNotNull(buffer.csvFilePath)
            assertEquals(1, buffer.recordCount)
            every { client.putInStage(table, path.toString()) } answers { assertReadablePayload() }
            every { client.copyFromStage(table, path.fileName.toString(), columns) } answers
                {
                    snowflakeEntered.complete(Unit)
                    try {
                        check(releaseSnowflake.await(10, TimeUnit.SECONDS)) {
                            "Snowflake gate timed out"
                        }
                        assertReadablePayload()
                        snowflakeFailure?.let { throw it }
                    } finally {
                        snowflakeFinished.complete(Unit)
                    }
                }
            if (simulatedReader)
                coEvery { archive.upload(path, copyContext, 1, any()) } coAnswers
                    {
                        try {
                            GZIPInputStream(Files.newInputStream(path)).use { reader ->
                                // Keep a real partially consumed gzip reader alive through
                                // cancellation.
                                assertTrue(reader.read() >= 0)
                                archiveEntered.complete(path)
                                try {
                                    releaseArchive.await()
                                    archiveFailure?.let { throw it }
                                } finally {
                                    withContext(NonCancellable) {
                                        readerCleanupEntered.complete(Unit)
                                        withTimeout(10_000) { releaseReader.await() }
                                        assertTrue(
                                            Files.exists(path),
                                            "Buffer deleted a live reader's file"
                                        )
                                        assertTrue(reader.readBytes().isNotEmpty())
                                    }
                                }
                            }
                        } finally {
                            archiveFinished.complete(Unit)
                        }
                    }
        }

        fun releaseAll() {
            releaseSnowflake.countDown()
            releaseArchive.complete(Unit)
            releaseReader.complete(Unit)
        }

        fun assertPending(flush: Deferred<Result<Unit>>) {
            assertFalse(flush.isCompleted, "Flush completed while an upload still owned the file")
            assertEquals(path, buffer.csvFilePath)
            assertEquals(1, buffer.recordCount)
            assertNotNull(buffer.csvWriter)
            assertReadablePayload()
        }

        fun assertCleaned() {
            assertTrue(snowflakeFinished.isCompleted)
            if (simulatedReader) assertTrue(archiveFinished.isCompleted)
            assertFalse(Files.exists(path))
            assertNull(buffer.csvFilePath)
            assertNull(buffer.csvWriter)
            assertEquals(0, buffer.recordCount)
        }

        fun verifyUploads() {
            verify(exactly = 1) { client.putInStage(table, path.toString()) }
            verify(exactly = 1) { client.copyFromStage(table, path.fileName.toString(), columns) }
            if (simulatedReader)
                coVerify(exactly = 1) { archive.upload(path, copyContext, 1, any()) }
        }

        private fun assertReadablePayload() {
            assertTrue(Files.exists(path))
            val csv =
                GZIPInputStream(Files.newInputStream(path)).bufferedReader(Charsets.UTF_8).use {
                    it.readText()
                }
            assertTrue(csv.contains("nonempty payload ☃"))
            assertEquals(1, csv.lineSequence().count { it.isNotEmpty() })
        }
    }
}
