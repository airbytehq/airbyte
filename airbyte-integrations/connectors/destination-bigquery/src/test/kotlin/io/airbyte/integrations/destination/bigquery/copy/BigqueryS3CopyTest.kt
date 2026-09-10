/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.implementor.SetupTask
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsFilePostProcessing
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.nio.file.Files
import java.nio.file.Path
import java.util.UUID
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit
import java.util.zip.GZIPOutputStream
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

class BigqueryS3CopyTest {
    @TempDir lateinit var directory: Path

    @Test
    fun `disabled writes and all nonwrite operations ignore enabled-only configuration`() {
        val enabledFactory = mockk<(S3CopyConfiguration) -> BigqueryS3Copy>()
        for (operation in listOf("spec", "check", "discover")) {
            assertSame(
                DisabledBigqueryS3Copy,
                BigqueryS3CopyFactory.createForOperation(
                    operation,
                    mapOf("AIRBYTE_S3_COPY_ENABLED" to "invalid"),
                    enabledFactory,
                ),
            )
        }
        assertSame(
            DisabledBigqueryS3Copy,
            BigqueryS3CopyFactory.createForOperation(
                "write",
                mapOf("AIRBYTE_S3_COPY_ROLE_ARN" to "invalid"),
                enabledFactory,
            ),
        )
        verify(exactly = 0) { enabledFactory.invoke(any()) }
    }

    @Test
    fun `zero row refresh writes schema then cutoff once before writer setup completes`() =
        runBlocking {
            val fixture = Fixture(minimumGeneration = 5)
            fixture.archive.use { archive ->
                val delegate = mockk<DestinationWriter>(relaxed = true)
                val writer = BigqueryCopyWriter(delegate, fixture.catalog, archive)
                writer.setup()
                archive.prepare(fixture.catalog)
                assertEquals(
                    listOf("schema.json", "generation-cutoff.json"),
                    fixture.uploader.objects.map { it.key.substringAfterLast('/') },
                )
                assertEquals(1, fixture.uploader.credentialsChecks)
                assertEquals("schema-hash", archive.context(fixture.stream).schemaId)
                coVerify(exactly = 1) { delegate.setup() }
            }
            assertEmptyDirectory()
        }

    @Test
    fun `invalid strategy or duplicate stream name fails before database setup or AWS`() =
        runBlocking {
            val fixture = Fixture()
            fixture.archive.use { archive ->
                every { fixture.configuration.loadingMethod } returns
                    BatchedStandardInsertConfiguration
                val delegate = mockk<DestinationWriter>(relaxed = true)
                val result = runCatching {
                    BigqueryCopyWriter(delegate, fixture.catalog, archive).setup()
                }
                assertInstanceOf(SystemErrorException::class.java, result.exceptionOrNull())
                coVerify(exactly = 0) { delegate.setup() }
                assertEquals(0, fixture.uploader.credentialsChecks)
            }
            val other = Fixture()
            other.archive.use { archive ->
                val duplicate = other.stream.copy(unmappedNamespace = "another")
                assertThrows(SystemErrorException::class.java) {
                    archive.validate(DestinationCatalog(listOf(other.stream, duplicate)))
                }
                assertEquals(0, other.uploader.credentialsChecks)
            }
        }

    @Test
    fun `metadata failure never publishes a run context and closes uploader`() = runBlocking {
        val fixture = Fixture()
        val failure = IllegalStateException("metadata failed")
        fixture.uploader.beforeUpload = { throw failure }
        val writer = BigqueryCopyWriter(mockk(relaxed = true), fixture.catalog, fixture.archive)
        val thrown = runCatching { writer.setup() }.exceptionOrNull()
        assertInstanceOf(SystemErrorException::class.java, thrown)
        assertTrue(generateSequence(thrown) { it.cause }.any { it.message == failure.message })
        assertThrows(IllegalStateException::class.java) { fixture.archive.context(fixture.stream) }
        assertTrue(fixture.uploader.closed)
        assertEmptyDirectory()
    }

