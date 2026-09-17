/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

/**
 * Runs READ against the seeded emulator: full refresh of every kind of table, cursor-based
 * incremental with resume, resume from a legacy `source-bigquery` state, and a stream that no
 * longer exists.
 *
 * Record values reflect what Google's JDBC driver returns for the emulator's responses; the
 * emulator is known to be lossy for some types (see `BigQueryEmulatorTestFixture`), so the
 * value-level assertions are limited to the columns it renders faithfully. Real-service parity is
 * checked with the docker images (see CONTRIBUTING.md).
 */
class BigQuerySourceReadTest {

    private val config: BigQuerySourceConfigurationSpecification =
        BigQueryEmulatorTestFixture.config(datasetId = BigQueryEmulatorTestFixture.DATASET)

    @Test
    fun testFullRefresh() {
        val catalog: AirbyteCatalog = discover()
        val configured =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        configured(catalog.stream("all_types"), SyncMode.FULL_REFRESH),
                        configured(catalog.stream("no_rows"), SyncMode.FULL_REFRESH),
                        configured(catalog.stream("with_pk"), SyncMode.FULL_REFRESH),
                        configured(catalog.stream("all_types_view"), SyncMode.FULL_REFRESH),
                    )
                )
        val output: BufferingOutputConsumer = read(configured)

        Assertions.assertEquals(
            mapOf("all_types" to 2, "no_rows" to 0, "with_pk" to 3, "all_types_view" to 2),
            output.recordsByStream().mapValues { it.value.size } +
                mapOf("no_rows" to output.recordsByStream()["no_rows"].orEmpty().size),
            output.dump(),
        )
        for (stream in listOf("all_types", "no_rows", "with_pk", "all_types_view")) {
            Assertions.assertEquals(
                listOf(
                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED,
                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
                ),
                output.statuses(stream),
                "statuses of $stream\n" + output.dump(),
            )
            Assertions.assertNotNull(output.lastState(stream), "state of $stream\n" + output.dump())
        }

        val allTypesRecords: List<AirbyteRecordMessage> = output.recordsByStream()["all_types"]!!
        val allTypes: JsonNode = allTypesRecords.single { it.data["id"].asLong() == 1L }.data
        Assertions.assertEquals(1L, allTypes["id"].asLong(), allTypes.toString())
        Assertions.assertEquals("alice", allTypes["name"].asText(), allTypes.toString())
        Assertions.assertTrue(allTypes["active"].asBoolean(), allTypes.toString())
        Assertions.assertEquals(0.25, allTypes["ratio"].asDouble(), 0.0, allTypes.toString())
        Assertions.assertEquals("2021-10-20", allTypes["day"].asText(), allTypes.toString())
        // BigQuery renders WKT as `POINT(1 2)`, the emulator as `POINT (1 2)`.
        Assertions.assertTrue(
            allTypes["geo"].asText().matches(Regex("POINT ?\\(1 2\\)")),
            allTypes.toString()
        )
        Assertions.assertEquals("YWJj", allTypes["blob"].asText(), allTypes.toString())
        Assertions.assertEquals(1.5, allTypes["price"].asDouble(), 0.0, allTypes.toString())
        Assertions.assertEquals(2.5, allTypes["big"].asDouble(), 0.0, allTypes.toString())
        Assertions.assertEquals("15:30:00.000000", allTypes["tod"].asText(), allTypes.toString())
        Assertions.assertEquals(
            "2021-10-20T11:22:33.000000",
            allTypes["local_ts"].asText(),
            allTypes.toString()
        )
        Assertions.assertEquals(
            "2021-10-20T11:22:33.000000Z",
            allTypes["ts"].asText(),
            allTypes.toString()
        )
        Assertions.assertEquals(
            "2021-10 10 10:10:10",
            allTypes["span"].asText(),
            allTypes.toString()
        )
        Assertions.assertEquals(Jsons.readTree("""{"a":1}"""), allTypes["doc"], allTypes.toString())
        Assertions.assertEquals(
            Jsons.readTree(
                """{"city":"Paris","zip":75001,"geo":{"observed_at":"08:00:00.000000"}}"""
            ),
            allTypes["address"],
            allTypes.toString(),
        )
        Assertions.assertEquals(
            Jsons.readTree("""["a","b"]"""),
            allTypes["tags"],
            allTypes.toString()
        )
        Assertions.assertEquals(
            Jsons.readTree(
                """[{"sku":"sku-1","qty":2,"discounts":[{"code":"SUMMER","pct":10}]}]"""
            ),
            allTypes["line_items"],
            allTypes.toString(),
        )
        // The all-NULL row: every type goes through the driver's NULL path without a retrieval
        // error (the driver's primitive getters throw on NULL, see BigQueryFieldTypes).
        val nullRow: AirbyteRecordMessage = allTypesRecords.single { it.data["id"].asLong() == 2L }
        Assertions.assertTrue(nullRow.meta?.changes.isNullOrEmpty(), nullRow.toString())
        for (column in
            listOf(
                "name",
                "price",
                "big",
                "ratio",
                "active",
                "blob",
                "day",
                "local_ts",
                "ts",
                "tod",
                "geo",
                "doc",
                "span",
                "address",
            )) {
            Assertions.assertTrue(nullRow.data[column]?.isNull == true, "$column of $nullRow")
        }
        // BigQuery stores a NULL ARRAY as an empty array.
        for (column in listOf("tags", "line_items")) {
            val value: JsonNode? = nullRow.data[column]
            Assertions.assertTrue(
                value != null && (value.isNull || (value.isArray && value.isEmpty)),
                "$column of $nullRow",
            )
        }
        val view: JsonNode =
            output
                .recordsByStream()["all_types_view"]!!
                .single { it.data["id"].asLong() == 1L }
                .data
        Assertions.assertEquals(
            setOf("id", "name", "address"),
            view.fieldNames().asSequence().toSet()
        )

        // A completed snapshot of a table with a primary key is checkpointed as such.
        Assertions.assertEquals(
            Jsons.readTree("""{"primary_key":{},"cursors":{}}"""),
            output.lastState("with_pk"),
            output.dump(),
        )
    }

    /**
     * `max_db_connections` above 1 lets the toolkit read partitions concurrently, and a
     * `job_project_id` (the emulator's only project) exercises the fully qualified table
     * references; the output must not change.
     */
    @Test
    fun testFullRefreshWithConcurrentQueriesAndJobProject() {
        val concurrent: BigQuerySourceConfigurationSpecification =
            BigQueryEmulatorTestFixture.config(
                datasetId = BigQueryEmulatorTestFixture.DATASET,
                jobProjectId = BigQueryEmulatorTestFixture.PROJECT_ID,
                maxDbConnections = 3,
            )
        val catalog: AirbyteCatalog = discover()
        val configured =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        configured(catalog.stream("all_types"), SyncMode.FULL_REFRESH),
                        configured(catalog.stream("with_pk"), SyncMode.FULL_REFRESH),
                        configured(catalog.stream("all_types_view"), SyncMode.FULL_REFRESH),
                    )
                )
        val output: BufferingOutputConsumer = CliRunner.source("read", concurrent, configured).run()

        Assertions.assertEquals(
            mapOf("all_types" to 2, "with_pk" to 3, "all_types_view" to 2),
            output.recordsByStream().mapValues { it.value.size },
            output.dump(),
        )
        for (stream in listOf("all_types", "with_pk", "all_types_view")) {
            Assertions.assertEquals(
                listOf(
                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED,
                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
                ),
                output.statuses(stream),
                "statuses of $stream\n" + output.dump(),
            )
        }
    }

    @Test
    fun testIncrementalThenResume() {
        val catalog: AirbyteCatalog = discover()
        val configured =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        configured(
                            catalog.stream("with_pk"),
                            SyncMode.INCREMENTAL,
                            cursor = listOf("updated_at")
                        )
                    )
                )
        val first: BufferingOutputConsumer = read(configured)
        val firstRecords: List<AirbyteRecordMessage> = first.recordsByStream()["with_pk"].orEmpty()
        Assertions.assertEquals(3, firstRecords.size, first.dump())
        val state: JsonNode = first.lastState("with_pk")!!
        Assertions.assertEquals(
            setOf("cursors"),
            state.fieldNames().asSequence().toSet() - "primary_key",
            state.toString()
        )
        Assertions.assertTrue(
            state["primary_key"] == null || state["primary_key"].isEmpty,
            state.toString()
        )
        val checkpoint: JsonNode = state["cursors"]["updated_at"]
        Assertions.assertEquals(
            "2024-01-03T00:00:00.000000Z",
            checkpoint.asText(),
            state.toString()
        )

        // Resuming re-reads the boundary row (inclusive lower bound) and nothing else.
        val second: BufferingOutputConsumer = read(configured, first.states())
        val secondRecords: List<AirbyteRecordMessage> =
            second.recordsByStream()["with_pk"].orEmpty()
        Assertions.assertEquals(
            listOf(2L),
            secondRecords.map { it.data["order_id"].asLong() },
            second.dump()
        )
        Assertions.assertEquals(
            checkpoint,
            second.lastState("with_pk")!!["cursors"]["updated_at"],
            second.dump()
        )
    }

    @Test
    fun testResumeFromLegacyState() {
        val catalog: AirbyteCatalog = discover()
        val configured =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        configured(
                            catalog.stream("with_pk"),
                            SyncMode.INCREMENTAL,
                            cursor = listOf("updated_at")
                        )
                    )
                )
        // What airbyte/source-bigquery 0.4.5 persists after reading the first two rows.
        val legacyState: JsonNode =
            Jsons.readTree(
                """{"stream_name":"with_pk","stream_namespace":"${BigQueryEmulatorTestFixture.DATASET}",
                   "cursor_field":["updated_at"],"cursor":"2024-01-02T00:00:00Z","cursor_record_count":1}"""
            )
        val output: BufferingOutputConsumer =
            read(configured, listOf(streamState("with_pk", legacyState)))
        val records: List<AirbyteRecordMessage> = output.recordsByStream()["with_pk"].orEmpty()
        // Legacy semantics: strictly after the legacy cursor.
        Assertions.assertEquals(
            listOf(2L),
            records.map { it.data["order_id"].asLong() },
            output.dump()
        )
        Assertions.assertEquals(
            Jsons.readTree(
                """{"primary_key":{},"cursors":{"updated_at":"2024-01-03T00:00:00.000000Z"}}"""
            ),
            output.lastState("with_pk"),
            output.dump(),
        )
    }

    @Test
    fun testMissingStreamIsSkipped() {
        val catalog: AirbyteCatalog = discover()
        val missing: AirbyteStream =
            Jsons.readValue(
                    Jsons.writeValueAsString(catalog.stream("all_types")),
                    AirbyteStream::class.java
                )
                .withName("does_not_exist")
        val configured =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    listOf(
                        configured(missing, SyncMode.FULL_REFRESH),
                        configured(catalog.stream("with_pk"), SyncMode.FULL_REFRESH),
                    )
                )
        val output: BufferingOutputConsumer = read(configured)
        Assertions.assertEquals(setOf("with_pk"), output.recordsByStream().keys, output.dump())
        Assertions.assertEquals(3, output.recordsByStream()["with_pk"]!!.size, output.dump())
        // The CDK reports the missing stream as INCOMPLETE with a config error and reads the rest.
        Assertions.assertEquals(
            listOf(
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE,
            ),
            output.statuses("does_not_exist"),
            output.dump(),
        )
        val error: AirbyteTraceMessage =
            output.traces().single { it.type == AirbyteTraceMessage.Type.ERROR }
        Assertions.assertEquals("does_not_exist", error.error.streamDescriptor.name, output.dump())
        Assertions.assertEquals(
            io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            error.error.failureType,
            output.dump(),
        )
        Assertions.assertTrue(error.error.message.contains("not found"), output.dump())
    }

    private fun discover(): AirbyteCatalog =
        CliRunner.source("discover", config).run().catalogs().single()

    private fun read(
        configured: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage> = listOf(),
    ): BufferingOutputConsumer = CliRunner.source("read", config, configured, state).run()

    private fun AirbyteCatalog.stream(name: String): AirbyteStream =
        streams.first { it.name == name }

    private fun configured(
        stream: AirbyteStream,
        syncMode: SyncMode,
        cursor: List<String>? = null,
    ): ConfiguredAirbyteStream =
        ConfiguredAirbyteStream()
            .withStream(stream)
            .withSyncMode(syncMode)
            .withCursorField(cursor ?: emptyList())
            .withPrimaryKey(stream.sourceDefinedPrimaryKey)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)

    private fun streamState(name: String, state: JsonNode): AirbyteStateMessage =
        AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(
                AirbyteStreamState()
                    .withStreamDescriptor(
                        StreamDescriptor()
                            .withName(name)
                            .withNamespace(BigQueryEmulatorTestFixture.DATASET)
                    )
                    .withStreamState(state)
            )

    private fun BufferingOutputConsumer.recordsByStream(): Map<String, List<AirbyteRecordMessage>> =
        records().groupBy { it.stream }

    private fun BufferingOutputConsumer.statuses(
        stream: String
    ): List<AirbyteStreamStatusTraceMessage.AirbyteStreamStatus> =
        traces()
            .filter { it.type == AirbyteTraceMessage.Type.STREAM_STATUS }
            .map { it.streamStatus }
            .filter { it.streamDescriptor.name == stream }
            .map { it.status }

    private fun BufferingOutputConsumer.lastState(stream: String): JsonNode? =
        states()
            .mapNotNull { it.stream }
            .lastOrNull { it.streamDescriptor.name == stream }
            ?.streamState

    /** Everything but LOG messages, for assertion messages. */
    private fun BufferingOutputConsumer.dump(): String =
        messages()
            .filter { it.type != io.airbyte.protocol.models.v0.AirbyteMessage.Type.LOG }
            .joinToString("\n") { Jsons.writeValueAsString(it) }

    companion object {
        @JvmStatic
        @BeforeAll
        fun startEmulator() {
            BigQueryEmulatorTestFixture.start()
        }
    }
}
