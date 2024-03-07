/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.components.debezium

import io.airbyte.commons.json.Jsons
import java.time.Clock
import java.time.Duration
import java.time.Instant
import java.time.ZoneOffset
import java.util.*
import org.apache.kafka.connect.source.SourceRecord
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

typealias Record = DebeziumComponent.Record

typealias Kind = DebeziumComponent.Record.Kind

typealias Reason = DebeziumComponent.CompletionReason

typealias Config = DebeziumComponent.Config

class DebeziumEngineSharedStateTest {

    val zeroState =
        DebeziumComponent.State(DebeziumComponent.State.Offset(mapOf()), Optional.empty())
    val zeroClock = Clock.fixed(Instant.ofEpochSecond(1709164800), ZoneOffset.UTC)
    val noCompletion = testConfig()

    @Test
    fun testZero() {
        val expected =
            EndState(
                listOf(),
                setOf(),
            )
        doTestCase(noCompletion, expected)
    }

    @Test
    fun testNoCompletion() {
        val expected =
            EndState(
                listOf(Pair(3, Kind.CHANGE), Pair(4, Kind.CHANGE), Pair(6, Kind.CHANGE)),
                setOf(),
                numHeartbeats = 3,
                totalDuration = Duration.ofSeconds(6),
                maxEventLatency = Duration.ofSeconds(1),
                maxRecordLatency = Duration.ofSeconds(3),
            )
        doTestCase(
            noCompletion,
            expected,
            Wait(),
            Heartbeat(1),
            Wait(),
            Heartbeat(2),
            Wait(),
            Change(3),
            Wait(),
            Change(4),
            Wait(),
            Heartbeat(5),
            Wait(),
            Change(6)
        )
    }

    @Test
    fun testMaxRecords() {
        val expected =
            EndState(
                listOf(Pair(1, Kind.CHANGE), Pair(2, Kind.CHANGE)),
                setOf(Reason.HAS_COLLECTED_ENOUGH_RECORDS),
            )
        doTestCase(testConfig(maxRecords = 2), expected, Change(1), Change(2), Change(3))
    }

    @Test
    fun testSnapshotting() {
        val expected =
            EndState(
                listOf(
                    Pair(1, Kind.SNAPSHOT_ONGOING),
                    Pair(2, Kind.SNAPSHOT_ONGOING),
                    Pair(3, Kind.SNAPSHOT_COMPLETE),
                ),
                setOf(Reason.HAS_FINISHED_SNAPSHOTTING),
            )
        doTestCase(
            testConfig(),
            expected,
            SnapshotOngoing(1),
            SnapshotOngoing(2),
            SnapshotComplete(3),
            Change(4)
        )
    }

    @Test
    fun testBoundChecks() {
        val expected =
            EndState(
                listOf(Pair(1, Kind.CHANGE), Pair(2, Kind.CHANGE)),
                setOf(Reason.HAS_EVENTS_OUT_OF_BOUNDS),
                numRecordsOutOfBounds = 1,
                totalDuration = Duration.ofSeconds(2),
                maxEventLatency = Duration.ofSeconds(1),
                maxRecordLatency = Duration.ofSeconds(1),
                maxRecordOutOfBoundsLatency = Duration.ofSeconds(2)
            )
        doTestCase(
            testConfig(maxLsn = 2),
            expected,
            Wait(),
            Change(1),
            Wait(),
            Change(2),
            Wait(),
            Change(3),
        )
    }

    @Test
    fun testMemoryPressure() {
        val expected =
            EndState(
                listOf(Pair(3, Kind.CHANGE), Pair(4, Kind.CHANGE)),
                setOf(Reason.MEMORY_PRESSURE),
                numHeartbeats = 2,
            )
        doTestCase(
            testConfig(maxRecordBytes = 60),
            expected,
            Heartbeat(1),
            Heartbeat(2),
            Change(3),
            Change(4),
            Heartbeat(5),
            Change(6)
        )
    }

    @Test
    fun testOverallLatency() {
        val expected =
            EndState(
                listOf(),
                setOf(Reason.HAS_COLLECTED_LONG_ENOUGH),
                numHeartbeats = 3,
                totalDuration = Duration.ofSeconds(3),
                maxEventLatency = Duration.ofSeconds(1),
            )
        doTestCase(
            testConfig(maxTime = Duration.ofSeconds(2)),
            expected,
            Wait(),
            Heartbeat(1),
            Wait(),
            Heartbeat(2),
            Wait(),
            Heartbeat(3),
        )
    }

