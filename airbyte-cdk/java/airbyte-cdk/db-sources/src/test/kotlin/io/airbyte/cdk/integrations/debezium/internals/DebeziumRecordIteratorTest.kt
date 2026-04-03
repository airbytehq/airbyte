/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.integrations.debezium.CdcTargetPosition
import io.debezium.engine.ChangeEvent
import java.time.Duration
import java.util.*
import java.util.concurrent.LinkedBlockingQueue
import org.apache.kafka.connect.source.SourceRecord
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import org.mockito.Mockito.mock
import org.mockito.Mockito.`when`

class DebeziumRecordIteratorTest {

    /** Helper to create a ChangeEvent with a given op code. */
    private fun createChangeEvent(op: String): ChangeEvent<String?, String?> {
        return object : ChangeEvent<String?, String?> {
            override fun key(): String? = ""
            override fun value(): String = "{\"op\":\"$op\", \"source\": {\"snapshot\": \"false\"}}"
            override fun destination(): String? = null
        }
    }

    /**
     * Regression test for https://github.com/airbytehq/airbyte/issues/72476
     *
     * Verifies that op:m (message) events in the shutdown cleanup queue are properly filtered out.
     * Before the fix, these events would be passed to the converter which throws
     * IllegalStateException because they have no before/after records.
     */
    @Test
    fun `op m events in shutdown cleanup queue should be filtered out`() {
        // Setup: Create queues
        val mainQueue = LinkedBlockingQueue<ChangeEvent<String?, String?>>()

        // Create shutdown procedure mock with op:m event followed by valid op:c event
        val shutdownQueue = LinkedBlockingQueue<ChangeEvent<String?, String?>>()
        shutdownQueue.add(createChangeEvent("m")) // This should be filtered
        shutdownQueue.add(createChangeEvent("c")) // This should be returned

        val mockShutdownProcedure =
            mock(DebeziumShutdownProcedure::class.java)
                as DebeziumShutdownProcedure<ChangeEvent<String?, String?>>
        `when`(mockShutdownProcedure.recordsRemainingAfterShutdown).thenReturn(shutdownQueue)

        // Publisher is closed (returns true) so main loop exits immediately
        val publisherClosed = { true }

        val iterator =
            DebeziumRecordIterator(
                mainQueue,
                object : CdcTargetPosition<Long> {
                    override fun reachedTargetPosition(
                        changeEventWithMetadata: ChangeEventWithMetadata?
                    ): Boolean = false
                    override fun extractPositionFromHeartbeatOffset(
                        sourceOffset: Map<String?, *>
                    ): Long = 0L
                },
                publisherClosed,
                mockShutdownProcedure,
                Duration.ofMillis(100),
                getTestConfig()
            )

        // Act: Get the next event from the iterator
        val result = iterator.next()

        // Assert: Should get the op:c event, not the op:m event
        val opCode = result.eventValueAsJson?.get("op")?.asText()
        assertEquals(
            "c",
            opCode,
            "Expected op:c event but got op:$opCode - op:m was not filtered in shutdown loop"
        )
    }
    @Test
    fun getHeartbeatPositionTest() {
        val debeziumRecordIterator =
            DebeziumRecordIterator(
                mock(),
                object : CdcTargetPosition<Long> {
                    override fun reachedTargetPosition(
                        changeEventWithMetadata: ChangeEventWithMetadata?
                    ): Boolean {
                        return false
                    }

                    override fun extractPositionFromHeartbeatOffset(
                        sourceOffset: Map<String?, *>
                    ): Long {
                        return sourceOffset["lsn"] as Long
                    }
                },
                { false },
                mock(),
                Duration.ZERO,
                getTestConfig(), // Heartbeats should not be ignored for tests.
            )
        val lsn =
            debeziumRecordIterator.getHeartbeatPosition(
                object : ChangeEvent<String?, String?> {
                    private val sourceRecord =
                        SourceRecord(
                            null,
                            Collections.singletonMap("lsn", 358824993496L),
                            null,
                            null,
                            null,
                        )

                    override fun key(): String? {
                        return null
                    }

                    override fun value(): String {
                        return "{\"ts_ms\":1667616934701}"
                    }

                    override fun destination(): String? {
                        return null
                    }
                },
            )

        Assertions.assertEquals(lsn, 358824993496L)
    }

    fun getTestConfig(): JsonNode {
        val mapper: ObjectMapper = ObjectMapper()
        val testConfig = "{\"is_test\": true}"
        return mapper.readTree(testConfig)
    }

    @Test
    fun test_format_duration(): Unit {
        val debeziumRecordIterator =
            DebeziumRecordIterator(
                mock(),
                object : CdcTargetPosition<Long> {
                    override fun reachedTargetPosition(
                        changeEventWithMetadata: ChangeEventWithMetadata?
                    ): Boolean {
                        return false
                    }

                    override fun extractPositionFromHeartbeatOffset(
                        sourceOffset: Map<String?, *>
                    ): Long {
                        return sourceOffset["lsn"] as Long
                    }
                },
                { false },
                mock(),
                Duration.ZERO,
                getTestConfig(), // Heartbeats should not be ignored for tests.
            )
        val testCases =
            listOf(
                // include duration and expected output
                listOf(Duration.ofNanos(10), "0.00 ms"),
                listOf(Duration.ofNanos(40_560), "0.04 ms"),
                listOf(Duration.ofNanos(500_000), "0.50 ms"),
                listOf(Duration.ofMillis(42), "42.00 ms"),
                listOf(Duration.ofMillis(999), "999.00 ms"),
                listOf(Duration.ofSeconds(1), "1.00 seconds"),
                listOf(Duration.ofMillis(12500), "12.50 seconds"),
                listOf(Duration.ofSeconds(45), "45.00 seconds"),
                listOf(Duration.ofSeconds(60), "1.00 minutes"),
                listOf(Duration.ofSeconds(90), "1.50 minutes"),
                listOf(Duration.ofMinutes(30), "30.00 minutes"),
                listOf(Duration.ofMinutes(59), "59.00 minutes"),
                listOf(Duration.ofMinutes(60), "1.00 hours"),
                listOf(Duration.ofMinutes(150), "2.50 hours"),
                listOf(Duration.ofHours(5), "5.00 hours")
            )

        testCases.forEach { testCase ->
            val duration = testCase[0] as Duration
            val expected = testCase[1] as String
            assertEquals(expected, debeziumRecordIterator.formatDuration(duration))
        }
    }

    @ParameterizedTest
    @CsvSource(
        "c, true",
        "u, true",
        "d, true",
        "r, false",
        "t, true",
        "m, false",
        "badVal, false",
        "'', false",
    )
    fun handledEventTypesTest(op: String, handled: Boolean) {
        Assertions.assertEquals(
            handled,
            DebeziumRecordIterator.isEventTypeHandled(
                ChangeEventWithMetadata(
                    object : ChangeEvent<String?, String?> {

                        private val sourceRecord =
                            SourceRecord(
                                null,
                                Collections.singletonMap("lsn", 358824993496L),
                                null,
                                null,
                                null,
                            )

                        override fun key(): String? {
                            return ""
                        }

                        override fun value(): String {
                            return "{\"op\":\"$op\", \"source\": {\"snapshot\": \"false\"}}"
                        }

                        override fun destination(): String? {
                            return null
                        }
                    }
                )
            )
        )
    }
}
