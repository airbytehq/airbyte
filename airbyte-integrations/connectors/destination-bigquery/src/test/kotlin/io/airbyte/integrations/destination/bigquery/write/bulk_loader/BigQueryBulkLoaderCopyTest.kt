/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.bulk_loader

import com.google.cloud.RetryOption
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.Schema
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.airbyte.integrations.destination.bigquery.copy.BigqueryCopyContext
import io.airbyte.integrations.destination.bigquery.copy.BigqueryS3Copy
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryRegion
import io.airbyte.integrations.destination.bigquery.spec.GcsFilePostProcessing
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.util.UUID
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.async
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class BigQueryBulkLoaderCopyTest {
    @ParameterizedTest
    @EnumSource(GcsFilePostProcessing::class)
    fun `successful BigQuery job waits for archive before postprocessing and return`(
        postProcessing: GcsFilePostProcessing
    ) = runTest {
        val fixture = BigQueryCopyLoadFixture(postProcessing)
        val load = async { fixture.loader.load(fixture.blob) }
        fixture.archiveEntered.await()
        assertFalse(load.isCompleted)
        coVerify(exactly = 0) { fixture.storage.delete(any<GcsBlob>()) }
        verify(exactly = 1) { fixture.bigQuery.create(any<JobInfo>()) }
        coVerify(exactly = 1) {
            fixture.archive.copyCompletedGcsObject(
                fixture.storage,
                fixture.blob,
                fixture.context,
                7L,
            )
        }

        fixture.archiveResult.complete(Unit)
        load.await()
        assertEquals(
            if (postProcessing == GcsFilePostProcessing.DELETE) {
                listOf("archive", "delete")
            } else {
                listOf("archive")
            },
            fixture.events,
        )
        verify(exactly = 1) { fixture.bigQuery.create(any<JobInfo>()) }
    }

    @Test
    fun `archive failure retains GCS and does not resubmit successful BigQuery job`() = runTest {
        val fixture = BigQueryCopyLoadFixture()
        val failure = IllegalStateException("archive multipart completion failed")
        val load = async { runCatching { fixture.loader.load(fixture.blob) } }
        fixture.archiveEntered.await()
        fixture.archiveResult.completeExceptionally(failure)
        val actual = load.await().exceptionOrNull()
        assertEquals(failure::class, actual!!::class)
        assertEquals(failure.message, actual.message)
        coVerify(exactly = 0) { fixture.storage.delete(any<GcsBlob>()) }
        verify(exactly = 1) { fixture.bigQuery.create(any<JobInfo>()) }
    }

    @Test
    fun `cancellation while archiving retains GCS`() = runTest {
        val fixture = BigQueryCopyLoadFixture()
        val load = async { fixture.loader.load(fixture.blob) }
        fixture.archiveEntered.await()
        load.cancel(CancellationException("sync cancelled"))
        load.join()
        assertTrue(load.isCancelled)
        coVerify(exactly = 0) { fixture.storage.delete(any<GcsBlob>()) }
        verify(exactly = 1) { fixture.bigQuery.create(any<JobInfo>()) }
    }

    @Test
    fun `failed BigQuery job cannot archive or delete`() = runTest {
        val fixture = BigQueryCopyLoadFixture()
        fixture.failBigQuery()
        assertNotNull(runCatching { fixture.loader.load(fixture.blob) }.exceptionOrNull())
        coVerify(exactly = 0) {
            fixture.archive.copyCompletedGcsObject(any(), any(), any(), any())
            fixture.storage.delete(any<GcsBlob>())
        }
        verify(exactly = 1) { fixture.bigQuery.create(any<JobInfo>()) }
    }

    @Test
    fun `nonzero bad records cannot archive or delete`() = runTest {
        val fixture = BigQueryCopyLoadFixture()
        every { fixture.statistics.badRecords } returns 1L
        val failure = runCatching { fixture.loader.load(fixture.blob) }.exceptionOrNull()
        assertTrue(failure?.message.orEmpty().contains("Nonzero bad records"))
        coVerify(exactly = 0) {
            fixture.archive.copyCompletedGcsObject(any(), any(), any(), any())
            fixture.storage.delete(any<GcsBlob>())
        }
    }

    @Test
    fun `delete failure propagates after archive without repeating BigQuery load`() = runTest {
        val fixture = BigQueryCopyLoadFixture()
        val failure = IllegalStateException("GCS deletion failed")
        coEvery { fixture.storage.delete(fixture.blob) } throws failure
        fixture.archiveResult.complete(Unit)
        assertSame(failure, runCatching { fixture.loader.load(fixture.blob) }.exceptionOrNull())
        assertEquals(listOf("archive"), fixture.events)
        verify(exactly = 1) { fixture.bigQuery.create(any<JobInfo>()) }
    }

    @Test
    fun `null context preserves existing load without invoking archive`() = runTest {
        val fixture = BigQueryCopyLoadFixture()
        fixture.newLoader(withContext = false).load(fixture.blob)
        runCurrent()
        assertEquals(listOf("delete"), fixture.events)
        coVerify(exactly = 0) { fixture.archive.copyCompletedGcsObject(any(), any(), any(), any()) }
    }
}

/** Shared with the checkpoint tests so their gate is the real BigQuery loader's archive call. */
internal class BigQueryCopyLoadFixture(
    postProcessing: GcsFilePostProcessing = GcsFilePostProcessing.DELETE,
    objectKey: String = "staging/input.csv.gz",
) {
    val storage = mockk<GcsClient>()
    val bigQuery = mockk<BigQuery>()
    val archive = mockk<BigqueryS3Copy>()
    val job = mockk<Job>(relaxed = true)
    val statistics = mockk<JobStatistics.LoadStatistics>()
    val blob = GcsBlob(objectKey, mockk { every { gcsBucketName } returns "staging-bucket" })
    val context =
        BigqueryCopyContext("stream-key", 42L, 101L, "schema-id", UUID.randomUUID(), "run/path")
    val archiveEntered = CompletableDeferred<Unit>()
    val archiveResult = CompletableDeferred<Unit>()
    val events = mutableListOf<String>()
    private val config =
        mockk<BigqueryConfiguration> {
            every { jobProjectId } returns "job-project"
            every { datasetLocation } returns BigqueryRegion.US
            every { loadingMethod } returns GcsStagingConfiguration(mockk(), postProcessing)
        }

    init {
        every { bigQuery.create(any<JobInfo>()) } returns job
        every { job.waitFor(any<RetryOption>()) } returns job
        every { job.status.error } returns null
        every { job.reload() } returns job
        every { job.getStatistics<JobStatistics.LoadStatistics>() } returns statistics
        every { statistics.outputRows } returns 7L
        every { statistics.badRecords } returns 0L
        coEvery { archive.copyCompletedGcsObject(storage, blob, context, 7L) } coAnswers
            {
                archiveEntered.complete(Unit)
                archiveResult.await()
                events.add("archive")
                Unit
            }
        coEvery { storage.delete(blob) } coAnswers
            {
                events.add("delete")
                Unit
            }
    }

    val loader = newLoader()

    fun newLoader(withContext: Boolean = true) =
        BigQueryBulkLoader(
            storage,
            bigQuery,
            config,
            TableId.of("dataset", "table"),
            Schema.of(),
            archive,
            if (withContext) context else null,
        )

    fun failBigQuery() {
        every { job.status.error } returns BigQueryError("invalid", "load", "load failed")
    }
}
