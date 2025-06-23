/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce.http.job

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Response
import io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.job.Job
import io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.job.JobRepository
import io.mockk.every
import io.mockk.mockk
import java.io.InputStream
import kotlin.test.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class JobRepositoryTest {
    private val BASE_URL: String = "https://base-url.com"
    private val A_JOB_ID: String = "aJobId"
    private val AN_EXTERNAL_ID_FIELD: String = "anExternalIdField"
    private val DESTINATION_OBJECT_NAME: String = "destinationObjectName"
    private lateinit var httpClient: HttpClient
    private lateinit var repo: JobRepository

    @BeforeEach
    fun setUp() {
        httpClient = mockk()
        repo = JobRepository(httpClient, { BASE_URL })
    }

    @Test
    internal fun `test given append when create then create insert job`() {
        every {
            httpClient.send(
                match {
                    it.url == "$BASE_URL/services/data/v62.0/jobs/ingest" &&
                        (it.body?.toString(Charsets.UTF_8) ?: "").contains("insert")
                }
            )
        } returns aResponse(200, """{"id": "$A_JOB_ID"}""".byteInputStream())
        every {
            httpClient.send(
                match { it.url == "$BASE_URL/services/data/v62.0/jobs/ingest/$A_JOB_ID/batches" }
            )
        } returns aResponse(201, """{"any": "request body"}""".byteInputStream())

        val job = repo.create(aStream(Append), "aBatch".toByteArray())

        assertEquals(Job(A_JOB_ID), job)
    }

    @Test
    internal fun `test given dedupe when create then create upsert job with external id`() {
        every {
            httpClient.send(
                match {
                    val bodyAsString = it.body?.toString(Charsets.UTF_8) ?: ""
                    it.url == "$BASE_URL/services/data/v62.0/jobs/ingest" &&
                        bodyAsString.contains("upsert") &&
                        bodyAsString.contains(AN_EXTERNAL_ID_FIELD)
                }
            )
        } returns aResponse(200, """{"id": "$A_JOB_ID"}""".byteInputStream())
        every {
            httpClient.send(
                match { it.url == "$BASE_URL/services/data/v62.0/jobs/ingest/$A_JOB_ID/batches" }
            )
        } returns aResponse(201, """{"any": "request body"}""".byteInputStream())

        val job =
            repo.create(
                aStream(
                    Dedupe(emptyList<List<String>>(), emptyList()),
                    listOf(AN_EXTERNAL_ID_FIELD)
                ),
                "aBatch".toByteArray()
            )

        assertEquals(Job(A_JOB_ID), job)
    }

    @Test
    internal fun `test given update when create then create update job`() {
        every {
            httpClient.send(
                match {
                    it.url == "$BASE_URL/services/data/v62.0/jobs/ingest" &&
                        (it.body?.toString(Charsets.UTF_8) ?: "").contains("update")
                }
            )
        } returns aResponse(200, """{"id": "$A_JOB_ID"}""".byteInputStream())
        every {
            httpClient.send(
                match { it.url == "$BASE_URL/services/data/v62.0/jobs/ingest/$A_JOB_ID/batches" }
            )
        } returns aResponse(201, """{"any": "request body"}""".byteInputStream())

        val job = repo.create(aStream(Update), "aBatch".toByteArray())

        assertEquals(Job(A_JOB_ID), job)
    }

    @Test
    internal fun `test given soft delete when create then create delete job`() {
        every {
            httpClient.send(
                match {
                    it.url == "$BASE_URL/services/data/v62.0/jobs/ingest" &&
                        (it.body?.toString(Charsets.UTF_8) ?: "").contains("delete")
                }
            )
        } returns aResponse(200, """{"id": "$A_JOB_ID"}""".byteInputStream())
        every {
            httpClient.send(
                match { it.url == "$BASE_URL/services/data/v62.0/jobs/ingest/$A_JOB_ID/batches" }
            )
        } returns aResponse(201, """{"any": "request body"}""".byteInputStream())

        val job = repo.create(aStream(SoftDelete), "aBatch".toByteArray())

        assertEquals(Job(A_JOB_ID), job)
    }

    private fun aStream(
        importType: ImportType,
        matchingKey: List<String>? = null
    ): DestinationStream {
        return DestinationStream(
            "a_namespace",
            "test_stream",
            importType,
            ObjectType(
                linkedMapOf(
                    "Id" to FieldType(StringType, nullable = true),
                    "Title" to FieldType(StringType, nullable = true)
                )
            ),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 42,
            destinationObjectName = DESTINATION_OBJECT_NAME,
            matchingKey = matchingKey,
            namespaceMapper = NamespaceMapper()
        )
    }

    private fun aResponse(statusCode: Int, body: InputStream): Response {
        val response = mockk<Response>()
        every { response.statusCode } returns statusCode
        every { response.body } returns body
        every { response.close() } returns Unit
        return response
    }
}
