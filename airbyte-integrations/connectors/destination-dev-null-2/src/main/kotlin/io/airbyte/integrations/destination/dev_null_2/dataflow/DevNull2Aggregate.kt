/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_2.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.dataflow.transform.RecordDTO
import io.airbyte.integrations.destination.dev_null_2.DevNull2Configuration
import io.airbyte.integrations.destination.dev_null_2.Logging
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import kotlin.random.Random

private val log = KotlinLogging.logger {}

/**
 * Dev Null Aggregate - processes records according to configuration but doesn't persist them.
 * Supports logging, silent, throttled, and failing modes.
 */
class DevNull2Aggregate(
    private val config: DevNull2Configuration,
    private val streamName: String,
) : Aggregate {
    private var recordCount: Long = 0L
    private var logCount: Long = 0L
    private val prng: Random =
        when (val type = config.type) {
            is Logging -> type.seed?.let { Random(it) } ?: Random.Default
            else -> Random.Default
        }

    override fun accept(record: RecordDTO) {
        recordCount++

        when (val type = config.type) {
            is Logging -> {
                if (recordCount % type.logEvery == 0L) {
                    if (type.sampleRate == 1.0 || prng.nextDouble() < type.sampleRate) {
                        if (++logCount <= type.maxEntryCount) {
                            log.info {
                                "Logging Destination(stream=$streamName, recordIndex=$recordCount, " +
                                    "logEntry=$logCount/${type.maxEntryCount}): ${record.fields}"
                            }
                        }
                    }
                }
            }
            is io.airbyte.integrations.destination.dev_null_2.Silent -> {
                // Do nothing - silent mode
            }
            is io.airbyte.integrations.destination.dev_null_2.Throttled -> {
                Thread.sleep(type.millisPerRecord)
            }
            is io.airbyte.integrations.destination.dev_null_2.Failing -> {
                if (recordCount > type.numMessages) {
                    val message =
                        "Failing Destination(stream=$streamName, numMessages=${type.numMessages}): " +
                            "failing at record $recordCount"
                    log.info { message }
                    throw RuntimeException(message)
                }
            }
        }
    }

    override suspend fun flush() {
        // Nothing to flush - we don't persist data
        log.debug {
            "DevNull2Aggregate flush called for stream=$streamName, processed $recordCount records"
        }
    }
}

@Factory
class DevNull2AggregateFactory(
    private val config: DevNull2Configuration,
) {
    @Singleton
    fun aggregateFactory(): AggregateFactory {
        return object : AggregateFactory {
            override fun create(key: StoreKey): Aggregate {
                // StoreKey is a typealias for DestinationStream.Descriptor
                val streamName = "${key.namespace ?: "default"}.${key.name}"
                log.info {
                    "Creating DevNull2Aggregate for stream=$streamName with mode=${config.type::class.simpleName}"
                }
                return DevNull2Aggregate(config, streamName)
            }
        }
    }
}
