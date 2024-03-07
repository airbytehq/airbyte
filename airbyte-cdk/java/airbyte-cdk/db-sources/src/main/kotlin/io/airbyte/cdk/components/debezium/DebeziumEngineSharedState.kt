/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.components.debezium

import com.google.common.collect.ImmutableList
import io.airbyte.commons.json.Jsons
import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics
import org.apache.kafka.connect.source.SourceRecord
import java.time.Clock
import java.time.Duration
import java.time.Instant
import java.util.*
import java.util.concurrent.atomic.AtomicLong
import kotlin.collections.Iterator
import kotlin.math.max

class DebeziumEngineSharedState(val config: DebeziumComponent.Config) {

    private val startEpochMilli = AtomicLong()
    private val numRecords = AtomicLong()
    private val numRecordBytes = AtomicLong()
    private val completionReasonsBitfield = AtomicLong()
    private val buffer: MutableList<BufferElement> = Collections.synchronizedList(ArrayList(1_000_000))
    internal var clock: Clock = Clock.systemUTC()

    fun reset() {
        startEpochMilli.set(Instant.now(clock).toEpochMilli())
        numRecords.set(0L)
        numRecordBytes.set(0L)
        completionReasonsBitfield.set(0L)
        synchronized(buffer) {
            buffer.clear()
        }
    }

    val isComplete: Boolean
        get() = completionReasonsBitfield.get() != 0L

    fun add(record: DebeziumComponent.Record, sourceRecord: SourceRecord?) {
        // Store current state before updating it.
        val now = Instant.now(clock)
        val elapsedSinceStart = Duration.between(startedAt(), now)
        val isWithinBounds = config.checkWithinBound(record, sourceRecord)
        // Update buffer.
        addToBuffer(record, isWithinBounds, now)
        // Time-based completion checks.
        if (config.maxTime.minus(elapsedSinceStart).isNegative) {
            // We have spent enough time collecting records, shut down.
            addCompletionReason(DebeziumComponent.CompletionReason.HAS_COLLECTED_LONG_ENOUGH)
        }
        // Other engine completion checks.
        if (!isWithinBounds) {
            // We exceeded the high-water mark, shut down.
            addCompletionReason(DebeziumComponent.CompletionReason.HAS_EVENTS_OUT_OF_BOUNDS)
        }
        if (!record.isHeartbeat && numRecords() >= config.maxRecords) {
            // We have collected enough records, shut down.
            addCompletionReason(DebeziumComponent.CompletionReason.HAS_COLLECTED_ENOUGH_RECORDS)
        }
        if (!record.isHeartbeat && numRecordBytes() >= config.maxRecordBytes) {
            // We have collected enough record bytes, shut down.
            addCompletionReason(DebeziumComponent.CompletionReason.MEMORY_PRESSURE)
        }
        if (record.kind() == DebeziumComponent.Record.Kind.SNAPSHOT_COMPLETE) {
            // We were snapshotting and we finished the snapshot, shut down.
            addCompletionReason(DebeziumComponent.CompletionReason.HAS_FINISHED_SNAPSHOTTING)
        }
    }

    private fun numRecords(): Long {
        return numRecords.get()
    }

    private fun numRecordBytes(): Long {
        return numRecordBytes.get()
    }

    private fun startedAt(): Instant {
        return Instant.ofEpochMilli(startEpochMilli.get())
    }

    private fun addToBuffer(record: DebeziumComponent.Record, isWithinBounds: Boolean, timestamp: Instant) {
        val e = BufferElement(if (record.isHeartbeat) null else Jsons.toBytes(record.debeziumEventValue), isWithinBounds, timestamp.toEpochMilli())
        synchronized(buffer) {
            buffer.add(e)
        }
        if (!e.isHeartbeat) {
            numRecordBytes.getAndAdd(e.recordJsonBytes?.size?.toLong() ?: 0L)
            numRecords.getAndIncrement()
        }
    }

