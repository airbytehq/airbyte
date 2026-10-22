/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import com.google.api.gax.core.NoCredentialsProvider
import com.google.api.gax.grpc.GrpcTransportChannel
import com.google.api.gax.rpc.FixedTransportChannelProvider
import com.google.api.gax.rpc.PermissionDeniedException
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobConfiguration
import com.google.cloud.bigquery.JobInfo
import com.google.cloud.bigquery.QueryJobConfiguration
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.storage.v1.BigQueryReadClient
import com.google.cloud.bigquery.storage.v1.BigQueryReadGrpc
import com.google.cloud.bigquery.storage.v1.BigQueryReadSettings
import com.google.cloud.bigquery.storage.v1.CreateReadSessionRequest
import com.google.cloud.bigquery.storage.v1.ReadRowsRequest
import com.google.cloud.bigquery.storage.v1.ReadRowsResponse
import com.google.cloud.bigquery.storage.v1.ReadSession
import com.google.cloud.bigquery.storage.v1.ReadStream
import io.airbyte.integrations.source.bigquery.BigQuerySourceConfiguration
import io.airbyte.integrations.source.bigquery.readapi.BigQueryReadApiPermissionProbe.Outcome
import io.grpc.ManagedChannel
import io.grpc.Server
import io.grpc.Status
import io.grpc.inprocess.InProcessChannelBuilder
import io.grpc.inprocess.InProcessServerBuilder
import io.grpc.stub.StreamObserver
import java.util.concurrent.TimeUnit
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.ArgumentMatchers.any
import org.mockito.Mockito

/**
 * [BigQueryReadApiPermissionProbe] against an in-process gRPC Storage Read API, so that the client
 * raises the same gax exceptions as the real service does, and the messages the user gets for each
 * kind of failure.
 */
class BigQueryReadApiPermissionProbeTest {

    private val fake = FakeReadApi()
    private lateinit var server: Server
    private lateinit var channel: ManagedChannel
    private lateinit var client: BigQueryReadClient

    private fun config(credentialsJson: String = CREDENTIALS): BigQuerySourceConfiguration =
        BigQuerySourceConfiguration(
            projectId = "data",
            credentialsJson = credentialsJson,
            datasetId = null,
            jobProjectId = "jobs",
            useStorageReadApi = true,
            emulatorHost = null,
            jdbcUrlFmt = "jdbc:bigquery://x",
            baseJdbcProperties = mapOf("ProjectId" to "jobs"),
            maxConcurrency = 1,
            realHost = "www.googleapis.com",
        )

    private val table = TableId.of("data", "ds", "events")

    @BeforeEach
    fun start() {
        val name: String = InProcessServerBuilder.generateName()
        server = InProcessServerBuilder.forName(name).addService(fake).build().start()
        channel = InProcessChannelBuilder.forName(name).build()
        client =
            BigQueryReadClient.create(
                BigQueryReadSettings.newBuilder()
                    .setTransportChannelProvider(
                        FixedTransportChannelProvider.create(GrpcTransportChannel.create(channel))
                    )
                    .setCredentialsProvider(NoCredentialsProvider.create())
                    .build()
            )
    }

    @AfterEach
    fun stop() {
        client.close()
        channel.shutdownNow().awaitTermination(5, TimeUnit.SECONDS)
        server.shutdownNow().awaitTermination(5, TimeUnit.SECONDS)
    }

    private fun probe(
        config: BigQuerySourceConfiguration = config(),
        bigquery: () -> BigQuery = { error("no query job expected") },
    ): BigQueryReadApiPermissionProbe =
        BigQueryReadApiPermissionProbe(config, bigquery, { client }, BigQueryReadApiConstants())

    @Test
    fun testAllowedOnTheGivenTableAndColumn() {
        val outcome: Outcome = probe().probe(table, "id")

        Assertions.assertEquals(Outcome.Allowed(table), outcome)
        val request: CreateReadSessionRequest = fake.createRequests.single()
        Assertions.assertEquals("projects/jobs", request.parent)
        Assertions.assertEquals(
            "projects/data/datasets/ds/tables/events",
            request.readSession.table
        )
        Assertions.assertEquals(listOf("id"), request.readSession.readOptions.selectedFieldsList)
        Assertions.assertEquals(1, request.maxStreamCount)
        Assertions.assertEquals(1, fake.readRowsRequests.size)
    }

