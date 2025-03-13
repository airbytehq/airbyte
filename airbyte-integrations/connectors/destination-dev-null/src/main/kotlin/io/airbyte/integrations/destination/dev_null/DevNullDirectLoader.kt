/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import kotlin.random.Random

/** Wraps the configured operation in logic that acks all state so far every N records. */
abstract class DevNullDirectLoader(
    private val config: DevNullConfiguration,
) : DirectLoader {
    private var recordCount: Long = 0L

    abstract fun acceptInner(record: DestinationRecordAirbyteValue)

    override fun accept(record: DestinationRecordAirbyteValue): DirectLoader.DirectLoadResult {
        acceptInner(record)
        return if (++recordCount % config.ackRatePerRecord == 0L) {
            DirectLoader.Complete
        } else {
            DirectLoader.Incomplete
        }
    }

    override fun finish() {
        /* do nothing */
    }

    override fun close() {
        /* do nothing */
    }
}

@Singleton
class DevNullDirectLoaderFactory(private val config: DevNullConfiguration) :
    DirectLoaderFactory<DevNullDirectLoader> {
    private val log = KotlinLogging.logger {}

    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): DevNullDirectLoader {
        return when (config.type) {
            is Logging -> {
                log.info {
                    "Creating LoggingDirectLoader for LoggingDestination. The File messages will be ignored"
                }
                LoggingDirectLoader(config, streamDescriptor, config.type)
            }
            is Silent -> {
                log.info {
                    "Creating SilentDirectLoader for SilentDestination. The File messages will be ignored"
                }
                SilentDirectLoader(config)
            }
            is Throttled -> {
                log.info {
                    "Creating ThrottledDirectLoader for ThrottledDestination. The File messages will be ignored"
                }
                ThrottledDirectLoader(config, config.type.millisPerRecord)
            }
            is Failing -> {
                log.info {
                    "Creating FailingDirectLoader for FailingDestination. The File messages will be ignored"
                }
                FailingDirectLoader(config, streamDescriptor, config.type.numMessages)
            }
        }
    }
}

class LoggingDirectLoader(
    config: DevNullConfiguration,
    private val stream: DestinationStream.Descriptor,
    private val loggingConfig: Logging,
) : DevNullDirectLoader(config) {
    private val log = KotlinLogging.logger {}

    private var recordCount: Long = 0L
    private var logCount: Long = 0L
    private val prng: Random = loggingConfig.seed?.let { Random(it) } ?: Random.Default

    override fun acceptInner(record: DestinationRecordAirbyteValue) {
        if (recordCount++ % loggingConfig.logEvery == 0L) {
            if (loggingConfig.sampleRate == 1.0 || prng.nextDouble() < loggingConfig.sampleRate) {
                if (++logCount < loggingConfig.maxEntryCount) {
                    log.info {
                        "Logging Destination(stream=$stream, recordIndex=$recordCount, logEntry=$logCount/${loggingConfig.maxEntryCount}): $record"
                    }
                }
            }
        }
    }
}

class SilentDirectLoader(config: DevNullConfiguration) : DevNullDirectLoader(config) {
    override fun acceptInner(record: DestinationRecordAirbyteValue) {
        /* Do nothing */
    }
}

class ThrottledDirectLoader(config: DevNullConfiguration, private val millisPerRecord: Long) :
    DevNullDirectLoader(config) {

    override fun acceptInner(record: DestinationRecordAirbyteValue) {
        Thread.sleep(millisPerRecord)
    }
}

class FailingDirectLoader(
    config: DevNullConfiguration,
    private val stream: DestinationStream.Descriptor,
    private val numMessages: Int
) : DevNullDirectLoader(config) {
    private val log = KotlinLogging.logger {}

    private var messageCount: Long = 0L

    override fun acceptInner(record: DestinationRecordAirbyteValue) {
        if (messageCount++ > numMessages) {
            val message =
                "Failing Destination(stream=$stream, numMessages=$numMessages: failing at $record)"
            log.info { message }
            throw RuntimeException(message)
        }
    }
}