    fun addCompletionReason(reason: DebeziumComponent.CompletionReason) {
        completionReasonsBitfield.getAndUpdate { acc: Long -> acc or (1L shl reason.ordinal) }
    }

    fun build(state: DebeziumComponent.State): DebeziumComponent.Output {
        val serializedRecordsBuilder = ImmutableList.builderWithExpectedSize<ByteArray>(numRecords.get().toInt())
        val eventStats = DescriptiveStatistics()
        val recordStats = DescriptiveStatistics()
        val recordOutOfBoundsStats = DescriptiveStatistics()
        synchronized(buffer) {
            var previousEventEpochMilli = startEpochMilli.get()
            var previousRecordEpochMilli = startEpochMilli.get()
            var previousRecordOutOfBoundsEpochMilli = startEpochMilli.get()
            for ((serializedRecord, isWithinBounds, epochMilli) in buffer) {
                eventStats.addValue(max(0.0, (epochMilli - previousEventEpochMilli).toDouble()))
                previousEventEpochMilli = epochMilli
                if (serializedRecord != null) {
                    serializedRecordsBuilder.add(serializedRecord)
                    recordStats.addValue(max(0.0, (epochMilli - previousRecordEpochMilli).toDouble()))
                    previousRecordEpochMilli = epochMilli
                    if (!isWithinBounds) {
                        recordOutOfBoundsStats.addValue(max(0.0, (epochMilli - previousRecordOutOfBoundsEpochMilli).toDouble()))
                        previousRecordOutOfBoundsEpochMilli = epochMilli
                    }
                }
            }
        }
        val completionReasons = EnumSet.noneOf(DebeziumComponent.CompletionReason::class.java)
        for (reason in DebeziumComponent.CompletionReason.entries.toTypedArray()) {
            if ((completionReasonsBitfield.get() and (1L shl reason.ordinal)) != 0L) {
                completionReasons.add(reason)
            }
        }
        val serializedRecords: List<ByteArray> = serializedRecordsBuilder.build()
        val lazyRecordSequence = Sequence { object: Iterator<DebeziumComponent.Record> {

            var index = 0

            override fun hasNext(): Boolean = index < serializedRecords.size

            override fun next() = DebeziumComponent.Record(Jsons.fromBytes(serializedRecords.get(index++)))
        }}
        return DebeziumComponent.Output(
                lazyRecordSequence,
                state,
                DebeziumComponent.ExecutionSummary(
                        DebeziumComponent.ExecutionSummary.LatencyStats(eventStats),
                        DebeziumComponent.ExecutionSummary.LatencyStats(recordStats),
                        DebeziumComponent.ExecutionSummary.LatencyStats(recordOutOfBoundsStats),
                        Duration.ofMillis(Instant.now(clock).toEpochMilli() - startEpochMilli.get())),
                completionReasons)
    }


    @JvmRecord
    internal data class BufferElement(val recordJsonBytes: ByteArray?, val isWithinBounds: Boolean, val tsEpochMilli: Long) {

        val isHeartbeat: Boolean
            get() = recordJsonBytes == null

        override fun toString(): String {
            val record = recordJsonBytes?.let { String } ?: "<heartbeat>"
            return "BufferElement(record=$record}, isWithinBounds=$isWithinBounds, ts=${Instant.ofEpochMilli(tsEpochMilli)})"
        }

        override fun equals(other: Any?): Boolean {
            if (this === other) return true
            if (javaClass != other?.javaClass) return false

            other as BufferElement

            if (recordJsonBytes != null) {
                if (other.recordJsonBytes == null) return false
                if (!recordJsonBytes.contentEquals(other.recordJsonBytes)) return false
            } else if (other.recordJsonBytes != null) return false
            if (isWithinBounds != other.isWithinBounds) return false
            if (tsEpochMilli != other.tsEpochMilli) return false

            return true
        }

        override fun hashCode(): Int {
            var result = recordJsonBytes?.contentHashCode() ?: 0
            result = 31 * result + isWithinBounds.hashCode()
            result = 31 * result + tsEpochMilli.hashCode()
            return result
        }


    }

}