    /** The real service's wording, captured from a Cloud sync log on 2026-10-02. */
    @Test
    fun testMissingRoleNamesTheServiceAccountTheRoleTheProjectAndTheWayOut() {
        val detail =
            "request failed: the user does not have 'bigquery.readsessions.create' permission " +
                "for 'projects/jobs'"
        fake.createStatus = Status.PERMISSION_DENIED.withDescription(detail)

        val outcome: Outcome = probe().probe(table, null)

        val denied: Outcome.Denied =
            Assertions.assertInstanceOf(Outcome.Denied::class.java, outcome)
        Assertions.assertEquals(
            "The service account sa@jobs.iam.gserviceaccount.com is not allowed to use the " +
                "BigQuery Storage Read API in project 'jobs'. Grant it the BigQuery Read Session " +
                "User role (roles/bigquery.readSessionUser, which holds " +
                "bigquery.readsessions.create and bigquery.readsessions.getData) on project " +
                "'jobs', or turn off 'Use the BigQuery Storage Read API' (use_storage_read_api) " +
                "in the source settings to read through the standard query API, which is much " +
                "slower on large tables. BigQuery said: $detail",
            denied.message,
        )
        // BigQueryReadSession.create wraps the gax exception in a ConfigErrorException; the probe
        // must see through that (the READ probe did not, before 2026-10-02).
        Assertions.assertTrue(
            generateSequence(denied.cause) { it.cause }.any { it is PermissionDeniedException },
            denied.cause.toString(),
        )
        Assertions.assertTrue(fake.readRowsRequests.isEmpty())
    }

    @Test
    fun testMissingRoleWithoutAParsableKeyStillReadsWell() {
        fake.createStatus =
            Status.PERMISSION_DENIED.withDescription(
                "the user does not have 'bigquery.readsessions.create' permission"
            )

        val outcome: Outcome = probe(config(credentialsJson = "not json")).probe(table, "id")

        val denied: Outcome.Denied =
            Assertions.assertInstanceOf(Outcome.Denied::class.java, outcome)
        Assertions.assertTrue(
            denied.message.startsWith(
                "The service account is not allowed to use the BigQuery Storage Read API in " +
                    "project 'jobs'. Grant it the BigQuery Read Session User role"
            ),
            denied.message,
        )
    }

    @Test
    fun testDeniedOnReadRowsIsAMissingRoleToo() {
        fake.readRowsStatus =
            Status.PERMISSION_DENIED.withDescription(
                "the user does not have 'bigquery.readsessions.getData' permission"
            )

        val outcome: Outcome = probe().probe(table, "id")

        val denied: Outcome.Denied =
            Assertions.assertInstanceOf(Outcome.Denied::class.java, outcome)
        Assertions.assertTrue(
            denied.message.contains("Grant it the BigQuery Read Session User role"),
            denied.message
        )
        Assertions.assertTrue(
            denied.message.endsWith(
                "BigQuery said: the user does not have 'bigquery.readsessions.getData' permission"
            ),
            denied.message,
        )
    }

    /** Google's wording when an API is not enabled on the project (reason SERVICE_DISABLED). */
    @Test
    fun testDisabledApiNamesTheApiToEnable() {
        val detail =
            "BigQuery Storage API has not been used in project 123 before or it is disabled. " +
                "Enable it by visiting https://console.developers.google.com/apis/api/" +
                "bigquerystorage.googleapis.com/overview?project=123 then retry."
        fake.createStatus = Status.PERMISSION_DENIED.withDescription(detail)

        val outcome: Outcome = probe().probe(table, "id")

        val denied: Outcome.Denied =
            Assertions.assertInstanceOf(Outcome.Denied::class.java, outcome)
        Assertions.assertEquals(
            "The BigQuery Storage Read API is not enabled in project 'jobs'. Enable the BigQuery " +
                "Storage API (bigquerystorage.googleapis.com) for that project in the Google " +
                "Cloud console, or turn off 'Use the BigQuery Storage Read API' " +
                "(use_storage_read_api) in the source settings to read through the standard " +
                "query API, which is much slower on large tables. BigQuery said: $detail",
            denied.message,
        )
    }

    @Test
    fun testOtherDenialsQuoteBigQueryAndPointAtTheRoles() {
        fake.createStatus = Status.PERMISSION_DENIED.withDescription("Access Denied: Table x:y.z")

        val outcome: Outcome = probe().probe(table, "id")

        val denied: Outcome.Denied =
            Assertions.assertInstanceOf(Outcome.Denied::class.java, outcome)
        Assertions.assertTrue(
            denied.message.startsWith(
                "BigQuery denied the service account sa@jobs.iam.gserviceaccount.com the use of " +
                    "the Storage Read API in project 'jobs'. Check its roles on that project"
            ),
            denied.message,
        )
        Assertions.assertTrue(
            denied.message.endsWith("BigQuery said: Access Denied: Table x:y.z"),
            denied.message
        )
    }

