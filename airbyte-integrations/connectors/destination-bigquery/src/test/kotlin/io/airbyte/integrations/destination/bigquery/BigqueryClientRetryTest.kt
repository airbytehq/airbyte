/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery

import com.google.api.client.http.LowLevelHttpRequest
import com.google.api.client.testing.http.MockHttpTransport
import com.google.api.client.testing.http.MockLowLevelHttpRequest
import com.google.api.client.testing.http.MockLowLevelHttpResponse
import com.google.cloud.NoCredentials
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.http.HttpTransportOptions
import io.airbyte.cdk.load.orchestration.db.Sql
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.BigQueryDatabaseHandler
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class BigqueryClientRetryTest {
    @ParameterizedTest
    @ValueSource(ints = [500, 502, 503, 504])
    fun `getJob retries a retryable 5xx backendError and then succeeds`(statusCode: Int) {
        val failedAttempts = if (statusCode == 503) 2 else 1
        val transport =
            ScriptedHttpTransport(
                List(failedAttempts) { backendErrorResponse(statusCode) } +
                    response(200, jobJson("test-project", TEST_JOB_ID)),
            )
        val bigquery = bigqueryClient(transport)

        val job = bigquery.getJob(TEST_JOB_ID)

        assertNotNull(job)
        assertEquals(TEST_JOB_ID, job.jobId.job)
        assertEquals(failedAttempts + 1, transport.requests.size)
    }

    @Test
    fun `getJob does not retry a 400`() {
        val transport =
            ScriptedHttpTransport(
                listOf(
                    response(
                        400,
                        """{"error":{"code":400,"errors":[{"domain":"global","message":"Invalid request","reason":"invalid"}],"message":"Invalid request","status":"INVALID_ARGUMENT"}}""",
                    ),
                ),
            )
        val bigquery = bigqueryClient(transport)

        val exception = assertThrows<BigQueryException> { bigquery.getJob(TEST_JOB_ID) }

        assertEquals(400, exception.code)
        assertEquals(1, transport.requests.size)
    }

    @Test
    fun `create retries jobs insert with the same job id`() {
        val transport =
            ScriptedHttpTransport(
                listOf(
                    backendErrorResponse(503),
                    response(200, jobJson("test-project", "fixed-job-id")),
                ),
            )
        val bigquery = bigqueryClient(transport)

        bigquery.create(
            JobInfo.of(
                JobId.newBuilder().setJob("fixed-job-id").setLocation("US").build(),
                QueryJobConfiguration.of("SELECT 1"),
            ),
        )

        assertEquals(2, transport.requests.size)
        assertTrue(transport.requests.all { it.method == "POST" })
        assertTrue(transport.requests.all { it.body.contains("fixed-job-id") })
    }

    @Test
    fun `job project client retries 503`() {
        val transport =
            ScriptedHttpTransport(
                listOf(
                    backendErrorResponse(503),
                    response(200, jobJson("other-project", TEST_JOB_ID)),
                ),
            )
        val mainClient = bigqueryClient(transport)
        val config: BigqueryConfiguration = mockk {
            every { projectId } returns "test-project"
            every { jobProjectId } returns "other-project"
        }
        val jobProjectClient =
            BigqueryBeansFactory().getJobProjectBigqueryClient(config, mainClient)

        val job = jobProjectClient.getJob(TEST_JOB_ID)

        assertNotNull(job)
        assertEquals(TEST_JOB_ID, job.jobId.job)
        assertEquals(2, transport.requests.size)
        assertTrue(transport.requests.all { it.url.contains("other-project") })
    }

    @Test
    fun `execute waits on the existing job when a retried jobs insert gets 409`() {
        val now = System.currentTimeMillis()
        val transport =
            ScriptedHttpTransport(
                listOf(
                    backendErrorResponse(503),
                    response(
                        409,
                        """{"error":{"code":409,"errors":[{"domain":"global","message":"Already Exists: Job test-project:US.some-job","reason":"duplicate"}],"message":"Already Exists: Job test-project:US.some-job","status":"ALREADY_EXISTS"}}""",
                    ),
                    response(
                        200,
                        """{"jobReference":{"projectId":"test-project","jobId":"some-job","location":"US"},"configuration":{"query":{"query":"SELECT 1"}},"statistics":{"creationTime":"$now"}}""",
                    ),
                    response(
                        200,
                        """{"jobReference":{"projectId":"test-project","jobId":"some-job","location":"US"},"configuration":{"query":{"query":"SELECT 1"}},"statistics":{"creationTime":"$now","startTime":"$now","endTime":"$now","query":{}},"status":{"state":"DONE"}}""",
                    ),
                ),
            )
        val bigquery = bigqueryClient(transport)
        val handler = BigQueryDatabaseHandler(bigquery, bigquery, "US", "test-project")

        handler.execute(Sql.of("SELECT 1"))

        val posts = transport.requests.filter { it.method == "POST" }
        assertEquals(2, posts.size)
        val jobIds = posts.map { JOB_ID_REGEX.find(it.body)?.groupValues?.get(1) }
        assertNotNull(jobIds[0])
        assertEquals(jobIds[0], jobIds[1])
        assertEquals(4, transport.requests.size)
    }

    @Test
    fun `job project client sends the Airbyte user agent`() {
        val transport =
            ScriptedHttpTransport(listOf(response(200, jobJson("other-project", TEST_JOB_ID))))
        val mainClient = bigqueryClient(transport)
        val config: BigqueryConfiguration = mockk {
            every { projectId } returns "test-project"
            every { jobProjectId } returns "other-project"
        }
        val jobProjectClient =
            BigqueryBeansFactory().getJobProjectBigqueryClient(config, mainClient)

        jobProjectClient.getJob(TEST_JOB_ID)

        val userAgent =
            transport.requests.single().headers.entries.firstOrNull {
                it.key.equals("user-agent", ignoreCase = true)
            }
        assertNotNull(userAgent)
        assertTrue(userAgent!!.value.any { it.contains("airbyte", ignoreCase = true) })
    }

    private fun bigqueryClient(transport: ScriptedHttpTransport): BigQuery =
        bigqueryOptionsBuilder("test-project", NoCredentials.getInstance())
            .setTransportOptions(
                HttpTransportOptions.newBuilder().setHttpTransportFactory { transport }.build(),
            )
            .build()
            .service

    private fun backendErrorResponse(statusCode: Int): ScriptedResponse =
        response(
            statusCode,
            """{"error":{"code":$statusCode,"errors":[{"domain":"global","message":"Error encountered during execution. Retrying may solve the problem.","reason":"backendError"}],"message":"Error encountered during execution. Retrying may solve the problem.","status":"UNAVAILABLE"}}""",
        )

    private fun response(statusCode: Int, body: String) = ScriptedResponse(statusCode, body)

    private fun jobJson(projectId: String, jobId: String) =
        """{"jobReference":{"projectId":"$projectId","jobId":"$jobId","location":"US"},"status":{"state":"DONE"}}"""

    private data class ScriptedResponse(val statusCode: Int, val body: String)

    private data class RecordedRequest(
        val method: String,
        val url: String,
        val body: String,
        val headers: Map<String, List<String>>,
    )

    private class ScriptedHttpTransport(private val responses: List<ScriptedResponse>) :
        MockHttpTransport() {
        val requests = mutableListOf<RecordedRequest>()
        private var nextResponseIndex = 0

        override fun buildRequest(method: String, url: String): LowLevelHttpRequest {
            val response = responses[nextResponseIndex++]
            return object : MockLowLevelHttpRequest(url) {
                override fun execute(): MockLowLevelHttpResponse {
                    requests += RecordedRequest(method, url, contentAsString.orEmpty(), headers)
                    return MockLowLevelHttpResponse()
                        .setStatusCode(response.statusCode)
                        .setContentType("application/json")
                        .setContent(response.body)
                }
            }
        }
    }

    private companion object {
        const val TEST_JOB_ID = "test-job-id"
        val JOB_ID_REGEX = Regex(""""jobId"\s*:\s*"([^"]+)"""")
    }
}
