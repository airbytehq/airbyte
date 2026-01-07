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

abstract class DevNullV2Aggregate(
    private val config: DevNullV2Configuration,
    streamDescriptor: DestinationStream.Descriptor,
) : Aggregate {
    protected val log = KotlinLogging.logger {}
    protected var recordCount: Long = 0L
    
    abstract fun acceptInner(record: RecordDTO)
    
    override fun accept(record: RecordDTO) {
        acceptInner(record)
        recordCount++
    }
    
    override suspend fun flush() {
        /* Do nothing - dev-null doesn't persist data */
    }
}

@Singleton
class DevNullV2AggregateFactory(
    private val config: DevNullV2Configuration,
) : AggregateFactory {
    private val log = KotlinLogging.logger {}

    override fun create(
        key: StoreKey // This is actually DestinationStream.Descriptor
    ): Aggregate {
        val streamDescriptor = key as DestinationStream.Descriptor
        return when (config.mode) {
            "logging" -> {
                log.info {
                    "Creating LoggingAggregate for mode=logging"
                }
                LoggingAggregate(config, streamDescriptor)
            }
            "silent" -> {
                log.info {
                    "Creating SilentAggregate for mode=silent"
                }
                SilentAggregate(config, streamDescriptor)
            }
            "failing" -> {
                log.info {
                    "Creating FailingAggregate for mode=failing"
                }
                FailingAggregate(config, streamDescriptor)
            }
            else -> {
                log.info {
                    "Unknown mode ${config.mode}, defaulting to silent"
                }
                SilentAggregate(config, streamDescriptor)
            }
        }
    }
}

class LoggingAggregate(
    config: DevNullV2Configuration,
    private val streamDescriptor: DestinationStream.Descriptor,
) : DevNullV2Aggregate(config, streamDescriptor) {
    private val logEveryN = config.logEveryN
    private var logCount: Long = 0L
    private val maxLogCount: Int = 1000

    override fun acceptInner(record: RecordDTO) {
        if (recordCount % logEveryN == 0L) {
            if (++logCount <= maxLogCount) {
                log.info {
                    "Logging Destination(stream=$streamDescriptor, recordIndex=$recordCount, logEntry=$logCount/$maxLogCount): ${record.fields}"
                }
            }
        }
    }
}

class SilentAggregate(
    config: DevNullV2Configuration,
    streamDescriptor: DestinationStream.Descriptor,
) : DevNullV2Aggregate(config, streamDescriptor) {
    
    override fun acceptInner(record: RecordDTO) {
        /* Do nothing - silently discard */
    }
}

class FailingAggregate(
    config: DevNullV2Configuration,
    private val streamDescriptor: DestinationStream.Descriptor,
) : DevNullV2Aggregate(config, streamDescriptor) {
    private val failAfter: Int = 100

    override fun acceptInner(record: RecordDTO) {
        if (recordCount > failAfter) {
            val message =
                "Failing Destination(stream=$streamDescriptor, failAfter=$failAfter: failing at record $recordCount)"
            log.info { message }
            throw RuntimeException(message)
        }
    }
}