    @Test
    fun testOtherFailuresAreInconclusiveAndSayWhatFailed() {
        fake.createStatus = Status.INVALID_ARGUMENT.withDescription("read_session.table malformed")

        val outcome: Outcome = probe().probe(table, "id")

        val inconclusive: Outcome.Inconclusive =
            Assertions.assertInstanceOf(Outcome.Inconclusive::class.java, outcome)
        Assertions.assertTrue(
            inconclusive.message.startsWith(
                "Could not verify that the service account sa@jobs.iam.gserviceaccount.com may " +
                    "use the BigQuery Storage Read API in project 'jobs': the probe on " +
                    "data.ds.events failed: "
            ),
            inconclusive.message,
        )
        Assertions.assertTrue(
            inconclusive.message.contains("read_session.table malformed"),
            inconclusive.message
        )
    }

    @Test
    fun testWithoutATableTheQueryResultTableIsProbed() {
        val anonymous = TableId.of("jobs", "_anon", "anon123")
        val bigquery: BigQuery = Mockito.mock(BigQuery::class.java)
        val job: Job = Mockito.mock(Job::class.java)
        Mockito.`when`(bigquery.create(any(JobInfo::class.java))).thenReturn(job)
        Mockito.`when`(job.waitFor()).thenReturn(job)
        Mockito.`when`(job.getConfiguration<JobConfiguration>())
            .thenReturn(
                QueryJobConfiguration.newBuilder(BigQueryReadApiPermissionProbe.PROBE_QUERY)
                    .setDestinationTable(anonymous)
                    .build()
            )

        val outcome: Outcome = probe(bigquery = { bigquery }).probe(null, null)

        Assertions.assertEquals(Outcome.Allowed(anonymous), outcome)
        val request: CreateReadSessionRequest = fake.createRequests.single()
        Assertions.assertEquals("projects/jobs", request.parent)
        Assertions.assertEquals(
            "projects/jobs/datasets/_anon/tables/anon123",
            request.readSession.table
        )
        Assertions.assertEquals(
            listOf(BigQueryReadApiPermissionProbe.PROBE_COLUMN),
            request.readSession.readOptions.selectedFieldsList,
        )
        Assertions.assertEquals(1, fake.readRowsRequests.size)
    }

    @Test
    fun testAFailingQueryJobIsInconclusive() {
        val outcome: Outcome =
            probe(bigquery = { throw IllegalStateException("no jobs today") }).probe(null, null)

        val inconclusive: Outcome.Inconclusive =
            Assertions.assertInstanceOf(Outcome.Inconclusive::class.java, outcome)
        Assertions.assertEquals(
            "Could not verify that the service account sa@jobs.iam.gserviceaccount.com may use " +
                "the BigQuery Storage Read API in project 'jobs': the query job whose result the " +
                "probe reads failed: no jobs today",
            inconclusive.message,
        )
        Assertions.assertTrue(fake.createRequests.isEmpty())
    }

    private class FakeReadApi : BigQueryReadGrpc.BigQueryReadImplBase() {
        var createStatus: Status? = null
        var readRowsStatus: Status? = null
        val createRequests = mutableListOf<CreateReadSessionRequest>()
        val readRowsRequests = mutableListOf<ReadRowsRequest>()

        override fun createReadSession(
            request: CreateReadSessionRequest,
            responseObserver: StreamObserver<ReadSession>,
        ) {
            createRequests += request
            val status: Status? = createStatus
            if (status != null) {
                responseObserver.onError(status.asRuntimeException())
                return
            }
            responseObserver.onNext(
                ReadSession.newBuilder()
                    .setName(SESSION)
                    .addStreams(ReadStream.newBuilder().setName("$SESSION/streams/0"))
                    .build()
            )
            responseObserver.onCompleted()
        }

        override fun readRows(
            request: ReadRowsRequest,
            responseObserver: StreamObserver<ReadRowsResponse>,
        ) {
            readRowsRequests += request
            val status: Status? = readRowsStatus
            if (status != null) {
                responseObserver.onError(status.asRuntimeException())
                return
            }
            responseObserver.onNext(ReadRowsResponse.newBuilder().setRowCount(1).build())
            responseObserver.onCompleted()
        }

        companion object {
            const val SESSION = "projects/jobs/locations/us/sessions/CAIS"
        }
    }

    companion object {
        const val CREDENTIALS =
            """{"type":"service_account","client_email":"sa@jobs.iam.gserviceaccount.com"}"""
    }
}
