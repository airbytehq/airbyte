/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunnable
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.output.BufferingOutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.dynamodbv2.DynamoDbLocalContainer.Companion.batchPutItems
import io.airbyte.integrations.source.dynamodbv2.DynamoDbLocalContainer.Companion.createTableWithItems
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.airbyte.protocol.models.v0.SyncMode
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.KeyType
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest
import software.amazon.awssdk.services.dynamodb.model.ScalarAttributeType

/**
 * Runs READ against a seeded DynamoDB Local container: full refresh and incremental syncs, page
 * boundaries and checkpoints, resuming from saved (including legacy) states, and stream statuses.
 */
class DynamoDbSourceReadTest {

    // ---------------------------------------------------------------- full refresh

    @Test
    fun testFullRefreshRecordsMatchLegacy() {
        val result: ReadResult = read(catalog(configured("all_types", SyncMode.FULL_REFRESH)))
        result.assertNoErrors()
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("all_types"))
        val records: List<JsonNode> = result.records("all_types")
        Assertions.assertEquals(3, records.size)
        val item1: JsonNode = records.first { it["id"].asText() == "1" }
        Assertions.assertEquals(
            normalizeSets(Jsons.readTree(EXPECTED_ALL_TYPES_ITEM_1)),
            normalizeSets(item1),
        )
        // The final state marks the full refresh as complete.
        Assertions.assertEquals(
            listOf(Jsons.readTree("""{"scan_complete":true}""")),
            result.states("all_types"),
        )
        Assertions.assertEquals(
            3.0,
            result.stateMessages("all_types").last().sourceStats.recordCount
        )
    }

    @Test
    fun testFullRefreshReadsEveryItem() {
        val result: ReadResult = read(catalog(configured("many_items", SyncMode.FULL_REFRESH)))
        result.assertNoErrors()
        val ids: List<String> = result.records("many_items").map { it["id"].asText() }
        Assertions.assertEquals(1200, ids.size)
        Assertions.assertEquals(1200, ids.toSet().size)
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("many_items"))
    }

    /** Several 1 MB pages, with the service's own paging (no `Limit`). */
    @Test
    fun testFullRefreshFollowsLastEvaluatedKey() {
        val result: ReadResult = read(catalog(configured("wide", SyncMode.FULL_REFRESH)))
        result.assertNoErrors()
        val ids: List<String> = result.records("wide").map { it["id"].asText() }
        Assertions.assertEquals(WIDE_ITEMS, ids.size)
        Assertions.assertEquals(WIDE_ITEMS, ids.toSet().size)
    }

    @Test
    fun testFullRefreshResumesFromSavedKey() {
        val allIds: List<String> =
            read(catalog(configured("many_items", SyncMode.FULL_REFRESH)))
                .records("many_items")
                .map { it["id"].asText() }
        val resumed: ReadResult =
            read(
                catalog(configured("many_items", SyncMode.FULL_REFRESH)),
                state =
                    listOf(
                        streamState(
                            "many_items",
                            """{"scan":{"exclusive_start_key":{"id":{"S":"${allIds[599]}"}}}}""",
                        ),
                    ),
            )
        resumed.assertNoErrors()
        Assertions.assertEquals(
            allIds.subList(600, allIds.size),
            resumed.records("many_items").map { it["id"].asText() },
        )
        Assertions.assertEquals(
            Jsons.readTree("""{"scan_complete":true}"""),
            resumed.states("many_items").last(),
        )
    }

    /** After a failed attempt in which the stream had completed, the platform passes this back. */
    @Test
    fun testFullRefreshCompleteStateIsNotReadAgain() {
        val result: ReadResult =
            read(
                catalog(configured("many_items", SyncMode.FULL_REFRESH)),
                state = listOf(streamState("many_items", """{"scan_complete":true}""")),
            )
        result.assertNoErrors()
        Assertions.assertEquals(0, result.records("many_items").size)
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("many_items"))
    }

    /** A stream switched from incremental to full refresh: the saved cursor does not apply. */
    @Test
    fun testFullRefreshIgnoresIncrementalState() {
        val result: ReadResult =
            read(
                catalog(configured("many_items", SyncMode.FULL_REFRESH)),
                state =
                    listOf(streamState("many_items", """{"cursor_field":["v"],"cursor":"1100"}""")),
            )
        result.assertNoErrors()
        Assertions.assertEquals(1200, result.records("many_items").size)
    }

    /**
     * With a 1 second checkpoint interval and one item per page (2500 requests), the scan is
     * usually cut into several rounds by the CDK's timeout or the reader's own deadline. Whether
     * that happens depends on the machine (DynamoDB Local answers in well under a millisecond), so
     * only the outcome is asserted: every record once, well-formed intermediate states, a final
     * complete state. [DynamoDbPartitionReaderTest] covers the rounds deterministically.
     */
    @Test
    fun testCheckpointsBetweenPages() {
        val result: ReadResult =
            withScanPageLimit(1) {
                read(
                    catalog(configured("wide", SyncMode.FULL_REFRESH)),
                    extraConfig = mapOf("checkpoint_target_interval_seconds" to 1),
                )
            }
        result.assertNoErrors()
        val ids: List<String> = result.records("wide").map { it["id"].asText() }
        Assertions.assertEquals(WIDE_ITEMS, ids.size)
        Assertions.assertEquals(WIDE_ITEMS, ids.toSet().size)
        val states: List<JsonNode> = result.states("wide")
        for (state in states.dropLast(1)) {
            Assertions.assertTrue(state.has("scan"), state.toString())
            val segment: JsonNode = state["scan"]["segments"].single()
            Assertions.assertTrue(segment["exclusive_start_key"].has("id"), state.toString())
        }
        Assertions.assertEquals(Jsons.readTree("""{"scan_complete":true}"""), states.last())
        Assertions.assertEquals(
            WIDE_ITEMS.toDouble(),
            result.stateMessages("wide").sumOf { it.sourceStats.recordCount },
        )
    }

    @Test
    fun testCompositeNumericAndBinaryKeysResume() {
        for (table in listOf("composite_key", "numeric_key", "binary_key")) {
            val first: ReadResult = read(catalog(configured(table, SyncMode.FULL_REFRESH)))
            first.assertNoErrors()
            val records: List<JsonNode> = first.records(table)
            Assertions.assertTrue(records.size >= 2, table)
            // Resume after the first item: its key, as the service would have returned it.
            val firstKey: Map<String, AttributeValue> =
                client
                    .getItem { req -> req.tableName(table).key(keyOf(table, records.first())) }
                    .item()
                    .filterKeys { it in keyAttributes(table) }
            val resumed: ReadResult =
                read(
                    catalog(configured(table, SyncMode.FULL_REFRESH)),
                    state =
                        listOf(
                            streamState(
                                table,
                                Jsons.objectNode()
                                    .set<ObjectNode>(
                                        "scan",
                                        Jsons.objectNode()
                                            .set<ObjectNode>(
                                                "exclusive_start_key",
                                                DynamoDbJson.itemToDynamoDbJson(firstKey),
                                            ),
                                    )
                                    .toString(),
                            ),
                        ),
                )
            resumed.assertNoErrors()
            Assertions.assertEquals(records.drop(1), resumed.records(table), table)
        }
    }

    @Test
    fun testEmptyTable() {
        val stream: AirbyteStream =
            AirbyteStream()
                .withName("empty_table")
                .withJsonSchema(
                    Jsons.readTree(
                        """{"type":"object","properties":{"id":{"type":["null","string"]}}}"""
                    )
                )
                .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                .withSourceDefinedPrimaryKey(listOf(listOf("id")))
        val result: ReadResult =
            read(catalog(configured("empty_table", SyncMode.FULL_REFRESH, stream = stream)))
        result.assertNoErrors()
        Assertions.assertEquals(0, result.records("empty_table").size)
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("empty_table"))
        Assertions.assertEquals(
            listOf(Jsons.readTree("""{"scan_complete":true}""")),
            result.states("empty_table"),
        )
    }

    /** Reserved words and special characters need no `reserved_attribute_names` any more. */
    @Test
    fun testReservedAttributeNamesWithoutConfiguration() {
        val result: ReadResult = read(catalog(configured("reserved_words", SyncMode.FULL_REFRESH)))
        result.assertNoErrors()
        val r1: JsonNode = result.records("reserved_words").first { it["id"].asText() == "r1" }
        Assertions.assertEquals(
            Jsons.readTree(
                """{"id":"r1","name":"first","status":"active","data":{"inner":"payload"},
                    "field.name":"dotted","field-name":"dashed","count":5}"""
            ),
            r1,
        )
    }

    @Test
    fun testMissingTable() {
        val missing: AirbyteStream =
            AirbyteStream()
                .withName("does_not_exist")
                .withJsonSchema(
                    Jsons.readTree(
                        """{"type":"object","properties":{"id":{"type":["null","string"]}}}"""
                    )
                )
                .withSupportedSyncModes(listOf(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
        val result: ReadResult =
            read(
                catalog(
                    configured("all_types", SyncMode.FULL_REFRESH),
                    configured("does_not_exist", SyncMode.FULL_REFRESH, stream = missing),
                ),
            )
        Assertions.assertEquals(listOf("STARTED", "INCOMPLETE"), result.statuses("does_not_exist"))
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("all_types"))
        Assertions.assertEquals(3, result.records("all_types").size)
        Assertions.assertTrue(
            result.errors.any { it.contains("does_not_exist") },
            "expected an error trace naming the missing table, got ${result.errors}",
        )
    }

    // ---------------------------------------------------------------- incremental

    @Test
    fun testIncrementalIntegerCursor() {
        client.createTableWithItems(
            "orders",
            listOf(KeyElement("id", KeyType.HASH, ScalarAttributeType.S)),
            (1..300).map { orderItem(it) },
        )
        val catalog: ConfiguredAirbyteCatalog =
            catalog(configured("orders", SyncMode.INCREMENTAL, cursor = "v"))

        // First sync: no state, the whole table.
        val first: ReadResult = read(catalog)
        first.assertNoErrors()
        Assertions.assertEquals(300, first.records("orders").size)
        val expectedState: JsonNode =
            Jsons.readTree("""{"cursor_field":["v"],"cursor":"300","cursor_record_count":1}""")
        Assertions.assertEquals(listOf(expectedState), first.states("orders"))

        // Second sync with that state: nothing new, the state is re-emitted unchanged.
        val second: ReadResult = read(catalog, state = listOf(streamState("orders", expectedState)))
        second.assertNoErrors()
        Assertions.assertEquals(0, second.records("orders").size)
        Assertions.assertEquals(listOf(expectedState), second.states("orders"))

        // Third sync after new items: only those, and the cursor moves.
        for (i in 301..310) {
            client.putItem(PutItemRequest.builder().tableName("orders").item(orderItem(i)).build())
        }
        val third: ReadResult = read(catalog, state = listOf(streamState("orders", expectedState)))
        third.assertNoErrors()
        Assertions.assertEquals(
            (301..310).map { "o-$it" }.toSet(),
            third.records("orders").map { it["id"].asText() }.toSet(),
        )
        Assertions.assertEquals(
            listOf(
                Jsons.readTree("""{"cursor_field":["v"],"cursor":"310","cursor_record_count":1}""")
            ),
            third.states("orders"),
        )
    }

    /** The exact state message the legacy connector persisted, `data` duplicate included. */
    @Test
    fun testIncrementalResumesFromLegacyState() {
        val legacyState: AirbyteStateMessage =
            Jsons.readValue(
                """
                {"type":"STREAM",
                 "stream":{"stream_descriptor":{"name":"all_types"},
                           "stream_state":{"stream_name":"all_types","stream_namespace":null,
                                           "cursor_field":["str"],"cursor":"hello","cursor_record_count":1}},
                 "data":{"cdc":false,"streams":[{"stream_name":"all_types","stream_namespace":null,
                                                  "cursor_field":["str"],"cursor":"hello","cursor_record_count":1}]},
                 "sourceStats":{"recordCount":3.0}}
                """,
                AirbyteStateMessage::class.java,
            )
        val result: ReadResult =
            read(
                catalog(configured("all_types", SyncMode.INCREMENTAL, cursor = "str")),
                state = listOf(legacyState),
            )
        result.assertNoErrors()
        Assertions.assertEquals(
            setOf("solo", "world"),
            result.records("all_types").map { it["str"].asText() }.toSet(),
        )
        Assertions.assertEquals(
            listOf(
                Jsons.readTree(
                    """{"cursor_field":["str"],"cursor":"world","cursor_record_count":1}"""
                )
            ),
            result.states("all_types"),
        )
    }

    /** A bare date cursor is compared with `>=` so the items of that day are not skipped. */
    @Test
    fun testIncrementalBareDateCursorIsInclusive() {
        val result: ReadResult =
            read(
                catalog(configured("events", SyncMode.INCREMENTAL, cursor = "d")),
                state =
                    listOf(
                        streamState("events", """{"cursor_field":["d"],"cursor":"2024-01-02"}""")
                    ),
            )
        result.assertNoErrors()
        Assertions.assertEquals(
            listOf("e3", "e4", "e5"),
            result.records("events").map { it["id"].asText() }.sorted(),
        )
        // Two events share the last day.
        Assertions.assertEquals(
            listOf(
                Jsons.readTree(
                    """{"cursor_field":["d"],"cursor":"2024-01-03","cursor_record_count":2}"""
                )
            ),
            result.states("events"),
        )
    }

    /** A timestamp cursor is compared with `>`; the record count tracks ties. */
    @Test
    fun testIncrementalTimestampCursorCountsTies() {
        val result: ReadResult =
            read(catalog(configured("events", SyncMode.INCREMENTAL, cursor = "ts")))
        result.assertNoErrors()
        Assertions.assertEquals(5, result.records("events").size)
        Assertions.assertEquals(
            listOf(
                Jsons.readTree(
                    """{"cursor_field":["ts"],"cursor":"2024-01-03T00:00:00Z","cursor_record_count":2}"""
                )
            ),
            result.states("events"),
        )
        val next: ReadResult =
            read(
                catalog(configured("events", SyncMode.INCREMENTAL, cursor = "ts")),
                state = listOf(streamState("events", result.states("events").single())),
            )
        next.assertNoErrors()
        Assertions.assertEquals(0, next.records("events").size)
    }

    @Test
    fun testIncrementalCursorFieldChangeStartsOver() {
        val result: ReadResult =
            read(
                catalog(configured("many_items", SyncMode.INCREMENTAL, cursor = "v")),
                state =
                    listOf(
                        streamState("many_items", """{"cursor_field":["other"],"cursor":"1100"}""")
                    ),
            )
        result.assertNoErrors()
        Assertions.assertEquals(1200, result.records("many_items").size)
        Assertions.assertEquals(
            listOf(
                Jsons.readTree("""{"cursor_field":["v"],"cursor":"1200","cursor_record_count":1}""")
            ),
            result.states("many_items"),
        )
    }

    /** An interrupted incremental scan resumes with the same filter and the running maximum. */
    @Test
    fun testIncrementalResumesMidScan() {
        val allRecords: List<JsonNode> =
            read(catalog(configured("many_items", SyncMode.FULL_REFRESH))).records("many_items")
        val resumeAfter: JsonNode = allRecords[599]
        val remaining: List<JsonNode> =
            allRecords.subList(600, allRecords.size).filter { it["v"].asLong() > 600 }
        val result: ReadResult =
            read(
                catalog(configured("many_items", SyncMode.INCREMENTAL, cursor = "v")),
                state =
                    listOf(
                        streamState(
                            "many_items",
                            """{"cursor_field":["v"],"cursor":"600","cursor_record_count":1,
                                "scan":{"exclusive_start_key":{"id":{"S":"${resumeAfter["id"].asText()}"}},
                                        "max_cursor":"5000","max_cursor_record_count":1}}""",
                        ),
                    ),
            )
        result.assertNoErrors()
        Assertions.assertEquals(
            remaining.map { it["id"].asText() },
            result.records("many_items").map { it["id"].asText() },
        )
        // The running maximum from the interrupted scan is higher than anything in the table.
        Assertions.assertEquals(
            listOf(
                Jsons.readTree("""{"cursor_field":["v"],"cursor":"5000","cursor_record_count":1}""")
            ),
            result.states("many_items"),
        )
    }

    /** In-progress incremental states keep the filter bound and carry the running maximum. */
    @Test
    fun testIncrementalCheckpointsKeepTheLowerBound() {
        val result: ReadResult =
            withScanPageLimit(1) {
                read(
                    catalog(configured("wide", SyncMode.INCREMENTAL, cursor = "id")),
                    state =
                        listOf(
                            streamState("wide", """{"cursor_field":["id"],"cursor":"w-0100"}""")
                        ),
                    extraConfig = mapOf("checkpoint_target_interval_seconds" to 1),
                )
            }
        result.assertNoErrors()
        Assertions.assertEquals(WIDE_ITEMS - 100, result.records("wide").size)
        val states: List<JsonNode> = result.states("wide")
        for (state in states.dropLast(1)) {
            Assertions.assertEquals("w-0100", state["cursor"].asText(), state.toString())
            val segment: JsonNode = state["scan"]["segments"].single()
            Assertions.assertTrue(segment.has("exclusive_start_key"), state.toString())
            Assertions.assertTrue(segment.has("max_cursor"), state.toString())
        }
        Assertions.assertEquals(
            Jsons.readTree("""{"cursor_field":["id"],"cursor":"w-2500","cursor_record_count":1}"""),
            states.last(),
        )
    }

    @Test
    fun testIncrementalRejectsUnsupportedCursorType() {
        val result: ReadResult =
            read(catalog(configured("all_types", SyncMode.INCREMENTAL, cursor = "flag")))
        Assertions.assertEquals(listOf("STARTED", "INCOMPLETE"), result.statuses("all_types"))
        Assertions.assertTrue(
            result.errors.any { it.contains("only string and number attributes") },
            result.errors.toString(),
        )
    }

    // ---------------------------------------------------------------- parallel-scan segments

    /**
     * `many_items` has 1,200 distinct partition keys; split 8 ways (the tiny target makes
     * `DescribeTable`'s size ask for far more, the cap yields exactly 8) and scanned 4 at a time,
     * the table comes out identical to the single-segment read, with valid intermediate states.
     */
    @Test
    fun testSegmentedFullRefreshMatchesSingleSegment() {
        val single: ReadResult = read(catalog(configured("many_items", SyncMode.FULL_REFRESH)))
        single.assertNoErrors()
        val segmented: ReadResult =
            withSegments(8) {
                read(
                    catalog(configured("many_items", SyncMode.FULL_REFRESH)),
                    extraConfig = mapOf("concurrency" to 4),
                )
            }
        segmented.assertNoErrors()
        Assertions.assertEquals(1200, segmented.records("many_items").size)
        Assertions.assertEquals(
            single.records("many_items").map { it.toString() }.sorted(),
            segmented.records("many_items").map { it.toString() }.sorted(),
        )
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), segmented.statuses("many_items"))
        val states: List<JsonNode> = segmented.states("many_items")
        Assertions.assertEquals(Jsons.readTree("""{"scan_complete":true}"""), states.last())
        assertSegmentStatesAreConsistent(states.filter { it.has("scan") }, totalSegments = 8)
        // No record of the stream follows the state that declares it complete.
        val messages = segmented.output.messages()
        val terminalIndex: Int =
            messages.indexOfLast {
                it.state?.stream?.streamDescriptor?.name == "many_items" &&
                    it.state.stream.streamState == states.last()
            }
        Assertions.assertTrue(terminalIndex >= 0)
        Assertions.assertTrue(
            messages.drop(terminalIndex + 1).none { it.record?.stream == "many_items" },
            "records after the terminal state",
        )
        Assertions.assertEquals(
            1200.0,
            segmented.stateMessages("many_items").sumOf { it.sourceStats.recordCount },
        )
    }

    /** Incremental scans use the same segments; the cursor maximum is merged across them. */
    @Test
    fun testSegmentedIncrementalIntegerCursor() {
        val first: ReadResult =
            withSegments(8) {
                read(
                    catalog(configured("many_items", SyncMode.INCREMENTAL, cursor = "v")),
                    extraConfig = mapOf("concurrency" to 3),
                )
            }
        first.assertNoErrors()
        Assertions.assertEquals(1200, first.records("many_items").size)
        Assertions.assertEquals(1200, first.records("many_items").map { it["id"] }.toSet().size)
        val states: List<JsonNode> = first.states("many_items")
        Assertions.assertEquals(
            Jsons.readTree("""{"cursor_field":["v"],"cursor":"1200","cursor_record_count":1}"""),
            states.last(),
        )
        val inProgress: List<JsonNode> = states.filter { it.has("scan") }
        for (state in inProgress) {
            // No saved cursor: nothing to filter on until the scan completes.
            Assertions.assertFalse(state.has("cursor"), state.toString())
            Assertions.assertEquals(listOf("v"), state["cursor_field"].map { it.asText() })
        }
        assertSegmentStatesAreConsistent(inProgress, totalSegments = 8)
        val messages = first.output.messages()
        val terminalIndex: Int =
            messages.indexOfFirst {
                it.state?.stream?.streamDescriptor?.name == "many_items" &&
                    it.state.stream.streamState == states.last()
            }
        Assertions.assertTrue(terminalIndex >= 0)
        Assertions.assertTrue(
            messages.drop(terminalIndex + 1).none { it.record?.stream == "many_items" },
            "records after the terminal state",
        )
        val next: ReadResult =
            withSegments(8) {
                read(
                    catalog(configured("many_items", SyncMode.INCREMENTAL, cursor = "v")),
                    state = listOf(streamState("many_items", states.last())),
                    extraConfig = mapOf("concurrency" to 3),
                )
            }
        next.assertNoErrors()
        Assertions.assertEquals(0, next.records("many_items").size)
        Assertions.assertEquals(states.last(), next.states("many_items").last())
    }

    /** Ties on the maximum are counted across segments, for `>` and for the `>=` bare-date rule. */
    @Test
    fun testSegmentedIncrementalDateCursorsCountTiesAcrossSegments() {
        // Five partition keys spread over 8 segments: e4 and e5 (both 2024-01-03) may well land
        // in different segments.
        val byTimestamp: ReadResult =
            withSegments(8) {
                read(catalog(configured("events", SyncMode.INCREMENTAL, cursor = "ts")))
            }
        byTimestamp.assertNoErrors()
        Assertions.assertEquals(5, byTimestamp.records("events").size)
        Assertions.assertEquals(
            Jsons.readTree(
                """{"cursor_field":["ts"],"cursor":"2024-01-03T00:00:00Z","cursor_record_count":2}"""
            ),
            byTimestamp.states("events").last(),
        )
        val byDate: ReadResult =
            withSegments(8) {
                read(
                    catalog(configured("events", SyncMode.INCREMENTAL, cursor = "d")),
                    state =
                        listOf(
                            streamState(
                                "events",
                                """{"cursor_field":["d"],"cursor":"2024-01-02"}"""
                            )
                        ),
                )
            }
        byDate.assertNoErrors()
        Assertions.assertEquals(
            listOf("e3", "e4", "e5"),
            byDate.records("events").map { it["id"].asText() }.sorted(),
        )
        Assertions.assertEquals(
            Jsons.readTree(
                """{"cursor_field":["d"],"cursor":"2024-01-03","cursor_record_count":2}"""
            ),
            byDate.states("events").last(),
        )
    }

    /** A saved segment count wins over the current sizing: the keys belong to it. */
    @Test
    fun testResumesSegmentedScanWithItsSavedSegmentCount() {
        val all: List<String> =
            read(catalog(configured("many_items", SyncMode.FULL_REFRESH)))
                .records("many_items")
                .map { it["id"].asText() }
        // Segments 0 and 2 of 4 complete, 1 and 3 not started: the resumed read must produce
        // exactly the items DynamoDB hashes into segments 1 and 3, and nothing twice.
        val state =
            """{"scan":{"total_segments":4,"segments":[
                 {"segment":0,"complete":true},{"segment":1},
                 {"segment":2,"complete":true},{"segment":3}]}}"""
        val resumed: ReadResult =
            withSegments(2) {
                read(
                    catalog(configured("many_items", SyncMode.FULL_REFRESH)),
                    state = listOf(streamState("many_items", state)),
                    extraConfig = mapOf("concurrency" to 2),
                )
            }
        resumed.assertNoErrors()
        val expected: Set<String> = segmentMembers("many_items", setOf(1, 3), totalSegments = 4)
        val ids: List<String> = resumed.records("many_items").map { it["id"].asText() }
        Assertions.assertEquals(ids.size, ids.toSet().size, "duplicates")
        Assertions.assertEquals(expected, ids.toSet())
        Assertions.assertTrue(expected.size in 1 until all.size)
        Assertions.assertEquals(
            Jsons.readTree("""{"scan_complete":true}"""),
            resumed.states("many_items").last(),
        )
    }

    /**
     * Every in-progress state parses and keeps the segment count. The states of one round are
     * snapshots taken when each reader stopped but applied in partition order, so a later state can
     * show less progress than an earlier one (a segment complete in one, not started in the next);
     * each is still a valid resume point, and the freshest one is applied last.
     */
    private fun assertSegmentStatesAreConsistent(states: List<JsonNode>, totalSegments: Int) {
        val streamID = io.airbyte.cdk.StreamIdentifier.from(StreamDescriptor().withName("x"))
        Assertions.assertTrue(states.isNotEmpty())
        for (state in states) {
            val parsed: DynamoDbStreamStateValue = DynamoDbStreamStateValue.parse(streamID, state)!!
            Assertions.assertEquals(totalSegments, parsed.scan!!.totalSegments, state.toString())
            Assertions.assertEquals(totalSegments, parsed.scan!!.segments!!.size, state.toString())
            for (segment in parsed.scan!!.segments!!) {
                Assertions.assertFalse(
                    segment.complete == true && segment.exclusiveStartKey != null,
                    "complete segment with a key: $state",
                )
            }
        }
    }

    /** The keys DynamoDB assigns to the given segments of a table. */
    private fun segmentMembers(table: String, segments: Set<Int>, totalSegments: Int): Set<String> {
        val ids = mutableSetOf<String>()
        for (segment in segments) {
            var key: Map<String, AttributeValue>? = null
            while (true) {
                val response =
                    client.scan {
                        it.tableName(table).segment(segment).totalSegments(totalSegments)
                        if (key != null) it.exclusiveStartKey(key)
                    }
                response.items().forEach { item -> ids.add(item["id"]!!.s()) }
                if (!response.hasLastEvaluatedKey() || response.lastEvaluatedKey().isEmpty()) break
                key = response.lastEvaluatedKey()
            }
        }
        return ids
    }

    /** Forces every table of the runs in [block] to be scanned in exactly [segments] segments. */
    private fun <T> withSegments(segments: Int, block: () -> T): T {
        // One byte per segment asks for one segment per table byte; the cap decides.
        System.setProperty(DynamoDbSharedState.SEGMENT_TARGET_BYTES_PROPERTY, "1")
        System.setProperty(DynamoDbSharedState.MAX_SEGMENTS_PROPERTY, segments.toString())
        try {
            return block()
        } finally {
            System.clearProperty(DynamoDbSharedState.SEGMENT_TARGET_BYTES_PROPERTY)
            System.clearProperty(DynamoDbSharedState.MAX_SEGMENTS_PROPERTY)
        }
    }

    // ---------------------------------------------------------------- helpers

    /**
     * A catalog configured from the legacy connector, or from this connector before its schemas
     * became canonical, carries `{"type": ["null", <type>]}` shapes. The CDK types those fields as
     * JSONB at READ time and so does the connector, so the stream still validates and reads the
     * same records (as JSON values) until the schema is refreshed.
     */
    @Test
    fun testLegacyShapedCatalogStillReads() {
        val canonical: ConfiguredAirbyteStream = configured("all_types", SyncMode.FULL_REFRESH)
        val legacyStream: AirbyteStream =
            Jsons.readValue(Jsons.writeValueAsString(canonical.stream), AirbyteStream::class.java)
                .withJsonSchema(legacyShaped(canonical.stream.jsonSchema))
        Assertions.assertEquals(
            Jsons.readTree("""["null","string"]"""),
            legacyStream.jsonSchema["properties"]["str"]["type"],
        )
        Assertions.assertEquals(
            Jsons.readTree("""["null","integer"]"""),
            legacyStream.jsonSchema["properties"]["int"]["type"],
        )
        val expected: ReadResult = read(catalog(canonical))
        val result: ReadResult =
            read(catalog(configured("all_types", SyncMode.FULL_REFRESH, stream = legacyStream)))
        result.assertNoErrors()
        Assertions.assertEquals(listOf("STARTED", "COMPLETE"), result.statuses("all_types"))
        Assertions.assertEquals(
            expected.records("all_types").map { normalizeSets(it).toString() }.sorted(),
            result.records("all_types").map { normalizeSets(it).toString() }.sorted(),
        )
        // The integer cursor is still recognised through the legacy shape.
        val incremental: ReadResult =
            read(
                catalog(
                    configured(
                        "all_types",
                        SyncMode.INCREMENTAL,
                        cursor = "int",
                        stream = legacyStream
                    )
                )
            )
        incremental.assertNoErrors()
        Assertions.assertEquals(
            Jsons.readTree("""{"cursor_field":["int"],"cursor":"42","cursor_record_count":1}"""),
            incremental.states("all_types").last(),
        )
    }

    /** The legacy shapes of a canonical schema: `["null", <type>]`, integers as `integer`. */
    private fun legacyShaped(schema: JsonNode): JsonNode {
        if (!schema.isObject) return schema
        val result: ObjectNode = Jsons.objectNode()
        val airbyteType: String? = schema["airbyte_type"]?.asText()
        for ((key: String, value: JsonNode) in schema.properties()) {
            when (key) {
                "type" -> {
                    val type: String =
                        if (value.asText() == "number" && airbyteType == "integer") "integer"
                        else value.asText()
                    if (type == "null") result.put("type", "null")
                    else result.set<JsonNode>("type", Jsons.arrayNode().add("null").add(type))
                }
                "airbyte_type" -> if (airbyteType != "integer") result.set<JsonNode>(key, value)
                "properties" -> {
                    val properties: ObjectNode = Jsons.objectNode()
                    for ((name: String, property: JsonNode) in value.properties()) {
                        properties.set<JsonNode>(name, legacyShaped(property))
                    }
                    result.set<JsonNode>(key, properties)
                }
                "items" -> result.set<JsonNode>(key, legacyShaped(value))
                "anyOf" ->
                    result.set<JsonNode>(
                        key,
                        Jsons.arrayNode().apply { value.forEach { add(legacyShaped(it)) } },
                    )
                else -> result.set<JsonNode>(key, value)
            }
        }
        return result
    }

    private fun discovered(): AirbyteCatalog =
        CliRunner.source("discover", container.config()).run().catalogs().single()

    private fun configured(
        name: String,
        syncMode: SyncMode,
        cursor: String? = null,
        stream: AirbyteStream? = null,
    ): ConfiguredAirbyteStream {
        val airbyteStream: AirbyteStream =
            stream
                ?: discoveredCatalog.streams.firstOrNull { it.name == name }
                    ?: discovered().streams.first { it.name == name }
        return ConfiguredAirbyteStream()
            .withStream(airbyteStream)
            .withSyncMode(syncMode)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withCursorField(listOfNotNull(cursor))
            .withPrimaryKey(airbyteStream.sourceDefinedPrimaryKey)
    }

    private fun catalog(vararg streams: ConfiguredAirbyteStream): ConfiguredAirbyteCatalog =
        ConfiguredAirbyteCatalog().withStreams(streams.toList())

    private fun streamState(name: String, json: String): AirbyteStateMessage =
        streamState(name, Jsons.readTree(json))

    private fun streamState(name: String, json: JsonNode): AirbyteStateMessage =
        AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(
                AirbyteStreamState()
                    .withStreamDescriptor(StreamDescriptor().withName(name))
                    .withStreamState(json),
            )

    private fun read(
        catalog: ConfiguredAirbyteCatalog,
        state: List<AirbyteStateMessage>? = null,
        extraConfig: Map<String, Any?> = emptyMap(),
    ): ReadResult {
        val runnable: CliRunnable =
            CliRunner.source("read", container.config(extra = extraConfig), catalog, state)
        val failure: Throwable? =
            try {
                runnable.run()
                null
            } catch (e: Throwable) {
                e
            }
        return ReadResult(runnable.results, failure)
    }

    /** Sets the scan page size (items per `Scan` request) for the connector runs in [block]. */
    private fun <T> withScanPageLimit(limit: Int, block: () -> T): T {
        System.setProperty(DynamoDbSharedState.SCAN_PAGE_LIMIT_PROPERTY, limit.toString())
        try {
            return block()
        } finally {
            System.clearProperty(DynamoDbSharedState.SCAN_PAGE_LIMIT_PROPERTY)
        }
    }

    class ReadResult(val output: BufferingOutputConsumer, val failure: Throwable?) {
        val errors: List<String> =
            output
                .traces()
                .filter { it.type == AirbyteTraceMessage.Type.ERROR }
                .map { it.error.message ?: "" }

        fun assertNoErrors() {
            Assertions.assertTrue(errors.isEmpty(), "unexpected error traces: $errors")
            Assertions.assertNull(failure, "unexpected failure: $failure")
        }

        fun records(stream: String): List<JsonNode> =
            output.records().filter { it.stream == stream }.map(AirbyteRecordMessage::getData)

        fun statuses(stream: String): List<String> =
            output
                .traces()
                .filter { it.type == AirbyteTraceMessage.Type.STREAM_STATUS }
                .filter { it.streamStatus.streamDescriptor.name == stream }
                .map { it.streamStatus.status.let(AirbyteStreamStatus::name) }

        fun stateMessages(stream: String): List<AirbyteStateMessage> =
            output.states().filter { it.stream?.streamDescriptor?.name == stream }

        fun states(stream: String): List<JsonNode> =
            stateMessages(stream).map { it.stream.streamState }
    }

    /** Sets are unordered; sort their elements before comparing records. */
    private fun normalizeSets(record: JsonNode): JsonNode {
        val copy: ObjectNode = record.deepCopy()
        for (name in listOf("sset", "nset", "bset")) {
            val sorted: List<JsonNode> = copy[name].sortedBy { it.toString() }
            copy.set<JsonNode>(name, Jsons.arrayNode().addAll(sorted))
        }
        return copy
    }

    private fun keyAttributes(table: String): Set<String> =
        client
            .describeTable { it.tableName(table) }
            .table()
            .keySchema()
            .map { it.attributeName() }
            .toSet()

    /** The key of a record, typed according to the table's key schema. */
    private fun keyOf(table: String, record: JsonNode): Map<String, AttributeValue> {
        val types: Map<String, ScalarAttributeType> =
            client
                .describeTable { it.tableName(table) }
                .table()
                .attributeDefinitions()
                .associate { it.attributeName() to it.attributeType() }
        return keyAttributes(table).associateWith { name: String ->
            val value: JsonNode = record[name]
            when (types[name]) {
                ScalarAttributeType.N -> AttributeValue.fromN(value.asText())
                ScalarAttributeType.B ->
                    AttributeValue.fromB(
                        software.amazon.awssdk.core.SdkBytes.fromByteArray(value.binaryValue())
                    )
                else -> AttributeValue.fromS(value.asText())
            }
        }
    }

    private fun orderItem(i: Int): Map<String, AttributeValue> =
        mapOf("id" to AttributeValue.fromS("o-$i"), "v" to AttributeValue.fromN(i.toString()))

    companion object {
        const val WIDE_ITEMS = 2500

        /**
         * Item 1 of `all_types` as this connector emits it. Differences from the legacy connector:
         * `big` is exact instead of the double `1.2345678901234568E29`, and the attributes the item
         * does not have (`only_in_2`, `only_in_2_num`) are present as null instead of absent.
         */
        const val EXPECTED_ALL_TYPES_ITEM_1 =
            """
            {"id": "1", "str": "hello", "int": 42, "dec": 12.34, "big": 123456789012345678901234567890,
             "neg": -7, "bin": "AQID", "sset": ["a", "b"], "nset": [1, 2.5, -3], "bset": ["AQID", "BAUG"],
             "flag": true, "nothing": null,
             "map": {"s": "x", "n_int": 1, "n_dec": 1.5, "b": "AQ==", "bool": false, "nul": null, "ss": ["m"],
                     "ns": [1], "bs": ["AQ=="], "nested_map": {"deep": "y"}, "nested_list": ["z", 9]},
             "list": ["s", 1, 2.5, true, null, {"k": "v"}, ["inner"]],
             "flexible": "text", "only_in_2": null, "only_in_2_num": null}
            """

        lateinit var container: DynamoDbLocalContainer
        lateinit var client: software.amazon.awssdk.services.dynamodb.DynamoDbClient
        lateinit var discoveredCatalog: AirbyteCatalog

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            container = DynamoDbLocalContainer().also { it.start() }
            client = container.client()
            DynamoDbParitySeed.seed(client)
            // Over 1 MB, so that a Scan without Limit needs several pages.
            client.createTableWithItems(
                "wide",
                listOf(KeyElement("id", KeyType.HASH, ScalarAttributeType.S)),
                emptyList(),
            )
            val filler: String = "x".repeat(600)
            client.batchPutItems(
                "wide",
                (1..WIDE_ITEMS).map {
                    mapOf(
                        "id" to AttributeValue.fromS("w-%04d".format(it)),
                        "filler" to AttributeValue.fromS(filler),
                    )
                },
            )
            // Date and timestamp cursors.
            client.createTableWithItems(
                "events",
                listOf(KeyElement("id", KeyType.HASH, ScalarAttributeType.S)),
                listOf(
                    event("e1", "2024-01-01", "2024-01-01T00:00:00Z"),
                    event("e2", "2024-01-01", "2024-01-01T12:00:00Z"),
                    event("e3", "2024-01-02", "2024-01-02T00:00:00Z"),
                    event("e4", "2024-01-03", "2024-01-03T00:00:00Z"),
                    event("e5", "2024-01-03", "2024-01-03T00:00:00Z"),
                ),
            )
            discoveredCatalog =
                CliRunner.source("discover", container.config()).run().catalogs().single()
        }

        private fun event(id: String, d: String, ts: String): Map<String, AttributeValue> =
            mapOf(
                "id" to AttributeValue.fromS(id),
                "d" to AttributeValue.fromS(d),
                "ts" to AttributeValue.fromS(ts),
            )

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            client.close()
            container.stop()
        }
    }
}