    @Test
    fun `cutoff failure on zero records prevents actual setup task from launching streams`() =
        runBlocking {
            val fixture = Fixture(minimumGeneration = 5)
            val launcher = mockk<DestinationTaskLauncher>(relaxed = true)
            fixture.uploader.beforeUpload = {
                if (fixture.uploader.objects.isNotEmpty()) error("cutoff refused")
            }
            val writer = BigqueryCopyWriter(mockk(relaxed = true), fixture.catalog, fixture.archive)
            val result = runCatching { SetupTask(writer, launcher).execute() }
            assertInstanceOf(SystemErrorException::class.java, result.exceptionOrNull())
            assertEquals(
                listOf("schema.json"),
                fixture.uploader.objects.map { it.key.substringAfterLast('/') },
            )
            coVerify(exactly = 0) { launcher.handleSetupComplete() }
            assertTrue(fixture.uploader.closed)
            assertEmptyDirectory()
        }

    @Test
    fun `copies exact compressed bytes with durable routing and loaded output count`() =
        runBlocking {
            val fixture = Fixture()
            fixture.archive.use { archive ->
                archive.prepare(fixture.catalog)
                val bytes = gzip("\"id\",\"text\"\r\n\"1\",\"Unicode ☃, newline\nquote \"\"\"\r\n")
                val storage = fixture.storage(bytes)
                archive.copyCompletedGcsObject(
                    storage,
                    fixture.blob,
                    archive.context(fixture.stream),
                    1,
                )
                val copied = fixture.uploader.objects.last()
                assertArrayEquals(bytes, copied.bytes)
                assertEquals("application/gzip", copied.contentType)
                assertEquals("1", copied.metadata["loaded-record-count"])
                assertEquals(fixture.config.sourceId.toString(), copied.metadata["source-id"])
                assertTrue(copied.key.startsWith("fusion/test-run/batches/"))
                assertTrue(copied.key.endsWith(".csv.gz"))
                coVerify(exactly = 0) { storage.delete(any<GcsBlob>()) }
            }
            assertEmptyDirectory()
        }

    @Test
    fun `all streams and socket partitions share four transfer slots`() = runBlocking {
        withTimeout(10_000) {
            val fixture = Fixture()
            fixture.archive.use { archive ->
                archive.prepare(fixture.catalog)
                val release = CompletableDeferred<Unit>()
                val fourEntered = CompletableDeferred<Unit>()
                val paths = CopyOnWriteArrayList<Path>()
                fixture.uploader.beforeUpload = { path ->
                    paths.add(path)
                    if (paths.size == 4) fourEntered.complete(Unit)
                    release.await()
                }
                val tasks =
                    (1..6).map {
                        async {
                            archive.copyCompletedGcsObject(
                                fixture.storage(gzip("header\r\n")),
                                fixture.blob,
                                archive.context(fixture.stream),
                                0,
                            )
                        }
                    }
                fourEntered.await()
                delay(50)
                assertEquals(4, paths.size)
                assertEquals(4L, Files.list(directory).use { it.count() })
                release.complete(Unit)
                tasks.awaitAll()
                assertEquals(6, paths.size)
                assertEquals(
                    6,
                    fixture.uploader.objects
                        .filter { it.contentType == "application/gzip" }
                        .map { it.key }
                        .toSet()
                        .size,
                )
            }
        }
        assertEmptyDirectory()
    }

    @Test
    fun `cancellation waits for uploader cleanup before unlinking spool`() = runBlocking {
        val fixture = Fixture()
        fixture.archive.use { archive ->
            archive.prepare(fixture.catalog)
            val entered = CompletableDeferred<Path>()
            var presentInCleanup = false
            fixture.uploader.beforeUpload = { path ->
                entered.complete(path)
                try {
                    awaitCancellation()
                } finally {
                    presentInCleanup = Files.exists(path)
                }
            }
            val task = async {
                archive.copyCompletedGcsObject(
                    fixture.storage(gzip("header\r\n")),
                    fixture.blob,
                    archive.context(fixture.stream),
                    0,
                )
            }
            val path = entered.await()
            task.cancelAndJoin()
            assertTrue(presentInCleanup)
            assertFalse(Files.exists(path))
        }
    }

