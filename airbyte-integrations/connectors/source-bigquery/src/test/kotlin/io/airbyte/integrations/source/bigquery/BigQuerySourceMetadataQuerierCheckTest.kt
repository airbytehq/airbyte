/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.storage.v1.BigQueryReadClient
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.airbyte.integrations.source.bigquery.readapi.BigQueryReadApiAvailability
import io.airbyte.integrations.source.bigquery.readapi.BigQueryReadApiConstants
import io.airbyte.integrations.source.bigquery.readapi.BigQueryReadApiPermissionProbe
import io.airbyte.integrations.source.bigquery.readapi.BigQueryReadApiPermissionProbe.Outcome
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.mockito.Mockito

/**
 * The Storage Read API check that CHECK runs after the JDBC check queries, through
 * [BigQuerySourceMetadataQuerier.extraChecks]: every failed probe fails CHECK with a message that
 * says what to do. The probe is faked; the emulator-based CHECK tests never reach it because the
 * API is not wired against the emulator.
 */
class BigQuerySourceMetadataQuerierCheckTest {

    private val config =
        BigQuerySourceConfiguration(
            projectId = "data",
            credentialsJson = "{}",
            datasetId = null,
            jobProjectId = "jobs",
            useStorageReadApi = true,
            emulatorHost = null,
            jdbcUrlFmt = "jdbc:bigquery://x",
            baseJdbcProperties = mapOf("ProjectId" to "jobs"),
            maxConcurrency = 1,
            realHost = "www.googleapis.com",
            readApiAvailability = BigQueryReadApiAvailability(),
        )

    private inner class FixedProbe(private val outcome: Outcome) :
        BigQueryReadApiPermissionProbe(
            config,
            { error("unused") },
            { error("unused") },
            BigQueryReadApiConstants(),
        ) {
        var calls = 0

        override fun probe(table: TableId?, column: String?): Outcome {
            calls++
            return outcome
        }
    }

    private val base: JdbcMetadataQuerier = Mockito.mock(JdbcMetadataQuerier::class.java)

    private fun querier(
        probe: BigQueryReadApiPermissionProbe?,
        readApiClient: Lazy<BigQueryReadClient>? = null,
    ): BigQuerySourceMetadataQuerier =
        BigQuerySourceMetadataQuerier(
            base,
            Mockito.mock(BigQuery::class.java),
            config,
            prefetchNamespaces = false,
            tableTypes = BigQueryTableTypes(),
            readApiProbe = probe,
            readApiClient = readApiClient,
        )

    @Test
    fun testADeniedPermissionFailsTheCheckWithTheProbeMessage() {
        val probe = FixedProbe(Outcome.Denied("grant the role", RuntimeException("denied")))

        val e: ConfigErrorException = assertThrows { querier(probe).extraChecks() }

        Assertions.assertEquals("grant the role", e.message)
        Assertions.assertEquals("denied", e.cause?.message)
        // The JDBC checks ran first.
        Mockito.verify(base).extraChecks()
    }

    @Test
    fun testAnInconclusiveProbeFailsTheCheckAndSaysWhatToTry() {
        val probe = FixedProbe(Outcome.Inconclusive("Could not verify X", RuntimeException("job")))

        val e: ConfigErrorException = assertThrows { querier(probe).extraChecks() }

        Assertions.assertEquals(
            "Could not verify X. Retry the connection test; if the error persists, turn off 'Use " +
                "the BigQuery Storage Read API' (use_storage_read_api) in the source settings to " +
                "read through the standard query API, which is much slower on large tables.",
            e.message,
        )
        Assertions.assertEquals("job", e.cause?.message)
    }

    @Test
    fun testAnAllowedPermissionPasses() {
        val probe = FixedProbe(Outcome.Allowed(TableId.of("jobs", "_anon", "t")))

        querier(probe).extraChecks()

        Assertions.assertEquals(1, probe.calls)
        Mockito.verify(base).extraChecks()
    }

    @Test
    fun testNoProbeWhenTheApiIsNotInUse() {
        querier(probe = null).extraChecks()

        Mockito.verify(base).extraChecks()
    }

    @Test
    fun testCloseClosesTheReadApiClientOnlyWhenItWasOpened() {
        val client: BigQueryReadClient = Mockito.mock(BigQueryReadClient::class.java)
        val opened: Lazy<BigQueryReadClient> = lazy { client }.also { it.value }
        val neverOpened: Lazy<BigQueryReadClient> = lazy { error("must not be opened by close()") }
        val probe = FixedProbe(Outcome.Allowed(TableId.of("jobs", "_anon", "t")))

        querier(probe, opened).close()
        querier(probe, neverOpened).close()

        Mockito.verify(client).close()
        Mockito.verify(base, Mockito.times(2)).close()
    }
}
