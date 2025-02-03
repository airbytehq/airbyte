/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import kotlin.random.Random
import kotlinx.coroutines.delay

@Singleton
class DevNullWriter(private val config: DevNullConfiguration) : DestinationWriter {
    private val log = KotlinLogging.logger {}

    override fun createStreamLoader(stream: DestinationStream): StreamLoader {
        return when (config.type) {
            is Logging -> {
                log.info {
                    "Creating LoggingStreamLoader for LoggingDestination. The File messages will be ignored"
                }
                LoggingStreamLoader(stream, config.type)
            }
            is Silent -> {
                log.info {
                    "Creating SilentStreamLoader for SilentDestination. The File messages will be ignored"
                }
                SilentStreamLoader(stream)
            }
            is Throttled -> {
                log.info {
                    "Creating ThrottledStreamLoader for ThrottledDestination. The File messages will be ignored"
                }
                ThrottledStreamLoader(stream, config.type.millisPerRecord)
            }
            is Failing -> {
                log.info {
                    "Creating FailingStreamLoader for FailingDestination. The File messages will be ignored"
                }
                FailingStreamLoader(stream, config.type.numMessages)
            }
        }
    }
}

class LoggingStreamLoader(override val stream: DestinationStream, loggingConfig: Logging) :
    StreamLoader {
    private val log = KotlinLogging.logger {}

    private val maxEntryCount: Int = loggingConfig.maxEntryCount
    private val logEvery: Int = loggingConfig.logEvery
    private val sampleRate: Double = loggingConfig.sampleRate
    private val prng: Random = loggingConfig.seed?.let { Random(it) } ?: Random.Default

    companion object {
        private val recordCount = AtomicLong()
        private val logCount = AtomicLong()
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean,
    ): Batch {
        log.info { "Processing record batch with logging" }

        records.forEach { record ->
            if (recordCount.getAndIncrement() % logEvery == 0L) {
                if (sampleRate == 1.0 || prng.nextDouble() < sampleRate) {
                    if (logCount.incrementAndGet() < maxEntryCount) {
                        log.info {
                            "Logging Destination(stream=$stream, recordIndex=$recordCount, logEntry=$logCount/$maxEntryCount): $record"
                        }
                    }
                }
            }
        }

        log.info { "Completed record batch." }

        return SimpleBatch(state = Batch.State.COMPLETE)
    }
}

class SilentStreamLoader(override val stream: DestinationStream) : StreamLoader {
    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        return SimpleBatch(state = Batch.State.COMPLETE)
    }
}

@SuppressFBWarnings(
    "NP_NONNULL_PARAM_VIOLATION",
    justification = "message is guaranteed to be non-null by Kotlin's type system"
)
class ThrottledStreamLoader(
    override val stream: DestinationStream,
    private val millisPerRecord: Long
) : StreamLoader {
    private val log = KotlinLogging.logger {}

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        log.info { "Processing record batch with delay of $millisPerRecord per record" }

        records.forEach { _ -> delay(millisPerRecord) }
        log.info { "Completed record batch." }

        return SimpleBatch(state = Batch.State.COMPLETE)
    }
}

class FailingStreamLoader(override val stream: DestinationStream, private val numMessages: Int) :
    StreamLoader {
    private val log = KotlinLogging.logger {}

    companion object {
        private val messageCount = AtomicInteger(0)
    }

    override suspend fun processRecords(
        records: Iterator<DestinationRecordAirbyteValue>,
        totalSizeBytes: Long,
        endOfStream: Boolean
    ): Batch {
        log.info { "Processing record batch with failure after $numMessages messages" }

        records.forEach { record ->
            messageCount.getAndIncrement().let { messageCount ->
                if (messageCount > numMessages) {
                    val message =
                        "Failing Destination(stream=$stream, numMessages=$numMessages: failing at $record"
                    log.info { message }
                    throw RuntimeException(message)
                }
            }
        }
        log.info { "Completed record batch." }

        return SimpleBatch(state = Batch.State.COMPLETE)
    }
}