    @Test
    fun `unproven reader shutdown retains file and prevents further spools`() = runBlocking {
        val fixture = Fixture()
        fixture.archive.use { archive ->
            archive.prepare(fixture.catalog)
            val context = archive.context(fixture.stream)
            fixture.uploader.beforeUpload = { path ->
                throw ArchiveReaderStillActiveException(path, IllegalStateException("reader alive"))
            }
            val result = runCatching {
                archive.copyCompletedGcsObject(
                    fixture.storage(gzip("header\r\n")),
                    fixture.blob,
                    context,
                    0,
                )
            }
            assertInstanceOf(
                ArchiveReaderStillActiveException::class.java,
                result.exceptionOrNull()?.cause,
            )
            assertEquals(1L, Files.list(directory).use { it.count() })
            assertTrue(
                runCatching {
                        archive.copyCompletedGcsObject(
                            fixture.storage(gzip("header\r\n")),
                            fixture.blob,
                            context,
                            0,
                        )
                    }
                    .isFailure
            )
            assertEquals(1L, Files.list(directory).use { it.count() })
        }
    }

    @Test
    fun `teardown closes archive even when table finalization fails`() = runBlocking {
        val delegate = mockk<DestinationWriter>()
        val archive = mockk<BigqueryS3Copy>(relaxed = true)
        val failure = IllegalStateException("swap failed")
        coEvery { delegate.teardown(any()) } throws failure
        val catalog = Fixture().also { it.archive.close() }.catalog
        assertSame(
            failure,
            runCatching { BigqueryCopyWriter(delegate, catalog, archive).teardown(null) }
                .exceptionOrNull(),
        )
        verify(exactly = 1) { archive.close() }
    }

    @Test
    fun `wrapped or suppressed reader failures preserve spool even with an exception cycle`() =
        runBlocking {
            val fixture = Fixture()
            fixture.archive.use { archive ->
                archive.prepare(fixture.catalog)
                val context = archive.context(fixture.stream)
                fixture.uploader.beforeUpload = { path ->
                    val wrapper = IllegalStateException("outer")
                    val unsafe = ArchiveReaderStillActiveException(path, wrapper)
                    wrapper.addSuppressed(unsafe)
                    throw wrapper
                }
                assertTrue(
                    runCatching {
                            archive.copyCompletedGcsObject(
                                fixture.storage(gzip("header\r\n")),
                                fixture.blob,
                                context,
                                0,
                            )
                        }
                        .isFailure
                )
                assertEquals(1L, Files.list(directory).use { it.count() })
                assertThrows(IllegalStateException::class.java) { archive.context(fixture.stream) }
            }
        }

    @Test
    fun `close during uploader construction closes the late client before it can upload`() =
        runBlocking {
            val fixture = Fixture()
            fixture.archive.close()
            val entered = CountDownLatch(1)
            val release = CountDownLatch(1)
            val archive =
                EnabledBigqueryS3Copy(
                    fixture.config,
                    fixture.configuration,
                    fixture.metadata,
                    fixture.runId,
                    {
                        entered.countDown()
                        check(release.await(10, TimeUnit.SECONDS))
                        fixture.uploader
                    },
                    spoolDirectory = directory,
                )
            try {
                val preparation =
                    async(Dispatchers.IO) { runCatching { archive.prepare(fixture.catalog) } }
                withContext(Dispatchers.IO) { assertTrue(entered.await(10, TimeUnit.SECONDS)) }
                archive.close()
                assertFalse(archive.metadataReady())
                release.countDown()
                assertTrue(preparation.await().isFailure)
                assertTrue(fixture.uploader.closed)
                assertEquals(0, fixture.uploader.credentialsChecks)
                assertTrue(fixture.uploader.objects.isEmpty())
            } finally {
                release.countDown()
                archive.close()
            }
        }

