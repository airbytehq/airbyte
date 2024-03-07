/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.components.debezium

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import io.debezium.relational.history.HistoryRecord
import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics
import org.apache.kafka.connect.source.SourceRecord
import java.time.Duration
import java.util.*
import kotlin.NoSuchElementException

fun interface DebeziumComponent {

    fun collect(input: Input): Output

    @JvmRecord
    data class Input(val config: Config, val state: State)

    data class Config(val debeziumProperties: Properties,
                      val lsnMapper: LsnMapper<*>,
                      val upperBound: State.Offset,
                      val maxRecords: Long,
                      val maxRecordBytes: Long,
                      val maxTime: Duration,
    ) {

        val debeziumName: String
            get() = debeziumProperties.getProperty("name")

        interface LsnMapper<T : Comparable<T>> {
            fun get(offset: State.Offset): T
            fun get(record: Record): T?
            fun get(sourceRecord: SourceRecord): T?
        }

        fun checkWithinBound(record: Record, sourceRecord: SourceRecord?): Boolean {
            val lsn = (sourceRecord?.let(typedLsnMapper()::get) ?: typedLsnMapper().get(record))
            return if (lsn == null) true else lsn < upperBoundLsn
        }

        fun checkProgress(before: State, after: State): Boolean =
            typedLsnMapper().get(before.offset) < typedLsnMapper().get(after.offset)

        @Suppress("UNCHECKED_CAST")
        private fun typedLsnMapper(): LsnMapper<Comparable<Any>> =
                lsnMapper as LsnMapper<Comparable<Any>>

        private val upperBoundLsn = typedLsnMapper().get(upperBound)
    }

    @JvmRecord
    data class State(val offset: Offset, val schema: Optional<Schema>) {

        @JvmRecord
        data class Offset(val debeziumOffset: Map<JsonNode, JsonNode>)

        @JvmRecord
        data class Schema(val debeziumSchemaHistory: List<HistoryRecord>)

    }

    @JvmRecord
    data class Output(val data: Sequence<Record>,
                      val state: State,
                      val executionSummary: ExecutionSummary,
                      val completionReasons: Set<CompletionReason>)


    @JvmRecord
    data class Record(val debeziumEventValue: JsonNode) {
        val isHeartbeat: Boolean
            get() = kind() == Kind.HEARTBEAT

        fun before(): JsonNode {
            return element("before")
        }

        fun after(): JsonNode {
            return element("after")
        }

        fun source(): JsonNode {
            return element("source")
        }

        fun element(fieldName: String?): JsonNode {
            if (!debeziumEventValue.has(fieldName)) {
                return NullNode.getInstance()
            }
            return debeziumEventValue[fieldName]
        }

        fun kind(): Kind {
            val source = source()
            if (source.isNull) {
                return Kind.HEARTBEAT
            }
            val snapshot = source["snapshot"] ?: return Kind.CHANGE
            return when (snapshot.asText().lowercase(Locale.getDefault())) {
                "false" -> Kind.CHANGE
                "last" -> Kind.SNAPSHOT_COMPLETE
                else -> Kind.SNAPSHOT_ONGOING
            }
        }

        enum class Kind {
            HEARTBEAT,
            CHANGE,
            SNAPSHOT_ONGOING,
            SNAPSHOT_COMPLETE,
        }
    }


    @JvmRecord
    data class ExecutionSummary(val events: LatencyStats,
                                val records: LatencyStats,
                                val recordsOutOfBounds: LatencyStats,
                                val collectDuration: Duration) {
        @JvmRecord
        data class LatencyStats(val elapsedSincePreviousMilli: DescriptiveStatistics) {

            fun count(): Long {
                return elapsedSincePreviousMilli.n
            }

            fun first(): Duration {
                return durationStat(if (count() == 0L) Double.NaN else elapsedSincePreviousMilli.getElement(0))
            }

            fun last(): Duration {
                return durationStat(if (count() == 0L) Double.NaN else elapsedSincePreviousMilli.getElement(count().toInt() - 1))
            }

            fun sum(): Duration {
                return durationStat(elapsedSincePreviousMilli.sum)
            }

            fun min(): Duration {
                return durationStat(elapsedSincePreviousMilli.min)
            }

            fun p01(): Duration {
                return durationStat(elapsedSincePreviousMilli.getPercentile(0.01))
            }

            fun p05(): Duration {
                return durationStat(elapsedSincePreviousMilli.getPercentile(0.05))
            }

            fun p10(): Duration {
                return durationStat(elapsedSincePreviousMilli.getPercentile(0.10))
            }

            fun p25(): Duration {
                return durationStat(elapsedSincePreviousMilli.getPercentile(0.25))
            }

            fun median(): Duration {
                return durationStat(elapsedSincePreviousMilli.getPercentile(0.50))
            }

            fun p75(): Duration {
                return durationStat(elapsedSincePreviousMilli.getPercentile(0.75))
            }

            fun p90(): Duration {
                return durationStat(elapsedSincePreviousMilli.getPercentile(0.90))
            }

            fun p95(): Duration {
                return durationStat(elapsedSincePreviousMilli.getPercentile(0.95))
            }

            fun p99(): Duration {
                return durationStat(elapsedSincePreviousMilli.getPercentile(0.99))
            }

            fun max(): Duration {
                return durationStat(elapsedSincePreviousMilli.max)
            }

            private fun durationStat(stat: Double): Duration {
                return if (stat.isNaN()) Duration.ZERO else Duration.ofMillis(stat.toLong())
            }
        }
    }

    enum class CompletionReason {
        HAS_FINISHED_SNAPSHOTTING,
        HAS_EVENTS_OUT_OF_BOUNDS,
        HAS_COLLECTED_ENOUGH_RECORDS,
        HAS_COLLECTED_LONG_ENOUGH,
        MEMORY_PRESSURE,
    }

    fun collectRepeatedly(initialInput: Input): Iterable<Output> = Iterable {
        object : Iterator<Output> {
            var nextOutput: Output? = collect(initialInput)

            override fun hasNext(): Boolean {
                return nextOutput != null
            }

            override fun next(): Output {
                val currentOutput = nextOutput ?: throw NoSuchElementException()
                if (currentOutput.completionReasons.contains(CompletionReason.HAS_EVENTS_OUT_OF_BOUNDS)) {
                    // Subsequent progress will always be beyond the upper bound.
                    nextOutput = null
                }
                if (currentOutput.completionReasons.contains(CompletionReason.HAS_FINISHED_SNAPSHOTTING)) {
                    // Snapshot completion can be thought of as a sort of upper bound as well.
                    nextOutput = null
                } else {
                    // Compute the successor output ahead of time for the next iteration.
                    val successorInput = Input(initialInput.config, currentOutput.state)
                    val successorOutput = collect(successorInput)
                    // Stop when reaching a fixed point.
                    val hasProgress = initialInput.config.checkProgress(successorInput.state, successorOutput.state)
                    nextOutput = if (hasProgress) successorOutput else null
                }
                return currentOutput
            }
        }
    }

}