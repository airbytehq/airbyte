/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery.readapi

import com.google.cloud.bigquery.TableDefinition
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.bigquery.BigQuerySourceConfiguration
import io.airbyte.integrations.source.bigquery.BigQueryTableTypes
import io.airbyte.integrations.source.bigquery.readapi.BigQueryReadApiPermissionProbe.Outcome
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * What the READ-start probe does with each [Outcome], and which table it asks the permission probe
 * to use. The permission probe itself is faked here; see [BigQueryReadApiPermissionProbeTest] for
 * it.
 */
class BigQueryReadApiAvailabilityProbeTest {

    private fun config(useStorageReadApi: Boolean = true): BigQuerySourceConfiguration =
        BigQuerySourceConfiguration(
            projectId = "data",
            credentialsJson = "{}",
            datasetId = null,
            jobProjectId = "jobs",
            useStorageReadApi = useStorageReadApi,
            emulatorHost = null,
            jdbcUrlFmt = "jdbc:bigquery://x",
            baseJdbcProperties = mapOf("ProjectId" to "jobs"),
            maxConcurrency = 1,
            realHost = "www.googleapis.com",
            readApiAvailability = BigQueryReadApiAvailability(),
        )

    private class FixedProbe(config: BigQuerySourceConfiguration, private val outcome: Outcome) :
        BigQueryReadApiPermissionProbe(
            config,
            { error("unused") },
            { error("unused") },
            BigQueryReadApiConstants(),
        ) {
        val calls = mutableListOf<Pair<TableId?, String?>>()

        override fun probe(table: TableId?, column: String?): Outcome {
            calls += table to column
            return outcome
        }
    }

    private val tableTypes = BigQueryTableTypes()

    private fun stream(name: String, type: TableDefinition.Type): ConfiguredAirbyteStream {
        val airbyteStream: AirbyteStream =
            AirbyteStream()
                .withName(name)
                .withNamespace("ds")
                .withJsonSchema(
                    Jsons.readTree(
                        """{"type":"object","properties":{"id":{"type":"integer"},"name":{"type":"string"}}}"""
                    )
                )
        tableTypes.register(StreamIdentifier.from(airbyteStream), type)
        return ConfiguredAirbyteStream().withStream(airbyteStream)
    }

    private fun availabilityProbe(
        config: BigQuerySourceConfiguration,
        vararg streams: ConfiguredAirbyteStream,
    ): BigQueryReadApiAvailabilityProbe =
        BigQueryReadApiAvailabilityProbe(
            BigQueryReadApiClients(config),
            ConfiguredAirbyteCatalog().withStreams(streams.toList()),
            tableTypes,
            config.readApiAvailability,
            BigQueryReadApiConstants(),
        )

    /** The Cloud sync of 2026-10-02: a catalog with one view, no role. */
    @Test
    fun testViewOnlyCatalogIsStillProbedAndADenialDisablesTheApi() {
        val config = config()
        val fixed = FixedProbe(config, Outcome.Denied("no role", RuntimeException("denied")))

        availabilityProbe(config, stream("customer_vw", TableDefinition.Type.VIEW)).runOnce(fixed)

        Assertions.assertEquals(listOf<Pair<TableId?, String?>>(null to null), fixed.calls)
        Assertions.assertFalse(config.readApiAvailability.isAvailable)
        Assertions.assertEquals("no role", config.readApiAvailability.reason)
        // The JDBC driver stops opening read sessions of its own too.
        Assertions.assertFalse(config.jdbcProperties.containsKey("EnableHighThroughputAPI"))
    }

    @Test
    fun testTheFirstBaseTableOfTheCatalogIsProbedOnItsFirstColumn() {
        val config = config()
        val fixed = FixedProbe(config, Outcome.Allowed(TableId.of("data", "ds", "events")))

        availabilityProbe(
                config,
                stream("customer_vw", TableDefinition.Type.VIEW),
                stream("events", TableDefinition.Type.TABLE),
            )
            .runOnce(fixed)

        Assertions.assertEquals(listOf(TableId.of("data", "ds", "events") to "id"), fixed.calls)
        Assertions.assertTrue(config.readApiAvailability.isAvailable)
        Assertions.assertEquals("1", config.jdbcProperties["EnableHighThroughputAPI"])
    }

    @Test
    fun testAnInconclusiveProbeKeepsTheApiEnabled() {
        val config = config()
        val fixed = FixedProbe(config, Outcome.Inconclusive("gone", RuntimeException("gone")))

        availabilityProbe(config, stream("events", TableDefinition.Type.TABLE)).runOnce(fixed)

        Assertions.assertEquals(1, fixed.calls.size)
        Assertions.assertTrue(config.readApiAvailability.isAvailable)
    }

    @Test
    fun testTheProbeRunsOnce() {
        val config = config()
        val fixed = FixedProbe(config, Outcome.Denied("no role", RuntimeException("denied")))
        val probe = availabilityProbe(config, stream("events", TableDefinition.Type.TABLE))

        probe.runOnce(fixed)
        probe.runOnce(fixed)

        Assertions.assertEquals(1, fixed.calls.size)
    }

    @Test
    fun testTheFlagOffSkipsTheProbe() {
        val config = config(useStorageReadApi = false)
        val fixed = FixedProbe(config, Outcome.Denied("no role", RuntimeException("denied")))

        availabilityProbe(config, stream("events", TableDefinition.Type.TABLE)).runOnce(fixed)

        Assertions.assertTrue(fixed.calls.isEmpty())
        Assertions.assertTrue(config.readApiAvailability.isAvailable)
    }
}