    @Test
    fun `failed sync still signals completion when archive cleanup fails`() = runBlocking {
        val fixture = Fixture()
        fixture.archive.close()
        val archive = mockk<BigqueryS3Copy>()
        every { archive.close() } throws IllegalStateException("close failed")
        val delegate = mockk<DestinationWriter>(relaxed = true)
        val launcher = mockk<DestinationTaskLauncher>(relaxed = true)
        val sync = mockk<io.airbyte.cdk.load.state.SyncManager>()
        val checkpoints = mockk<io.airbyte.cdk.load.state.CheckpointManager>(relaxed = true)
        val failure = mockk<io.airbyte.cdk.load.state.DestinationFailure>(relaxed = true)
        coEvery { sync.markDestinationFailed(any()) } returns failure
        io.airbyte.cdk.load.task.implementor
            .FailSyncTask(
                launcher,
                BigqueryCopyWriter(delegate, fixture.catalog, archive),
                IllegalStateException("original failure"),
                sync,
                checkpoints,
            )
            .execute()
        coVerify(exactly = 1) { launcher.handleTeardownComplete(success = false) }
        coVerify(exactly = 1) { delegate.teardown(failure) }
    }

    private fun assertEmptyDirectory() = assertEquals(0L, Files.list(directory).use { it.count() })

    private inner class Fixture(minimumGeneration: Long = 0) {
        val config =
            S3CopyConfiguration(
                "archive",
                "us-east-2",
                "arn:aws:iam::123456789012:role/archive",
                UUID.randomUUID(),
                UUID.randomUUID(),
                UUID.randomUUID(),
            )
        val configuration = mockk<BigqueryConfiguration>()
        val runId = UUID.randomUUID()
        val stream =
            DestinationStream(
                "namespace",
                "stream",
                Append,
                ObjectType(linkedMapOf("id" to FieldType(StringType, true))),
                5,
                minimumGeneration,
                12,
                namespaceMapper = NamespaceMapper(),
            )
        val catalog = DestinationCatalog(listOf(stream))
        val metadata = mockk<BigqueryCopyMetadata>()
        val uploader = CapturingUploader()
        val blob = GcsBlob("completed.csv.gz", mockk())

        init {
            every { configuration.loadingMethod } returns
                GcsStagingConfiguration(mockk(), GcsFilePostProcessing.DELETE)
            every { metadata.descriptor(stream) } returns mapOf("schema_id" to "schema-hash")
            every { metadata.runPath(stream) } returns "fusion/test-run"
            every { metadata.streamKey(stream) } returns "stream-hash"
            every { metadata.cutoff(stream) } returns
                mapOf("minimum_generation_id" to minimumGeneration)
            every { metadata.serialize(any()) } answers
                {
                    com.fasterxml.jackson.databind.ObjectMapper().writeValueAsBytes(firstArg<Any>())
                }
        }

        val archive =
            EnabledBigqueryS3Copy(
                config,
                configuration,
                metadata,
                runId,
                { uploader },
                spoolDirectory = directory,
            )

        fun storage(bytes: ByteArray): GcsClient =
            mockk<GcsClient>().also { client ->
                coEvery { client.get<Long>(blob.key, any()) } coAnswers
                    {
                        secondArg<(InputStream) -> Long>().invoke(ByteArrayInputStream(bytes))
                    }
            }
    }

    private data class Uploaded(
        val key: String,
        val bytes: ByteArray,
        val contentType: String,
        val metadata: Map<String, String>,
    )

    private class CapturingUploader : ArchiveUploader {
        var credentialsChecks = 0
        var closed = false
        var beforeUpload: suspend (Path) -> Unit = {}
        val objects = CopyOnWriteArrayList<Uploaded>()

        override suspend fun validateCredentials() {
            credentialsChecks++
        }

        override suspend fun upload(
            path: Path,
            key: String,
            contentType: String,
            metadata: Map<String, String>,
        ) {
            beforeUpload(path)
            objects.add(Uploaded(key, Files.readAllBytes(path), contentType, metadata))
        }

        override fun close() {
            closed = true
        }
    }

    private fun gzip(text: String): ByteArray =
        ByteArrayOutputStream()
            .also { output ->
                GZIPOutputStream(output).use { it.write(text.toByteArray(Charsets.UTF_8)) }
            }
            .toByteArray()
}
