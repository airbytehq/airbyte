/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

@Singleton
class DevNullV2AggregateFactory(
    private val config: DevNullV2Configuration,
) : AggregateFactory {
    private val log = KotlinLogging.logger {}

    override fun create(
        key: StoreKey // This is actually DestinationStream.Descriptor
    ): Aggregate {
        val streamDescriptor = key as DestinationStream.Descriptor
        return when (config.type) {
            DevNullV2Configuration.Type.LOGGING -> {
                log.info { "Creating LoggingAggregate for type=LOGGING" }
                LoggingAggregate(
                    logEveryN = config.logEvery,
                    streamDescriptor = streamDescriptor,
                    maxLogCount = config.maxEntryCount,
                    sampleRate = config.sampleRate,
                    seed = config.seed
                )
            }
            DevNullV2Configuration.Type.SILENT -> {
                log.info { "Creating SilentAggregate for type=SILENT" }
                SilentAggregate()
            }
            DevNullV2Configuration.Type.THROTTLED -> {
                log.info { "Creating ThrottledAggregate for type=THROTTLED" }
                ThrottledAggregate(config.millisPerRecord)
            }
            DevNullV2Configuration.Type.FAILING -> {
                log.info { "Creating FailingAggregate for type=FAILING" }
                FailingAggregate(streamDescriptor, config.numMessages)
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
