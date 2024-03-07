/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.components.debezium

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.NullNode
import io.debezium.relational.history.HistoryRecord
import java.time.Duration
import java.util.*
import kotlin.NoSuchElementException
import org.apache.commons.math3.stat.descriptive.DescriptiveStatistics
import org.apache.kafka.connect.source.SourceRecord

/** API for collecting CDC records using Debezium. */
fun interface DebeziumComponent {

    /**
     * Collect CDC records from the source database as specified by the [input]. This should have
     * little to no side effects: the state of source database and the [input] determine the output.
     *
     * This is intended to be an atomic operation which should be straightforward to mock in
     * high-level unit tests of a database source. As such its space and time usage are capped
     * according to paramenters in the [input].
     *
     * In production, we need to checkpoint overall progress at regular intervals; the intention
     * here is to do so after each call to [collect]. The [collectRepeatedly] method can be used to
     * call [collect] in sequence.
     */
    fun collect(input: Input): Output

    /**
     * Input for [collect].
     *
     * This is separated into two parts according to the following principle:
     * - [config] contains the input parameters which don't change from one successive call to
     * [collect] to the next;
     * - [state] contains those which do, these will be the initial content of Debezium's offset and
     * schema history files.
     */
    @JvmRecord data class Input(val config: Config, val state: State)

    /**
     * [Config] holds the [Input] parameters which don't change from one successive call to
     * [collect] to the next.
     *
     * The [debeziumProperties] property map is used to initialize the Debezium engine.
     *
     * The [lsnMapper] interface is used to compare relative CDC progress without knowledge of how
     * the progress itself is encoded.
     *
     * The rest are termination criteria:
     * - [upperBound] is the targeted upper bound of CDC progress, [collect] stops when it's reached
     * or exceeded,
     * - [maxRecords] is the threshold of collected [Record]s at or beyond which [collect] stops,
     * - [maxRecordBytes] is the threshold of collected JSON [Record] bytes at or beyond which
     * [collect] stops,
     * - [maxTime] is the threshold of collected JSON-serialized [Record] bytes at or beyond which
     * [collect] stops,
     */
    data class Config(
        val debeziumProperties: Properties,
        val lsnMapper: LsnMapper<*>,
        val upperBound: State.Offset,
        val maxRecords: Long,
        val maxRecordBytes: Long,
        val maxTime: Duration,
    ) {

        /** Name of the Debezium instance defined by this [Config]. */
        val debeziumName: String
            get() = debeziumProperties.getProperty("name")

        /**
         * [LsnMapper] abstracts the mapping from [State.Offset] and [Record] to a
         * database-dependent LSN value. All that matters as far as the [DebeziumComponent] is
         * concerned is that the values are [Comparable]. Its clients by design are the
         * [checkWithinBound] and [checkProgress] methods.
         */
        interface LsnMapper<T : Comparable<T>> {

            /** Maps a [State.Offset] to an LSN value. */
            fun get(offset: State.Offset): T

            /** Maps a [Record] to an LSN value. */
            fun get(record: Record): T?

            /** Maps a [SourceRecord] to an LSN value. */
            fun get(sourceRecord: SourceRecord): T?
        }

        /**
         * Returns true iff the Debezium [Record] is within bounds as defined by [upperBound]. The
         * Debezium [SourceRecord] accompanying the [Record] is preferred, but this object is
         * internal to the Debezium Engine and therefore may not always be available.
         */
        fun checkWithinBound(record: Record, sourceRecord: SourceRecord?): Boolean {
            val lsn = (sourceRecord?.let(typedLsnMapper()::get) ?: typedLsnMapper().get(record))
            return if (lsn == null) true else lsn < upperBoundLsn
        }

        /** Returns true iff progress has been made between [before] and [after]. */
        fun checkProgress(before: State, after: State): Boolean =
            typedLsnMapper().get(before.offset) < typedLsnMapper().get(after.offset)

        /**
         * Convenience function that allows us to ignore the type parameter. The compiler can't tell
         * that LsnMapper<*> methods all return the same (albeit unknown) type.
         */
        @Suppress("UNCHECKED_CAST")
        private fun typedLsnMapper(): LsnMapper<Comparable<Any>> =
            lsnMapper as LsnMapper<Comparable<Any>>

        /** Precomputed for performance reasons: every [Record] is compared against this value. */
        private val upperBoundLsn = typedLsnMapper().get(upperBound)
    }

    /**
     * [State] maps to the contents of the Debezium offset and schema history files, either prior to
     * or after a call to [collect]. [State] is also what gets serialized into an Airbyte STATE
     * message as global CDC state.
     */
    @JvmRecord
    data class State(val offset: Offset, val schema: Optional<Schema>) {

        /** [Offset] maps to the Debezium offset file contents. */
        @JvmRecord data class Offset(val debeziumOffset: Map<JsonNode, JsonNode>)

        /** [Schema] maps to the Debezium schema history file contents. */
        @JvmRecord data class Schema(val debeziumSchemaHistory: List<HistoryRecord>)
    }

    /**
     * [Output] is the return type of [collect] and contains:
     * - [data] contains the [Record] objects,
     * - [state] has the contents of the Debezium offset and schema history files, see [State]
     * - [executionSummary] has statistics on the execution of [collect] like runtime, etc, see
     * [ExecutionSummary],
     * - [completionReasons] is the set of reasons of what cause [collect] to stop, see
     * [CompletionReason].
     */
    @JvmRecord
    data class Output(
        val data: Sequence<Record>,
        val state: State,
        val executionSummary: ExecutionSummary,
        val completionReasons: Set<CompletionReason>
    )

    /** [Record] wraps a Debezium change data event. */
    @JvmRecord
    data class Record(val debeziumEventValue: JsonNode) {

        /** True if this is a Debezium heartbeat event. These aren't persisted in [Output]. */
        val isHeartbeat: Boolean
            get() = kind() == Kind.HEARTBEAT

        /** The datum prior to this event; null for insertions. */
        fun before(): JsonNode {
            return element("before")
        }

        /** The datum following this event; null for deletions. */
        fun after(): JsonNode {
            return element("after")
        }

        /** Metadata containing transaction IDs, LSNs, etc, null for heartbeats. */
        fun source(): JsonNode {
            return element("source")
        }

        /**
         * Convenience function for accessing child object nodes of the debezium event root node.
         */
        fun element(fieldName: String?): JsonNode {
            if (!debeziumEventValue.has(fieldName)) {
                return NullNode.getInstance()
            }
            return debeziumEventValue[fieldName]
        }

        /** Change data event [Kind]. */
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

        /** Kinds of Debezium change data events. */
        enum class Kind {
            /** [SNAPSHOT_ONGOING] is a change data event part of a Debezium Snapshot. */
            SNAPSHOT_ONGOING,

            /**
             * [SNAPSHOT_COMPLETE] is a change data event which signals the completion of a Debezium
             * Snapshot.
             */
            SNAPSHOT_COMPLETE,

            /**
             * [CHANGE] is a change data event emitted following the completion of a Debezium
             * Snapshot.
             */
            CHANGE,

            /**
             * [HEARTBEAT] is a keep-alive event which has no data, but which may encode progress in
             * the form of an LSN, etc.
             */
            HEARTBEAT,
        }
    }

    /**
     * [ExecutionSummary] holds counters and latency statistics:
     * - [events] has statistics for all Debezium events including [Record.Kind.HEARTBEAT].
     * - [records] has statistics for all non-heartbeat events.
     * - [recordsOutOfBounds] has statistics for all non-heartbeat events failing
     * [Config.checkWithinBound].
     * - [collectDuration] is the overall latency of the [collect] call.
     */
    @JvmRecord
    data class ExecutionSummary(
        val events: LatencyStats,
        val records: LatencyStats,
        val recordsOutOfBounds: LatencyStats,
        val collectDuration: Duration
    ) {

        /**
         * [LatencyStats] is a convenience wrapper mapping [DescriptiveStatistics] output into
         * [Duration] types suitable for encoding event latencies. Event latencies are computed by
         * subtracting the [collect] start timestamp from the event's timestamp.
         */
        @JvmRecord
        data class LatencyStats(val elapsedSincePreviousMilli: DescriptiveStatistics) {

            fun count(): Long {
                return elapsedSincePreviousMilli.n
            }

            fun first(): Duration {
                return durationStat(
                    if (count() == 0L) Double.NaN else elapsedSincePreviousMilli.getElement(0)
                )
            }

            fun last(): Duration {
                return durationStat(
                    if (count() == 0L) Double.NaN
                    else elapsedSincePreviousMilli.getElement(count().toInt() - 1)
                )
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

    /** Reasons which might trigger [collect] to stop. */
    enum class CompletionReason {
        /** [HAS_FINISHED_SNAPSHOTTING] if an ongoing snapshot was completed. */
        HAS_FINISHED_SNAPSHOTTING,

        /** [HAS_EVENTS_OUT_OF_BOUNDS] if at least one event failed [Config.checkWithinBound]. */
        HAS_EVENTS_OUT_OF_BOUNDS,

        /**
         * [HAS_COLLECTED_ENOUGH_RECORDS] if [Output.data] contains at least [Config.maxRecords].
         */
        HAS_COLLECTED_ENOUGH_RECORDS,

        /**
         * [HAS_COLLECTED_LONG_ENOUGH] if [ExecutionSummary.collectDuration] is not less than
         * [Config.maxTime].
         */
        HAS_COLLECTED_LONG_ENOUGH,

        /** [MEMORY_PRESSURE] if [Output.data] contains at least [Config.maxRecordBytes]. */
        MEMORY_PRESSURE,
    }

    /**
     * Calls [collect] repeatedly until:
     * - either the upper bound has been reached (event fails to verify [Config.checkWithinBound])
     * - or forward progress stalls ([Config.checkProgress] fails for two successive [State]
     * instances).
     *
     * This method gets called exactly once in a source connector READ call.
     */
    fun collectRepeatedly(initialInput: Input): Iterable<Output> = Iterable {
        object : Iterator<Output> {
            var nextOutput: Output? = collect(initialInput)

            override fun hasNext(): Boolean {
                return nextOutput != null
            }

            override fun next(): Output {
                val currentOutput = nextOutput ?: throw NoSuchElementException()
                if (
                    currentOutput.completionReasons.contains(
                        CompletionReason.HAS_EVENTS_OUT_OF_BOUNDS
                    )
                ) {
                    // Subsequent progress will always be beyond the upper bound.
                    nextOutput = null
                }
                if (
                    currentOutput.completionReasons.contains(
                        CompletionReason.HAS_FINISHED_SNAPSHOTTING
                    )
                ) {
                    // Snapshot completion can be thought of as a sort of upper bound as well.
                    nextOutput = null
                } else {
                    // Compute the successor output ahead of time for the next iteration.
                    val successorInput = Input(initialInput.config, currentOutput.state)
                    val successorOutput = collect(successorInput)
                    // Stop when reaching a fixed point.
                    val hasProgress =
                        initialInput.config.checkProgress(
                            successorInput.state,
                            successorOutput.state
                        )
                    nextOutput = if (hasProgress) successorOutput else null
                }
                return currentOutput
            }
        }
    }
}
