/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicLong

@Singleton
class DevNullAggregateFactory(
    private val config: DevNullConfiguration,
) : AggregateFactory {
    private val log = KotlinLogging.logger {}

    /**
     * The CDK creates a new [Aggregate] for every batch it flushes, so counters must live here,
     * keyed by stream, for "first N" / "fail after N" to mean N per stream rather than N per batch.
     */
    private val streamCounters = ConcurrentHashMap<StoreKey, StreamCounters>()

    internal fun countersFor(key: StoreKey): StreamCounters =
        streamCounters.computeIfAbsent(key) { StreamCounters() }

    override fun create(key: StoreKey): Aggregate {
        return when (val type = config.type) {
            is Logging -> {
                log.info { "Creating LoggingAggregate for type=LOGGING" }
                LoggingAggregate(
                    logEveryN = type.logEvery,
                    streamDescriptor = key,
                    maxLogCount = type.maxEntryCount,
                    sampleRate = type.sampleRate,
                    seed = type.seed,
                    counters = countersFor(key),
                )
            }
            is Silent -> {
                log.info { "Creating SilentAggregate for type=SILENT" }
                SilentAggregate()
            }
            is Throttled -> {
                log.info { "Creating ThrottledAggregate for type=THROTTLED" }
                ThrottledAggregate(type.millisPerRecord)
            }
            is Failing -> {
                log.info { "Creating FailingAggregate for type=FAILING" }
                FailingAggregate(key, type.numMessages, countersFor(key))
            }
        }
    }
}

/** Per-stream record/log counters shared by all aggregates of one stream. */
class StreamCounters {
    val recordCount = AtomicLong(0L)
    val logCount = AtomicLong(0L)
}

class LoggingAggregate(
    private val logEveryN: Int,
    private val streamDescriptor: DestinationStream.Descriptor,
    private val maxLogCount: Int = 1000,
    private val sampleRate: Double = 1.0,
    seed: Long? = null,
    private val counters: StreamCounters = StreamCounters(),
) : Aggregate {
    private val log = KotlinLogging.logger {}
    private val random = seed?.let { kotlin.random.Random(it) } ?: kotlin.random.Random.Default

    override fun accept(record: RecordDTO) {
        val recordIndex = counters.recordCount.getAndIncrement()
        if (recordIndex % logEveryN == 0L) {
            if (sampleRate == 1.0 || random.nextDouble() < sampleRate) {
                val logEntry = counters.logCount.incrementAndGet()
                if (logEntry <= maxLogCount) {
                    log.info {
                        "Logging Destination(stream=$streamDescriptor, recordIndex=$recordIndex, logEntry=$logEntry/$maxLogCount): ${record.fields}"
                    }
                }
            }
        }
    }

    override suspend fun flush() {
        /* Do nothing - dev-null doesn't persist data */
    }
}

class SilentAggregate : Aggregate {
    override fun accept(record: RecordDTO) {
        /* Do nothing - silently discard */
    }

    override suspend fun flush() {
        /* Do nothing - dev-null doesn't persist data */
    }
}

class ThrottledAggregate(private val millisPerRecord: Long) : Aggregate {
    override fun accept(record: RecordDTO) {
        Thread.sleep(millisPerRecord)
    }

    override suspend fun flush() {
        /* Do nothing - dev-null doesn't persist data */
    }
}

class FailingAggregate(
    private val streamDescriptor: DestinationStream.Descriptor,
    private val failAfter: Int,
    private val counters: StreamCounters = StreamCounters(),
) : Aggregate {
    private val log = KotlinLogging.logger {}

    override fun accept(record: RecordDTO) {
        val recordCount = counters.recordCount.incrementAndGet()
        if (recordCount >= failAfter) {
            val message =
                "Failing Destination(stream=$streamDescriptor, failAfter=$failAfter: failing at record $recordCount)"
            log.info { message }
            throw RuntimeException(message)
        }
    }

    override suspend fun flush() {
        /* Do nothing - dev-null doesn't persist data */
    }
}
