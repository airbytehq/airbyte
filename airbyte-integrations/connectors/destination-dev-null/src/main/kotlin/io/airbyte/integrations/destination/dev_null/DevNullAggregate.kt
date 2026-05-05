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

@Singleton
class DevNullAggregateFactory(
    private val config: DevNullConfiguration,
) : AggregateFactory {
    private val log = KotlinLogging.logger {}

    override fun create(key: StoreKey): Aggregate {
        return when (val type = config.type) {
            is Logging -> {
                log.info { "Creating LoggingAggregate for type=LOGGING" }
                LoggingAggregate(
                    logEveryN = type.logEvery,
                    streamDescriptor = key,
                    maxLogCount = type.maxEntryCount,
                    sampleRate = type.sampleRate,
                    seed = type.seed
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
                FailingAggregate(key, type.numMessages)
            }
        }
    }
}

class LoggingAggregate(
    private val logEveryN: Int,
    private val streamDescriptor: DestinationStream.Descriptor,
    private val maxLogCount: Int = 1000,
    private val sampleRate: Double = 1.0,
    seed: Long? = null
) : Aggregate {
    private val log = KotlinLogging.logger {}
    private var recordCount: Long = 0L
    private var logCount: Long = 0L
    private val random = seed?.let { kotlin.random.Random(it) } ?: kotlin.random.Random.Default

    override fun accept(record: RecordDTO) {
        if (recordCount % logEveryN == 0L) {
            if (sampleRate == 1.0 || random.nextDouble() < sampleRate) {
                if (++logCount <= maxLogCount) {
                    log.info {
                        "Logging Destination(stream=$streamDescriptor, recordIndex=$recordCount, logEntry=$logCount/$maxLogCount): ${record.fields}"
                    }
                }
            }
        }
        recordCount++
    }

    override suspend fun flush() {
        /* Do nothing - dev-null doesn't persist data */
    }
}

class SilentAggregate : Aggregate {
    private val log = KotlinLogging.logger {}
    private var recordCount: Long = 0L

    override fun accept(record: RecordDTO) {
        // DO NOT MERGE: pre-release force-fail injection used to investigate an
        // orchestrator race that drops connector-emitted ERROR trace messages.
        // See https://github.com/airbytehq/airbyte/pull/77746 for the source-side
        // analogue + investigation notes.
        if (recordCount >= 0) {
            val message =
                "destination-dev-null pre-release force-fail injection. DO NOT MERGE."
            log.info { message }
            throw ForceFailError(message)
        }
        recordCount++
    }

    override suspend fun flush() {
        /* Do nothing - dev-null doesn't persist data */
    }
}

/** Custom exception raised by the pre-release force-fail injection. DO NOT MERGE. */
class ForceFailError(message: String) : RuntimeException(message)

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
    private val failAfter: Int
) : Aggregate {
    private val log = KotlinLogging.logger {}
    private var recordCount: Long = 0L

    override fun accept(record: RecordDTO) {
        if (recordCount > failAfter) {
            val message =
                "Failing Destination(stream=$streamDescriptor, failAfter=$failAfter: failing at record $recordCount)"
            log.info { message }
            throw RuntimeException(message)
        }
        recordCount++
    }

    override suspend fun flush() {
        /* Do nothing - dev-null doesn't persist data */
    }
}