    fun testConfig(
        maxLsn: Long = Long.MAX_VALUE,
        maxRecords: Long = Long.MAX_VALUE,
        maxRecordBytes: Long = Long.MAX_VALUE,
        maxTime: Duration = Duration.ofHours(1_000),
    ) =
        (ConfigBuilder()
            .withUpperBound(zeroState.offset)
            .withLsnMapper(
                object : DebeziumComponent.Config.LsnMapper<Long> {

                    override fun get(offset: DebeziumComponent.State.Offset): Long = maxLsn

                    override fun get(record: DebeziumComponent.Record): Long? =
                        record.debeziumEventValue["lsn"].asLong()

                    override fun get(sourceRecord: SourceRecord): Long? = null
                }
            )
            .withMaxRecords(maxRecords)
            .withMaxRecordBytes(maxRecordBytes)
            .withMaxTime(maxTime)
            .build())

    sealed interface Event {
        fun get(): Pair<Duration, String?>
    }

    data class Wait(val seconds: Long = 1L) : Event {
        override fun get(): Pair<Duration, String?> {
            return Pair(Duration.ofSeconds(seconds), null)
        }
    }

    data class Heartbeat(val lsn: Int) : Event {
        override fun get(): Pair<Duration, String?> {
            return Pair(Duration.ZERO, "{\"lsn\":$lsn}")
        }
    }

    data class Change(val lsn: Int) : Event {
        override fun get(): Pair<Duration, String?> {
            return Pair(Duration.ZERO, "{\"lsn\":$lsn,\"source\":{\"snapshot\":\"false\"}}")
        }
    }

    data class SnapshotOngoing(val lsn: Int) : Event {
        override fun get(): Pair<Duration, String?> {
            return Pair(Duration.ZERO, "{\"lsn\":$lsn,\"source\":{\"snapshot\":\"true\"}}")
        }
    }

    data class SnapshotComplete(val lsn: Int) : Event {
        override fun get(): Pair<Duration, String?> {
            return Pair(Duration.ZERO, "{\"lsn\":$lsn,\"source\":{\"snapshot\":\"last\"}}")
        }
    }

    data class EndState(
        val data: List<Pair<Int, Kind>>,
        val completionReasons: Set<Reason>,
        val numHeartbeats: Long = 0L,
        val numRecordsOutOfBounds: Long = 0L,
        val totalDuration: Duration = Duration.ZERO,
        val maxEventLatency: Duration = Duration.ZERO,
        val maxRecordLatency: Duration = Duration.ZERO,
        val maxRecordOutOfBoundsLatency: Duration = Duration.ZERO
    )

    fun doTestCase(config: Config, expected: EndState, vararg events: Event) {
        var usedHeap: Long = 0
        var elapsedTotal = Duration.ZERO
        val sharedState = DebeziumEngineSharedState(config)
        sharedState.clock = zeroClock
        sharedState.reset()
        for (e in events) {
            val (elapsed, jsonString) = e.get()
            elapsedTotal = elapsedTotal.plus(elapsed)
            sharedState.clock = Clock.offset(zeroClock, elapsedTotal)
            if (jsonString != null) {
                usedHeap += 0.coerceAtLeast(jsonString.length - 12)
                sharedState.add(Record(Jsons.deserialize(jsonString)), null)
            }
            if (sharedState.isComplete) break
        }
        val output = sharedState.build(zeroState)
        Assertions.assertEquals(
            output.data.count().toLong(),
            output.executionSummary.records.count()
        )
        Assertions.assertTrue(
            output.executionSummary.records.count() <= output.executionSummary.events.count()
        )
        Assertions.assertTrue(
            output.executionSummary.recordsOutOfBounds.count() <=
                output.executionSummary.records.count()
        )
        val actual =
            EndState(
                output.data
                    .map { r -> Pair(r.debeziumEventValue["lsn"].asInt(), r.kind()) }
                    .toList(),
                output.completionReasons,
                output.executionSummary.events.count() - output.executionSummary.records.count(),
                output.executionSummary.recordsOutOfBounds.count(),
                output.executionSummary.collectDuration,
                output.executionSummary.events.max(),
                output.executionSummary.records.max(),
                output.executionSummary.recordsOutOfBounds.max()
            )
        Assertions.assertEquals(expected, actual)
    }
}
